# LLM_model_api/base_api.py
from abc import ABC, abstractmethod
from typing import List, Dict


class BaseChatAPI(ABC):
    """聊天 API 抽象基类 - 定义统一接口"""

    def __init__(self, system_prompt: str, max_history: int = 20):
        """
        Args:
            system_prompt: 系统提示词
            max_history: 最大历史对话数
        """
        self.system_prompt = system_prompt
        self.max_history = max_history
        self.history: List[Dict[str, str]] = []

    @abstractmethod
    def chat(self, user_prompt: str) -> str:
        """
        发送消息并获取回复（抽象方法）

        Args:
            user_prompt: 用户输入

        Returns:
            AI 回复文本
        """
        pass

    def _build_messages(self, user_prompt: str) -> List[Dict[str, str]]:
        """构建消息列表（通用方法）"""
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": user_prompt})
        return messages

    def _update_history(self, user_prompt: str, response: str):
        """更新历史记录（通用方法）"""
        self.history.append({"role": "user", "content": user_prompt})
        self.history.append({"role": "assistant", "content": response})

        # 限制长度
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-(self.max_history * 2):]

    def clear_history(self):
        """清空历史记录"""
        self.history = []

    def get_history(self) -> List[Dict[str, str]]:
        """获取历史记录"""
        return self.history.copy()
