# LLM_model_api/ollama_api.py
import ollama
from .base_api import BaseChatAPI


class OllamaChat(BaseChatAPI):
    """Ollama 本地聊天实现"""

    def __init__(self, system_prompt: str = "you are a helpful assistant",
                 max_history: int = 20,
                 model_name: str = "deepseek-r1:8b"):
        super().__init__(system_prompt, max_history)
        self.model_name = model_name

    def chat(self, user_prompt: str) -> str:
        """发送消息并获取回复"""
        messages = self._build_messages(user_prompt)

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages
            )

            result = response['message']['content']

            self._update_history(user_prompt, result)

            return result

        except Exception as e:
            error_msg = f"Ollama 调用失败：{str(e)}"
            print(f"❌ {error_msg}")
            return error_msg


# 兼容旧的 create_chat 函数
def create_chat(system_prompt='you are a helpful assistant',
                max_history=20,
                model_name=""):
    """兼容旧代码的工厂函数"""
    return OllamaChat(system_prompt, max_history, model_name).chat
