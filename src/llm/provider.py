from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ChatResponse:
    content: str
    usage: Dict[str, int]
    model: str


class LLMProvider(ABC):
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> ChatResponse:
        pass
    
    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ):
        pass
    
    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        pass
