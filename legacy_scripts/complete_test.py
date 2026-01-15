"""
完整测试脚本 - 验证所有功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from genshin_bettergi_adapter import ConfigurableGenshinBetterGIAdapter


async def complete_test():
    """完整测试函数"""
    print("🎮 完整测试 - 验证所有功能")
    print("=" * 50)
    
    print("\n📋 测试准备:")
    print("   1. 请确保BetterGI ('更好的原神') 已启动")
    print("   2. 请确保原神游戏已启动")
    print("   3. 请确保两个窗口都可见")
    print("   4. 按Enter键开始测试...")
    
    input()
    
    config = {
        'genshin_path': r"F:\Genshin Impact\Genshin Impact Game\YuanShen.exe",
        'bettergi_path': r"F:\better\BetterGI.exe",
        'check_interval': 10,
        'timeout': 1800,
        'close_after_completion': False,
        'click_positions': {
            'initial_start_button': (675, 485),  # 从测试结果获得的坐标
            'dragon_button_before': (733, 665),  # 从测试结果获得的坐标
            'blue_play_button': (280, 926)       # 从测试结果获得的坐标
        },
        'image_templates': {
            'initial_start_btn': 'templates/bettergi_initial_start_btn.png',
            'dragon_btn_before': 'templates/bettergi_dragon_btn_before.png',
            'blue_play_btn': 'templates/bettergi_blue_play_btn.png',
            'general_start_btn': 'templates/bettergi_start_btn.png',
            'general_dragon_btn': 'templates/bettergi_dragon_btn.png',
            'general_play_btn': 'templates/bettergi_play_btn.png'
        },
        'bettergi_workflow': {
            'steps': [
                {
                    'name': '点击初始启动按钮',
                    'templates': ['templates/bettergi_initial_start_btn.png', 'templates/bettergi_start_btn.png'],
                    'fallback_coords': [675, 485],
                    'delay_after': 3
                },
                {
                    'name': '点击一条龙按钮',
                    'templates': ['templates/bettergi_dragon_btn_before.png', 'templates/bettergi_dragon_btn.png'],
                    'fallback_coords': [733, 665],
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
                    'fallback_coords': [280, 926],
                    'delay_after': 2
                }
            ]
        }
    }
    
    print("\n🔧 创建适配器实例...")
    adapter = ConfigurableGenshinBetterGIAdapter(config)
    
    print("\n🚀 开始执行完整测试...")
    print("⚠️  请勿操作鼠标键盘")
    
    try:
        # 执行自动化流程的核心部分
        success = await adapter.switch_to_framework_and_start()
        
        if success:
            print(f"\n✅ 完整测试成功!")
            print(f"🎉 自动化流程已启动")
            print(f"👀 请观察原神游戏中是否开始自动化操作")
        else:
            print(f"\n❌ 完整测试失败")
        
        return success
        
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("🧪 开始完整功能验证测试...")
    
    success = await complete_test()
    
    print(f"\n🏁 完整测试结束")
    
    if success:
        print(f"\n✅ 所有功能测试通过!")
        print(f"🎉 您的自动化流程已准备就绪")
    else:
        print(f"\n❌ 测试未完全成功")
    
    print(f"\n💡 下一步:")
    print(f"   1. 运行完整自动化流程: python genshin_automation_starter.py")
    print(f"   2. 或使用快速启动: python quick_genshin_start.py")


if __name__ == "__main__":
    asyncio.run(main())