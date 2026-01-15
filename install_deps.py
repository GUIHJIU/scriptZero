#!/usr/bin/env python3
"""
ScriptZero 依赖安装脚本
用于安装项目所需的所有依赖
"""
import subprocess
import sys
import os
from pathlib import Path


def install_requirements():
    """安装requirements.txt中的依赖"""
    requirements_path = Path(__file__).parent / "requirements.txt"
    
    if not requirements_path.exists():
        print(f"错误: 未找到 {requirements_path}")
        return False
    
    print("正在安装依赖...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_path)
        ])
        print("依赖安装完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
        return False


def install_pydantic():
    """确保安装了pydantic"""
    try:
        import pydantic
        print("Pydantic 已安装")
    except ImportError:
        print("正在安装 Pydantic...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pydantic>=1.10.0"])
            print("Pydantic 安装完成！")
        except subprocess.CalledProcessError as e:
            print(f"Pydantic 安装失败: {e}")
            return False
    return True


def install_pyside6():
    """确保安装了PySide6"""
    try:
        import PySide6
        print("PySide6 已安装")
    except ImportError:
        print("正在安装 PySide6...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PySide6"])
            print("PySide6 安装完成！")
        except subprocess.CalledProcessError as e:
            print(f"PySide6 安装失败: {e}")
            return False
    return True


def verify_installation():
    """验证安装"""
    print("\n验证安装...")
    
    # 检查关键依赖
    dependencies = [
        ("pyautogui", "pyautogui"),
        ("pydirectinput", "pydirectinput"),
        ("pygetwindow", "pygetwindow"),
        ("pywinauto", "pywinauto"),
        ("cv2", "opencv-python"),
        ("numpy", "numpy"),
        ("psutil", "psutil"),
        ("yaml", "pyyaml"),
        ("ttkbootstrap", "ttkbootstrap"),
        ("PySide6", "PySide6"),
        ("pydantic", "pydantic"),
    ]
    
    missing_deps = []
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f"✓ {module_name} (via {package_name})")
        except ImportError:
            print(f"✗ {module_name} (via {package_name}) - 缺失")
            missing_deps.append(package_name)
    
    if missing_deps:
        print(f"\n缺失依赖: {', '.join(missing_deps)}")
        print("请运行: pip install " + " ".join(missing_deps))
        return False
    
    print("\n所有依赖验证通过！")
    return True


def main():
    """主函数"""
    print("ScriptZero 依赖安装器")
    print("=" * 30)
    
    # 安装基础依赖
    if not install_requirements():
        print("基础依赖安装失败，请手动安装")
        return 1
    
    # 安装额外依赖
    if not install_pydantic():
        print("Pydantic 安装失败")
        return 1
    
    if not install_pyside6():
        print("PySide6 安装失败")
        return 1
    
    # 验证安装
    if not verify_installation():
        print("\n安装验证失败，请检查依赖")
        return 1
    
    print("\n所有依赖安装并验证成功！")
    print("您可以运行以下命令启动应用:")
    print("  python start_gui.py")
    print("  或")
    print("  python -m src.apps.gui.modern_gui_app")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())