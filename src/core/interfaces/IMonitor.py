"""
监控器接口
定义所有监控器必须实现的方法
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Protocol, Callable, Optional


class IMonitor(Protocol):
    """监控器协议"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化监控器"""
        ...
    
    async def start(self) -> bool:
        """启动监控"""
        ...
    
    async def stop(self) -> bool:
        """停止监控"""
        ...
    
    async def monitor(self) -> Any:
        """执行监控任务"""
        ...
    
    def register_callback(self, event: str, callback: Callable):
        """注册事件回调"""
        ...


class IMonitorAbstract(ABC):
    """监控器抽象基类（传统方式）"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化监控器"""
        self.config = config
    
    @abstractmethod
    async def start(self) -> bool:
        """启动监控"""
        pass
    
    @abstractmethod
    async def stop(self) -> bool:
        """停止监控"""
        pass
    
    @abstractmethod
    async def monitor(self) -> Any:
        """执行监控任务"""
        pass
    
    @abstractmethod
    def register_callback(self, event: str, callback: Callable):
        """注册事件回调"""
        pass