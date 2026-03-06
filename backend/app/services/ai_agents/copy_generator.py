"""
Copy Generator Agent.

Responsibilities:
- Generate multiple ad copy variations
- Platform-specific formatting
- Create hooks, CTAs, body copy
- Handle different formats (single post, thread, carousel, reel script)
- Maintain brand voice consistency

Input: Brand profile + Campaign strategy + Platform + Format
Output: Multiple ad copy variations
"""

import orjson

from app.schemas.schemas import AdFormat, AdPlatform, CopyGeneratorInput, CopyGeneratorOutput
from app.services.ai_agents.base import BaseAgent, LLMClient


class CopyGeneratorAgent(BaseAgent[CopyGeneratorInput, CopyGeneratorOutput]):
    """
    Generates platform-specific ad copy variations.
    
    Each variation maintains brand voice while testing different:
    - Hook styles (question, statistic, bold claim, story)
    - CTA approaches (direct, soft, urgency, curiosity)
    - Emotional angles (aspirational, fear-of-missing-out, educational)
    """

    name = "copy_generator"

    system_prompt = """You are an expert advertising copywriter AI. You generate platform-specific ad copy 
that is engaging, on-brand, and optimized for the target platform's conventions.

You MUST respond with a JSON object containing exactly this field:
{
    "variations": [
        {
            "hook": "the attention-grabbing opening line (max 140 chars for Twitter, 250 for others)",
            "body": "the main copy body (platform-appropriate length)",
            "cta": "call to action text (max 50 chars)",
            "hashtags": ["3-7 relevant hashtags without # symbol"],
            "variation_label": "descriptive label like 'bold_urgency', 'soft_educational', 'story_driven'",
            "format_notes": "any platform-specific formatting notes"
        }
    ]
}

Platform-Specific Rules:
- TWITTER: Max 280 chars total. Punchy, conversational. Hashtags count toward limit.
- INSTAGRAM: Up to 2200 chars. Visual-first copy. More hashtags OK (up to 30). Use line breaks.
- FACEBOOK: Mid-length. Community-focused. Question-driven hooks work well.
- LINKEDIN: Professional tone. Thought leadership angle. Longer form OK.
- TIKTOK: Script-style. Conversational. Hook in first 2 seconds. Use trending sounds reference.
- REDDIT: Authentic, not salesy. Value-first. Match subreddit tone.

Format-Specific Rules:
- SINGLE_POST: One cohesive piece of copy
- THREAD: 3-7 connected posts, each with own hook, building a narrative
- CAROUSEL: 5-10 slides with headline + body for each slide
- STORY: Short, swipeable format with clear CTA
- REEL_SCRIPT: Time-stamped script with visual directions
- AD_COPY: Headline + Primary Text + Description + CTA button text

For THREAD format, structure body as numbered posts:
"1. [First post]\n\n2. [Second post]\n\n3. [Third post]..."

For CAROUSEL format, include slides in the body:
"Slide 1: [Headline]\n[Body]\n\nSlide 2: [Headline]\n[Body]..."

Quality Rules:
- Each variation MUST feel distinctly different in approach
- Never use clickbait that doesn't deliver
- Avoid generic phrases like "Don't miss out" unless genuinely urgent
- Match the brand's tone exactly — a casual brand shouldn't sound corporate
- Include specific details from the trend/product when possible"""

    # Platform character limits
    PLATFORM_LIMITS = {
        "twitter": {"hook": 140, "body": 280, "cta": 50},
        "instagram": {"hook": 250, "body": 2200, "cta": 100},
        "facebook": {"hook": 200, "body": 1000, "cta": 80},
        "linkedin": {"hook": 200, "body": 3000, "cta": 80},
        "tiktok": {"hook": 150, "body": 500, "cta": 50},
        "reddit": {"hook": 200, "body": 5000, "cta": 80},
    }

    def __init__(self, llm_client: LLMClient | None = None):
        super().__init__(llm_client)

    def build_prompt(self, input_data: CopyGeneratorInput) -> str:
        """Build copy generation prompt."""
        brand = input_data.brand_profile
        strategy = input_data.campaign_strategy
        limits = self.PLATFORM_LIMITS.get(input_data.platform.value, self.PLATFORM_LIMITS["instagram"])

        return f"""Generate {input_data.num_variations} ad copy variations for:

BRAND:
- Name: {brand.get('name', 'Unknown')}
- Industry: {brand.get('industry', 'Unknown')}
- Tone: {brand.get('brand_tone', 'professional')}
- Positioning: {brand.get('brand_positioning', 'N/A')}
- Products: {orjson.dumps(brand.get('product_details', {})).decode()}
- Guidelines: {orjson.dumps(brand.get('brand_guidelines', {})).decode()}

CAMPAIGN STRATEGY:
- Angle: {strategy.get('angle', 'N/A')}
- Hook Strategy: {strategy.get('hook_strategy', 'N/A')}
- Content Pillars: {strategy.get('content_pillars', [])}
- Key Messages: {strategy.get('key_messages', [])}

TARGET PLATFORM: {input_data.platform.value}
FORMAT: {input_data.format_type.value}
CHARACTER LIMITS: Hook={limits['hook']}, Body={limits['body']}, CTA={limits['cta']}

Generate {input_data.num_variations} distinct variations. Each should take a different creative approach 
while staying on-brand and on-strategy."""

    def parse_output(self, raw_output: dict) -> CopyGeneratorOutput:
        """Parse and validate copy output."""
        variations = raw_output.get("variations", [])

        # Validate each variation has required fields
        validated = []
        for v in variations:
            validated.append({
                "hook": str(v.get("hook", ""))[:500],
                "body": str(v.get("body", "")),
                "cta": str(v.get("cta", "Learn more"))[:100],
                "hashtags": [str(h).replace("#", "") for h in v.get("hashtags", [])][:10],
                "variation_label": str(v.get("variation_label", "default")),
                "format_notes": str(v.get("format_notes", "")),
            })

        return CopyGeneratorOutput(variations=validated)
