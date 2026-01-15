"""
脚本适配器接口
定义所有脚本适配器必须实现的方法
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Protocol


class IScriptAdapter(Protocol):
    """脚本适配器协议"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化适配器"""
        ...
    
    async def start(self) -> bool:
        """启动适配器"""
        ...
    
    async def stop(self) -> bool:
        """停止适配器"""
        ...
    
    async def execute(self, *args, **kwargs) -> Any:
        """执行脚本"""
        ...


class IScriptAdapterAbstract(ABC):
    """脚本适配器抽象基类（传统方式）"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化适配器"""
        self.config = config
    
    @abstractmethod
    async def start(self) -> bool:
        """启动适配器"""
        pass
    
    @abstractmethod
    async def stop(self) -> bool:
        """停止适配器"""
        pass
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """执行脚本"""
        pass