"""
图像识别功能演示脚本
展示如何使用图像识别功能进行自动化操作
"""
import asyncio
import pyautogui
import time
from pathlib import Path


async def demo_image_recognition():
    """演示图像识别功能"""
    print("🎮 图像识别功能演示")
    print("=" * 40)
    
    # 演示图像识别的基本用法
    print("\n1. 图像识别基本原理:")
    print("   - 从templates目录加载模板图片")
    print("   - 在屏幕上寻找相似区域")
    print("   - 返回匹配位置并执行操作")
    
    print("\n2. 检查模板目录:")
    templates_dir = Path("templates")
    if templates_dir.exists():
        template_files = list(templates_dir.glob("*.png"))
        if template_files:
            print(f"   ✓ 发现 {len(template_files)} 个模板文件:")
            for file in template_files[:5]:  # 只显示前5个
                print(f"     - {file.name}")
            if len(template_files) > 5:
                print(f"     ... 还有 {len(template_files) - 5} 个文件")
        else:
            print("   ⚠ templates目录为空，请先使用图像模板生成工具创建模板")
    else:
        print("   ⚠ templates目录不存在，请先创建该目录")
        templates_dir.mkdir(exist_ok=True)
        print(f"   ✓ 已创建 {templates_dir} 目录")
    
    print("\n3. 图像识别参数说明:")
    print("   - 置信度(confidence): 匹配相似度阈值(0.0-1.0)")
    print("   - 推荐值: 0.7-0.9，过高可能找不到，过低可能误匹配")
    print("   - 超时时间: 等待图像出现的最大时间")
    
    print("\n4. 实际操作演示:")
    print("   为了演示目的，我们将展示如何编写图像识别代码:")
    
    demo_code = '''
# 示例：查找并点击启动按钮
def find_and_click_button(template_path, confidence=0.8):
    try:
        # 查找图像位置
        location = pyautogui.locateOnScreen(template_path, confidence=confidence)
        if location:
            # 获取中心点
            center = pyautogui.center(location)
            # 点击中心点
            pyautogui.click(center.x, center.y)
            print(f"成功点击按钮: {template_path}")
            return True
        else:
            print(f"未找到按钮: {template_path}")
            return False
    except Exception as e:
        print(f"图像识别失败: {e}")
        return False

# 示例：等待特定图像出现
def wait_for_image(template_path, timeout=30, confidence=0.8):
    import time
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            location = pyautogui.locateOnScreen(template_path, confidence=confidence)
            if location:
                print(f"找到图像: {template_path}")
                return True
        except:
            pass
        time.sleep(0.5)
    print(f"超时未找到图像: {template_path}")
    return False
'''
    
    print(demo_code)
    
    print("\n5. 最佳实践建议:")
    print("   ✓ 使用高质量、清晰的模板图片")
    print("   ✓ 在游戏相同分辨率下制作模板")
    print("   ✓ 优先使用图像识别，坐标点击作为备选")
    print("   ✓ 设置合适的置信度值")
    print("   ✓ 实现重试机制以防识别失败")
    print("   ✓ 记录识别日志便于调试")
    
    print("\n6. 运行图像模板生成工具:")
    print("   python image_template_generator.py")
    print("   按提示创建所需的图像模板")
    
    print("\n✅ 演示完成！图像识别功能已介绍完毕。")


async def main():
    """主函数"""
    await demo_image_recognition()


if __name__ == "__main__":
    asyncio.run(main())