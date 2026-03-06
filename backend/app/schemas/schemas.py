"""
Pydantic schemas for API request/response validation.

Organized by domain entity. All schemas use Pydantic v2 with strict validation.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── Enums ───────────────────────────────────────────────────────────────

class UserTier(str, Enum):
    free = "free"
    pro = "pro"
    enterprise = "enterprise"


class PlatformType(str, Enum):
    twitter = "twitter"
    reddit = "reddit"
    instagram = "instagram"
    facebook = "facebook"


class BrandTone(str, Enum):
    professional = "professional"
    casual = "casual"
    witty = "witty"
    bold = "bold"
    inspirational = "inspirational"
    edgy = "edgy"


class ContentFormat(str, Enum):
    text = "text"
    meme = "meme"
    thread = "thread"
    carousel = "carousel"
    video = "video"
    image = "image"
    poll = "poll"


class SentimentLabel(str, Enum):
    very_negative = "very_negative"
    negative = "negative"
    neutral = "neutral"
    positive = "positive"
    very_positive = "very_positive"


class CampaignObjective(str, Enum):
    brand_awareness = "brand_awareness"
    engagement = "engagement"
    lead_generation = "lead_generation"
    sales_conversion = "sales_conversion"
    app_installs = "app_installs"
    traffic = "traffic"


class CampaignStatus(str, Enum):
    draft = "draft"
    generating = "generating"
    ready = "ready"
    active = "active"
    paused = "paused"
    completed = "completed"


class AdPlatform(str, Enum):
    twitter = "twitter"
    reddit = "reddit"
    instagram = "instagram"
    facebook = "facebook"
    linkedin = "linkedin"
    tiktok = "tiktok"


class AdFormat(str, Enum):
    single_post = "single_post"
    thread = "thread"
    carousel = "carousel"
    story = "story"
    reel_script = "reel_script"
    ad_copy = "ad_copy"


# ── Auth Schemas ────────────────────────────────────────────────────────

class AuthRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=256)


class AuthLogin(BaseModel):
    email: EmailStr
    password: str


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthRefresh(BaseModel):
    refresh_token: str


# ── User Schemas ────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str | None
    is_active: bool
    tier: UserTier
    created_at: datetime


# ── Brand Schemas ───────────────────────────────────────────────────────

class TargetAudience(BaseModel):
    age_range: str = Field(default="18-65", examples=["25-34"])
    gender: str = Field(default="all", examples=["all", "male", "female"])
    interests: list[str] = Field(default_factory=list, examples=[["tech", "fitness"]])
    platforms: list[PlatformType] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list, examples=[["US", "UK"]])


class ProductDetail(BaseModel):
    name: str
    price: float | None = None
    category: str
    description: str | None = None


class BrandGuidelines(BaseModel):
    colors: list[str] = Field(default_factory=list, examples=[["#FF5733", "#333333"]])
    forbidden_words: list[str] = Field(default_factory=list)
    preferred_hashtags: list[str] = Field(default_factory=list)
    voice_examples: list[str] = Field(default_factory=list)


class BrandCreate(BaseModel):
    name: str = Field(min_length=1, max_length=256)
    industry: str = Field(min_length=1, max_length=128)
    description: str | None = None
    target_audience: TargetAudience = Field(default_factory=TargetAudience)
    brand_tone: BrandTone = BrandTone.professional
    brand_positioning: str | None = None
    product_details: list[ProductDetail] = Field(default_factory=list)
    marketing_goals: list[CampaignObjective] = Field(default_factory=list)
    brand_guidelines: BrandGuidelines = Field(default_factory=BrandGuidelines)


class BrandUpdate(BaseModel):
    name: str | None = None
    industry: str | None = None
    description: str | None = None
    target_audience: TargetAudience | None = None
    brand_tone: BrandTone | None = None
    brand_positioning: str | None = None
    product_details: list[ProductDetail] | None = None
    marketing_goals: list[CampaignObjective] | None = None
    brand_guidelines: BrandGuidelines | None = None


class BrandResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    industry: str
    description: str | None
    target_audience: dict
    brand_tone: str
    brand_positioning: str | None
    product_details: dict
    marketing_goals: list
    brand_guidelines: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ── Trend Schemas ───────────────────────────────────────────────────────

class TrendResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    platform: PlatformType
    title: str
    description: str | None
    category: str | None
    topics: list[str]
    keywords: list[str]
    content_format: ContentFormat
    sentiment_score: float
    sentiment_label: SentimentLabel
    engagement_score: float
    engagement_velocity: float
    volume: int
    trend_score: float
    audience_clusters: list
    detected_at: datetime
    is_active: bool


class TrendListResponse(BaseModel):
    trends: list[TrendResponse]
    total: int
    page: int
    page_size: int


class TrendFilter(BaseModel):
    platforms: list[PlatformType] | None = None
    min_score: float = 0.0
    categories: list[str] | None = None
    sentiment: SentimentLabel | None = None
    content_format: ContentFormat | None = None
    hours_ago: int = 24
    page: int = 1
    page_size: int = Field(default=20, le=100)


# ── Brand-Trend Match Schemas ──────────────────────────────────────────

class BrandTrendMatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    brand_id: UUID
    trend_id: UUID
    relevance_score: float
    semantic_similarity: float
    audience_overlap: float
    industry_match: float
    tone_compatibility: float
    reasoning: str | None
    is_relevant: bool
    created_at: datetime


# ── Campaign Schemas ────────────────────────────────────────────────────

class CampaignCreate(BaseModel):
    brand_id: UUID
    trend_id: UUID | None = None
    name: str = Field(min_length=1, max_length=256)
    objective: CampaignObjective
    target_platforms: list[AdPlatform] = Field(default_factory=list)
    custom_instructions: str | None = None


class CampaignStrategy(BaseModel):
    angle: str
    hook_strategy: str
    target_platforms: list[str]
    content_pillars: list[str]
    campaign_duration_days: int = 7
    key_messages: list[str] = Field(default_factory=list)


class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    brand_id: UUID
    trend_id: UUID | None
    name: str
    objective: CampaignObjective
    strategy: dict
    estimated_engagement: dict
    status: CampaignStatus
    created_at: datetime
    updated_at: datetime
    ad_copies: list["AdCopyResponse"] = Field(default_factory=list)


# ── Ad Copy Schemas ─────────────────────────────────────────────────────

class AdCopyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    campaign_id: UUID
    platform: AdPlatform
    hook: str
    body: str
    cta: str
    hashtags: list[str]
    format_type: AdFormat
    slides: list[dict]
    predicted_engagement_rate: float
    variation_label: str | None
    created_at: datetime


class AdCopyExport(BaseModel):
    ad_copy_id: UUID
    format: str = Field(default="json", pattern="^(json|csv|txt|markdown)$")


# ── AI Agent Schemas ────────────────────────────────────────────────────

class AgentInput(BaseModel):
    """Base input schema for all AI agents."""
    request_id: str
    context: dict = Field(default_factory=dict)


class TrendClassifierInput(AgentInput):
    raw_content: str
    platform: PlatformType
    metadata: dict = Field(default_factory=dict)


class TrendClassifierOutput(BaseModel):
    topics: list[str]
    keywords: list[str]
    category: str
    content_format: ContentFormat
    sentiment_score: float
    sentiment_label: SentimentLabel
    audience_clusters: list[dict]
    confidence: float


class BrandRelevanceInput(AgentInput):
    brand_profile: dict
    trend_data: dict


class BrandRelevanceOutput(BaseModel):
    relevance_score: float
    semantic_similarity: float
    audience_overlap: float
    industry_match: float
    tone_compatibility: float
    is_relevant: bool
    reasoning: str


class CampaignStrategyInput(AgentInput):
    brand_profile: dict
    trend_data: dict
    objective: CampaignObjective
    custom_instructions: str | None = None


class CampaignStrategyOutput(BaseModel):
    campaign_name: str
    angle: str
    hook_strategy: str
    target_platforms: list[str]
    content_pillars: list[str]
    key_messages: list[str]
    campaign_duration_days: int
    estimated_budget_range: dict | None = None


class CopyGeneratorInput(AgentInput):
    brand_profile: dict
    campaign_strategy: dict
    platform: AdPlatform
    format_type: AdFormat
    num_variations: int = Field(default=3, ge=1, le=10)


class CopyGeneratorOutput(BaseModel):
    variations: list[dict]
    # Each: {"hook": str, "body": str, "cta": str, "hashtags": list, "variation_label": str}


class PerformanceHeuristicInput(AgentInput):
    ad_copy: dict
    platform: AdPlatform
    trend_data: dict
    brand_profile: dict


class PerformanceHeuristicOutput(BaseModel):
    predicted_engagement_rate: float
    confidence_level: str  # "low", "medium", "high"
    reasoning: str
    optimization_suggestions: list[str]


# Rebuild forward references
CampaignResponse.model_rebuild()
