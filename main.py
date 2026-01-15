"""
ScriptZero - 零适配游戏自动化框架
主入口文件 - 支持命令行和GUI模式
"""
import asyncio
import sys
import argparse
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from game_automation_framework import GameAutomationFramework


def print_hi(name):
    """打印欢迎信息"""
    print(f'Hi, {name}')


async def run_automation(config_path: str = "config.yaml"):
    """运行自动化任务"""
    try:
        framework = GameAutomationFramework(config_path)
        await framework.run()
    except FileNotFoundError:
        print(f"配置文件 {config_path} 不存在，创建示例配置文件...")
        create_example_config(config_path)
        framework = GameAutomationFramework(config_path)
        await framework.run()
    except Exception as e:
        print(f"执行出错: {e}")


def create_example_config(config_path: str):
    """创建示例配置文件"""
    example_config = """version: 1.0
name: "示例自动化任务"

variables:
  game_path: "C:/Games/ExampleGame/game.exe"
  account: "player123"

games:
  example_game:
    executable: "${variables.game_path}"
    arguments: ["-windowed"]
    window_title: "ExampleGame"

workflow:
  - name: "示例脚本链"
    type: "script_chain"
    scripts:
      - path: "scripts/example_script.py"
        arguments: ["--mode", "auto"]
        completion:
          any_of:
            - type: "timeout"
              seconds: 300
"""
    
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(example_config)
    print(f"已创建示例配置文件: {config_path}")


def run_gui():
    """运行图形用户界面"""
    try:
        # 首先尝试使用现代化UI
        from src.ui.modern_ui import ModernUI
        app = ModernUI()
        app.run()
    except ImportError as e:
        print(f"现代化UI导入失败: {e}")
        print("尝试使用传统UI...")
        try:
            from src.ui.main_window import MainWindow
            app = MainWindow()
            app.run()
        except ImportError as e2:
            print(f"GUI模块导入失败: {e2}")
            print("请确保安装了必要的GUI库")
            sys.exit(1)


def main():
    """主函数 - 统一入口点"""
    parser = argparse.ArgumentParser(description='ScriptZero - 零适配游戏自动化框架')
    parser.add_argument('config_file', nargs='?', default='config.yaml',
                       help='配置文件路径 (默认: config.yaml)')
    parser.add_argument('--gui', action='store_true',
                       help='启动图形用户界面模式')
    parser.add_argument('--cli', action='store_true',
                       help='强制使用命令行界面模式')
    
    args = parser.parse_args()
    
    # 根据参数决定运行模式
    if args.gui:
        print_hi('ScriptZero (GUI Mode)')
        run_gui()
    elif args.cli or len(sys.argv) == 1:  # 没有参数时默认使用CLI模式
        print_hi('ScriptZero (CLI Mode)')
        
        # 从命令行参数获取配置文件路径（如果提供）
        config_file = args.config_file
        
        # 运行自动化任务
        asyncio.run(run_automation(config_file))
    else:
        # 如果指定了配置文件或其他参数，则使用CLI模式
        print_hi('ScriptZero (CLI Mode)')
        config_file = args.config_file
        asyncio.run(run_automation(config_file))


if __name__ == '__main__':
    main()