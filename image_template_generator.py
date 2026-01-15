"""
图像模板生成工具
帮助用户创建用于图像识别的模板图片
"""
import pyautogui
import cv2
import numpy as np
from PIL import Image
import time
import os
from pathlib import Path


class ImageTemplateGenerator:
    """图像模板生成器"""
    
    def __init__(self, templates_dir="templates"):
        """
        初始化模板生成器
        
        Args:
            templates_dir: 模板存储目录
        """
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        
        # 设置pyautogui参数
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
    
    def capture_screen_region(self, region=None, filename=None):
        """
        捕获屏幕指定区域
        
        Args:
            region: 截图区域 (x, y, width, height)，如果为None则全屏截图
            filename: 保存的文件名
            
        Returns:
            截图的PIL图像对象
        """
        print("准备截图，请确保目标窗口可见...")
        time.sleep(3)  # 给用户时间准备
        
        if region:
            screenshot = pyautogui.screenshot(region=region)
            print(f"已截取区域 {region}")
        else:
            screenshot = pyautogui.screenshot()
            print("已截取全屏")
        
        if filename:
            filepath = self.templates_dir / filename
            screenshot.save(filepath)
            print(f"截图已保存至: {filepath}")
        
        return screenshot
    
    def select_region_interactive(self):
        """
        交互式选择截图区域
        
        Returns:
            截图区域 (x, y, width, height)
        """
        print("即将开始区域选择，请将鼠标移动到要截图的区域左上角...")
        time.sleep(2)
        
        # 获取左上角坐标
        x1, y1 = pyautogui.position()
        print(f"左上角坐标: ({x1}, {y1})")
        
        print("请将鼠标移动到要截图的区域右下角...")
        time.sleep(2)
        
        # 获取右下角坐标
        x2, y2 = pyautogui.position()
        print(f"右下角坐标: ({x2}, {y2})")
        
        # 计算区域
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        region = (x, y, width, height)
        print(f"选择的区域: {region}")
        
        return region
    
    def crop_image(self, image, region):
        """
        裁剪图像
        
        Args:
            image: PIL图像对象
            region: 裁剪区域 (x, y, width, height)
            
        Returns:
            裁剪后的PIL图像对象
        """
        x, y, width, height = region
        cropped = image.crop((x, y, x + width, y + height))
        return cropped
    
    def preprocess_template(self, image, resize_factor=1.0, enhance_contrast=False):
        """
        预处理模板图像
        
        Args:
            image: PIL图像对象
            resize_factor: 缩放因子
            enhance_contrast: 是否增强对比度
            
        Returns:
            预处理后的PIL图像对象
        """
        # 转换为OpenCV格式进行处理
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 缩放
        if resize_factor != 1.0:
            height, width = img_cv.shape[:2]
            new_width = int(width * resize_factor)
            new_height = int(height * resize_factor)
            img_cv = cv2.resize(img_cv, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # 增强对比度
        if enhance_contrast:
            lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            lab = cv2.merge([l, a, b])
            img_cv = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # 转换回PIL格式
        processed_image = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
        return processed_image
    
    def create_template_from_screenshot(self, name, region=None, preprocess=True):
        """
        从屏幕截图创建模板
        
        Args:
            name: 模板名称（将用于文件名）
            region: 截图区域，如果为None则交互式选择
            preprocess: 是否预处理图像
            
        Returns:
            模板文件路径
        """
        if region is None:
            print("请选择要截图的区域...")
            region = self.select_region_interactive()
        
        # 截图
        screenshot = self.capture_screen_region(region=region)
        
        # 预处理
        if preprocess:
            screenshot = self.preprocess_template(screenshot, resize_factor=1.0, enhance_contrast=False)
        
        # 保存模板
        filename = f"{name}.png"
        filepath = self.templates_dir / filename
        screenshot.save(filepath)
        
        print(f"模板已创建: {filepath}")
        return str(filepath)
    
    def batch_create_templates(self, template_configs):
        """
        批量创建模板
        
        Args:
            template_configs: 模板配置列表，每个配置包含name和region
        
        Returns:
            创建成功的模板路径列表
        """
        created_templates = []
        
        for config in template_configs:
            name = config['name']
            region = config.get('region')  # 如果没有指定region，则交互式选择
            preprocess = config.get('preprocess', True)
            
            print(f"\n创建模板: {name}")
            try:
                filepath = self.create_template_from_screenshot(name, region, preprocess)
                created_templates.append(filepath)
            except Exception as e:
                print(f"创建模板 {name} 失败: {e}")
        
        return created_templates


def main():
    """主函数 - 交互式模板创建工具"""
    generator = ImageTemplateGenerator()
    
    print("🎮 图像模板生成工具")
    print("=" * 40)
    print("此工具可以帮助您创建用于图像识别的模板图片")
    print()
    
    while True:
        print("请选择操作:")
        print("1. 创建单个模板（交互式选择区域）")
        print("2. 创建单个模板（指定坐标）")
        print("3. 批量创建常用模板（BetterGI相关）")
        print("4. 退出")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == '1':
            name = input("请输入模板名称（不含扩展名）: ").strip()
            if name:
                generator.create_template_from_screenshot(name)
        
        elif choice == '2':
            name = input("请输入模板名称: ").strip()
            if name:
                try:
                    x = int(input("请输入X坐标: "))
                    y = int(input("请输入Y坐标: "))
                    width = int(input("请输入宽度: "))
                    height = int(input("请输入高度: "))
                    region = (x, y, width, height)
                    
                    generator.create_template_from_screenshot(name, region)
                except ValueError:
                    print("输入的坐标不是有效数字！")
        
        elif choice == '3':
            print("\n正在批量创建BetterGI相关模板...")
            # 预定义的BetterGI相关模板配置
            configs = [
                {"name": "bettergi_start_btn", "desc": "BetterGI启动按钮"},
                {"name": "bettergi_dragon_btn", "desc": "一条龙按钮"},
                {"name": "bettergi_play_btn", "desc": "三角形播放按钮"},
                {"name": "automation_complete", "desc": "自动化完成标志"},
            ]
            
            print("\n请按以下顺序准备界面，并在提示时按回车:")
            for config in configs:
                input(f"\n请准备 {config['desc']} 界面，然后按回车开始截图...")
                print(f"正在创建 {config['name']} 模板...")
                
                # 交互式创建模板
                generator.create_template_from_screenshot(config['name'])
        
        elif choice == '4':
            print("\n感谢使用图像模板生成工具！")
            break
        
        else:
            print("无效选择，请重新输入！")
        
        print()


if __name__ == "__main__":
    main()