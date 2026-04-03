import re
from typing import List, Set, Optional
from pathlib import Path

from src.utils import get_config, get_logger

logger = get_logger()


class SensitiveWordFilter:
    def __init__(self):
        self.enabled = get_config("sensitive_words.enabled", True)
        self.word_list_path = get_config("sensitive_words.word_list_path", "./data/words/")
        
        self._sensitive_words: Set[str] = set()
        self._regex_patterns: List[re.Pattern] = []
        
        if self.enabled:
            self._load_word_lists()
    
    def _load_word_lists(self):
        word_path = Path(self.word_list_path)
        if not word_path.exists():
            word_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created word list directory: {word_path}")
            return
        
        for file_path in word_path.glob("*.txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        word = line.strip()
                        if word and not word.startswith("#"):
                            if word.startswith("regex:"):
                                pattern = word[6:].strip()
                                try:
                                    self._regex_patterns.append(re.compile(pattern, re.IGNORECASE))
                                except re.error as e:
                                    logger.warning(f"Invalid regex pattern: {pattern}, error: {e}")
                            else:
                                self._sensitive_words.add(word.lower())
                
                logger.info(f"Loaded words from: {file_path}")
            except Exception as e:
                logger.error(f"Failed to load word list {file_path}: {e}")
        
        logger.info(f"Loaded {len(self._sensitive_words)} sensitive words and {len(self._regex_patterns)} regex patterns")
    
    def add_word(self, word: str):
        self._sensitive_words.add(word.lower())
    
    def add_regex(self, pattern: str) -> bool:
        try:
            self._regex_patterns.append(re.compile(pattern, re.IGNORECASE))
            return True
        except re.error:
            return False
    
    def check(self, text: str) -> tuple[bool, List[str]]:
        if not self.enabled:
            return False, []
        
        found_words = []
        text_lower = text.lower()
        
        for word in self._sensitive_words:
            if word in text_lower:
                found_words.append(word)
        
        for pattern in self._regex_patterns:
            if pattern.search(text):
                found_words.append(f"regex:{pattern.pattern}")
        
        return len(found_words) > 0, found_words
    
    def filter(self, text: str, replacement: str = "*") -> str:
        if not self.enabled:
            return text
        
        result = text
        
        for word in self._sensitive_words:
            if word in result.lower():
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                result = pattern.sub(replacement * len(word), result)
        
        for pattern in self._regex_patterns:
            result = pattern.sub(replacement, result)
        
        return result
    
    def is_safe(self, text: str) -> bool:
        has_sensitive, _ = self.check(text)
        return not has_sensitive


sensitive_filter = SensitiveWordFilter()
