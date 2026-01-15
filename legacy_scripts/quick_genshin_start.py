"""
快速启动脚本 - 原神与BetterGI自动化
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from genshin_automation_starter import run_genshin_automation

print("🎮 快速启动 - 原神与BetterGI自动化")
print("=" * 40)
print("即将启动自动化流程...")
print("- 启动BetterGI脚本框架")
print("- 启动原神游戏")
print("- 执行自动化操作")
print("- 监控完成状态")
print("=" * 40)

async def quick_start():
    """快速启动函数"""
    result = await run_genshin_automation()
    return result

if __name__ == "__main__":
    try:
        success = asyncio.run(quick_start())
        if success:
            input("\n按回车键退出...")
        else:
            input("\n按回车键退出...")
    except KeyboardInterrupt:
        print("\n\n用户中断了自动化流程")
        input("按回车键退出...")
    except Exception as e:
        print(f"\n发生错误: {e}")
        input("按回车键退出...")