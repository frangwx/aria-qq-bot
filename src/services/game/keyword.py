import re
from typing import List, Dict, Optional
from dataclasses import dataclass

from src.utils import get_config, get_logger

logger = get_logger()


@dataclass
class KeywordRule:
    word: str
    reply: str
    is_regex: bool = False
    enabled: bool = True


class KeywordManager:
    def __init__(self):
        self._rules: List[KeywordRule] = []
        self._load_rules()
    
    def _load_rules(self):
        keywords_config = get_config("keywords", [])
        
        for item in keywords_config:
            if isinstance(item, dict):
                word = item.get("word", "")
                reply = item.get("reply", "")
                is_regex = item.get("regex", False)
                
                if word and reply:
                    self._rules.append(KeywordRule(
                        word=word,
                        reply=reply,
                        is_regex=is_regex
                    ))
        
        logger.info(f"Loaded {len(self._rules)} keyword rules")
    
    def add_rule(self, word: str, reply: str, is_regex: bool = False) -> bool:
        for rule in self._rules:
            if rule.word == word:
                return False
        
        self._rules.append(KeywordRule(word=word, reply=reply, is_regex=is_regex))
        logger.info(f"Added keyword rule: {word}")
        return True
    
    def remove_rule(self, word: str) -> bool:
        for i, rule in enumerate(self._rules):
            if rule.word == word:
                self._rules.pop(i)
                logger.info(f"Removed keyword rule: {word}")
                return True
        return False
    
    def match(self, text: str) -> Optional[str]:
        for rule in self._rules:
            if not rule.enabled:
                continue
            
            if rule.is_regex:
                if re.search(rule.word, text, re.IGNORECASE):
                    return rule.reply
            else:
                if rule.word.lower() in text.lower():
                    return rule.reply
        
        return None
    
    def get_rules(self) -> List[Dict]:
        return [
            {
                "word": rule.word,
                "reply": rule.reply,
                "is_regex": rule.is_regex,
                "enabled": rule.enabled
            }
            for rule in self._rules
        ]


keyword_manager = KeywordManager()
