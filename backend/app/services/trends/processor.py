"""
Trend Processing Pipeline.

Takes raw social media data and transforms it into structured Trend objects:
1. Text normalization
2. Keyword extraction
3. Sentiment analysis
4. Content format detection
5. Engagement velocity calculation
6. Trend scoring
7. Vector embedding generation

Scoring Algorithm:
──────────────────
trend_score = (engagement_velocity_norm * 0.35)
            + (volume_norm * 0.25)
            + (sentiment_magnitude * 0.15)
            + (recency_factor * 0.25)

Where:
- engagement_velocity_norm = min(velocity / max_velocity, 1.0)
- volume_norm = min(volume / max_volume, 1.0)
- sentiment_magnitude = abs(sentiment_score)  # Strong sentiment = more interesting
- recency_factor = exp(-0.1 * hours_since_detection)
"""

import math
import re
from datetime import datetime, timezone
from uuid import uuid4

import httpx
from textblob import TextBlob

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class TrendProcessor:
    """
    Processes raw social media data into structured, scored trend objects.
    
    This is a stateless processor — call process_batch() with raw data
    and get back enriched trend dictionaries ready for database insertion.
    """

    # Engagement velocity thresholds for normalization
    MAX_VELOCITY = 10000  # engagements per hour
    MAX_VOLUME = 100000   # total post count
    RECENCY_DECAY_LAMBDA = 0.1  # Half-life ≈ 7 hours

    # Content format detection patterns
    FORMAT_PATTERNS = {
        "thread": [r"🧵", r"\bthread\b", r"1/\d+", r"\(1/\d+\)"],
        "meme": [r"\bmeme\b", r"😂{2,}", r"💀{2,}", r"\bbruh\b"],
        "carousel": [r"\bswipe\b", r"\bcarousel\b", r"👉", r"slide \d+"],
        "poll": [r"\bpoll\b", r"\bvote\b", r"option [a-d]", r"🗳"],
        "video": [r"\bvideo\b", r"\bwatch\b", r"\breel\b", r"\btiktok\b"],
        "image": [r"\bphoto\b", r"\bpic\b", r"\bimage\b", r"📸"],
    }

    def __init__(self):
        self.embedding_client = httpx.AsyncClient(
            base_url="https://api.openai.com/v1",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            timeout=30.0,
        )

    async def process_batch(self, raw_trends: list[dict]) -> list[dict]:
        """
        Process a batch of raw trend data into enriched trend objects.
        
        Input: list of dicts from ScraperAggregator
        Output: list of dicts ready for Trend model insertion
        """
        processed = []
        for raw in raw_trends:
            try:
                trend = await self._process_single(raw)
                processed.append(trend)
            except Exception as e:
                logger.warning(
                    "trend_processing_failed",
                    external_id=raw.get("external_id"),
                    error=str(e),
                )
                continue

        # Normalize scores relative to batch
        if processed:
            processed = self._normalize_scores(processed)

        logger.info("batch_processed", input_count=len(raw_trends), output_count=len(processed))
        return processed

    async def _process_single(self, raw: dict) -> dict:
        """Process a single raw trend into enriched format."""
        text = f"{raw.get('title', '')} {raw.get('description', '')}"
        clean_text = self._clean_text(text)

        # NLP analysis
        keywords = self._extract_keywords(clean_text)
        sentiment = self._analyze_sentiment(clean_text)
        content_format = self._detect_content_format(text)

        # Engagement metrics
        metrics = raw.get("engagement_metrics", {})
        total_engagement = sum(metrics.values())
        
        # Calculate velocity (engagement per hour since detection)
        detected_at = raw.get("detected_at")
        if isinstance(detected_at, str):
            try:
                detected_at = datetime.fromisoformat(detected_at.replace("Z", "+00:00"))
            except ValueError:
                detected_at = datetime.now(timezone.utc)
        elif detected_at is None:
            detected_at = datetime.now(timezone.utc)

        hours_since = max(
            (datetime.now(timezone.utc) - detected_at).total_seconds() / 3600,
            0.1,  # Avoid division by zero
        )
        velocity = total_engagement / hours_since

        # Recency factor
        recency = math.exp(-self.RECENCY_DECAY_LAMBDA * hours_since)

        # Generate embedding
        embedding = await self._generate_embedding(clean_text)

        return {
            "id": str(uuid4()),
            "platform": raw.get("platform", "twitter"),
            "external_id": raw.get("external_id"),
            "source_url": raw.get("source_url"),
            "title": raw.get("title", "")[:512],
            "description": raw.get("description", ""),
            "raw_content": raw.get("raw_content", {}),
            "keywords": keywords,
            "topics": keywords[:5],  # Top keywords as topics
            "content_format": content_format,
            "sentiment_score": sentiment["score"],
            "sentiment_label": sentiment["label"],
            "engagement_score": float(total_engagement),
            "engagement_velocity": velocity,
            "volume": metrics.get("impressions", total_engagement),
            "engagement_metrics": metrics,
            "recency_factor": recency,
            "embedding": embedding,
            "detected_at": detected_at.isoformat(),
            "is_active": True,
            # Trend score calculated after batch normalization
            "trend_score": 0.0,
        }

    def _clean_text(self, text: str) -> str:
        """Normalize text for NLP processing."""
        # Remove URLs
        text = re.sub(r"https?://\S+", "", text)
        # Remove mentions
        text = re.sub(r"@\w+", "", text)
        # Remove excessive hashtags but keep words
        text = re.sub(r"#(\w+)", r"\1", text)
        # Remove emojis (keep for format detection, remove for NLP)
        text = re.sub(
            r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]",
            "",
            text,
        )
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _extract_keywords(self, text: str, max_keywords: int = 10) -> list[str]:
        """
        Extract keywords using TextBlob noun phrases + frequency analysis.
        
        For production at scale, replace with KeyBERT or a fine-tuned model.
        """
        blob = TextBlob(text.lower())

        # Extract noun phrases
        noun_phrases = list(set(blob.noun_phrases))

        # Extract single-word nouns with frequency
        words = blob.words
        # Filter stopwords and short words
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "can", "shall",
            "this", "that", "these", "those", "i", "you", "he", "she",
            "it", "we", "they", "me", "him", "her", "us", "them",
            "my", "your", "his", "its", "our", "their", "what", "which",
            "who", "whom", "when", "where", "why", "how", "not", "no",
            "but", "or", "and", "if", "so", "just", "get", "got",
        }
        filtered = [w for w in words if len(w) > 2 and w not in stopwords]

        # Frequency-based ranking
        freq: dict[str, int] = {}
        for w in filtered:
            freq[w] = freq.get(w, 0) + 1

        single_keywords = sorted(freq.keys(), key=lambda x: freq[x], reverse=True)

        # Combine noun phrases and single keywords, deduplicate
        all_keywords = noun_phrases + single_keywords
        seen: set[str] = set()
        deduped: list[str] = []
        for kw in all_keywords:
            if kw not in seen:
                seen.add(kw)
                deduped.append(kw)

        return deduped[:max_keywords]

    def _analyze_sentiment(self, text: str) -> dict:
        """
        Analyze sentiment using TextBlob.
        
        Returns score (-1.0 to 1.0) and categorical label.
        For production, consider fine-tuned BERT sentiment model.
        """
        blob = TextBlob(text)
        score = blob.sentiment.polarity  # -1.0 to 1.0

        if score >= 0.5:
            label = "very_positive"
        elif score >= 0.1:
            label = "positive"
        elif score > -0.1:
            label = "neutral"
        elif score > -0.5:
            label = "negative"
        else:
            label = "very_negative"

        return {"score": round(score, 4), "label": label}

    def _detect_content_format(self, text: str) -> str:
        """Detect content format from text patterns."""
        text_lower = text.lower()
        for format_name, patterns in self.FORMAT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return format_name
        return "text"

    async def _generate_embedding(self, text: str) -> list[float] | None:
        """
        Generate vector embedding using OpenAI's embedding model.
        
        Falls back to None if API is unavailable.
        """
        if not settings.openai_api_key:
            return None

        try:
            response = await self.embedding_client.post(
                "/embeddings",
                json={
                    "input": text[:8000],  # Token limit safety
                    "model": settings.embedding_model,
                    "dimensions": settings.embedding_dimensions,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
        except Exception as e:
            logger.warning("embedding_generation_failed", error=str(e))
            return None

    def _normalize_scores(self, trends: list[dict]) -> list[dict]:
        """
        Normalize and calculate final trend scores for a batch.
        
        Scores are relative to the batch to handle varying baseline engagement
        across platforms.
        """
        if not trends:
            return trends

        # Find max values for normalization
        max_velocity = max(t["engagement_velocity"] for t in trends) or 1.0
        max_volume = max(t.get("volume", 0) for t in trends) or 1.0

        for trend in trends:
            velocity_norm = min(trend["engagement_velocity"] / max_velocity, 1.0)
            volume_norm = min(trend.get("volume", 0) / max_volume, 1.0)
            sentiment_magnitude = abs(trend["sentiment_score"])
            recency = trend.get("recency_factor", 1.0)

            # Weighted composite score
            trend["trend_score"] = round(
                (velocity_norm * 0.35)
                + (volume_norm * 0.25)
                + (sentiment_magnitude * 0.15)
                + (recency * 0.25),
                4,
            )

        # Sort by score descending
        trends.sort(key=lambda t: t["trend_score"], reverse=True)
        return trends

    async def close(self):
        await self.embedding_client.aclose()
