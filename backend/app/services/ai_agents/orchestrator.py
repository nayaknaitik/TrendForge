"""
Agent Orchestrator — Multi-Agent Pipeline Controller.

Chains AI agents in a deterministic pipeline:

    Trend → [Trend Classifier] 
          → [Brand Relevance + filter] 
          → [Campaign Strategist] 
          → [Copy Generator × N platforms] 
          → [Performance Heuristic × N copies]
          → Final Campaign Output

Design choices:
- Sequential where dependencies exist (strategy before copy)
- Parallel where independent (copy generation across platforms)
- Fail-fast on irrelevant trends (Brand Relevance rejects early)
- Graceful degradation (copy still generated if heuristic fails)
"""

import asyncio
from uuid import uuid4

from app.core.logging import get_logger
from app.schemas.schemas import (
    AdFormat,
    AdPlatform,
    BrandRelevanceInput,
    CampaignObjective,
    CampaignStrategyInput,
    CopyGeneratorInput,
    PerformanceHeuristicInput,
    PlatformType,
    TrendClassifierInput,
)
from app.services.ai_agents.base import LLMClient
from app.services.ai_agents.brand_relevance import BrandRelevanceAgent
from app.services.ai_agents.campaign_strategist import CampaignStrategistAgent
from app.services.ai_agents.copy_generator import CopyGeneratorAgent
from app.services.ai_agents.performance_heuristic import PerformanceHeuristicAgent
from app.services.ai_agents.trend_classifier import TrendClassifierAgent

logger = get_logger(__name__)


class AgentOrchestrator:
    """
    Orchestrates the multi-agent pipeline for campaign generation.
    
    Pipeline:
    ─────────
    1. Trend Classification (enrich raw trend data)
    2. Brand Relevance Scoring (filter irrelevant trends)
    3. Campaign Strategy Generation (create campaign plan)
    4. Copy Generation (produce ad variations per platform)
    5. Performance Estimation (score each variation)
    
    The orchestrator manages:
    - Agent instantiation with shared LLM client
    - Pipeline execution order
    - Error handling and partial result collection
    - Parallel execution where possible
    """

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm = llm_client or LLMClient()
        self.trend_classifier = TrendClassifierAgent(self.llm)
        self.brand_relevance = BrandRelevanceAgent(self.llm)
        self.campaign_strategist = CampaignStrategistAgent(self.llm)
        self.copy_generator = CopyGeneratorAgent(self.llm)
        self.performance_heuristic = PerformanceHeuristicAgent(self.llm)

    async def classify_trend(self, raw_content: str, platform: str, metadata: dict | None = None) -> dict:
        """
        Step 1: Classify a trend.
        
        Returns enriched trend classification.
        """
        request_id = str(uuid4())
        
        input_data = TrendClassifierInput(
            request_id=request_id,
            raw_content=raw_content,
            platform=PlatformType(platform),
            metadata=metadata or {},
        )

        result = await self.trend_classifier.run(input_data)
        logger.info("trend_classified", request_id=request_id, topics=result.topics)
        return result.model_dump()

    async def score_brand_relevance(self, brand_profile: dict, trend_data: dict) -> dict:
        """
        Step 2: Score brand-trend relevance.
        
        Returns relevance scores. Caller decides whether to proceed based on threshold.
        """
        request_id = str(uuid4())

        input_data = BrandRelevanceInput(
            request_id=request_id,
            brand_profile=brand_profile,
            trend_data=trend_data,
        )

        result = await self.brand_relevance.run(input_data)
        logger.info(
            "brand_relevance_scored",
            request_id=request_id,
            relevance=result.relevance_score,
            is_relevant=result.is_relevant,
        )
        return result.model_dump()

    async def generate_campaign(
        self,
        brand_profile: dict,
        trend_data: dict,
        objective: str,
        target_platforms: list[str] | None = None,
        num_variations: int = 3,
        custom_instructions: str | None = None,
    ) -> dict:
        """
        Full pipeline: Generate a complete campaign from brand + trend.
        
        Executes the full agent chain:
        1. Check brand relevance
        2. Create campaign strategy
        3. Generate platform-specific copy (parallel across platforms)
        4. Score each variation (parallel)
        
        Args:
            brand_profile: Complete brand profile dict
            trend_data: Enriched trend data dict
            objective: Campaign objective (e.g., "brand_awareness")
            target_platforms: List of platforms to generate for (auto-selected if None)
            num_variations: Number of copy variations per platform
            custom_instructions: Optional user guidance for the campaign
            
        Returns:
            Complete campaign dict with strategy, copies, and performance estimates
        """
        pipeline_id = str(uuid4())
        logger.info("campaign_pipeline_started", pipeline_id=pipeline_id)

        # ── Step 1: Brand Relevance Check ───────────────────────────
        relevance = await self.score_brand_relevance(brand_profile, trend_data)

        if not relevance["is_relevant"]:
            logger.info(
                "campaign_rejected_irrelevant",
                pipeline_id=pipeline_id,
                score=relevance["relevance_score"],
            )
            return {
                "pipeline_id": pipeline_id,
                "status": "rejected",
                "reason": "Trend not relevant to brand",
                "relevance": relevance,
                "strategy": None,
                "ad_copies": [],
            }

        # ── Step 2: Campaign Strategy ───────────────────────────────
        strategy_input = CampaignStrategyInput(
            request_id=pipeline_id,
            brand_profile=brand_profile,
            trend_data=trend_data,
            objective=CampaignObjective(objective),
            custom_instructions=custom_instructions,
        )
        strategy_result = await self.campaign_strategist.run(strategy_input)
        strategy = strategy_result.model_dump()

        # Determine target platforms
        platforms = target_platforms or strategy.get("target_platforms", ["twitter", "instagram"])

        # ── Step 3: Generate Copy for Each Platform (Parallel) ──────
        copy_tasks = []
        for platform in platforms:
            try:
                ad_platform = AdPlatform(platform)
            except ValueError:
                continue

            copy_input = CopyGeneratorInput(
                request_id=pipeline_id,
                brand_profile=brand_profile,
                campaign_strategy=strategy,
                platform=ad_platform,
                format_type=self._select_format_for_platform(ad_platform),
                num_variations=num_variations,
            )
            copy_tasks.append((platform, self.copy_generator.run(copy_input)))

        # Execute copy generation concurrently
        all_copies = []
        for platform, task in copy_tasks:
            try:
                result = await task
                for variation in result.variations:
                    variation["platform"] = platform
                    all_copies.append(variation)
            except Exception as e:
                logger.error("copy_generation_failed", platform=platform, error=str(e))

        # ── Step 4: Performance Estimation (Parallel) ───────────────
        performance_tasks = []
        for copy in all_copies:
            try:
                perf_input = PerformanceHeuristicInput(
                    request_id=pipeline_id,
                    ad_copy=copy,
                    platform=AdPlatform(copy["platform"]),
                    trend_data=trend_data,
                    brand_profile=brand_profile,
                )
                performance_tasks.append((copy, self.performance_heuristic.run(perf_input)))
            except Exception:
                continue

        for copy, task in performance_tasks:
            try:
                perf_result = await task
                copy["performance"] = perf_result.model_dump()
            except Exception as e:
                logger.warning("performance_estimation_failed", error=str(e))
                copy["performance"] = {
                    "predicted_engagement_rate": 0.02,
                    "confidence_level": "low",
                    "reasoning": "Performance estimation failed; using default",
                    "optimization_suggestions": [],
                }

        # Sort copies by predicted engagement
        all_copies.sort(
            key=lambda c: c.get("performance", {}).get("predicted_engagement_rate", 0),
            reverse=True,
        )

        logger.info(
            "campaign_pipeline_completed",
            pipeline_id=pipeline_id,
            copies_generated=len(all_copies),
        )

        return {
            "pipeline_id": pipeline_id,
            "status": "completed",
            "relevance": relevance,
            "strategy": strategy,
            "ad_copies": all_copies,
        }

    def _select_format_for_platform(self, platform: AdPlatform) -> AdFormat:
        """Select optimal ad format based on platform conventions."""
        format_map = {
            AdPlatform.twitter: AdFormat.single_post,
            AdPlatform.instagram: AdFormat.carousel,
            AdPlatform.facebook: AdFormat.ad_copy,
            AdPlatform.linkedin: AdFormat.single_post,
            AdPlatform.tiktok: AdFormat.reel_script,
            AdPlatform.reddit: AdFormat.single_post,
        }
        return format_map.get(platform, AdFormat.single_post)

    async def batch_score_trends(
        self, brand_profile: dict, trends: list[dict], min_relevance: float = 0.65
    ) -> list[dict]:
        """
        Score multiple trends against a brand in parallel.
        
        Returns only trends that meet the relevance threshold, sorted by score.
        """
        async def score_one(trend: dict) -> dict | None:
            try:
                result = await self.score_brand_relevance(brand_profile, trend)
                if result["relevance_score"] >= min_relevance:
                    return {**trend, "relevance": result}
                return None
            except Exception as e:
                logger.warning("trend_scoring_failed", trend_id=trend.get("id"), error=str(e))
                return None

        # Run all scoring in parallel with concurrency limit
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent LLM calls

        async def limited_score(trend: dict) -> dict | None:
            async with semaphore:
                return await score_one(trend)

        results = await asyncio.gather(*[limited_score(t) for t in trends])
        relevant = [r for r in results if r is not None]
        relevant.sort(key=lambda x: x["relevance"]["relevance_score"], reverse=True)

        logger.info(
            "batch_scoring_completed",
            total=len(trends),
            relevant=len(relevant),
        )
        return relevant
