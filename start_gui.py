#!/usr/bin/env python3
"""
ScriptZero GUI启动器
用于启动图形用户界面
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