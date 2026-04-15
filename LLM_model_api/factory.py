# LLM_model_api/factory.py
from typing import Optional, Type
from .base_api import BaseChatAPI
from .deepseek_api import DeepSeekChat
from .ollama_api import OllamaChat


class ModelFactory:
    """模型工厂类 - 统一管理所有 AI 模型"""

    # 注册表：记录所有可用的模型
    _registry: dict[str, Type[BaseChatAPI]] = {
        "deepseek": DeepSeekChat,
        "ollama": OllamaChat,
    }

    @classmethod
    def register_model(cls, name: str, model_class: Type[BaseChatAPI]):
        """
        注册新的模型

        Args:
            name: 模型名称（如 "gpt4", "claude"）
            model_class: 模型类（必须是 BaseChatAPI 的子类）
        """
        cls._registry[name.lower()] = model_class
        print(f"✅ 已注册模型：{name}")

    @classmethod
    def create(cls, provider: str = "ollama", **kwargs) -> BaseChatAPI:
        """
        创建模型实例（工厂方法）

        Args:
            provider: 模型提供商（"deepseek", "ollama" 等）
            **kwargs: 传递给模型构造函数的参数

        Returns:
            模型实例

        Raises:
            ValueError: 不支持的提供商
        """
        provider = provider.lower()

        if provider not in cls._registry:
            available = ", ".join(cls._registry.keys())
            raise ValueError(
                f"不支持的模型提供商：{provider}\n"
                f"可用的提供商：{available}"
            )

        model_class = cls._registry[provider]
        return model_class(**kwargs)

    @classmethod
    def list_available_models(cls) -> list[str]:
        """列出所有可用的模型"""
        return list(cls._registry.keys())


# 快捷函数（兼容旧代码）
def create_chat(provider: str = "ollama", **kwargs):
    """
    快捷创建聊天函数

    Args:
        provider: 模型提供商
        **kwargs: 模型参数

    Returns:
        chat 函数
    """
    model = ModelFactory.create(provider, **kwargs)
    return model.chat
