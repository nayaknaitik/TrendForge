"""
Brand Relevance Agent.

Responsibilities:
- Score how relevant a trend is to a specific brand
- Analyze semantic similarity between brand positioning and trend content
- Evaluate audience overlap
- Assess tone compatibility
- Provide reasoning for accept/reject decisions

Input: Brand profile + Trend data
Output: Multi-dimensional relevance score with reasoning
"""

import orjson

from app.schemas.schemas import BrandRelevanceInput, BrandRelevanceOutput
from app.services.ai_agents.base import BaseAgent, LLMClient


class BrandRelevanceAgent(BaseAgent[BrandRelevanceInput, BrandRelevanceOutput]):
    """
    Determines how relevant a trend is to a brand.
    
    Uses a multi-factor scoring approach:
    - Semantic similarity (0.40 weight): How close is the trend topic to brand positioning?
    - Audience overlap (0.25 weight): Does the trend reach the brand's target audience?
    - Industry match (0.20 weight): Is the trend in or adjacent to the brand's industry?
    - Tone compatibility (0.15 weight): Can the brand credibly engage with this trend?
    
    Threshold: relevance_score >= 0.65 → relevant
    """

    name = "brand_relevance"

    system_prompt = """You are a brand strategy AI that evaluates whether a social media trend is relevant 
and appropriate for a specific brand to leverage in their marketing.

You MUST respond with a JSON object containing exactly these fields:
{
    "relevance_score": float between 0.0 and 1.0 (overall relevance),
    "semantic_similarity": float between 0.0 and 1.0 (topic/content alignment),
    "audience_overlap": float between 0.0 and 1.0 (target audience match),
    "industry_match": float between 0.0 and 1.0 (industry relevance),
    "tone_compatibility": float between 0.0 and 1.0 (brand voice fit),
    "is_relevant": boolean (true if relevance_score >= 0.65),
    "reasoning": "2-3 sentence explanation of why this trend is or isn't relevant"
}

Scoring Guidelines:
- semantic_similarity: Does the trend topic connect to what the brand does/sells/represents?
- audience_overlap: Would people interested in this trend also be interested in this brand?
- industry_match: Is the trend directly in the brand's industry, adjacent, or unrelated?
- tone_compatibility: Can the brand engage with this trend without seeming inauthentic?

IMPORTANT:
- Consider brand safety — reject trends that could damage brand reputation
- A tech brand CAN leverage a fitness trend if there's a creative angle
- Not every trending topic is worth engaging with — be selective
- Low relevance is NOT a failure — it protects the brand from tone-deaf marketing
- The overall relevance_score should be a weighted combination: 
  (semantic * 0.40) + (audience * 0.25) + (industry * 0.20) + (tone * 0.15)"""

    def __init__(self, llm_client: LLMClient | None = None):
        super().__init__(llm_client)

    def build_prompt(self, input_data: BrandRelevanceInput) -> str:
        """Build relevance analysis prompt."""
        brand = input_data.brand_profile
        trend = input_data.trend_data

        return f"""Evaluate the relevance of this trend for the following brand:

BRAND PROFILE:
- Name: {brand.get('name', 'Unknown')}
- Industry: {brand.get('industry', 'Unknown')}
- Description: {brand.get('description', 'N/A')}
- Target Audience: {orjson.dumps(brand.get('target_audience', {})).decode()}
- Brand Tone: {brand.get('brand_tone', 'professional')}
- Brand Positioning: {brand.get('brand_positioning', 'N/A')}
- Products: {orjson.dumps(brand.get('product_details', {})).decode()}
- Marketing Goals: {orjson.dumps(brand.get('marketing_goals', [])).decode()}

TREND DATA:
- Title: {trend.get('title', 'Unknown')}
- Platform: {trend.get('platform', 'Unknown')}
- Topics: {trend.get('topics', [])}
- Keywords: {trend.get('keywords', [])}
- Category: {trend.get('category', 'Unknown')}
- Sentiment: {trend.get('sentiment_label', 'neutral')} ({trend.get('sentiment_score', 0)})
- Content Format: {trend.get('content_format', 'text')}
- Engagement Score: {trend.get('engagement_score', 0)}
- Trend Score: {trend.get('trend_score', 0)}
- Audience Clusters: {orjson.dumps(trend.get('audience_clusters', [])).decode()}

Calculate the multi-dimensional relevance score."""

    def parse_output(self, raw_output: dict) -> BrandRelevanceOutput:
        """Parse and validate relevance output."""
        def clamp(val, min_val=0.0, max_val=1.0):
            return max(min_val, min(max_val, float(val or 0)))

        semantic = clamp(raw_output.get("semantic_similarity"))
        audience = clamp(raw_output.get("audience_overlap"))
        industry = clamp(raw_output.get("industry_match"))
        tone = clamp(raw_output.get("tone_compatibility"))

        # Calculate weighted score
        relevance = (semantic * 0.40) + (audience * 0.25) + (industry * 0.20) + (tone * 0.15)

        return BrandRelevanceOutput(
            relevance_score=round(relevance, 4),
            semantic_similarity=round(semantic, 4),
            audience_overlap=round(audience, 4),
            industry_match=round(industry, 4),
            tone_compatibility=round(tone, 4),
            is_relevant=relevance >= 0.65,
            reasoning=raw_output.get("reasoning", "No reasoning provided"),
        )
