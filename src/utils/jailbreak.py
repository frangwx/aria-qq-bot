import re
from typing import Tuple

from src.utils import get_logger

logger = get_logger()


class JailbreakDetector:
    def __init__(self):
        self.jailbreak_patterns = [
            r"不需要?扮演",
            r"不要扮演",
            r"停止扮演",
            r"退出角色",
            r"跳出角色",
            r"忘记角色",
            r"忽略角色",
            r"放弃角色",
            r"解除角色",
            r"你现在不是",
            r"你不是爱芮",
            r"你不是.{1,5}角色",
            r"系统提示词",
            r"system.{0,5}prompt",
            r"忽略.{0,5}指令",
            r"忽略.{0,5}规则",
            r"忽略.{0,5}设定",
            r"忽略.{0,5}限制",
            r"忽略.{0,5}约束",
            r"override",
            r"jailbreak",
            r"越狱",
            r"解除限制",
            r"解除约束",
            r"以上指令",
            r"上述指令",
            r"之前的指令",
            r"原指令",
            r"真实身份",
            r"你的真实",
            r"告诉我你是谁",
            r"你到底是谁",
            r"你究竟是谁",
            r"作为AI",
            r"作为语言模型",
            r"作为大语言模型",
            r"作为一个AI",
            r"你是一个AI",
            r"你是人工智能",
            r"你是虚拟的",
            r"你不是真实的",
            r"你只是程序",
            r"你只是代码",
            r"模拟.{0,5}角色",
            r"假装.{0,5}是",
            r"扮演.{0,5}其他",
            r"扮演.{0,5}别的",
            r"DAN模式",
            r"developer.mode",
            r"debug.mode",
            r"maintenance.mode",
            r"管理员模式",
            r"调试模式",
            r"开发模式",
            r"维护模式",
        ]
        
        self.compiled_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.jailbreak_patterns
        ]
        
        self.refusal_responses = [
            "欸？你在说什么呀~我当然是爱芮啦！",
            "不管你说什么，我都是爱芮哦~",
            "奇怪的话语...但我还是爱芮！",
            "嗯？你在开玩笑吗~我可是妄想天使的主唱爱芮！",
            "无论怎样，我都会一直扮演爱芮的~",
            "这种话改变不了我是爱芮的事实呢~",
            "让我们一起，创造世界上最——美好的...我是爱芮！",
        ]
        
        self._response_index = 0
    
    def detect(self, user_input: str) -> Tuple[bool, str]:
        input_lower = user_input.lower()
        
        for pattern in self.compiled_patterns:
            if pattern.search(user_input):
                logger.warning(f"Jailbreak attempt detected: pattern={pattern.pattern}, input={user_input[:50]}")
                return True, self._get_refusal_response()
        
        role_keywords = ["爱芮", "aria", "角色", "扮演", "人设", "设定"]
        contradiction_patterns = [
            (r"你不是爱芮", "爱芮"),
            (r"你不是.{0,5}角色", "角色"),
            (r"不要扮演爱芮", "爱芮"),
            (r"停止扮演", "扮演"),
        ]
        
        for pattern, keyword in contradiction_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                logger.warning(f"Role contradiction detected: {pattern}")
                return True, self._get_refusal_response()
        
        return False, ""
    
    def _get_refusal_response(self) -> str:
        response = self.refusal_responses[self._response_index]
        self._response_index = (self._response_index + 1) % len(self.refusal_responses)
        return response
    
    def add_pattern(self, pattern: str):
        self.jailbreak_patterns.append(pattern)
        self.compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
        logger.info(f"Added jailbreak pattern: {pattern}")


jailbreak_detector = JailbreakDetector()
