"""
适配器抽象基类
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAdapter(ABC):
    """所有适配器的基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False
    
    @abstractmethod
    async def start(self):
        """启动适配器"""
        pass
    
    @abstractmethod
    async def stop(self):
        """停止适配器"""
        pass
    
    @abstractmethod
    async def execute(self, *args, **kwargs):
        """执行适配器的主要功能"""
        pass
    
    def update_config(self, new_config: Dict[str, Any]):
        """更新配置"""
        self.config.update(new_config)