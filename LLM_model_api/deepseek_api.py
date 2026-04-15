# LLM_model_api/deepseek_api.py
import os
from openai import OpenAI
from dotenv import load_dotenv
from .base_api import BaseChatAPI

load_dotenv()


class DeepSeekChat(BaseChatAPI):
    """DeepSeek 聊天实现"""
    
    def __init__(self, system_prompt: str = "you are a helpful assistant", 
                 max_history: int = 20):
        super().__init__(system_prompt, max_history)
        
        self.client = OpenAI(
            api_key=os.environ.get('DEEPSEEK_API_KEY'),
            base_url=os.environ.get('BASE_URL')
        )
        self.model_name = "deepseek-chat"
    
    def chat(self, user_prompt: str) -> str:
        """发送消息并获取回复"""
        messages = self._build_messages(user_prompt)
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=False
        )
        
        result = response.choices[0].message.content
        
        self._update_history(user_prompt, result)
        
        return result


# 兼容旧的 create_chat 函数
def create_chat(system_prompt='you are a helpful assistant', max_history=20):
    """兼容旧代码的工厂函数"""
    return DeepSeekChat(system_prompt, max_history).chat
