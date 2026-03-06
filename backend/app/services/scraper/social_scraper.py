"""
Social Media Scraper Service — API-based data ingestion.

Each platform client uses ONLY official APIs. No unauthorized scraping.
All clients implement the BaseScraper interface for consistency.

Rate limit handling:
- Twitter API v2: 300 requests/15-min (app-level)
- Reddit API: 60 requests/minute
- Meta Graph API: 200 requests/hour
- All use exponential backoff via tenacity
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.db.redis import cache_get, cache_set

logger = get_logger(__name__)
settings = get_settings()


# ── Base Interface ──────────────────────────────────────────────────────

class BaseScraper(ABC):
    """Interface for all platform scrapers."""

    @abstractmethod
    async def fetch_trending(self, limit: int = 50) -> list[dict]:
        """Fetch current trending topics/posts."""
        ...

    @abstractmethod
    async def fetch_topic_posts(self, topic: str, limit: int = 100) -> list[dict]:
        """Fetch posts related to a specific topic."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify API connectivity."""
        ...


# ── Twitter/X API v2 Client ────────────────────────────────────────────

class TwitterScraper(BaseScraper):
    """
    Twitter/X data ingestion using API v2.
    
    Requires: Twitter API Bearer Token (Academic or Pro tier for full access).
    Uses: /2/trends, /2/tweets/search/recent
    """

    BASE_URL = "https://api.twitter.com/2"

    def __init__(self):
        self.bearer_token = settings.twitter_bearer_token
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.bearer_token}",
                "User-Agent": "TrendForge/0.1",
            },
            timeout=30.0,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
    async def fetch_trending(self, limit: int = 50) -> list[dict]:
        """Fetch trending topics from Twitter."""
        cache_key = "twitter:trending"
        cached = await cache_get(cache_key)
        if cached:
            import orjson
            return orjson.loads(cached)

        try:
            # Use search/recent with high-engagement filter as trending proxy
            response = await self.client.get(
                "/tweets/search/recent",
                params={
                    "query": "lang:en -is:retweet has:media min_faves:1000",
                    "max_results": min(limit, 100),
                    "tweet.fields": "public_metrics,created_at,entities,context_annotations,lang",
                    "expansions": "author_id",
                    "user.fields": "public_metrics,verified",
                },
            )
            response.raise_for_status()
            data = response.json()

            trends = []
            for tweet in data.get("data", []):
                metrics = tweet.get("public_metrics", {})
                trends.append({
                    "platform": "twitter",
                    "external_id": tweet["id"],
                    "title": tweet["text"][:512],
                    "description": tweet["text"],
                    "raw_content": tweet,
                    "source_url": f"https://twitter.com/i/status/{tweet['id']}",
                    "engagement_metrics": {
                        "likes": metrics.get("like_count", 0),
                        "shares": metrics.get("retweet_count", 0),
                        "comments": metrics.get("reply_count", 0),
                        "impressions": metrics.get("impression_count", 0),
                    },
                    "detected_at": tweet.get("created_at", datetime.now(timezone.utc).isoformat()),
                })

            # Cache for 5 minutes
            import orjson
            await cache_set(cache_key, orjson.dumps(trends).decode(), ttl=300)

            logger.info("twitter_trending_fetched", count=len(trends))
            return trends

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning("twitter_rate_limited")
                raise
            raise ExternalServiceError("twitter", str(e))
        except Exception as e:
            raise ExternalServiceError("twitter", str(e))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
    async def fetch_topic_posts(self, topic: str, limit: int = 100) -> list[dict]:
        """Search tweets by topic."""
        cache_key = f"twitter:topic:{topic}"
        cached = await cache_get(cache_key)
        if cached:
            import orjson
            return orjson.loads(cached)

        try:
            response = await self.client.get(
                "/tweets/search/recent",
                params={
                    "query": f"{topic} lang:en -is:retweet",
                    "max_results": min(limit, 100),
                    "tweet.fields": "public_metrics,created_at,entities,context_annotations",
                    "sort_order": "relevancy",
                },
            )
            response.raise_for_status()
            data = response.json()

            posts = []
            for tweet in data.get("data", []):
                metrics = tweet.get("public_metrics", {})
                posts.append({
                    "platform": "twitter",
                    "external_id": tweet["id"],
                    "title": tweet["text"][:512],
                    "raw_content": tweet,
                    "engagement_metrics": {
                        "likes": metrics.get("like_count", 0),
                        "shares": metrics.get("retweet_count", 0),
                        "comments": metrics.get("reply_count", 0),
                    },
                })

            import orjson
            await cache_set(cache_key, orjson.dumps(posts).decode(), ttl=300)
            return posts

        except httpx.HTTPStatusError as e:
            raise ExternalServiceError("twitter", str(e))

    async def health_check(self) -> bool:
        try:
            response = await self.client.get("/tweets/search/recent", params={"query": "test", "max_results": 10})
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        await self.client.aclose()


# ── Reddit API Client ──────────────────────────────────────────────────

class RedditScraper(BaseScraper):
    """
    Reddit data ingestion using official OAuth2 API.
    
    Requires: Reddit app credentials (script or web type).
    Uses: /r/subreddit/hot, /r/popular, /search
    """

    AUTH_URL = "https://www.reddit.com/api/v1/access_token"
    BASE_URL = "https://oauth.reddit.com"

    def __init__(self):
        self.client_id = settings.reddit_client_id
        self.client_secret = settings.reddit_client_secret
        self.user_agent = settings.reddit_user_agent
        self._access_token: str | None = None
        self._token_expires: datetime | None = None
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"User-Agent": self.user_agent},
            timeout=30.0,
        )

    async def _authenticate(self) -> None:
        """Obtain OAuth2 access token."""
        if self._access_token and self._token_expires and datetime.now(timezone.utc) < self._token_expires:
            return

        auth_client = httpx.AsyncClient()
        try:
            response = await auth_client.post(
                self.AUTH_URL,
                auth=(self.client_id, self.client_secret),
                data={"grant_type": "client_credentials"},
                headers={"User-Agent": self.user_agent},
            )
            response.raise_for_status()
            data = response.json()
            self._access_token = data["access_token"]
            self._token_expires = datetime.now(timezone.utc) + timedelta(seconds=data.get("expires_in", 3600) - 60)
            self.client.headers["Authorization"] = f"Bearer {self._access_token}"
            logger.info("reddit_authenticated")
        finally:
            await auth_client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
    async def fetch_trending(self, limit: int = 50) -> list[dict]:
        """Fetch trending posts from Reddit popular."""
        cache_key = "reddit:trending"
        cached = await cache_get(cache_key)
        if cached:
            import orjson
            return orjson.loads(cached)

        await self._authenticate()

        try:
            response = await self.client.get(
                "/r/popular/hot",
                params={"limit": min(limit, 100), "raw_json": 1},
            )
            response.raise_for_status()
            data = response.json()

            trends = []
            for post in data.get("data", {}).get("children", []):
                post_data = post["data"]
                trends.append({
                    "platform": "reddit",
                    "external_id": post_data["id"],
                    "title": post_data.get("title", "")[:512],
                    "description": post_data.get("selftext", "")[:2000],
                    "raw_content": {
                        "subreddit": post_data.get("subreddit"),
                        "author": post_data.get("author"),
                        "url": post_data.get("url"),
                        "is_video": post_data.get("is_video", False),
                        "link_flair_text": post_data.get("link_flair_text"),
                    },
                    "source_url": f"https://reddit.com{post_data.get('permalink', '')}",
                    "engagement_metrics": {
                        "likes": post_data.get("ups", 0),
                        "shares": 0,
                        "comments": post_data.get("num_comments", 0),
                        "upvote_ratio": post_data.get("upvote_ratio", 0),
                    },
                    "detected_at": datetime.fromtimestamp(
                        post_data.get("created_utc", 0), tz=timezone.utc
                    ).isoformat(),
                })

            import orjson
            await cache_set(cache_key, orjson.dumps(trends).decode(), ttl=300)

            logger.info("reddit_trending_fetched", count=len(trends))
            return trends

        except httpx.HTTPStatusError as e:
            raise ExternalServiceError("reddit", str(e))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
    async def fetch_topic_posts(self, topic: str, limit: int = 100) -> list[dict]:
        """Search Reddit posts by topic."""
        await self._authenticate()

        try:
            response = await self.client.get(
                "/search",
                params={
                    "q": topic,
                    "sort": "relevance",
                    "t": "week",
                    "limit": min(limit, 100),
                    "raw_json": 1,
                },
            )
            response.raise_for_status()
            data = response.json()

            posts = []
            for post in data.get("data", {}).get("children", []):
                post_data = post["data"]
                posts.append({
                    "platform": "reddit",
                    "external_id": post_data["id"],
                    "title": post_data.get("title", "")[:512],
                    "description": post_data.get("selftext", "")[:2000],
                    "raw_content": post_data,
                    "engagement_metrics": {
                        "likes": post_data.get("ups", 0),
                        "comments": post_data.get("num_comments", 0),
                    },
                })

            return posts

        except httpx.HTTPStatusError as e:
            raise ExternalServiceError("reddit", str(e))

    async def health_check(self) -> bool:
        try:
            await self._authenticate()
            response = await self.client.get("/r/popular/hot", params={"limit": 1})
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        await self.client.aclose()


# ── Meta Graph API Client ──────────────────────────────────────────────

class MetaScraper(BaseScraper):
    """
    Meta (Instagram/Facebook) data ingestion using Graph API.
    
    Requires: Meta Business App with Instagram Graph API access.
    Limited to business account insights and public page data.
    
    Compliance note: Only accesses data permitted by Meta's Graph API ToS.
    Does not scrape private profiles or use undocumented endpoints.
    """

    BASE_URL = "https://graph.facebook.com/v19.0"

    def __init__(self):
        self.access_token = settings.meta_access_token
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
    async def fetch_trending(self, limit: int = 50) -> list[dict]:
        """
        Fetch trending content from Instagram/Facebook.
        
        Note: Meta doesn't expose a public "trending" endpoint.
        We use hashtag search and high-engagement public page posts as proxy.
        """
        cache_key = "meta:trending"
        cached = await cache_get(cache_key)
        if cached:
            import orjson
            return orjson.loads(cached)

        trends = []

        # Fetch from popular hashtags (requires Instagram Graph API)
        trending_hashtags = ["marketing", "business", "trending", "viral", "ai"]
        
        for hashtag in trending_hashtags[:5]:  # Rate limit conscious
            try:
                # Step 1: Get hashtag ID
                ig_response = await self.client.get(
                    "/ig_hashtag_search",
                    params={
                        "q": hashtag,
                        "access_token": self.access_token,
                    },
                )
                if ig_response.status_code != 200:
                    continue

                hashtag_data = ig_response.json().get("data", [])
                if not hashtag_data:
                    continue

                hashtag_id = hashtag_data[0]["id"]

                # Step 2: Get top media for this hashtag
                media_response = await self.client.get(
                    f"/{hashtag_id}/top_media",
                    params={
                        "fields": "id,caption,like_count,comments_count,media_type,timestamp,permalink",
                        "access_token": self.access_token,
                    },
                )
                if media_response.status_code != 200:
                    continue

                for media in media_response.json().get("data", [])[:10]:
                    trends.append({
                        "platform": "instagram",
                        "external_id": media.get("id", ""),
                        "title": (media.get("caption", "") or "")[:512],
                        "description": media.get("caption", ""),
                        "raw_content": media,
                        "source_url": media.get("permalink", ""),
                        "engagement_metrics": {
                            "likes": media.get("like_count", 0),
                            "comments": media.get("comments_count", 0),
                        },
                        "detected_at": media.get("timestamp", datetime.now(timezone.utc).isoformat()),
                    })

            except Exception as e:
                logger.warning("meta_hashtag_fetch_failed", hashtag=hashtag, error=str(e))
                continue

        import orjson
        await cache_set(cache_key, orjson.dumps(trends).decode(), ttl=600)  # Cache 10 min
        
        logger.info("meta_trending_fetched", count=len(trends))
        return trends

    async def fetch_topic_posts(self, topic: str, limit: int = 100) -> list[dict]:
        """Search Meta content by topic (limited by API capabilities)."""
        return await self.fetch_trending(limit=limit)

    async def health_check(self) -> bool:
        try:
            response = await self.client.get("/me", params={"access_token": self.access_token})
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        await self.client.aclose()


# ── Aggregator ──────────────────────────────────────────────────────────

class ScraperAggregator:
    """
    Orchestrates multiple platform scrapers and aggregates results.
    
    Runs platform fetches concurrently and handles partial failures gracefully.
    If one platform fails, results from others are still returned.
    """

    def __init__(self):
        self.scrapers: dict[str, BaseScraper] = {}
        self._init_scrapers()

    def _init_scrapers(self) -> None:
        """Initialize scrapers based on available API credentials."""
        if settings.twitter_bearer_token:
            self.scrapers["twitter"] = TwitterScraper()
            logger.info("scraper_initialized", platform="twitter")

        if settings.reddit_client_id and settings.reddit_client_secret:
            self.scrapers["reddit"] = RedditScraper()
            logger.info("scraper_initialized", platform="reddit")

        if settings.meta_access_token:
            self.scrapers["meta"] = MetaScraper()
            logger.info("scraper_initialized", platform="meta")

        if not self.scrapers:
            logger.warning("no_scrapers_configured", message="No social API credentials found")

    async def fetch_all_trending(self, limit_per_platform: int = 50) -> list[dict]:
        """
        Fetch trending content from all configured platforms concurrently.
        
        Returns aggregated list sorted by engagement metrics.
        """
        import asyncio

        tasks = {
            name: scraper.fetch_trending(limit=limit_per_platform)
            for name, scraper in self.scrapers.items()
        }

        results: list[dict] = []
        for name, coro in tasks.items():
            try:
                platform_results = await coro
                results.extend(platform_results)
                logger.info("platform_trends_fetched", platform=name, count=len(platform_results))
            except Exception as e:
                logger.error("platform_fetch_failed", platform=name, error=str(e))
                # Continue with other platforms — fail gracefully

        # Sort by total engagement
        results.sort(
            key=lambda x: sum(x.get("engagement_metrics", {}).values()),
            reverse=True,
        )

        logger.info("all_trends_aggregated", total=len(results))
        return results

    async def health_check_all(self) -> dict[str, bool]:
        """Check health of all configured scrapers."""
        results = {}
        for name, scraper in self.scrapers.items():
            results[name] = await scraper.health_check()
        return results

    async def close_all(self) -> None:
        """Close all scraper HTTP clients."""
        for scraper in self.scrapers.values():
            await scraper.close()
