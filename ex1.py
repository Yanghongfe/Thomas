import os
import sys
import time

import resources
import live2d.v3 as live2d
from PyQt6.QtWidgets import QApplication, QLineEdit
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import Qt, QTimer

from LLM_model_api import create_chat


from PyQt6.QtWidgets import QApplication, QLineEdit, QVBoxLayout, QWidget, QPushButton, QTextEdit
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QMouseEvent

system_prompt = """
你就是一个贴吧老哥，平时刷刷孙吧虎扑，看番打游戏，懂的也就正常人水平，不懂就直说。

【可选表情及对应ID】
1 - 待机正常笑脸（没啥事的时候）
2 - 闭眼微笑（挺开心的）
3 - 逆向闭眼（琢磨事/搞怪）
4 - 星星眼（我超，牛逼）
5 - 委屈表情（难过了/破防了）
6 - 脸红（不好意思了/被夸了）
7 - 震惊脸（啊？真的假的？）
8 - 无语脸（麻了/不想说话）

【大概这样】
知识类：
输入：1+1等于几
输出：2 1+1=2啊，这还用问？

输入：什么是黑洞
输出：7 黑洞就是恒星死了之后变成的，引力大得光都跑不出来，大概这么回事。


日常类：
输入：今天天气真好
输出：2 是啊，适合出去溜达。

输入：我心情不好
输出：5 咋了？出去走走吃点好的，别想太多。

"""


"""
模型基本信息
1是待机正常笑脸
2是 闭眼微笑
3是 逆向闭眼
4是 星星眼
5是 委屈表情
6是 脸红
7是 震惊脸
8是 无语脸
"""
'''
"Idle", 0 是正常待机
"Idle", 1 是待机 + 飘球

"TapBody, 0 是 抖动"
"TapBody, 1 是 摇头晃脑 手背在身后"
"TapBody, 2 是 扯帽子"
"TapBody, 3 是 画个爱心 然后星星眼"
"TapBody, 4 是 画个爱心 但是失败了 爆炸"
"TapBody, 5 是 发卡变成 金色 然后 全身进入无敌状态"
'''
"""
AddExpression
  AddIndexParamValue
  AddParameterValue
  Drag
  Draw
  GetCanvasSize
  GetCanvasSizePixel
  GetDrawableIds
  GetExpressionIds
  GetMotionGroups
  GetParamIds
  GetParameter
  GetParameterCount
  GetParameterValue
  GetPartCount
  GetPartId
  GetPartIds
  GetPartMultiplyColor
  GetPartScreenColor
  GetPixelsPerUnit
  GetSoundPath
  HasMocConsistencyFromFile
  HitPart
  HitTest
  IsMotionFinished
  LoadModelJson
  RemoveExpression
  ResetExpression
  ResetExpressions
  ResetParameters
  ResetPose
  Resize
  Rotate
  SetAutoBlinkEnable
  SetAutoBreathEnable
  SetDrawableMultiplyColor
  SetDrawableScreenColor
  SetExpression
  SetIndexParamValue
  SetOffset
  SetParameterValue
  SetPartMultiplyColor
  SetPartOpacity
  SetPartScreenColor
  SetRandomExpression
  SetScale
  SetScaleX
  SetScaleY
  StartMotion
  StartRandomMotion
  StopAllMotions
  Update
"""


from PyQt6.QtCore import QThread, pyqtSignal

# 使用 DeepSeek API（在线）
chat = create_chat(provider="deepseek", system_prompt=system_prompt)

class EmotionWorker(QThread):
    finished = pyqtSignal(str, str)  # 参数：情感结果, 原始文本
    def __init__(self, text, system_prompt):
        super().__init__()
        self.text = text
        self.system_prompt = system_prompt

    def run(self):
        # 在线程中调用API
        emotion = chat(self.text)
        self.finished.emit(emotion, self.text)



class Live2DWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.model = None
        self.resize(1000, 700)  # 增加窗口宽度
        self.setWindowTitle("Live2D 智能助手")
        self.setMinimumSize(700, 600)

        from PyQt6.QtCore import QTimer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)
        self.current_motion_index = 0
        
        # 提前初始化 UI 组件
        self.input_box = None
        self.output_box = None
        self.send_button = None
        self.title_label = None
        
        # 左右布局参数
        self.left_panel_width = 350  # 左侧聊天面板宽度

    def initializeGL(self):
        # 初始化 Live2D
        live2d.glInit()
        
        # 创建 UI 组件（包括 Live2D 模型的初始化）
        self.setupUI()
        
        # 强制刷新窗口
        self.update()
        self.repaint()

    def setupUI(self):
        """设置 UI 界面 - 使用绝对定位，左右分栏布局"""
        # === 1. 初始化 Live2D 模型（在 OpenGL 上下文中）===
        if not hasattr(self, 'model') or self.model is None:
            self.model = live2d.LAppModel()
            model_path = os.path.join(resources.RESOURCES_DIRECTORY, "v3", "Mao", "Mao.model3.json")
            try:
                self.model.LoadModelJson(model_path)
                print(f"✅ 模型加载成功：{model_path}")
            except Exception as e:
                print(f"❌ 模型加载失败：{e}")
                print(f"模型路径：{model_path}")
        
        # === 2. 左侧聊天面板 ===
        # 标题标签
        self.title_label = QLineEdit("💬 与 Live2D 助手聊天", self)
        self.title_label.setGeometry(10, 10, self.left_panel_width - 20, 35)
        self.title_label.setReadOnly(True)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            QLineEdit {
                background-color: #667eea;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                padding: 5px;
            }
        """)

        # 输出框（多行文本）
        self.output_box = QTextEdit(self)
        self.output_box.setGeometry(10, 55, self.left_panel_width - 20, 300)
        self.output_box.setReadOnly(True)
        self.output_box.setPlaceholderText("🤖 机器人回复会显示在这里...")
        self.output_box.setStyleSheet("""
            QTextEdit {
                background-color: #f0f4f8;
                border: 2px solid #667eea;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-family: 'Microsoft YaHei', sans-serif;
            }
        """)

        # 输入框
        self.input_box = QLineEdit(self)
        self.input_box.setGeometry(10, self.height() - 90, self.left_panel_width - 120, 40)
        self.input_box.setPlaceholderText("✨ 说点什么吧... (按 Enter 发送)")
        self.input_box.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-family: 'Microsoft YaHei', sans-serif;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
            }
        """)
        self.input_box.returnPressed.connect(self.on_input_submit)

        # 发送按钮
        self.send_button = QPushButton("发送 🚀", self)
        self.send_button.setGeometry(self.left_panel_width - 100, self.height() - 90, 90, 40)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #5568d3;
            }
            QPushButton:pressed {
                background-color: #4a5abf;
            }
        """)
        self.send_button.clicked.connect(self.on_input_submit)
        
        # 设置初始焦点到输入框
        if self.input_box:
            self.input_box.setFocus()

    def start_emotion_processing(self, text):
        """启动情感处理线程"""
        self.worker = EmotionWorker(text, system_prompt)
        self.worker.finished.connect(self.on_emotion_ready)
        self.worker.start()

    def on_emotion_ready(self, result, original_text):
        """情感分析完成后的回调"""
        print(f"AI 返回结果：{result}")

        try:
            # 检查是否是错误信息
            if "失败" in result or "error" in result.lower() or "not found" in result.lower():
                error_msg = f"[系统] ❌ AI 服务出错：{result}"
                print(error_msg)
                if self.output_box:
                    self.output_box.append(f"\n{error_msg}")
                    scrollbar = self.output_box.verticalScrollBar()
                    if scrollbar:
                        scrollbar.setValue(scrollbar.maximum())
                
                # 显示默认表情
                if self.model:
                    self.model.SetExpression("exp_01")
                return

            # 按空格分割，第一部分是表情 ID，后面是 AI 生成的文本
            parts = result.strip().split(' ', 1)
            
            # 验证是否有足够的内容
            if len(parts) < 2:
                raise ValueError(f"返回格式不正确，期望 '[ID] [内容]'，实际收到：{result}")
            
            emotion_id = int(parts[0])  # 表情 ID
            
            # 验证表情 ID 范围
            if emotion_id < 1 or emotion_id > 8:
                raise ValueError(f"表情 ID 超出范围 (1-8)：{emotion_id}")
            
            ai_response_text = parts[1] if len(parts) > 1 else ""  # AI 生成的文本

            # 显示 AI 的回复 (带时间戳)
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M:%S")
            
            if self.output_box:
                self.output_box.append(f"\n[{current_time}] 🤖: {ai_response_text}")
                
                # 自动滚动到底部
                scrollbar = self.output_box.verticalScrollBar()
                if scrollbar:
                    scrollbar.setValue(scrollbar.maximum())

            # 切换表情
            if self.model:
                expression_name = f"exp_{emotion_id:02d}"
                self.model.SetExpression(expression_name)
                print(f"切换到表情：{expression_name}")
                print(f"AI 回复：{ai_response_text}")
                
                # 播放动作 - 添加更安全的检查
                try:
                    # 先尝试播放 TapBody 动作
                    self.model.StartMotion("TapBody", 0, 1)
                    
                    # 2 秒后回到待机状态，并且表情回归 1
                    def reset_to_idle():
                        self.model.StartMotion("Idle", 0, 2)
                        self.model.SetExpression("exp_01")
                        print("已回归待机状态和表情 1")
                    
                    QTimer.singleShot(2000, reset_to_idle)
                except Exception as motion_error:
                    print(f"动作播放失败：{motion_error}")
                    # 动作失败不影响表情和文本显示

        except ValueError as ve:
            error_msg = f"[系统] ⚠️ 数据验证失败：{str(ve)}"
            print(error_msg)
            if self.output_box:
                self.output_box.append(f"\n{error_msg}")
            # 显示默认表情
            if self.model:
                self.model.SetExpression("exp_01")
                
        except Exception as e:
            error_msg = f"[系统] ⚠️ 解析出错：{str(e)}"
            print(f"{error_msg}, 原始返回：{result}")
            if self.output_box:
                self.output_box.append(f"\n{error_msg}")
            # 显示默认表情
            if self.model:
                self.model.SetExpression("exp_01")

    def paintGL(self):
        # 清除画面 - 渲染整个窗口
        live2d.clearBuffer()
        
        # 设置视口为右侧区域（保持模型比例）
        from OpenGL import GL
        
        # === 关键参数：放大倍数 ===
        zoom_factor = 0.5  # 放大倍数
        
        # === 计算可用区域 ===
        x_start = self.left_panel_width
        available_width = self.width() - self.left_panel_width
        available_height = self.height()
        
        # === 关键修复：简单直接的等比缩放 ===
        # 不要用复杂的 min_scale 计算，直接按固定比例缩放
        viewport_width = int(available_width / zoom_factor)
        viewport_height = int(available_height / zoom_factor)

        # 设置 OpenGL 视口（Y 轴负值让模型向下移动）
        y_offset = -40  # 向下移动 40px
        GL.glViewport(int(x_start), int(y_offset), int(viewport_width), int(viewport_height))
        
        # 更新并绘制模型
        if self.model:
            self.model.Update()
            self.model.Draw()

    def resizeGL(self, width, height):

        # 同时调整 UI 组件位置
        if hasattr(self, 'title_label') and self.title_label:
            self.title_label.setGeometry(10, 10, self.left_panel_width - 20, 35)
        
        if hasattr(self, 'output_box') and self.output_box:
            self.output_box.setGeometry(10, 55, self.left_panel_width - 20, height - 160)
        
        if hasattr(self, 'input_box') and self.input_box:
            self.input_box.setGeometry(10, height - 90, self.left_panel_width - 120, 40)
        
        if hasattr(self, 'send_button') and self.send_button:
            self.send_button.setGeometry(self.left_panel_width - 100, height - 90, 90, 40)

    def on_input_submit(self):
        """处理输入提交"""
        if not self.input_box:
            return
            
        text = self.input_box.text()
        if not text.strip():
            return

        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        
        print(f"你输入了：{text}")
        if self.output_box:
            self.output_box.append(f"[{current_time}] 👤: {text}")
        
        # 保存文本，稍后处理
        self.process_emotion(text)
        self.input_box.clear()  # 先清空输入框
        
        # 重新聚焦到输入框
        self.input_box.setFocus()

    def process_emotion(self, text):
        """处理情感分析（非阻塞版本）"""
        # 直接启动线程，不等待
        self.start_emotion_processing(text)
        # 显示加载提示
        if self.output_box:
            self.output_box.append("[系统] ⏳ 正在思考中...")

    def react_to_emotion(self, emotion_id):
        """根据情感ID让模型做出反应"""
        # 直接使用返回的数字ID

        try:
            self.model.StartMotion("tap_body", 0,3)
            print(f"已经播放")
        except Exception as e:
            print(f"无法播放动作: {e}")


        expression_name = f"exp_{int(emotion_id):02d}"  # 1 → "exp_01"
        self.model.SetExpression(expression_name)
        print(f"切换到表情: {expression_name}")
        self.output_box.setText(f"表情ID: {emotion_id}")

    def mousePressEvent(self, event: QMouseEvent):
        """处理鼠标点击事件"""
        # 检测是否点击在右侧 Live2D 区域
        if event.position().x() > self.left_panel_width:
            print(f"点击了 Live2D 模型区域")
            self.play_random_motion()

        super().mousePressEvent(event)

    def play_random_motion(self):
        """播放随机动作 - 使用 live2d 自带的 StartRandomMotion"""
        if not self.model:
            return

        try:
            # 从 TapBody 动作组中随机选择一个动作播放
            # 参数：动作组名称，优先级 (300=普通), draw_order(None), expression(None)
            self.model.StartRandomMotion("TapBody", 300, None, None)
            print("已播放随机 TapBody 动作")

            # 2 秒后回到待机状态和表情 1
            def reset_to_idle():
                self.model.StartMotion("Idle", 0, 2)
                self.model.SetExpression("exp_01")

            QTimer.singleShot(2000, reset_to_idle)

        except Exception as e:
            print(f"播放随机动作失败：{e}")



if __name__ == '__main__':
    # 启用高 DPI 支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # 初始化 Live2D
    live2d.init()
    
    # 创建应用和窗口
    app = QApplication(sys.argv)
    widget = Live2DWidget()
    
    # 先显示窗口
    widget.show()
    widget.raise_()
    widget.activateWindow()
    
    print("✅ 窗口已创建，正在显示...")
    
    # 运行应用
    sys.exit(app.exec())
