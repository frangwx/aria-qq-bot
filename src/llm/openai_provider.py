from typing import List, Dict
from openai import AsyncOpenAI

from .provider import LLMProvider, ChatResponse
from src.utils import get_logger

logger = get_logger()


class OpenAIProvider(LLMProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        logger.info(f"OpenAIProvider initialized: model={model}, base_url={base_url}")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> ChatResponse:
        try:
            model = kwargs.get("model", self.model)
            temperature = kwargs.get("temperature", self.temperature)
            max_tokens = kwargs.get("max_tokens", self.max_tokens)
            
            logger.debug(f"Chat request: model={model}, max_tokens={max_tokens}")
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            logger.debug(f"Chat response: {content[:100] if content else 'None'}...")
            
            return ChatResponse(
                content=content or "",
                usage={
                    "input": response.usage.prompt_tokens,
                    "output": response.usage.completion_tokens
                },
                model=response.model
            )
        except Exception as e:
            logger.error(f"Chat API error: {e}", exc_info=True)
            raise
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ):
        try:
            stream = await self.client.chat.completions.create(
                model=kwargs.get("model", self.model),
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Chat stream API error: {e}", exc_info=True)
            raise
    
    async def get_embedding(self, text: str) -> List[float]:
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
