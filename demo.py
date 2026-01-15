#!/usr/bin/env python3
"""
ScriptZero 项目演示脚本
这是一个面向初学者的项目介绍和使用演示
"""
import asyncio
import sys
from pathlib import Path

print("=" * 60)
print("欢迎使用 ScriptZero - 游戏自动化脚本管理框架")
print("=" * 60)

print("\n1. 什么是 ScriptZero？")
print("   ScriptZero 是一个现代化的游戏自动化脚本管理框架")
print("   它可以帮助您自动运行游戏脚本，比如原神的日常任务")

print("\n2. 项目的主要特点：")
print("   • 模块化架构 - 支持多种游戏和脚本框架")
print("   • 统一配置 - 使用配置文件管理所有设置")
print("   • 图像识别 - 通过图像匹配自动操作")
print("   • 适配器模式 - 支持不同的游戏和脚本框架")

print("\n3. 当前支持的适配器：")
print("   • GenshinBetterGIAdapter: 原神与BetterGI框架适配器")
print("   • PythonAdapter: Python脚本执行适配器")
print("   • ExeAdapter: 可执行文件执行适配器")
print("   • AhkAdapter: AutoHotKey脚本执行适配器")

print("\n4. 如何使用 ScriptZero：")

print("\n   方法1: 命令行使用")
print("     # 启动配置向导")
print("     python -m src.cli config wizard")
print("     # 启动自动化任务")
print("     python -m src.cli start config.yaml")

print("\n   方法2: 图形界面使用")
print("     # 启动GUI界面")
print("     python start_gui.py")

print("\n5. 配置文件示例：")
print("   您刚才创建的 config.yaml 文件包含了自动化任务的所有设置")
print("   包括游戏路径、脚本框架路径、执行参数等")

print("\n6. 项目结构：")
print("   src/: 源代码目录")
print("     ├─ adapters/: 适配器模块（连接不同游戏和脚本框架）")
print("     ├─ config/: 配置系统（管理所有配置）")
print("     ├─ core/: 核心模块（框架基础功能）")
print("     ├─ ui/: 用户界面（GUI相关代码）")
print("     └─ utils/: 工具函数（辅助功能）")

print("\n7. 工作原理：")
print("   1. 读取配置文件，确定要运行的游戏和脚本框架")
print("   2. 启动游戏客户端")
print("   3. 启动脚本框架（如BetterGI）")
print("   4. 通过图像识别技术监控游戏界面")
print("   5. 根据预设流程自动点击按钮、执行操作")
print("   6. 监控任务完成状态并适时结束")

print("\n8. 注意事项：")
print("   • 请确保游戏和脚本框架路径正确")
print("   • 确保模板图片与实际游戏界面匹配")
print("   • 遵守游戏使用条款，合理使用自动化工具")

print("\n9. 现在您可以：")
print("   • 运行 'python -m src.cli config wizard' 重新创建配置")
print("   • 运行 'python -m src.cli start config.yaml' 启动自动化")
print("   • 运行 'python start_gui.py' 使用图形界面")
print("   • 查看 'README.md' 获取详细文档")

print("\n感谢使用 ScriptZero！")
print("=" * 60)