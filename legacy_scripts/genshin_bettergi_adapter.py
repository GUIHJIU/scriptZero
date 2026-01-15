"""
原神与BetterGI自动化脚本框架适配器
处理启动游戏、启动脚本框架、执行自动化操作及结束判断的完整流程
"""
import asyncio
import subprocess
import sys
import time
import pyautogui
import pydirectinput
import pygetwindow as gw
import psutil
from pathlib import Path
from typing import Optional, Dict, Any
import cv2
import numpy as np


class GenshinBetterGIAdapter:
    """原神与BetterGI自动化脚本框架适配器"""
    
    def __init__(self, genshin_path: str, bettergi_path: str):
        """
        初始化适配器
        
        Args:
            genshin_path: 原神游戏路径
            bettergi_path: BetterGI脚本框架路径
        """
        self.genshin_path = Path(genshin_path)
        self.bettergi_path = Path(bettergi_path)
        self.genshin_process = None
        self.bettergi_process = None
        
        # 设置pyautogui参数
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
        # 用于存储游戏和脚本框架的窗口引用
        self.genshin_window = None
        self.bettergi_window = None
        
        # 图像模板路径 - 包含不同状态的按钮
        self.image_templates = {
            # BetterGI初始状态
            'bettergi_initial_start_btn': 'templates/bettergi_initial_start_btn.png',
            'bettergi_dragon_btn_before': 'templates/bettergi_dragon_btn_before.png',
            # BetterGI点击一条龙后状态
            'bettergi_blue_play_btn': 'templates/bettergi_blue_play_btn.png',
            'bettergi_dragon_btn_after': 'templates/bettergi_dragon_btn_after.png',
            # 通用模板（备用）
            'bettergi_start_btn': 'templates/bettergi_start_btn.png',
            'bettergi_dragon_btn': 'templates/bettergi_dragon_btn.png',
            'bettergi_play_btn': 'templates/bettergi_play_btn.png',
            # 游戏相关
            'genshin_login_screen': 'templates/genshin_login_screen.png',
            'genshin_main_menu': 'templates/genshin_main_menu.png',
            'automation_complete': 'templates/automation_complete.png'
        }
    
    async def find_multiple_templates(self, template_list: list, confidence: float = 0.8) -> Optional[tuple]:
        """
        尝试匹配多个模板，返回第一个匹配成功的
        
        Args:
            template_list: 模板路径列表
            confidence: 匹配置信度阈值
            
        Returns:
            匹配位置的中心坐标，如果未找到则返回None
        """
        for template_path in template_list:
            if not Path(template_path).exists():
                print(f"模板文件不存在: {template_path}")
                continue
            
            try:
                location = pyautogui.locateOnScreen(template_path, confidence=confidence)
                if location:
                    center = pyautogui.center(location)
                    print(f"成功匹配模板: {template_path} 位置: {center}")
                    return (center.x, center.y)
            except Exception as e:
                print(f"模板 {template_path} 识别失败: {e}")
        
        print(f"在 {len(template_list)} 个模板中未找到匹配项")
        return None
    
    async def wait_for_image(self, template_path: str, timeout: int = 30, confidence: float = 0.8) -> bool:
        """
        等待特定图像出现
        
        Args:
            template_path: 模板图像路径
            timeout: 超时时间（秒）
            confidence: 匹配置信度阈值
            
        Returns:
            是否找到图像
        """
        if not Path(template_path).exists():
            print(f"图像模板不存在: {template_path}")
            return False
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            position = await self.find_image_position(template_path, confidence)
            if position:
                print(f"找到图像: {template_path} 在位置 {position}")
                return True
            await asyncio.sleep(0.5)  # 短暂等待后重试
        
        print(f"在 {timeout} 秒内未找到图像: {template_path}")
        return False
    
    async def start_framework(self):
        """启动脚本框架"""
        print("启动BetterGI脚本框架...")
        
        if not self.bettergi_path.exists():
            raise FileNotFoundError(f"BetterGI路径不存在: {self.bettergi_path}")
        
        try:
            # 启动BetterGI脚本框架
            self.bettergi_process = subprocess.Popen([str(self.bettergi_path)])
            
            # 等待BetterGI窗口出现
            print("等待BetterGI窗口启动...")
            timeout = 30  # 30秒超时
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # 尝试找到BetterGI窗口，使用实际检测到的标题
                bettergi_windows = (
                    gw.getWindowsWithTitle("更好的原神") + 
                    gw.getWindowsWithTitle("BetterGI") + 
                    gw.getWindowsWithTitle("better") + 
                    gw.getWindowsWithTitle("Better")
                )
                
                if bettergi_windows:
                    self.bettergi_window = bettergi_windows[0]
                    print(f"BetterGI窗口已找到，标题: '{self.bettergi_window.title}'")
                    break
                await asyncio.sleep(1)
            
            if not self.bettergi_window:
                raise TimeoutError("未能在规定时间内找到BetterGI窗口")
            
            # 使用更可靠的窗口激活方法
            await self._safe_activate_window(self.bettergi_window)
            
            print("BetterGI脚本框架已启动")
            return True
            
        except Exception as e:
            print(f"启动BetterGI脚本框架失败: {e}")
            return False
    
    async def _safe_activate_window(self, window):
        """安全激活窗口的方法"""
        try:
            import win32gui
            import win32con
            
            # 尝试多种激活方法
            methods = [
                # 方法1: 使用pygetwindow
                lambda: window.activate(),
                # 方法2: 恢复并激活
                lambda: window.restore() or window.activate(),
                # 方法3: 使用win32 API（更底层的方法）
                lambda: win32gui.SetForegroundWindow(window._hWnd) or True,
                # 方法4: 显示窗口并置顶
                lambda: win32gui.ShowWindow(window._hWnd, win32con.SW_SHOW) or win32gui.SetForegroundWindow(window._hWnd) or True,
                # 方法5: 简单的bring to front
                lambda: window.bring_to_front() if hasattr(window, 'bring_to_front') else window.restore()
            ]
            
            for i, method in enumerate(methods):
                try:
                    method()
                    await asyncio.sleep(1)  # 给窗口时间响应
                    # 检查窗口是否确实处于活动状态
                    active_window = gw.getActiveWindow()
                    if active_window and active_window.title == window.title:
                        print(f"✓ 窗口激活成功 (方法 {i+1})")
                        return True
                except Exception as e:
                    print(f"⚠ 方法 {i+1} 失败: {e}")
                    continue
            
            print("⚠ 所有窗口激活方法都失败了，但将继续执行")
            return True  # 即使激活失败也继续，因为可能仍然可以进行图像识别
            
        except ImportError:
            # 如果没有win32扩展，回退到原来的方法
            print("⚠ 未安装pywin32，使用基础方法")
            try:
                # 尝试基础方法
                window.restore()
                window.bring_to_front()
                await asyncio.sleep(1)
                return True
            except:
                print("⚠ 基础激活方法也失败")
                return True
        except Exception as e:
            print(f"窗口激活出错: {e}")
            return False

    async def find_image_position(self, template_path: str, confidence: float = 0.8) -> Optional[tuple]:
        """
        查找图像在屏幕上的位置
        
        Args:
            template_path: 模板图像路径
            confidence: 匹配置信度阈值
            
        Returns:
            匹配位置的中心坐标，如果未找到则返回None
        """
        if not Path(template_path).exists():
            print(f"图像模板不存在: {template_path}")
            return None
        
        try:
            # 尝试使用pyautogui进行模板匹配
            location = pyautogui.locateOnScreen(template_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                return (center.x, center.y)
        except Exception as e:
            print(f"图像识别失败: {e}")
        
        return None
    
    async def click_image(self, template_path: str, confidence: float = 0.8, max_attempts: int = 3) -> bool:
        """
        点击图像所在位置 - 使用多种点击方法
        """
        for attempt in range(max_attempts):
            position = await self.find_image_position(template_path, confidence)
            if position:
                # 尝试多种点击方法
                click_methods = [
                    # 方法1: pyautogui.click
                    lambda x, y: pyautogui.click(x, y),
                    # 方法2: pydirectinput.click (绕过某些安全限制)
                    lambda x, y: pydirectinput.click(x, y),
                    # 方法3: pyautogui.moveTo + click
                    lambda x, y: pyautogui.moveTo(x, y) or pyautogui.click()
                ]
                
                for i, click_method in enumerate(click_methods):
                    try:
                        click_method(position[0], position[1])
                        print(f"已点击图像: {template_path} 在位置 {position} (尝试 {attempt + 1}/{max_attempts}, 方法 {i + 1})")
                        await asyncio.sleep(0.5)  # 等待点击响应
                        return True
                    except Exception as e:
                        print(f"点击方法 {i + 1} 失败: {e}")
                        continue
                
                # 如果所有点击方法都失败，继续尝试下一个匹配
                continue
            
            await asyncio.sleep(1)  # 等待后重试
        
        print(f"无法找到并点击图像: {template_path} (尝试 {max_attempts} 次后失败)")
        return False
    
    async def click_multiple_templates(self, template_list: list, confidence: float = 0.8, max_attempts: int = 3) -> bool:
        """
        尝试点击多个模板中的任意一个 - 使用多种点击方法
        """
        for attempt in range(max_attempts):
            position = await self.find_multiple_templates(template_list, confidence)
            if position:
                # 尝试多种点击方法
                click_methods = [
                    # 方法1: pyautogui.click
                    lambda x, y: pyautogui.click(x, y),
                    # 方法2: pydirectinput.click (更底层，可能绕过安全限制)
                    lambda x, y: pydirectinput.click(x, y),
                    # 方法3: pyautogui.moveTo + click
                    lambda x, y: pyautogui.moveTo(x, y) or pyautogui.click()
                ]
                
                for i, click_method in enumerate(click_methods):
                    try:
                        click_method(position[0], position[1])
                        print(f"已点击匹配的模板，位置: {position} (尝试 {attempt + 1}/{max_attempts}, 方法 {i + 1})")
                        await asyncio.sleep(0.5)  # 等待点击响应
                        return True
                    except Exception as e:
                        print(f"点击方法 {i + 1} 失败: {e}")
                        continue
            
            await asyncio.sleep(1)  # 等待后重试
        
        print(f"无法找到并点击任何模板 (尝试 {max_attempts} 次后失败)")
        print(f"尝试的模板: {template_list}")
        return False
    
    async def start_game(self):
        """启动原神游戏"""
        print("启动原神游戏...")
        
        if not self.genshin_path.exists():
            raise FileNotFoundError(f"原神路径不存在: {self.genshin_path}")
        
        try:
            # 启动原神游戏
            self.genshin_process = subprocess.Popen([str(self.genshin_path)])
            
            # 等待原神窗口出现
            print("等待原神窗口启动...")
            timeout = 60  # 60秒超时
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # 尝试找到原神窗口，可能有不同的标题
                genshin_windows = (
                    gw.getWindowsWithTitle("原神") + 
                    gw.getWindowsWithTitle("Genshin Impact") + 
                    gw.getWindowsWithTitle("YuanShen")
                )
                
                if genshin_windows:
                    self.genshin_window = genshin_windows[0]
                    print(f"原神窗口已找到，标题: '{self.genshin_window.title}'")
                    break
                await asyncio.sleep(1)
            
            if not self.genshin_window:
                raise TimeoutError("未能在规定时间内找到原神窗口")
            
            # 激活原神窗口
            self.genshin_window.activate()
            await asyncio.sleep(5)  # 给游戏更多时间加载
            
            print("原神游戏已启动")
            return True
            
        except Exception as e:
            print(f"启动原神游戏失败: {e}")
            return False
    
    async def switch_to_framework_and_start(self):
        """切换焦点到脚本框架，使用图像识别进行操作"""
        print("切换焦点到BetterGI脚本框架并启动自动化...")
        
        # 如果窗口未设置，尝试查找
        if not self.bettergi_window:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle("更好的原神")
            if windows:
                self.bettergi_window = windows[0]
                print(f"找到BetterGI窗口: '{self.bettergi_window.title}'")
            else:
                print("错误: 未找到BetterGI窗口")
                return False
        
        try:
            # 使用安全的窗口激活方法
            await self._safe_activate_window(self.bettergi_window)
            
            # 额外等待时间确保窗口完全就绪
            await asyncio.sleep(2)
            
            # 步骤1: 查找并点击一条龙按钮（优先使用图像识别）
            print("步骤1: 查找并点击一条龙按钮...")
            dragon_templates = [
                self.image_templates['bettergi_dragon_btn_before'],
                self.image_templates['bettergi_dragon_btn']  # 备用模板
            ]
            
            # 过滤存在的模板
            existing_templates = [tmpl for tmpl in dragon_templates if Path(tmpl).exists()]
            
            if existing_templates:
                if await self.click_multiple_templates(existing_templates, confidence=0.7):
                    print("✓ 成功点击一条龙按钮")
                    await asyncio.sleep(5)  # 等待界面变化
                else:
                    print("⚠ 未找到一条龙按钮，可能已点击或界面状态不同")
                    # 尝试查找蓝色启动按钮（可能一条龙按钮已经被点击）
                    await asyncio.sleep(2)
            else:
                print("⚠ 一条龙按钮模板不存在，跳过此步骤")
            
            # 步骤2: 查找并点击启动按钮（可能是蓝色启动按钮或通用播放按钮）
            print("步骤2: 查找并点击启动按钮...")
            play_templates = [
                self.image_templates['bettergi_blue_play_btn'],
                self.image_templates['bettergi_play_btn'],  # 备用模板
                self.image_templates['bettergi_start_btn']  # 更多备用模板
            ]
            
            # 过滤存在的模板
            existing_play_templates = [tmpl for tmpl in play_templates if Path(tmpl).exists()]
            
            if existing_play_templates:
                if await self.click_multiple_templates(existing_play_templates, confidence=0.7):
                    print("✓ 成功点击启动按钮")
                    await asyncio.sleep(2)
                else:
                    print("⚠ 未找到启动按钮，可能需要等待或界面状态不同")
                    # 最后的备用方案：尝试点击上次测试中发现的大概位置
                    print("尝试点击可能的启动按钮位置...")
                    # 使用pydirectinput进行更底层的点击
                    pydirectinput.click(280, 926)  # 从之前的测试中获得的坐标
                    await asyncio.sleep(2)
            else:
                print("⚠ 启动按钮模板不存在，使用备用坐标点击")
                pydirectinput.click(280, 926)
                await asyncio.sleep(2)
            
            print("自动化脚本已启动")
            return True
                
        except Exception as e:
            print(f"操作BetterGI脚本框架失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def wait_for_completion(self, check_interval: int = 30, timeout: int = 3600):
        """
        等待自动化操作完成，优先使用图像识别判断完成状态
        
        Args:
            check_interval: 检查间隔（秒）
            timeout: 超时时间（秒）
        """
        print(f"开始监控自动化操作，检查间隔: {check_interval}秒，超时: {timeout}秒")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 检查BetterGI进程是否仍在运行
            if self.bettergi_process and self.bettergi_process.poll() is not None:
                print("BetterGI进程已退出")
                return True
            
            # 检查原神进程是否仍在运行
            if self.genshin_process and self.genshin_process.poll() is not None:
                print("原神进程已退出")
                return True
            
            # 优先使用图像识别检查完成标志
            if await self.wait_for_image(self.image_templates['automation_complete'], timeout=1, confidence=0.8):
                print("检测到完成标志图像")
                return True
            
            # 等待下一次检查
            await asyncio.sleep(check_interval)
        
        print("等待超时")
        return False
    
    async def check_completion_indicators(self) -> bool:
        """
        检查完成标志 - 使用图像识别
        """
        # 检查是否存在完成标志图像
        return await self.wait_for_image(self.image_templates['automation_complete'], timeout=1, confidence=0.8)
    
    async def close_processes(self, close_game: bool = True, close_framework: bool = True):
        """
        关闭游戏和脚本框架进程
        
        Args:
            close_game: 是否关闭游戏
            close_framework: 是否关闭脚本框架
        """
        print("正在关闭进程...")
        
        # 关闭BetterGI框架
        if close_framework and self.bettergi_process:
            try:
                # 尝试优雅关闭
                self.bettergi_process.terminate()
                try:
                    self.bettergi_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # 如果优雅关闭失败，强制终止
                    self.bettergi_process.kill()
                    self.bettergi_process.wait()
                print("BetterGI进程已关闭")
            except Exception as e:
                print(f"关闭BetterGI进程时出错: {e}")
        
        # 关闭原神游戏
        if close_game and self.genshin_process:
            try:
                # 尝试通过psutil优雅关闭
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if 'YuanShen.exe' in proc.info['name'] or 'GenshinImpact.exe' in proc.info['name']:
                            proc.terminate()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # 等待进程关闭
                await asyncio.sleep(3)
                
                # 检查是否还有相关进程在运行
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if 'YuanShen.exe' in proc.info['name'] or 'GenshinImpact.exe' in proc.info['name']:
                            proc.kill()  # 强制终止
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                print("原神进程已关闭")
            except Exception as e:
                print(f"关闭原神进程时出错: {e}")
    
    async def run_automation(self, close_after_completion: bool = True):
        """
        执行完整的自动化流程
        
        Args:
            close_after_completion: 完成后是否关闭游戏和脚本框架
        """
        print("开始执行原神与BetterGI自动化流程...")
        
        try:
            # 1. 启动脚本框架
            if not await self.start_framework():
                print("启动脚本框架失败，退出")
                return False
            
            await asyncio.sleep(2)
            
            # 2. 启动游戏
            if not await self.start_game():
                print("启动游戏失败，退出")
                return False
            
            await asyncio.sleep(5)
            
            # 3. 切换焦点到脚本框架并启动自动化
            if not await self.switch_to_framework_and_start():
                print("启动自动化脚本失败，退出")
                return False
            
            # 4. 等待自动化操作完成
            print("等待自动化操作完成...")
            completion_result = await self.wait_for_completion()
            
            if completion_result:
                print("自动化操作已完成")
            else:
                print("自动化操作可能未正常完成")
            
            # 5. 检查关闭选项
            if close_after_completion:
                await self.close_processes()
                print("已关闭游戏和脚本框架")
            
            return completion_result
            
        except Exception as e:
            print(f"执行自动化流程时出错: {e}")
            # 在发生错误时也尝试关闭进程
            if close_after_completion:
                await self.close_processes()
            return False


# 配置驱动的适配器类
class ConfigurableGenshinBetterGIAdapter(GenshinBetterGIAdapter):
    """支持配置文件的原神与BetterGI适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        使用配置初始化适配器
        
        Args:
            config: 配置字典
        """
        genshin_path = config.get('genshin_path', '')
        bettergi_path = config.get('bettergi_path', '')
        
        super().__init__(genshin_path, bettergi_path)
        
        # 从配置中加载额外参数
        self.check_interval = config.get('check_interval', 30)
        self.timeout = config.get('timeout', 3600)
        self.close_after_completion = config.get('close_after_completion', True)
        
        # 更新图像模板配置
        template_config = config.get('image_templates', {})
        for key, value in template_config.items():
            if key in self.image_templates:
                self.image_templates[key] = value
        
        # 保持向后兼容：如果配置中提供了坐标，仍然支持坐标点击
        self.click_positions = config.get('click_positions', {})
        self.initial_start_button_pos = self.click_positions.get('initial_start_button', (150, 200))
        self.dragon_button_before_pos = self.click_positions.get('dragon_button_before', (250, 150))
        self.blue_play_button_pos = self.click_positions.get('blue_play_button', (350, 150))
    
    async def switch_to_framework_and_start(self):
        """使用多状态图像识别方法执行操作，坐标点击作为后备"""
        print("切换焦点到BetterGI脚本框架并启动自动化...")
        
        if not self.bettergi_window:
            print("错误: BetterGI窗口未找到")
            return False
        
        try:
            # 激活BetterGI窗口
            self.bettergi_window.activate()
            await asyncio.sleep(2)
            
            # 从配置中获取模板列表
            workflow_config = self.config.get('bettergi_workflow', {}).get('steps', [])
            
            # 步骤1: 点击初始启动按钮
            step1_config = next((s for s in workflow_config if s['name'] == "点击初始启动按钮"), None)
            if step1_config:
                templates = step1_config.get('templates', [self.image_templates['bettergi_initial_start_btn']])
                fallback_coords = step1_config.get('fallback_coords', (150, 200))
                delay_after = step1_config.get('delay_after', 3)
                
                print("步骤1: 查找并点击初始启动按钮...")
                if await self.click_multiple_templates(templates, confidence=0.7):
                    print("✓ 成功点击初始启动按钮")
                else:
                    print("⚠ 未找到初始启动按钮，使用备用坐标")
                    pyautogui.click(*fallback_coords)
                
                await asyncio.sleep(delay_after)
            
            # 步骤2: 点击一条龙按钮
            step2_config = next((s for s in workflow_config if s['name'] == "点击一条龙按钮"), None)
            if step2_config:
                templates = step2_config.get('templates', [self.image_templates['bettergi_dragon_btn_before']])
                fallback_coords = step2_config.get('fallback_coords', (250, 150))
                delay_after = step2_config.get('delay_after', 5)
                
                print("步骤2: 查找并点击一条龙按钮...")
                if await self.click_multiple_templates(templates, confidence=0.7):
                    print("✓ 成功点击一条龙按钮")
                else:
                    print("⚠ 未找到一条龙按钮，使用备用坐标")
                    pyautogui.click(*fallback_coords)
                
                await asyncio.sleep(delay_after)
            
            # 步骤3: 等待蓝色启动按钮出现
            step3_config = next((s for s in workflow_config if s['name'] == "等待蓝色启动按钮出现"), None)
            if step3_config:
                template = step3_config.get('template', self.image_templates['bettergi_blue_play_btn'])
                timeout = step3_config.get('timeout', 10)
                delay_after = step3_config.get('delay_after', 2)
                
                print("步骤3: 等待蓝色启动按钮出现...")
                if await self.wait_for_image(template, timeout=timeout, confidence=0.7):
                    print("✓ 蓝色启动按钮已出现")
                else:
                    print("⚠ 蓝色启动按钮未出现，继续下一步")
                
                await asyncio.sleep(delay_after)
            
            # 步骤4: 点击蓝色启动按钮
            step4_config = next((s for s in workflow_config if s['name'] == "点击蓝色启动按钮"), None)
            if step4_config:
                templates = step4_config.get('templates', [self.image_templates['bettergi_blue_play_btn']])
                fallback_coords = step4_config.get('fallback_coords', (350, 150))
                delay_after = step4_config.get('delay_after', 2)
                
                print("步骤4: 查找并点击蓝色启动按钮...")
                if await self.click_multiple_templates(templates, confidence=0.7):
                    print("✓ 成功点击蓝色启动按钮")
                else:
                    print("⚠ 未找到蓝色启动按钮，使用备用坐标")
                    pyautogui.click(*fallback_coords)
                
                await asyncio.sleep(delay_after)
            
            print("自动化脚本已启动")
            return True
                
        except Exception as e:
            print(f"操作BetterGI脚本框架失败: {e}")
            return False
    
    async def wait_for_completion(self):
        """使用配置参数等待完成"""
        return await super().wait_for_completion(
            check_interval=self.check_interval,
            timeout=self.timeout
        )
    
    async def run_automation(self):
        """使用配置参数运行自动化"""
        return await super().run_automation(close_after_completion=self.close_after_completion)


def create_adapter_from_config(config_path: str) -> ConfigurableGenshinBetterGIAdapter:
    """
    从配置文件创建适配器
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        ConfigurableGenshinBetterGIAdapter实例
    """
    import yaml
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return ConfigurableGenshinBetterGIAdapter(config)


async def main():
    """示例主函数"""
    # 示例配置
    config = {
        'genshin_path': r"F:\Genshin Impact\Genshin Impact Game\YuanShen.exe",
        'bettergi_path': r"F:\better\BetterGI.exe",
        'check_interval': 30,
        'timeout': 7200,  # 2小时
        'close_after_completion': True,
        'click_positions': {
            'initial_start_button': (150, 200),  # 实际使用时需要调整坐标
            'dragon_button_before': (250, 150),  # 实际使用时需要调整坐标
            'blue_play_button': (350, 150)       # 实际使用时需要调整坐标
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
    result = await adapter.run_automation()
    
    if result:
        print("自动化流程成功完成！")
    else:
        print("自动化流程执行失败！")


if __name__ == "__main__":
    asyncio.run(main())