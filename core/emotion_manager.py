# core/emotion_manager.py
import logging

logger = logging.getLogger(__name__)


class EmotionManager:
    """表情管理器 - 统一管理表情映射和日志"""

    # 表情 ID → 文件名映射
    EXPRESSION_MAP = {
        1: "exp_01",  # 待机正常笑脸
        2: "exp_02",  # 闭眼微笑
        3: "exp_03",  # 逆向闭眼
        4: "exp_04",  # 星星眼
        5: "exp_05",  # 委屈表情
        6: "exp_06",  # 脸红
        7: "exp_07",  # 震惊脸
        8: "exp_08",  # 无语脸
    }

    @classmethod
    def get_expression(cls, emotion_id: int) -> str:
        """获取表情文件名，带日志"""
        expression = cls.EXPRESSION_MAP.get(emotion_id, "exp_01")
        logger.info(f"表情切换：ID={emotion_id} → {expression}")
        return expression

    @staticmethod
    def log_motion(group: str, index: int, priority: int):
        """记录动作播放日志"""
        logger.info(f"播放动作：{group}[{index}], 优先级={priority}")

    @staticmethod
    def log_reset():
        """记录回归待机日志"""
        logger.info("回归待机状态")
