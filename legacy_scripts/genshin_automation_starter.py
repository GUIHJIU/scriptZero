"""
原神自动化启动器
用于启动原神与BetterGI的自动化流程
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from genshin_bettergi_adapter import ConfigurableGenshinBetterGIAdapter


async def run_genshin_automation(config_path: str = "genshin_bettergi_config.yaml"):
    """
    运行原神自动化流程
    
    Args:
        config_path: 配置文件路径
    """
    print("启动原神与BetterGI自动化流程...")
    
    try:
        # 从配置文件创建适配器
        adapter = ConfigurableGenshinBetterGIAdapter({
            'genshin_path': r"F:\Genshin Impact\Genshin Impact Game\YuanShen.exe",
            'bettergi_path': r"F:\better\BetterGI.exe",
            'check_interval': 30,
            'timeout': 7200,  # 2小时
            'close_after_completion': True,
            'click_positions': {
                'start_button': (150, 200),  # 需要根据实际情况调整
                'dragon_button': (250, 150),  # 需要根据实际情况调整
                'play_button': (350, 150)     # 需要根据实际情况调整
            }
        })
        
        # 执行自动化流程
        result = await adapter.run_automation()
        
        if result:
            print("\n✅ 自动化流程成功完成！")
        else:
            print("\n❌ 自动化流程执行失败！")
            
        return result
        
    except FileNotFoundError as e:
        print(f"\n❌ 配置文件或程序路径不存在: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 执行过程中发生错误: {e}")
        return False


def interactive_setup():
    """交互式设置函数"""
    print("🎮 原神与BetterGI自动化设置向导")
    print("=" * 50)
    
    # 获取游戏路径
    genshin_path = input("请输入原神游戏路径 (默认: F:\\Genshin Impact\\Genshin Impact Game\\YuanShen.exe): ").strip()
    if not genshin_path:
        genshin_path = r"F:\Genshin Impact\Genshin Impact Game\YuanShen.exe"
    
    # 获取脚本框架路径
    bettergi_path = input("请输入BetterGI路径 (默认: F:\\better\\BetterGI.exe): ").strip()
    if not bettergi_path:
        bettergi_path = r"F:\better\BetterGI.exe"
    
    # 获取其他配置
    timeout_input = input("请输入超时时间（秒，默认7200）: ").strip()
    timeout = int(timeout_input) if timeout_input.isdigit() else 7200
    
    close_after = input("完成后是否关闭游戏和脚本框架？(Y/n，默认Y): ").strip().lower()
    close_after_completion = close_after != 'n'
    
    print("\n📋 确认配置:")
    print(f"  原神路径: {genshin_path}")
    print(f"  BetterGI路径: {bettergi_path}")
    print(f"  超时时间: {timeout}秒")
    print(f"  完成后关闭: {'是' if close_after_completion else '否'}")
    
    confirm = input("\n确认以上配置？(Y/n): ").strip().lower()
    if confirm == 'n':
        print("已取消配置。")
        return None
    
    return {
        'genshin_path': genshin_path,
        'bettergi_path': bettergi_path,
        'check_interval': 30,
        'timeout': timeout,
        'close_after_completion': close_after_completion,
        'click_positions': {
            'start_button': (150, 200),  # 需要在实际使用时调整
            'dragon_button': (250, 150),  # 需要在实际使用时调整
            'play_button': (350, 150)     # 需要在实际使用时调整
        }
    }


async def main():
    """主函数"""
    print("🚀 ScriptZero - 原神与BetterGI自动化适配器")
    print("=" * 50)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == '--setup' or sys.argv[1] == '-s':
            config = interactive_setup()
            if config:
                adapter = ConfigurableGenshinBetterGIAdapter(config)
                result = await adapter.run_automation()
                if result:
                    print("\n✅ 自动化流程成功完成！")
                else:
                    print("\n❌ 自动化流程执行失败！")
        else:
            config_path = sys.argv[1]
            await run_genshin_automation(config_path)
    else:
        # 直接运行默认配置
        await run_genshin_automation()


if __name__ == "__main__":
    asyncio.run(main())