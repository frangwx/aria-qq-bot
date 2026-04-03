import os
from typing import Optional

from .provider import LLMProvider
from .openai_provider import OpenAIProvider
from src.utils import get_config, get_logger

logger = get_logger()

_provider: Optional[LLMProvider] = None


def create_llm_provider() -> LLMProvider:
    api_key = os.getenv("API_KEY") or get_config("llm.api_key", "")
    base_url = get_config("llm.base_url", "https://api.openai.com/v1")
    model = get_config("llm.model", "gpt-4o")
    temperature = get_config("llm.temperature", 0.7)
    max_tokens = get_config("llm.max_tokens", 2000)
    
    if not api_key:
        raise ValueError("API_KEY not configured")
    
    return OpenAIProvider(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )


def get_llm_provider() -> LLMProvider:
    global _provider
    if _provider is None:
        _provider = create_llm_provider()
    return _provider


def get_system_prompt() -> str:
    return get_config("llm.system_prompt", "你是绝区零中的角色「爱芮」。")
