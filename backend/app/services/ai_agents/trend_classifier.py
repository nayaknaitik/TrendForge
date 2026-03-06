"""
Trend Classifier Agent.

Responsibilities:
- Cluster and categorize trending content
- Topic modeling
- Sentiment scoring refinement
- Audience cluster estimation
- Content format classification

Input: Raw trend text + metadata
Output: Structured classification with topics, keywords, sentiment, audience clusters
"""

import orjson

from app.schemas.schemas import (
    ContentFormat,
    SentimentLabel,
    TrendClassifierInput,
    TrendClassifierOutput,
)
from app.services.ai_agents.base import BaseAgent, LLMClient


class TrendClassifierAgent(BaseAgent[TrendClassifierInput, TrendClassifierOutput]):
    """
    Classifies raw social media content into structured trend metadata.
    
    Uses LLM for nuanced understanding that rules-based NLP can't achieve:
    - Sarcasm detection in sentiment
    - Cultural context for topic classification
    - Audience inference from content style
    """

    name = "trend_classifier"

    system_prompt = """You are a social media trend analyst AI. Your task is to analyze social media content 
and produce a structured classification.

You MUST respond with a JSON object containing exactly these fields:
{
    "topics": ["list of 3-7 relevant topic tags"],
    "keywords": ["list of 5-10 most relevant keywords/phrases"],
    "category": "one of: technology, business, entertainment, sports, politics, health, science, lifestyle, education, finance, food, travel, fashion, gaming, other",
    "content_format": "one of: text, meme, thread, carousel, video, image, poll",
    "sentiment_score": float between -1.0 (very negative) and 1.0 (very positive),
    "sentiment_label": "one of: very_negative, negative, neutral, positive, very_positive",
    "audience_clusters": [
        {"cluster": "descriptive_name", "percentage": float between 0 and 1},
        ...up to 5 clusters
    ],
    "confidence": float between 0 and 1
}

Guidelines:
- Topics should be specific enough to be useful for matching but general enough to group similar content
- Keywords should capture the core concepts, not just common words
- Audience clusters should describe WHO is engaging with this content
- Consider cultural context and platform norms when analyzing sentiment
- Be specific with category — use 'other' only when nothing fits
- Account for sarcasm, irony, and platform-specific language"""

    def __init__(self, llm_client: LLMClient | None = None):
        super().__init__(llm_client)

    def build_prompt(self, input_data: TrendClassifierInput) -> str:
        """Build classification prompt from trend data."""
        return f"""Analyze this social media content from {input_data.platform}:

CONTENT:
{input_data.raw_content}

METADATA:
{orjson.dumps(input_data.metadata).decode() if input_data.metadata else "None"}

Classify this content according to the schema specified."""

    def parse_output(self, raw_output: dict) -> TrendClassifierOutput:
        """Parse and validate classifier output."""
        # Normalize sentiment label
        sentiment_label = raw_output.get("sentiment_label", "neutral")
        if sentiment_label not in [sl.value for sl in SentimentLabel]:
            sentiment_label = "neutral"

        # Normalize content format
        content_format = raw_output.get("content_format", "text")
        if content_format not in [cf.value for cf in ContentFormat]:
            content_format = "text"

        return TrendClassifierOutput(
            topics=raw_output.get("topics", [])[:7],
            keywords=raw_output.get("keywords", [])[:10],
            category=raw_output.get("category", "other"),
            content_format=ContentFormat(content_format),
            sentiment_score=max(-1.0, min(1.0, float(raw_output.get("sentiment_score", 0.0)))),
            sentiment_label=SentimentLabel(sentiment_label),
            audience_clusters=raw_output.get("audience_clusters", [])[:5],
            confidence=max(0.0, min(1.0, float(raw_output.get("confidence", 0.5)))),
        )
