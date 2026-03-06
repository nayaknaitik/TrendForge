"""
AI Agent Base Classes and LLM Client Factory.

Provides the foundation for all AI agents in the system.
Each agent has:
- A defined role and system prompt
- Structured JSON input/output contracts
- Token usage tracking
- Error handling and retry logic
- Composability for orchestration
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

import orjson
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.exceptions import AIAgentError
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


# ── LLM Client Factory ─────────────────────────────────────────────────

class LLMClient:
    """
    Unified interface for OpenAI and Anthropic LLM calls.
    
    Abstracts provider differences behind a consistent API.
    Supports structured JSON output enforcement.
    """

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ):
        self.provider = provider or settings.default_llm_provider
        self.model = model or settings.default_llm_model
        self.temperature = temperature if temperature is not None else settings.llm_temperature
        self.max_tokens = max_tokens or settings.llm_max_tokens

        if self.provider == "openai":
            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        elif self.provider == "anthropic":
            self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=15))
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        json_mode: bool = True,
    ) -> dict[str, Any]:
        """
        Generate a completion from the LLM.
        
        Args:
            system_prompt: Agent role/instructions
            user_prompt: The actual task/data input
            json_mode: If True, enforce JSON output
            
        Returns:
            Parsed JSON dict from LLM response
        """
        try:
            if self.provider == "openai":
                return await self._generate_openai(system_prompt, user_prompt, json_mode)
            else:
                return await self._generate_anthropic(system_prompt, user_prompt, json_mode)
        except Exception as e:
            logger.error("llm_generation_failed", provider=self.provider, error=str(e))
            raise

    async def _generate_openai(
        self, system_prompt: str, user_prompt: str, json_mode: bool
    ) -> dict[str, Any]:
        """OpenAI completion with optional JSON mode."""
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = await self._client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content

        # Track usage
        usage = response.usage
        logger.info(
            "llm_usage",
            provider="openai",
            model=self.model,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
        )

        if json_mode:
            return orjson.loads(content)
        return {"text": content}

    async def _generate_anthropic(
        self, system_prompt: str, user_prompt: str, json_mode: bool
    ) -> dict[str, Any]:
        """Anthropic completion with JSON enforcement via prompting."""
        if json_mode:
            system_prompt += (
                "\n\nIMPORTANT: You MUST respond with ONLY valid JSON. "
                "No markdown, no code blocks, no explanatory text outside the JSON."
            )

        response = await self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        content = response.content[0].text

        logger.info(
            "llm_usage",
            provider="anthropic",
            model=self.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

        if json_mode:
            # Try to extract JSON from response
            try:
                return orjson.loads(content)
            except orjson.JSONDecodeError:
                # Try to find JSON in response
                import re
                json_match = re.search(r"\{[\s\S]*\}", content)
                if json_match:
                    return orjson.loads(json_match.group())
                raise AIAgentError("llm", "Failed to parse JSON from Anthropic response")

        return {"text": content}


# ── Base Agent ──────────────────────────────────────────────────────────

class BaseAgent(ABC, Generic[InputT, OutputT]):
    """
    Abstract base class for all AI agents.
    
    Each agent must define:
    - name: Human-readable agent identifier
    - system_prompt: The agent's role and instructions
    - build_prompt(): Converts typed input into user prompt string
    - parse_output(): Validates and structures the LLM response
    """

    name: str = "base_agent"
    system_prompt: str = ""

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm = llm_client or LLMClient()

    async def run(self, input_data: InputT) -> OutputT:
        """
        Execute the agent's task.
        
        1. Build the prompt from structured input
        2. Call the LLM
        3. Parse and validate the output
        """
        logger.info("agent_started", agent=self.name)

        try:
            user_prompt = self.build_prompt(input_data)
            raw_output = await self.llm.generate(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                json_mode=True,
            )
            result = self.parse_output(raw_output)

            logger.info("agent_completed", agent=self.name)
            return result

        except Exception as e:
            logger.error("agent_failed", agent=self.name, error=str(e))
            raise AIAgentError(self.name, str(e))

    @abstractmethod
    def build_prompt(self, input_data: InputT) -> str:
        """Convert typed input into a prompt string."""
        ...

    @abstractmethod
    def parse_output(self, raw_output: dict) -> OutputT:
        """Validate and structure the LLM response."""
        ...
