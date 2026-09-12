from __future__ import annotations

from src.config.settings import Settings
from src.llm.provider import LLMProvider, OpenAILLMProvider


def build_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "OPENAI":
        return OpenAILLMProvider(model=settings.llm_model, api_key=settings.openai_api_key)
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
