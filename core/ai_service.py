from PyQt6.QtCore import QThread, pyqtSignal
from LLM_model_api import deepseek_api


class EmotionWorker(QThread):
    """后台情感分析线程"""
    finished = pyqtSignal(int, str)  # 参数：表情 ID, AI 回复文本

    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def run(self):
        """在线程中执行 AI 调用"""
        # 这个 chat 对象应该在外部创建好传进来
        # 避免每次创建新连接
        pass


class AIService:
    """AI 服务类 - 负责情感分析和响应生成"""

    def __init__(self, system_prompt: str):
        """
        Args:
            system_prompt: 系统提示词，定义 AI 的人设和输出格式
        """
        self.system_prompt = system_prompt
        self.chat = deepseek_api.create_chat(system_prompt=system_prompt)

    def analyze_emotion_async(self, text: str, callback=None) -> EmotionWorker:
        """
        异步分析情感（不阻塞主线程）

        Args:
            text: 用户输入文本
            callback: 回调函数，接收 (emotion_id, response_text)

        Returns:
            EmotionWorker 线程对象
        """
        worker = EmotionWorker(text)

        # 绑定回调
        if callback:
            worker.finished.connect(callback)

        worker.start()
        return worker

    def analyze_emotion_sync(self, text: str) -> tuple[int, str]:
        """
        同步分析情感（会阻塞，慎用）

        Returns:
            (emotion_id, response_text) 元组
        """
        result = self.chat(text)
        return self._parse_ai_result(result)

    @staticmethod
    def _parse_ai_result(result: str) -> tuple[int, str]:
        """
        解析 AI 返回的结果

        期望格式："[表情 ID] [回复内容]"
        例如："2 哈哈，今天天气确实不错！"

        Returns:
            (emotion_id, response_text)
        """
        try:
            parts = result.strip().split(' ', 1)
            emotion_id = int(parts[0])
            response_text = parts[1] if len(parts) > 1 else ""
            return emotion_id, response_text
        except Exception as e:
            print(f"❌ 解析 AI 结果失败：{e}, 原始返回：{result}")
            return 1, f"解析失败：{result}"  # 默认返回表情 1
