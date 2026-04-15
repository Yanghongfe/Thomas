from LLM_model_api import create_chat

# 使用 Ollama（默认）
chat = create_chat()
print(chat("你好"))

# 使用 DeepSeek
chat = create_chat(provider="deepseek")
print(chat("你好"))