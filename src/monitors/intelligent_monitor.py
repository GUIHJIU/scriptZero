"""
多维度智能监控器
实现进程、图像、窗口、性能等多维度监控
"""
import asyncio
import time
import cv2
import numpy as np
import psutil
import pygetwindow as gw
import pyautogui
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import threading


class ProcessMonitor:
    """进程监控器"""
    
    async def check(self, config: Dict[str, Any]) -> bool:
        """检查进程状态"""
        pid = config.get('pid')
        name = config.get('name')
        expected_status = config.get('expected_status', 'running')  # running, stopped, suspended
        
        if pid:
            try:
                process = psutil.Process(pid)
                if expected_status == 'running':
                    return process.is_running() and process.status() != psutil.STATUS_STOPPED
                elif expected_status == 'stopped':
                    return not process.is_running() or process.status() == psutil.STATUS_STOPPED
                elif expected_status == 'suspended':
                    return process.status() == psutil.STATUS_STOPPED
                else:
                    return process.is_running()
            except psutil.NoSuchProcess:
                return expected_status == 'stopped'
        elif name:
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                if proc.info['name'] == name:
                    if expected_status == 'running':
                        return proc.info['status'] != psutil.STATUS_STOPPED
                    elif expected_status == 'stopped':
                        return proc.info['status'] == psutil.STATUS_STOPPED
                    elif expected_status == 'suspended':
                        return proc.info['status'] == psutil.STATUS_STOPPED
                    else:
                        return True
            return expected_status == 'stopped'
        return False


class WindowMonitor:
    """窗口监控器"""
    
    async def check(self, config: Dict[str, Any]) -> bool:
        """检查窗口状态"""
        title = config.get('title')
        expected_state = config.get('expected_state', 'exists')  # exists, not_exists, active, inactive
        
        if title:
            try:
                windows = gw.getWindowsWithTitle(title)
                
                if expected_state == 'exists':
                    return len(windows) > 0
                elif expected_state == 'not_exists':
                    return len(windows) == 0
                elif expected_state == 'active':
                    active_window = gw.getActiveWindow()
                    return any(w == active_window for w in windows if w is not None)
                elif expected_state == 'inactive':
                    active_window = gw.getActiveWindow()
                    return not any(w == active_window for w in windows if w is not None)
                else:
                    return len(windows) > 0
            except Exception:
                return False
        return False


class ImageMonitor:
    """图像监控器"""
    
    def __init__(self):
        self.template_cache = {}  # 缓存模板图像以提高性能
    
    async def check(self, config: Dict[str, Any]) -> bool:
        """检查图像匹配"""
        template_path = config.get('template')
        threshold = config.get('threshold', 0.8)
        region = config.get('region')  # (left, top, width, height)
        grayscale = config.get('grayscale', True)
        
        if not template_path or not Path(template_path).exists():
            return False
        
        try:
            # 检查缓存
            if template_path in self.template_cache:
                template = self.template_cache[template_path]
            else:
                # 读取模板图像并缓存
                template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR)
                if template is None:
                    return False
                self.template_cache[template_path] = template
            
            # 截取屏幕
            screenshot = pyautogui.screenshot()
            screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            if grayscale:
                screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
                search_template = template
            else:
                search_template = template
            
            if region:
                # 只在指定区域内搜索
                left, top, width, height = region
                screen = screen[top:top+height, left:left+width]
            
            # 模板匹配
            result = cv2.matchTemplate(screen, search_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            return max_val >= threshold
        except Exception as e:
            print(f"Image monitoring error: {e}")
            return False
    
    def clear_cache(self):
        """清空模板缓存"""
        self.template_cache.clear()


class PerformanceMonitor:
    """性能监控器"""
    
    async def check(self, config: Dict[str, Any]) -> bool:
        """检查系统性能"""
        cpu_threshold = config.get('cpu_max')
        memory_threshold = config.get('memory_max')
        disk_threshold = config.get('disk_max')
        network_threshold = config.get('network_threshold')  # Mbps
        
        checks_passed = True
        
        if cpu_threshold is not None:
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > cpu_threshold:
                checks_passed = False
        
        if memory_threshold is not None:
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > memory_threshold:
                checks_passed = False
        
        if disk_threshold is not None:
            disk_usage = psutil.disk_usage('/').percent
            if disk_usage > disk_threshold:
                checks_passed = False
        
        return checks_passed


class NetworkMonitor:
    """网络监控器"""
    
    def __init__(self):
        self.last_bytes_sent = 0
        self.last_bytes_recv = 0
        self.last_time = time.time()
    
    async def check(self, config: Dict[str, Any]) -> bool:
        """检查网络状态"""
        url = config.get('url')
        port = config.get('port')
        timeout = config.get('timeout', 5)
        expected_speed = config.get('expected_speed')  # Mbps
        
        if url:
            # 检查URL可达性
            try:
                import socket
                from urllib.parse import urlparse
                
                parsed_url = urlparse(url)
                host = parsed_url.hostname or url
                port = parsed_url.port or port or 80
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result != 0:
                    return False
            except:
                return False
        
        if expected_speed is not None:
            # 检查网络速度
            current_time = time.time()
            net_io = psutil.net_io_counters()
            
            bytes_sent_diff = net_io.bytes_sent - self.last_bytes_sent
            bytes_recv_diff = net_io.bytes_recv - self.last_bytes_recv
            time_diff = current_time - self.last_time
            
            if time_diff > 0:
                # 计算传输速度 (Mbps)
                speed_mbps = ((bytes_sent_diff + bytes_recv_diff) * 8 / time_diff) / (1024 * 1024)
                
                if speed_mbps < expected_speed:
                    return False
            
            # 更新上次测量值
            self.last_bytes_sent = net_io.bytes_sent
            self.last_bytes_recv = net_io.bytes_recv
            self.last_time = current_time
        
        return True


class CustomMonitor:
    """自定义监控器"""
    
    def __init__(self):
        self.custom_checks = {}
        self.thread_local = threading.local()
    
    def register_custom_check(self, name: str, check_func: Callable[[Dict[str, Any]], bool]):
        """注册自定义检查函数"""
        self.custom_checks[name] = check_func
    
    async def check(self, config: Dict[str, Any]) -> bool:
        """执行自定义检查"""
        check_name = config.get('check_name')
        if check_name and check_name in self.custom_checks:
            try:
                # 在异步环境中运行同步函数
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, self.custom_checks[check_name], config)
            except Exception as e:
                print(f"Custom check error: {e}")
                return False
        return False


class IntelligentMonitor:
    """多维度智能监控"""
    
    def __init__(self):
        self.monitors = {
            'process': ProcessMonitor(),
            'window': WindowMonitor(),
            'image': ImageMonitor(),
            'performance': PerformanceMonitor(),
            'network': NetworkMonitor(),
            'custom': CustomMonitor()
        }
        
        # 复合条件评估器
        self.condition_evaluators = {
            'and': lambda results: all(results),
            'or': lambda results: any(results),
            'not': lambda results: not results[0] if len(results) == 1 else not any(results),
            'xor': lambda results: sum(results) % 2 == 1
        }
    
    def evaluate_conditions(self, results: List[tuple], logic: str = 'or') -> bool:
        """评估条件结果"""
        if not results:
            return True
        
        # 提取布尔结果
        boolean_results = [result[1] for result in results]
        
        # 使用适当的逻辑运算符
        evaluator = self.condition_evaluators.get(logic.lower(), self.condition_evaluators['or'])
        return evaluator(boolean_results)
    
    async def wait_for_condition(self, conditions: List[Dict[str, Any]], timeout: int = 60) -> bool:
        """等待复合条件满足"""
        start_time = time.time()
        
        # 提取顶层逻辑（如 'and', 'or', 'not'）
        logic = 'or'  # 默认为or
        if conditions and 'logic' in conditions[0]:
            logic = conditions[0]['logic']
        
        while time.time() - start_time < timeout:
            results = []
            for condition in conditions:
                monitor_type = condition.get('type', 'custom')
                monitor = self.monitors.get(monitor_type)
                
                if monitor:
                    result = await monitor.check(condition.get('config', {}))
                    results.append((condition, result))
                else:
                    results.append((condition, False))
            
            if self.evaluate_conditions(results, logic):
                return True
            
            await asyncio.sleep(0.5)
        
        return False
    
    async def register_custom_monitor(self, name: str, check_func: Callable[[Dict[str, Any]], bool]):
        """注册自定义监控器"""
        if isinstance(self.monitors['custom'], CustomMonitor):
            self.monitors['custom'].register_custom_check(name, check_func)
    
    async def monitor_continuously(self, conditions: List[Dict[str, Any]], 
                                 callback: Callable[[List[tuple]], None],
                                 interval: float = 1.0):
        """持续监控并回调"""
        while True:
            results = []
            for condition in conditions:
                monitor_type = condition.get('type', 'custom')
                monitor = self.monitors.get(monitor_type)
                
                if monitor:
                    result = await monitor.check(condition.get('config', {}))
                    results.append((condition, result))
                else:
                    results.append((condition, False))
            
            # 调用回调函数
            callback(results)
            
            await asyncio.sleep(interval)
    
    def get_monitor_stats(self) -> Dict[str, Any]:
        """获取监控器统计信息"""
        stats = {}
        for name, monitor in self.monitors.items():
            if hasattr(monitor, 'get_stats'):
                stats[name] = monitor.get_stats()
            else:
                stats[name] = {'type': type(monitor).__name__}
        return stats


# 示例用法
async def example_usage():
    monitor = IntelligentMonitor()
    
    # 示例：等待游戏窗口激活且CPU使用率低于80%
    conditions = [
        {
            'type': 'window',
            'config': {
                'title': '游戏标题',
                'expected_state': 'active'
            }
        },
        {
            'type': 'performance',
            'config': {
                'cpu_max': 80
            }
        }
    ]
    
    result = await monitor.wait_for_condition(conditions, timeout=30)
    print(f"条件满足: {result}")


if __name__ == "__main__":
    asyncio.run(example_usage())