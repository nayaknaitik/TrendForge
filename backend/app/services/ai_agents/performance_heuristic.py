"""
Performance Heuristic Agent (MVP).

Responsibilities:
- Estimate likely engagement rate for generated ad copy
- Provide confidence levels for predictions
- Suggest optimizations to improve performance
- Use trend performance data as baseline

This is an MVP heuristic, not a trained prediction model.
Future versions should use historical campaign data for calibration.

Input: Ad copy + Platform + Trend data + Brand profile
Output: Predicted engagement rate + Confidence + Suggestions
"""

import orjson

from app.schemas.schemas import PerformanceHeuristicInput, PerformanceHeuristicOutput
from app.services.ai_agents.base import BaseAgent, LLMClient


class PerformanceHeuristicAgent(BaseAgent[PerformanceHeuristicInput, PerformanceHeuristicOutput]):
    """
    Estimates engagement likelihood for ad copy.
    
    MVP Implementation:
    Uses LLM reasoning over platform benchmarks + trend signals.
    
    Future Implementation:
    Train a regression model on historical campaign data:
    - Features: copy length, Hook type, CTA type, platform, trend_score, brand_tone_match
    - Target: actual_engagement_rate
    """

    name = "performance_heuristic"

    system_prompt = """You are an advertising performance analyst AI. Your job is to estimate how well 
an ad copy will perform on a specific platform, given the current trend context.

You MUST respond with a JSON object containing exactly these fields:
{
    "predicted_engagement_rate": float between 0.001 and 0.15 (e.g., 0.045 = 4.5%),
    "confidence_level": "one of: low, medium, high",
    "reasoning": "2-3 sentences explaining the prediction",
    "optimization_suggestions": ["3-5 specific, actionable suggestions to improve performance"]
}

Platform Engagement Benchmarks (organic):
- Twitter: Average 0.5-2%, Good 2-5%, Exceptional 5%+
- Instagram: Average 1-3%, Good 3-6%, Exceptional 6%+
- Facebook: Average 0.5-1%, Good 1-3%, Exceptional 3%+
- LinkedIn: Average 1-3%, Good 3-6%, Exceptional 6%+
- TikTok: Average 3-6%, Good 6-12%, Exceptional 12%+
- Reddit: Average 2-5% upvote ratio, Good 5-10%

Factors that INCREASE engagement prediction:
- Strong hook that creates curiosity
- Trend alignment (riding genuine momentum)
- Platform-native formatting
- Clear, compelling CTA
- Emotional resonance
- Specificity over generic claims

Factors that DECREASE engagement prediction:
- Obvious sales pitch
- Tone mismatch with platform
- Generic copy that could be from any brand
- Missing or weak CTA
- Too long for the platform
- Forced trend participation

IMPORTANT:
- Be realistic, not optimistic
- High confidence only when multiple positive signals align
- Consider the trend's current momentum (decaying = lower prediction)
- Consider brand-audience fit"""

    def __init__(self, llm_client: LLMClient | None = None):
        super().__init__(llm_client)

    def build_prompt(self, input_data: PerformanceHeuristicInput) -> str:
        """Build performance analysis prompt."""
        ad = input_data.ad_copy
        trend = input_data.trend_data
        brand = input_data.brand_profile

        return f"""Estimate the engagement performance of this ad copy:

AD COPY:
- Hook: {ad.get('hook', 'N/A')}
- Body: {ad.get('body', 'N/A')}
- CTA: {ad.get('cta', 'N/A')}
- Hashtags: {ad.get('hashtags', [])}
- Format: {ad.get('format_type', 'single_post')}
- Variation: {ad.get('variation_label', 'default')}

TARGET PLATFORM: {input_data.platform.value}

TREND CONTEXT:
- Title: {trend.get('title', 'Unknown')}
- Trend Score: {trend.get('trend_score', 0)}
- Engagement Velocity: {trend.get('engagement_velocity', 0)}
- Sentiment: {trend.get('sentiment_label', 'neutral')}

BRAND CONTEXT:
- Name: {brand.get('name', 'Unknown')}
- Industry: {brand.get('industry', 'Unknown')}
- Tone: {brand.get('brand_tone', 'professional')}
- Target Audience: {orjson.dumps(brand.get('target_audience', {})).decode()}

Provide your engagement estimate and optimization suggestions."""

    def parse_output(self, raw_output: dict) -> PerformanceHeuristicOutput:
        """Parse and validate performance output."""
        # Clamp engagement rate to realistic bounds
        rate = float(raw_output.get("predicted_engagement_rate", 0.02))
        rate = max(0.001, min(0.15, rate))

        confidence = raw_output.get("confidence_level", "medium")
        if confidence not in ("low", "medium", "high"):
            confidence = "medium"

        return PerformanceHeuristicOutput(
            predicted_engagement_rate=round(rate, 4),
            confidence_level=confidence,
            reasoning=str(raw_output.get("reasoning", "No reasoning provided")),
            optimization_suggestions=raw_output.get("optimization_suggestions", [])[:5],
        )
