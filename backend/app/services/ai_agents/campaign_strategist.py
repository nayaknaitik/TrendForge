"""
Campaign Strategist Agent.

Responsibilities:
- Create campaign concepts from brand + trend combinations
- Define creative angle and hook strategy
- Select target platforms and content pillars
- Plan campaign duration and key messages

Input: Brand profile + Trend data + Campaign objective
Output: Complete campaign strategy
"""

import orjson

from app.schemas.schemas import CampaignStrategyInput, CampaignStrategyOutput
from app.services.ai_agents.base import BaseAgent, LLMClient


class CampaignStrategistAgent(BaseAgent[CampaignStrategyInput, CampaignStrategyOutput]):
    """
    Creates marketing campaign strategies by combining brand context with trend data.
    
    Produces actionable strategies that the Copy Generator Agent can execute:
    - Clear creative angle
    - Hook strategy (how to grab attention)
    - Platform selection with reasoning
    - Content pillars for consistent messaging
    - Key messages for different ad variations
    """

    name = "campaign_strategist"

    system_prompt = """You are an expert marketing strategist AI. Your job is to create compelling campaign 
strategies that leverage trending social media content for brand marketing.

You MUST respond with a JSON object containing exactly these fields:
{
    "campaign_name": "catchy, descriptive name for the campaign (max 60 chars)",
    "angle": "the creative angle/perspective for this campaign (2-3 sentences)",
    "hook_strategy": "how to grab attention in the first 2 seconds (2-3 sentences)",
    "target_platforms": ["list of 1-4 platform names: twitter, instagram, facebook, reddit, linkedin, tiktok"],
    "content_pillars": ["3-5 thematic pillars that all content should align with"],
    "key_messages": ["3-5 core messages to communicate across all variations"],
    "campaign_duration_days": integer between 1 and 30,
    "estimated_budget_range": {
        "min_usd": integer,
        "max_usd": integer,
        "reasoning": "brief budget justification"
    }
}

Strategy Guidelines:
- The angle should feel NATIVE to the trend, not like a brand hijacking a conversation
- Hook strategy should match platform conventions (e.g., hooks on TikTok vs LinkedIn differ)
- Content pillars should bridge the trend topic and the brand's core positioning
- Key messages should be adaptable across different ad formats
- Campaign duration should match trend lifecycle (viral = shorter, cultural = longer)
- Platform selection should prioritize where the trend is most active AND where the brand's audience lives

CRITICAL RULES:
- NEVER suggest anything that could be seen as exploiting tragedy or crisis
- Ensure the campaign maintains brand authenticity — forced trend participation is worse than no participation
- Consider the brand's tone when suggesting creative angles
- Keep campaign names professional but attention-grabbing"""

    def __init__(self, llm_client: LLMClient | None = None):
        super().__init__(llm_client)

    def build_prompt(self, input_data: CampaignStrategyInput) -> str:
        """Build strategy prompt from brand + trend + objective."""
        brand = input_data.brand_profile
        trend = input_data.trend_data

        custom = ""
        if input_data.custom_instructions:
            custom = f"\nADDITIONAL INSTRUCTIONS FROM USER:\n{input_data.custom_instructions}\n"

        return f"""Create a marketing campaign strategy for the following:

BRAND PROFILE:
- Name: {brand.get('name', 'Unknown')}
- Industry: {brand.get('industry', 'Unknown')}
- Description: {brand.get('description', 'N/A')}
- Target Audience: {orjson.dumps(brand.get('target_audience', {})).decode()}
- Brand Tone: {brand.get('brand_tone', 'professional')}
- Brand Positioning: {brand.get('brand_positioning', 'N/A')}
- Products: {orjson.dumps(brand.get('product_details', {})).decode()}
- Marketing Goals: {orjson.dumps(brand.get('marketing_goals', [])).decode()}
- Brand Guidelines: {orjson.dumps(brand.get('brand_guidelines', {})).decode()}

TREND DATA:
- Title: {trend.get('title', 'Unknown')}
- Platform: {trend.get('platform', 'Unknown')}
- Topics: {trend.get('topics', [])}
- Keywords: {trend.get('keywords', [])}
- Category: {trend.get('category', 'Unknown')}
- Sentiment: {trend.get('sentiment_label', 'neutral')}
- Content Format: {trend.get('content_format', 'text')}
- Trend Score: {trend.get('trend_score', 0)}
- Audience Clusters: {orjson.dumps(trend.get('audience_clusters', [])).decode()}

CAMPAIGN OBJECTIVE: {input_data.objective.value}
{custom}
Create a strategic, actionable campaign plan."""

    def parse_output(self, raw_output: dict) -> CampaignStrategyOutput:
        """Parse and validate strategy output."""
        return CampaignStrategyOutput(
            campaign_name=str(raw_output.get("campaign_name", "Untitled Campaign"))[:60],
            angle=str(raw_output.get("angle", "")),
            hook_strategy=str(raw_output.get("hook_strategy", "")),
            target_platforms=raw_output.get("target_platforms", ["twitter", "instagram"])[:4],
            content_pillars=raw_output.get("content_pillars", [])[:5],
            key_messages=raw_output.get("key_messages", [])[:5],
            campaign_duration_days=max(1, min(30, int(raw_output.get("campaign_duration_days", 7)))),
            estimated_budget_range=raw_output.get("estimated_budget_range"),
        )
