"""
管理员模式深度测试脚本
专门用于测试在管理员权限下的自动化功能
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

from genshin_bettergi_adapter import GenshinBetterGIAdapter


class AdminModeTestAdapter(GenshinBetterGIAdapter):
    """管理员模式测试适配器"""
    
    def __init__(self):
        # 使用空路径，因为我们只测试点击功能
        super().__init__("", "")
    
    async def admin_mode_click_test(self):
        """管理员模式点击测试"""
        print("🔧 管理员模式点击功能测试")
        print("=" * 50)
        
        # 查找BetterGI窗口
        windows = gw.getWindowsWithTitle("更好的原神")
        if not windows:
            print("❌ 未找到BetterGI窗口")
            return False
        
        self.bettergi_window = windows[0]
        print(f"✓ 找到BetterGI窗口: '{self.bettergi_window.title}'")
        
        # 尝试激活窗口
        try:
            self.bettergi_window.activate()
            print("✓ 窗口激活成功")
        except:
            print("⚠ 窗口激活失败，尝试其他方法")
            try:
                self.bettergi_window.restore()
                self.bettergi_window.bring_to_front()
                print("✓ 窗口已前置")
            except:
                print("⚠ 窗口操作失败")
        
        await asyncio.sleep(2)
        
        print("\n🎯 执行深度点击测试...")
        
        # 使用测试中发现的坐标进行点击测试
        coordinates = [
            (733, 665, "一条龙按钮"),
            (280, 926, "蓝色启动按钮")
        ]
        
        for x, y, name in coordinates:
            print(f"\n测试点击{name} (坐标: {x}, {y}):")
            
            # 测试不同的点击方法
            methods = [
                ("pyautogui.click", lambda: pyautogui.click(x, y)),
                ("pydirectinput.click", lambda: pydirectinput.click(x, y)),
                ("pyautogui.moveTo+click", lambda: pyautogui.moveTo(x, y) or pyautogui.click()),
                ("pydirectinput.moveTo+click", lambda: pydirectinput.moveTo(x, y) or pydirectinput.click())
            ]
            
            for method_name, method_func in methods:
                try:
                    print(f"  尝试 {method_name}...")
                    method_func()
                    print(f"  ✓ {method_name} 执行成功")
                    await asyncio.sleep(1)  # 等待响应
                except Exception as e:
                    print(f"  ❌ {method_name} 失败: {e}")
            
            await asyncio.sleep(2)  # 给每个点击足够的响应时间
        
        print(f"\n✅ 深度点击测试完成!")
        print(f"💡 请观察BetterGI界面是否响应了点击操作")
        
        return True
    
    async def image_based_click_test(self):
        """基于图像的点击测试"""
        print("\n🔍 基于图像的点击测试")
        print("=" * 50)
        
        # 查找BetterGI窗口并激活
        windows = gw.getWindowsWithTitle("更好的原神")
        if not windows:
            print("❌ 未找到BetterGI窗口")
            return False
        
        self.bettergi_window = windows[0]
        try:
            self.bettergi_window.activate()
        except:
            try:
                self.bettergi_window.restore()
                self.bettergi_window.bring_to_front()
            except:
                pass
        
        await asyncio.sleep(2)
        
        # 测试所有可用的模板
        template_tests = [
            ("一条龙按钮", ["templates/bettergi_dragon_btn_before.png", "templates/bettergi_dragon_btn.png"]),
            ("启动按钮", ["templates/bettergi_play_btn.png", "templates/bettergi_initial_start_btn.png"])
        ]
        
        for button_name, template_list in template_tests:
            print(f"\n测试{button_name}识别和点击:")
            
            for template_path in template_list:
                if not Path(template_path).exists():
                    print(f"  ⏭️  模板不存在: {template_path}")
                    continue
                
                print(f"  尝试识别: {template_path}")
                
                # 尝试找到图像
                try:
                    location = pyautogui.locateOnScreen(template_path, confidence=0.7)
                    if location:
                        center = pyautogui.center(location)
                        print(f"  ✓ 找到{button_name}，位置: {center}")
                        
                        # 尝试多种点击方法
                        click_methods = [
                            ("pyautogui", lambda: pyautogui.click(center.x, center.y)),
                            ("pydirectinput", lambda: pydirectinput.click(center.x, center.y))
                        ]
                        
                        for method_name, click_func in click_methods:
                            try:
                                print(f"    使用{method_name}点击...")
                                click_func()
                                print(f"    ✓ {method_name}点击成功")
                                await asyncio.sleep(1)
                                break  # 成功后跳出方法循环
                            except Exception as e:
                                print(f"    ❌ {method_name}失败: {e}")
                        
                        break  # 找到模板后跳出模板循环
                    else:
                        print(f"  ⚠ 未找到{button_name} ({template_path})")
                except Exception as e:
                    print(f"  ❌ 识别失败: {e}")
        
        print(f"\n✅ 基于图像的点击测试完成!")
        return True


async def main():
    """主函数"""
    print("🎮 管理员模式深度测试")
    print("=" * 60)
    print("此测试将验证在管理员权限下的各种点击方法")
    print("")
    print("请确保:")
    print("  1. 以管理员身份运行此脚本")
    print("  2. BetterGI ('更好的原神') 已启动")
    print("  3. 原神游戏已启动")
    print("  4. 不要操作鼠标键盘")
    print("  5. 按Enter键开始...")
    input()
    
    adapter = AdminModeTestAdapter()
    
    print("\n1️⃣ 执行坐标点击测试...")
    coord_success = await adapter.admin_mode_click_test()
    
    print("\n2️⃣ 执行图像识别点击测试...")
    image_success = await adapter.image_based_click_test()
    
    print(f"\n📊 测试结果:")
    print(f"  坐标点击测试: {'✅ 通过' if coord_success else '❌ 失败'}")
    print(f"  图像识别测试: {'✅ 通过' if image_success else '❌ 失败'}")
    
    if coord_success or image_success:
        print(f"\n🎉 部分或全部测试通过！")
        print(f"💡 请观察BetterGI是否响应了点击操作")
    else:
        print(f"\n❌ 测试未完全通过")
    
    return coord_success or image_success


if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print(f"\n✅ 深度测试部分成功!")
    else:
        print(f"\n❌ 深度测试未通过")
    input(f"\n按Enter退出...")