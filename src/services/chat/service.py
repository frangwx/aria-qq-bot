from typing import List, Dict, Optional

from src.llm import get_llm_provider, get_system_prompt
from src.memory import memory
from src.utils import get_logger, get_config
from src.utils.sensitive import sensitive_filter

logger = get_logger()


class ChatService:
    def __init__(self):
        self.llm = None
        self.system_prompt = None
        self.response_max_chars = get_config("llm.response_max_chars", 150)
        self._initialized = False
    
    async def init(self):
        if self._initialized:
            return
        
        try:
            self.llm = get_llm_provider()
            self.system_prompt = get_system_prompt()
            self._initialized = True
            logger.info("ChatService initialized successfully")
        except Exception as e:
            logger.error(f"ChatService init failed: {e}")
            self.llm = None
            self._initialized = False
    
    def _truncate_response(self, text: str, max_chars: int = None) -> str:
        if max_chars is None:
            max_chars = self.response_max_chars
        
        if len(text) <= max_chars:
            return text
        
        truncated = text[:max_chars]
        last_punct = max(
            truncated.rfind("。"),
            truncated.rfind("！"),
            truncated.rfind("？"),
            truncated.rfind("~"),
            truncated.rfind("…"),
            truncated.rfind("，")
        )
        
        if last_punct > max_chars * 0.6:
            truncated = truncated[:last_punct + 1]
        else:
            truncated = truncated + "..."
        
        return truncated
    
    async def chat(
        self,
        session_id: str,
        user_input: str,
        user_id: Optional[str] = None
    ) -> str:
        if self.llm is None:
            await self.init()
        
        if self.llm is None:
            logger.error("LLM provider not available")
            return "抱歉，爱芮没电了，我们稍后再聊吧~"
        
        has_sensitive, found_words = sensitive_filter.check(user_input)
        if has_sensitive:
            logger.warning(f"Sensitive words detected from user {user_id}: {found_words}")
            return "抱歉，你的消息包含敏感内容，无法处理~"
        
        await memory.add_message(session_id, "user", user_input)
        
        context = await memory.get_context(session_id)
        
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(context)
        
        try:
            logger.info(f"Sending chat request, messages count: {len(messages)}")
            response = await self.llm.chat(messages, max_tokens=get_config("llm.max_tokens", 300))
            reply = response.content
            
            logger.info(f"LLM response: {reply[:100] if reply else 'None'}...")
            
            if not reply or not reply.strip():
                logger.warning("LLM returned empty response")
                return "嗯...我好像不知道该说什么了~"
            
            reply = self._truncate_response(reply)
            
            filtered_reply = sensitive_filter.filter(reply)
            
            if not filtered_reply or not filtered_reply.strip():
                filtered_reply = "这个话题我不太好说呢~"
            
            await memory.add_message(session_id, "assistant", filtered_reply)
            
            logger.info(f"Final reply: {filtered_reply}")
            return filtered_reply
            
        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            return "抱歉，我现在有点累了，稍后再聊吧~"
    
    async def chat_stream(
        self,
        session_id: str,
        user_input: str,
        user_id: Optional[str] = None
    ):
        if self.llm is None:
            await self.init()
        
        if self.llm is None:
            yield "抱歉，AI服务暂时不可用，请稍后再试~"
            return
        
        has_sensitive, found_words = sensitive_filter.check(user_input)
        if has_sensitive:
            logger.warning(f"Sensitive words detected from user {user_id}: {found_words}")
            yield "抱歉，你的消息包含敏感内容，无法处理~"
            return
        
        await memory.add_message(session_id, "user", user_input)
        
        context = await memory.get_context(session_id)
        
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(context)
        
        full_reply = ""
        char_count = 0
        try:
            async for chunk in self.llm.chat_stream(messages, max_tokens=get_config("llm.max_tokens", 300)):
                char_count += len(chunk)
                if char_count <= self.response_max_chars + 50:
                    full_reply += chunk
                    yield chunk
                elif char_count <= self.response_max_chars + 100:
                    full_reply += chunk
            
            full_reply = self._truncate_response(full_reply)
            
            filtered_reply = sensitive_filter.filter(full_reply)
            
            await memory.add_message(session_id, "assistant", filtered_reply)
            
        except Exception as e:
            logger.error(f"Chat stream error: {e}", exc_info=True)
            yield "抱歉，我现在有点累了，稍后再聊吧~"
    
    async def clear_session(self, session_id: str):
        await memory.clear_session(session_id)
        logger.info(f"Session cleared: {session_id}")


chat_service = ChatService()
