"""
最终测试脚本 - 用于执行完整的自动化流程
"""
import asyncio
import sys
from pathlib import Path
import time

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from genshin_bettergi_adapter import ConfigurableGenshinBetterGIAdapter


async def final_test():
    """最终测试函数"""
    print("🎮 最终测试 - 原神BetterGI自动化流程")
    print("=" * 50)
    
    print("\n📋 测试准备:")
    print("   1. 请确保BetterGI已启动 (窗口标题: '更好的原神')")
    print("   2. 请确保原神游戏已手动启动")
    print("   3. 请确保两个窗口都可见")
    print("   4. 测试期间请勿操作鼠标键盘")
    print("   5. 按Enter键开始测试...")
    
    input()
    
    config = {
        'genshin_path': r"F:\Genshin Impact\Genshin Impact Game\YuanShen.exe",
        'bettergi_path': r"F:\better\BetterGI.exe",
        'check_interval': 10,
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
    
    print("\n🔧 创建适配器实例...")
    adapter = ConfigurableGenshinBetterGIAdapter(config)
    
    print("\n🚀 开始执行自动化流程...")
    print("⚠️  测试正在进行中，请勿操作计算机")
    print("⏰ 预计执行时间: 1-5分钟")
    
    start_time = time.time()
    
    try:
        # 执行自动化流程的核心部分（不启动游戏和框架）
        success = await adapter.switch_to_framework_and_start()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n⏱️  执行时间: {duration:.2f} 秒")
        
        if success:
            print(f"\n✅ 自动化流程执行成功!")
            print(f"🎉 BetterGI自动化脚本已启动")
            print(f"👀 请观察原神游戏中是否开始自动化操作")
            
            print(f"\n📋 后续步骤:")
            print(f"   - 观察自动化脚本是否正常工作")
            print(f"   - 等待脚本完成或手动终止")
            print(f"   - 检查是否正确执行了预期任务")
            
        else:
            print(f"\n❌ 自动化流程执行失败")
            print(f"⚠️  请检查:")
            print(f"   - BetterGI界面状态是否正确")
            print(f"   - 图像模板是否准确")
            print(f"   - 窗口是否可见")
        
        return success
        
    except KeyboardInterrupt:
        print(f"\n\n🛑 用户中断测试")
        return False
    except Exception as e:
        print(f"\n\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("🧪 开始最终自动化流程测试...")
    
    success = await final_test()
    
    print(f"\n🏁 测试完成")
    
    if success:
        print(f"\n✅ 测试成功!")
        print(f"🎉 您的自动化流程配置已验证有效")
        print(f"💡 现在可以使用完整流程运行自动化任务")
    else:
        print(f"\n❌ 测试未成功")
        print(f"📝 请根据错误信息进行调试")
    
    print(f"\n📌 下一步建议:")
    print(f"   1. 如果测试成功，可以使用完整启动脚本:")
    print(f"      python genshin_automation_starter.py")
    print(f"   2. 如果需要调整，可修改模板或配置")
    

if __name__ == "__main__":
    asyncio.run(main())