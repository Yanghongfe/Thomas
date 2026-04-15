# 项目架构
LLM_live2d/
├── main.py                          # 应用入口（只负责启动）
├── config/
│   ├── __init__.py
│   ├── settings.py                  # 全局配置（路径、参数等）
│   └── system_prompt.py             # System Prompt 管理
│
├── core/                            # 核心业务逻辑层
│   ├── __init__.py
│   ├── ai_service.py                # AI 服务封装（含情感分析）
│   ├── emotion_manager.py           # 表情/动作映射管理
│   └── chat_memory.py               # 聊天历史管理（可选）
│
├── ui/                              # UI 层
│   ├── __init__.py
│   ├── chat_panel.py                # 左侧聊天面板组件
│   ├── live2d_view.py               # Live2D 渲染组件
│   └── main_window.py               # 主窗口（整合左右面板）
│
├── live2d_wrapper/                  # Live2D 封装层
│   ├── __init__.py
│   ├── model_controller.py          # Live2D 模型控制（表情/动作）
│   └── renderer.py                  # OpenGL 渲染封装
│
├── resources/                       # 资源文件（保持不变）
└── LLM_model_api/                   # AI API（保持不变）