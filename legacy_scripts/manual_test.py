"""
手动测试脚本 - 逐步执行自动化流程
"""
import asyncio
import pyautogui
import pygetwindow as gw
import time
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from genshin_bettergi_adapter import ConfigurableGenshinBetterGIAdapter


async def manual_test():
    """手动测试函数"""
    print("🎮 手动测试 - 逐步执行自动化流程")
    print("=" * 50)
    
    print("\n📋 准备工作:")
    print("   1. 确保BetterGI ('更好的原神') 已启动")
    print("   2. 确保原神游戏已启动")
    print("   3. 按Enter键继续...")
    input()
    
    # 创建适配器
    config = {
        'genshin_path': r"F:\Genshin Impact\Genshin Impact Game\YuanShen.exe",
        'bettergi_path': r"F:\better\BetterGI.exe",
        'check_interval': 10,
        'timeout': 1800,
        'close_after_completion': False,
        'image_templates': {
            'bettergi_initial_start_btn': 'templates/bettergi_initial_start_btn.png',
            'bettergi_dragon_btn_before': 'templates/bettergi_dragon_btn_before.png',
            'bettergi_blue_play_btn': 'templates/bettergi_blue_play_btn.png',
            'bettergi_start_btn': 'templates/bettergi_start_btn.png',
            'bettergi_dragon_btn': 'templates/bettergi_dragon_btn.png',
            'bettergi_play_btn': 'templates/bettergi_play_btn.png'
        }
    }
    
    adapter = ConfigurableGenshinBetterGIAdapter(config)
    
    # 手动查找BetterGI窗口
    bettergi_windows = gw.getWindowsWithTitle("更好的原神")
    if bettergi_windows:
        adapter.bettergi_window = bettergi_windows[0]
        print(f"✓ 找到BetterGI窗口: '{adapter.bettergi_window.title}'")
    else:
        print("❌ 未找到BetterGI窗口，请确保它已启动")
        return False
    
    print("\n🎯 开始逐步测试:")
    print("步骤1: 激活BetterGI窗口")
    try:
        adapter.bettergi_window.activate()
        print("✓ 窗口激活成功")
    except:
        print("⚠ 窗口激活失败，尝试其他方法")
        try:
            adapter.bettergi_window.restore()
            adapter.bettergi_window.bring_to_front()
            print("✓ 窗口已前置")
        except:
            print("⚠ 窗口操作失败")
    
    await asyncio.sleep(2)
    
    print("\n🔍 分析BetterGI当前界面状态...")
    
    # 检查当前界面状态，尝试识别各种按钮
    available_buttons = []
    
    # 检查所有可能的按钮
    button_checks = [
        ('启动按钮', ['templates/bettergi_initial_start_btn.png', 'templates/bettergi_start_btn.png']),
        ('一条龙按钮', ['templates/bettergi_dragon_btn_before.png', 'templates/bettergi_dragon_btn.png']),
        ('启动按钮（激活后）', ['templates/bettergi_blue_play_btn.png', 'templates/bettergi_play_btn.png'])
    ]
    
    for button_name, template_list in button_checks:
        for template in template_list:
            if Path(template).exists():
                try:
                    position = await adapter.find_image_position(template, confidence=0.7)
                    if position:
                        print(f"✓ 检测到{button_name}，位置: {position}")
                        available_buttons.append((button_name, position, template))
                        break
                except Exception as e:
                    continue
    
    if not available_buttons:
        print("⚠ 未检测到任何已知按钮，界面状态可能与模板不符")
        print("💡 请根据当前界面手动执行以下操作:")
        print("   1. 找到一条龙按钮并点击")
        print("   2. 等待蓝色启动按钮出现")
        print("   3. 点击蓝色启动按钮")
        print("   4. 按Enter键继续测试...")
        input()
    else:
        print(f"\n📋 检测到 {len(available_buttons)} 个按钮:")
        for btn_name, pos, tmpl in available_buttons:
            print(f"   - {btn_name}: {pos} ({tmpl})")
        
        print("\n🔄 尝试自动执行操作...")
        
        # 尝试执行相应的操作
        dragon_found = any('龙' in btn[0] for btn in available_buttons)
        play_found = any('启动' in btn[0] or '播放' in btn[0] for btn in available_buttons)
        
        if not dragon_found:
            print("步骤2: 尝试点击一条龙按钮...")
            # 由于当前模板可能不匹配，使用坐标点击作为后备
            print("⚠ 未找到一条龙按钮，使用通用模板尝试...")
            if Path('templates/bettergi_dragon_btn.png').exists():
                try:
                    position = await adapter.find_image_position('templates/bettergi_dragon_btn.png', confidence=0.6)
                    if position:
                        print(f"✓ 找到一条龙按钮，位置: {position}")
                        pyautogui.click(position[0], position[1])
                        print("✓ 已点击一条龙按钮")
                        await asyncio.sleep(5)  # 等待界面变化
                    else:
                        print("⚠ 仍未能找到一条龙按钮，使用坐标点击")
                        # 尝试常见的一条龙按钮位置
                        pyautogui.click(100, 300)  # 假设位置
                        await asyncio.sleep(5)
                except Exception as e:
                    print(f"⚠ 一条龙按钮识别失败: {e}")
                    pyautogui.click(100, 300)  # 坐标点击作为最终后备
                    await asyncio.sleep(5)
        
        if not play_found:
            print("步骤3: 尝试点击启动按钮...")
            # 尝试点击启动按钮
            if Path('templates/bettergi_play_btn.png').exists():
                try:
                    position = await adapter.find_image_position('templates/bettergi_play_btn.png', confidence=0.6)
                    if position:
                        print(f"✓ 找到启动按钮，位置: {position}")
                        pyautogui.click(position[0], position[1])
                        print("✓ 已点击启动按钮")
                        await asyncio.sleep(2)
                    else:
                        print("⚠ 未找到启动按钮，使用坐标点击")
                        # 尝试常见的启动按钮位置
                        pyautogui.click(104, 630)  # 从之前的测试中得知大致位置
                        await asyncio.sleep(2)
                except Exception as e:
                    print(f"⚠ 启动按钮识别失败: {e}")
                    pyautogui.click(104, 630)  # 坐标点击作为最终后备
                    await asyncio.sleep(2)
    
    print("\n✅ 手动测试完成!")
    print("🎉 自动化流程已启动，请观察是否按预期工作")
    print("\n💡 提示: 如果自动化正常启动，请观察原神游戏中的变化")
    
    return True


if __name__ == "__main__":
    print("启动手动测试...")
    success = asyncio.run(manual_test())
    if success:
        print("\n✅ 测试完成！")
    else:
        print("\n❌ 测试失败！")
    input("\n按Enter键退出...")