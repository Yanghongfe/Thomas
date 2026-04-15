# live2d_wrapper/model_controller.py
import logging
import live2d.v3 as live2d

logger = logging.getLogger(__name__)


class ModelController:
    """Live2D 模型控制器 - 简化的封装"""

    def __init__(self):
        self.model = None
        self.is_loaded = False

    def load_model(self, model_path: str) -> bool:
        """
        加载模型

        Args:
            model_path: 模型文件路径（.model3.json）

        Returns:
            是否加载成功
        """
        try:
            logger.info(f"正在加载模型：{model_path}")
            self.model = live2d.LAppModel()
            self.model.LoadModelJson(model_path)
            self.is_loaded = True
            logger.info(f"✅ 模型加载成功")
            return True
        except Exception as e:
            logger.error(f"❌ 模型加载失败：{e}")
            self.is_loaded = False
            return False

    def set_expression(self, expression_name: str):
        """设置表情"""
        if not self.is_loaded or not self.model:
            logger.warning("模型未加载，无法设置表情")
            return

        logger.info(f"设置表情：{expression_name}")
        self.model.SetExpression(expression_name)

    def start_motion(self, group: str, index: int, priority: int):
        """播放动作"""
        if not self.is_loaded or not self.model:
            logger.warning("模型未加载，无法播放动作")
            return

        logger.info(f"播放动作：{group}[{index}], 优先级={priority}")
        try:
            self.model.StartMotion(group, index, priority)
        except Exception as e:
            logger.error(f"动作播放失败：{e}")

    def update(self):
        """更新模型状态"""
        if self.is_loaded and self.model:
            self.model.Update()

    def draw(self):
        """绘制模型"""
        if self.is_loaded and self.model:
            self.model.Draw()

    def reset_to_idle(self, expression_id: int = 1):
        """
        回归待机状态

        Args:
            expression_id: 默认表情 ID（默认 1）
        """
        if not self.is_loaded:
            return

        from core.emotion_manager import EmotionManager
        expr_name = EmotionManager.get_expression(expression_id)

        logger.info(f"回归待机：表情={expr_name}, 动作=Idle[0]")
        self.start_motion("Idle", 0, 2)
        self.set_expression(expr_name)
