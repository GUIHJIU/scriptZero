"""
原神BetterGI自动化全流程测试运行器
用于执行完整的自动化流程测试
"""
import asyncio
import sys
from pathlib import Path
import time

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from genshin_bettergi_adapter import ConfigurableGenshinBetterGIAdapter


async def run_full_test():
    """运行全流程测试"""
    print("🎮 原神BetterGI自动化全流程测试")
    print("=" * 60)
    
    print("\n📋 测试前检查:")
    print("   1. 请确保BetterGI脚本框架已启动")
    print("   2. 请确保原神游戏已启动")
    print("   3. 请确保两个窗口都可见")
    print("   4. 准备好后按Enter继续...")
    
    input()  # 等待用户确认
    
    print("\n🔧 配置测试参数...")
    config = {
        'genshin_path': r"F:\Genshin Impact\Genshin Impact Game\YuanShen.exe",
        'bettergi_path': r"F:\better\BetterGI.exe",
        'check_interval': 10,  # 增加检查频率
        'timeout': 1800,       # 30分钟超时
        'close_after_completion': False,  # 测试期间不自动关闭
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
    
    print("\n🚀 创建适配器实例...")
    adapter = ConfigurableGenshinBetterGIAdapter(config)
    
    print("\n🎯 开始执行自动化流程测试...")
    print("⚠️  注意：测试过程中请勿手动操作鼠标和键盘")
    print("⚠️  如需中断，请使用 Ctrl+C")
    
    try:
        start_time = time.time()
        print(f"\n⏰ 测试开始时间: {time.strftime('%H:%M:%S')}")
        
        # 执行自动化流程（不关闭游戏和框架）
        success = await adapter.run_automation(close_after_completion=False)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n⏱️  测试执行时间: {duration:.2f} 秒 ({duration/60:.2f} 分钟)")
        
        if success:
            print(f"\n✅ 全流程测试成功!")
            print(f"🎉 自动化脚本已成功启动并运行")
        else:
            print(f"\n❌ 全流程测试遇到问题")
            print(f"⚠️  请检查日志信息以了解具体问题")
        
        return success
        
    except KeyboardInterrupt:
        print(f"\n\n🛑 用户中断测试")
        print(f"⚠️  请注意：游戏和脚本框架可能仍在运行")
        return False
    except Exception as e:
        print(f"\n\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("🧪 开始原神BetterGI自动化全流程测试...")
    
    success = await run_full_test()
    
    print(f"\n🏁 全流程测试结束")
    
    if success:
        print(f"\n✅ 测试成功完成!")
        print(f"💡 您的模板配置和自动化流程已验证有效")
    else:
        print(f"\n❌ 测试未完全成功")
        print(f"📝 请参考输出信息进行调试")
    
    print(f"\n📌 测试后操作提示:")
    print(f"   - 检查BetterGI和原神是否正常运行")
    print(f"   - 观察自动化脚本是否按预期执行")
    print(f"   - 如需正式运行，请使用: python genshin_automation_starter.py")


if __name__ == "__main__":
    asyncio.run(main())