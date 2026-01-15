"""
独立的监控系统
与执行器完全解耦，支持多种监控策略
"""
import asyncio
import time
from typing import Dict, Any, List, Optional, Callable, Tuple
from ..monitors.intelligent_monitor import IntelligentMonitor


class MonitoringService:
    """独立的监控服务"""
    
    def __init__(self):
        self.intelligent_monitor = IntelligentMonitor()
        self.active_monitors = {}
    
    async def start_monitoring(self, monitor_id: str, conditions: List[Dict[str, Any]], 
                              callback: Optional[Callable] = None, timeout: int = 60) -> bool:
        """开始监控特定条件"""
        # 存储监控信息
        self.active_monitors[monitor_id] = {
            'conditions': conditions,
            'callback': callback,
            'start_time': time.time(),
            'timeout': timeout
        }
        
        # 等待条件满足
        result = await self.intelligent_monitor.wait_for_condition(conditions, timeout)
        
        # 执行回调（如果提供了的话）
        if callback:
            await self._execute_callback(callback, result, monitor_id)
        
        # 移除已完成的监控
        if monitor_id in self.active_monitors:
            del self.active_monitors[monitor_id]
        
        return result
    
    async def _execute_callback(self, callback: Callable, result: bool, monitor_id: str):
        """执行监控回调函数"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(result, monitor_id)
            else:
                # 在线程池中执行同步回调
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, callback, result, monitor_id)
        except Exception as e:
            print(f"Callback execution error for monitor {monitor_id}: {e}")
    
    async def check_condition(self, conditions: List[Dict[str, Any]]) -> bool:
        """检查条件是否满足（非阻塞）"""
        results = []
        for condition in conditions:
            monitor_type = condition.get('type', 'custom')
            config = condition.get('config', {})
            
            if monitor_type == 'process':
                from ..monitors.intelligent_monitor import ProcessMonitor
                monitor = ProcessMonitor()
            elif monitor_type == 'window':
                from ..monitors.intelligent_monitor import WindowMonitor
                monitor = WindowMonitor()
            elif monitor_type == 'image':
                from ..monitors.intelligent_monitor import ImageMonitor
                monitor = ImageMonitor()
            elif monitor_type == 'performance':
                from ..monitors.intelligent_monitor import PerformanceMonitor
                monitor = PerformanceMonitor()
            elif monitor_type == 'network':
                from ..monitors.intelligent_monitor import NetworkMonitor
                monitor = NetworkMonitor()
            else:
                from ..monitors.intelligent_monitor import CustomMonitor
                monitor = CustomMonitor()
            
            result = await monitor.check(config)
            results.append(result)
        
        # 使用OR逻辑作为默认行为
        return any(results) if results else True
    
    async def register_custom_monitor(self, name: str, check_func: Callable[[Dict[str, Any]], bool]):
        """注册自定义监控器"""
        await self.intelligent_monitor.register_custom_monitor(name, check_func)
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """获取监控统计信息"""
        return {
            'active_monitors': len(self.active_monitors),
            'monitor_details': {mid: {
                'conditions_count': len(info['conditions']),
                'elapsed_time': time.time() - info['start_time'],
                'timeout': info['timeout']
            } for mid, info in self.active_monitors.items()}
        }
    
    async def cancel_monitor(self, monitor_id: str) -> bool:
        """取消特定监控"""
        if monitor_id in self.active_monitors:
            del self.active_monitors[monitor_id]
            return True
        return False
    
    async def cleanup_all_monitors(self):
        """清理所有活动监控"""
        self.active_monitors.clear()


class EnhancedMonitor:
    """增强型监控器 - 支持多策略融合监控"""
    
    def __init__(self):
        self.strategies = [
            self.image_recognition,     # 图像识别
            self.ocr_detection,         # 文字识别
            self.color_analysis,        # 颜色分析
            self.motion_detection,      # 运动检测
        ]
        self.weights = [0.4, 0.3, 0.2, 0.1]  # 权重分配

    async def image_recognition(self, condition) -> Tuple[bool, float]:
        """图像识别策略"""
        # 使用原有的图像监控器
        from ..monitors.intelligent_monitor import ImageMonitor
        monitor = ImageMonitor()
        result = await monitor.check(condition.get('config', {}))
        # 这里应该返回 (结果, 置信度)
        return result, 0.8 if result else 0.2

    async def ocr_detection(self, condition) -> Tuple[bool, float]:
        """OCR文字检测策略 - 模拟实现"""
        # 模拟OCR检测
        ocr_config = condition.get('ocr_config', {})
        # 实际实现需要集成OCR库如pytesseract
        return False, 0.0  # 模拟未实现

    async def color_analysis(self, condition) -> Tuple[bool, float]:
        """颜色分析策略 - 模拟实现"""
        # 模拟颜色分析
        color_config = condition.get('color_config', {})
        # 实际实现需要颜色检测算法
        return False, 0.0  # 模拟未实现

    async def motion_detection(self, condition) -> Tuple[bool, float]:
        """运动检测策略 - 模拟实现"""
        # 模拟运动检测
        motion_config = condition.get('motion_config', {})
        # 实际实现需要运动检测算法
        return False, 0.0  # 模拟未实现

    async def check_condition(self, condition) -> bool:
        """使用多策略融合检查条件"""
        results = await asyncio.gather(*[
            strategy(condition) for strategy in self.strategies
        ])
        
        # 加权投票机制
        weighted_score = sum(
            result[1] * weight 
            for result, weight in zip(results, self.weights)
        )
        
        # 设定阈值
        threshold = condition.get('threshold', 0.5)
        return weighted_score >= threshold