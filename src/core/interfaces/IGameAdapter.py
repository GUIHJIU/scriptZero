"""
游戏适配器接口
定义所有游戏适配器必须实现的方法
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Protocol


class IGameAdapter(Protocol):
    """游戏适配器协议"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化适配器"""
        ...
    
    async def start(self) -> bool:
        """启动游戏和相关服务"""
        ...
    
    async def stop(self) -> bool:
        """停止游戏和相关服务"""
        ...
    
    async def execute(self, *args, **kwargs) -> Any:
        """执行主要功能"""
        ...
    
    async def find_game_window(self) -> Optional[int]:
        """查找游戏窗口句柄"""
        ...
    
    async def activate_game_window(self):
        """激活游戏窗口"""
        ...
    
    def is_feature_supported(self, feature: str) -> bool:
        """检查是否支持特定功能"""
        ...


class IGameAdapterAbstract(ABC):
    """游戏适配器抽象基类（传统方式）"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化适配器"""
        self.config = config
    
    @abstractmethod
    async def start(self) -> bool:
        """启动游戏和相关服务"""
        pass
    
    @abstractmethod
    async def stop(self) -> bool:
        """停止游戏和相关服务"""
        pass
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """执行主要功能"""
        pass
    
    @abstractmethod
    async def find_game_window(self) -> Optional[int]:
        """查找游戏窗口句柄"""
        pass
    
    @abstractmethod
    async def activate_game_window(self):
        """激活游戏窗口"""
        pass
    
    @abstractmethod
    def is_feature_supported(self, feature: str) -> bool:
        """检查是否支持特定功能"""
        pass