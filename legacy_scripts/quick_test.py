"""
快速测试脚本 - 用于快速验证自动化流程
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from genshin_automation_starter import run_genshin_automation
from genshin_bettergi_adapter import ConfigurableGenshinBetterGIAdapter


async def quick_test():
    """快速测试函数 - 仅测试自动化部分，假定游戏已启动"""
    print("🎮 快速测试 - 原神与BetterGI自动化")
    print("=" * 40)
    print("正在进行快速功能验证...")
    print("- 验证图像模板可用性")
    print("- 测试基本自动化流程")
    print("- 检查配置有效性")
    print("=" * 40)
    
    # 创建一个简化的适配器实例，跳过游戏启动步骤
    config = {
        'genshin_path': r"F:\Genshin Impact\Genshin Impact Game\YuanShen.exe",
        'bettergi_path': r"F:\better\BetterGI.exe",
        'check_interval': 10,
        'timeout': 1800,  # 30分钟
        'close_after_completion': False,  # 测试时不自动关闭
        'click_positions': {
            'initial_start_button': (150, 200),
            'dragon_button_before': (250, 150),
            'blue_play_button': (350, 150)
        },
        'image_templates': {
            'initial_start_btn': 'templates/bettergi_initial_start_btn.png',
            'dragon_btn_before': 'templates/bettergi_dragon_btn_before.png',
            'blue_play_btn': 'templates/bettergi_blue_play_btn.png',
            'general_start_btn': 'templates/bettergi_start_btn.png',
            'general_dragon_btn': 'templates/bettergi_dragon_btn.png',
            'general_play_btn': 'templates/bettergi_play_btn.png',
            'automation_complete': 'templates/automation_complete.png'
        },
        'bettergi_workflow': {
            'steps': [
                {
                    'name': '点击初始启动按钮',
                    'templates': ['templates/bettergi_initial_start_btn.png', 'templates/bettergi_start_btn.png'],
                    'fallback_coords': [150, 200],
                    'delay_after': 3
                },
                {
                    'name': '点击一条龙按钮',
                    'templates': ['templates/bettergi_dragon_btn_before.png', 'templates/bettergi_dragon_btn.png'],
                    'fallback_coords': [250, 150],
                    'delay_after': 5
                },
                {
                    'name': '等待蓝色启动按钮出现',
                    'template': 'templates/bettergi_blue_play_btn.png',
                    'timeout': 10,
                    'delay_after': 2
                },
                {
                    'name': '点击蓝色启动按钮',
                    'templates': ['templates/bettergi_blue_play_btn.png', 'templates/bettergi_play_btn.png'],
                    'fallback_coords': [350, 150],
                    'delay_after': 2
                }
            ]
        }
    }
    
    adapter = ConfigurableGenshinBetterGIAdapter(config)
    
    print("\n🔄 开始执行自动化流程（跳过游戏启动）...")
    print("⚠️  请确保：")
    print("   - BetterGI已启动且窗口可见")
    print("   - 原神游戏已手动启动")
    print("   - 不要手动操作鼠标键盘")
    print("   - 按Enter键继续测试...")
    
    input()
    
    # 执行自动化流程，但不启动游戏
    try:
        print("步骤1: 切换到BetterGI窗口...")
        if adapter.bettergi_window:
            adapter.bettergi_window.activate()
        else:
            # 尝试重新查找窗口
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle("更好的原神")
            if windows:
                adapter.bettergi_window = windows[0]
                adapter.bettergi_window.activate()
            else:
                print("❌ 未找到BetterGI窗口，请确保它已启动")
                return False
        
        await asyncio.sleep(2)
        
        print("步骤2: 执行自动化操作...")
        success = await adapter.switch_to_framework_and_start()
        
        if success:
            print("✅ 自动化流程执行成功！")
            print("🎉 脚本已启动，观察是否按预期工作")
        else:
            print("❌ 自动化流程执行失败")
        
        return success
        
    except Exception as e:
        print(f"❌ 执行过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        print("启动快速测试...")
        success = asyncio.run(quick_test())
        if success:
            print("\n✅ 快速测试通过！")
        else:
            print("\n❌ 快速测试遇到问题")
        input("\n按回车键退出...")
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        input("按回车键退出...")
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")