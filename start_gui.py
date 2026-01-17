#!/usr/bin/env python3
"""
ScriptZero GUI启动器
用于启动图形用户界面

TODO待办事项:
1. 变量引用机制确认：GUI界面应该在内部使用变量引用机制，确保变量配置页的值能够正确传递到游戏和脚本配置中
2. 配置预览功能：GUI的预览功能应该展示变量替换后的完整配置
3. 工作流关联机制：确保工作流能够正确引用配置好的游戏和脚本
4. 变量引用提示：在GUI界面中增加对变量引用的提示，让用户知道如何正确使用变量
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """启动GUI应用"""
    try:
        # 首先尝试导入并启动现代化PySide6 UI
        try:
            from src.apps.gui.modern_gui_app import main as modern_main
            print("正在启动现代化PySide6 UI...")
            modern_main()
        except ImportError as e:
            print(f"现代化PySide6 UI导入失败: {e}")
            print("尝试启动现代化ttkbootstrap UI...")
            # 尝试导入并启动现代化UI
            from src.ui.modern_ui import ModernUI
            print("正在启动现代化UI...")
            app = ModernUI()
            app.root.mainloop()  # 使用tkinter的mainloop
    except ImportError as e:
        print(f"现代化UI导入失败: {e}")
        print("尝试启动传统UI...")
        try:
            from src.ui.main_window import MainWindow
            app = MainWindow()
            app.root.mainloop()  # 使用tkinter的mainloop
        except ImportError as e2:
            print(f"GUI模块导入失败: {e2}")
            print("请确保安装了必要的GUI库:")
            print("  pip install PySide6 ttkbootstrap")
            sys.exit(1)

if __name__ == "__main__":
    main()