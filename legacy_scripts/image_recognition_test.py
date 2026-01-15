"""
图像识别测试脚本
专门用于测试图像识别和点击功能
"""
import asyncio
import pyautogui
import pydirectinput
import pygetwindow as gw
import time
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from genshin_bettergi_adapter import ConfigurableGenshinBetterGIAdapter


async def image_recognition_test():
    """图像识别测试"""
    print("🔍 图像识别功能测试")
    print("=" * 50)
    
    print("\n📋 检查模板文件...")
    # 使用绝对路径确保能找到templates目录
    templates_dir = project_root / "templates"
    print(f"模板目录路径: {templates_dir}")
    
    if not templates_dir.exists():
        print(f"❌ templates目录不存在: {templates_dir}")
        return False
    
    template_files = list(templates_dir.glob("*.png"))
    
    if not template_files:
        print("❌ templates目录中没有找到任何模板文件")
        print("💡 请先使用 image_template_generator.py 创建模板")
        return False
    
    print(f"✅ 发现 {len(template_files)} 个模板文件:")
    for file in template_files:
        print(f"   - {file.name}")
    
    print("\n🎯 开始图像识别测试...")
    print("请确保BetterGI ('更好的原神') 窗口可见")
    print("按Enter键继续...")
    input()
    
    # 查找BetterGI窗口
    windows = gw.getWindowsWithTitle("更好的原神")
    if not windows:
        print("❌ 未找到BetterGI窗口")
        return False
    
    bettergi_window = windows[0]
    print(f"✓ 找到BetterGI窗口: '{bettergi_window.title}'")
    
    try:
        # 激活窗口
        bettergi_window.activate()
    except:
        try:
            bettergi_window.restore()
            bettergi_window.bring_to_front()
        except:
            pass
    
    await asyncio.sleep(2)
    
    # 创建适配器实例
    config = {
        'image_templates': {
            'bettergi_dragon_btn_before': str(templates_dir / 'bettergi_dragon_btn_before.png'),
            'bettergi_dragon_btn': str(templates_dir / 'bettergi_dragon_btn.png'),
            'bettergi_blue_play_btn': str(templates_dir / 'bettergi_blue_play_btn.png'),
            'bettergi_play_btn': str(templates_dir / 'bettergi_play_btn.png'),
            'bettergi_start_btn': str(templates_dir / 'bettergi_start_btn.png'),
            'bettergi_initial_start_btn': str(templates_dir / 'bettergi_initial_start_btn.png')
        }
    }
    
    adapter = ConfigurableGenshinBetterGIAdapter(config)
    
    print("\n🔍 开始图像识别和点击测试...")
    
    # 测试所有模板
    button_types = [
        ("一条龙按钮", [
            str(templates_dir / 'bettergi_dragon_btn_before.png'),
            str(templates_dir / 'bettergi_dragon_btn.png')
        ]),
        ("启动按钮", [
            str(templates_dir / 'bettergi_blue_play_btn.png'),
            str(templates_dir / 'bettergi_play_btn.png'),
            str(templates_dir / 'bettergi_start_btn.png'),
            str(templates_dir / 'bettergi_initial_start_btn.png')
        ])
    ]
    
    found_elements = []
    
    for button_name, template_list in button_types:
        print(f"\n测试{button_name}识别:")
        
        for template_path in template_list:
            if not Path(template_path).exists():
                print(f"  ⏭️  模板不存在: {Path(template_path).name}")
                continue
            
            print(f"  尝试识别: {Path(template_path).name}")
            
            try:
                # 使用pyautogui进行图像识别
                location = pyautogui.locateOnScreen(template_path, confidence=0.7)
                
                if location:
                    center = pyautogui.center(location)
                    print(f"  ✓ 找到{button_name}! 位置: {center}")
                    
                    # 尝试点击（使用pydirectinput绕过安全限制）
                    print(f"    尝试点击位置: {center}")
                    pydirectinput.click(center.x, center.y)
                    print(f"    ✓ 点击成功!")
                    
                    found_elements.append((button_name, center, Path(template_path).name))
                    await asyncio.sleep(2)  # 等待界面响应
                    
                    break  # 找到一个就继续下一个按钮类型
                else:
                    print(f"  ⚠ 未找到{button_name} ({Path(template_path).name})")
            except Exception as e:
                print(f"  ❌ 识别失败: {e}")
    
    print(f"\n📊 识别结果:")
    for name, pos, tmpl in found_elements:
        print(f"  - {name}: {pos} ({tmpl})")
    
    if found_elements:
        print(f"\n✅ 图像识别测试部分成功!")
        print(f"🎉 成功识别并点击了 {len(found_elements)} 个元素")
        print(f"💡 请观察BetterGI界面是否响应了点击操作")
        return True
    else:
        print(f"\n❌ 未识别到任何元素")
        print(f"⚠️  可能的原因:")
        print(f"   - 模板与当前界面不匹配")
        print(f"   - 置信度过高")
        print(f"   - BetterGI界面状态不同")
        return False


async def main():
    """主函数"""
    print("🎮 图像识别专项测试")
    print("=" * 60)
    print("此测试将专门验证图像识别和点击功能")
    print("")
    print("请确保:")
    print("  1. BetterGI ('更好的原神') 已启动")
    print("  2. 窗口可见")
    print("  3. 不要操作鼠标键盘")
    
    success = await image_recognition_test()
    
    if success:
        print(f"\n🎉 图像识别测试成功!")
        print(f"✅ 识别并点击功能正常工作")
    else:
        print(f"\n⚠️  图像识别测试遇到问题")
        print(f"💡 请检查模板文件或界面状态")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print(f"\n✅ 测试成功!")
    else:
        print(f"\n❌ 测试未通过")
    input(f"\n按Enter退出...")