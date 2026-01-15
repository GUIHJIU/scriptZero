"""
依赖注入容器
管理应用程序中所有服务的生命周期和依赖关系
"""
from typing import Type, Dict, Any, Protocol, Optional, List
from collections import defaultdict
import asyncio
from contextlib import asynccontextmanager


class ServiceNotFoundException(Exception):
    """当请求的服务未找到时抛出"""
    pass


class CircularDependencyException(Exception):
    """当检测到循环依赖时抛出"""
    pass


class Container:
    """依赖注入容器"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, callable] = {}
        self._types: Dict[str, Type] = {}
        self._dependencies: Dict[str, List[str]] = defaultdict(list)
        self._resolved: set = set()
        self._resolving: set = set()
    
    def register(self, name: str, service: Any = None, factory: callable = None, singleton: bool = True):
        """
        注册服务
        
        Args:
            name: 服务名称
            service: 服务实例（用于单例）
            factory: 工厂函数（用于每次创建新实例）
            singleton: 是否为单例模式
        """
        if service is not None:
            self._services[name] = service
            self._resolved.add(name)
        elif factory is not None:
            self._factories[name] = factory
        
        if not singleton:
            # 非单例服务不会被缓存
            pass
    
    def register_singleton(self, name: str, service_class: Type, *args, **kwargs):
        """注册单例服务类"""
        def factory(container_instance):
            return service_class(*args, **kwargs)
        
        self._factories[name] = factory
        self._types[name] = service_class
    
    def register_transient(self, name: str, service_class: Type):
        """注册瞬态服务类"""
        def factory(container_instance):
            return service_class()
        
        self._factories[name] = factory
        self._types[name] = service_class
    
    def resolve(self, name: str) -> Any:
        """
        解析服务实例
        
        Args:
            name: 服务名称
            
        Returns:
            服务实例
        """
        # 检查是否已经在解析中（防止循环依赖）
        if name in self._resolving:
            raise CircularDependencyException(f"Circular dependency detected for service: {name}")
        
        # 检查是否已有实例
        if name in self._services:
            return self._services[name]
        
        # 检查是否有工厂函数
        if name not in self._factories:
            raise ServiceNotFoundException(f"Service '{name}' not registered")
        
        # 标记为正在解析
        self._resolving.add(name)
        
        try:
            factory = self._factories[name]
            instance = factory(self)
            
            # 如果是单例，缓存实例
            if name in self._types:
                # 对于注册为类的服务，我们默认当作单例处理
                self._services[name] = instance
            
            self._resolved.add(name)
            return instance
        finally:
            self._resolving.remove(name)
    
    def resolve_with_args(self, name: str, *args, **kwargs) -> Any:
        """
        解析服务实例并传递额外参数
        
        Args:
            name: 服务名称
            *args: 额外的位置参数
            **kwargs: 额外的关键字参数
            
        Returns:
            服务实例
        """
        if name not in self._factories:
            raise ServiceNotFoundException(f"Service '{name}' not registered")
        
        factory = self._factories[name]
        # 传递容器实例和额外参数
        instance = factory(self, *args, **kwargs)
        
        # 注意：这种方式不会缓存实例，每次都会创建新实例
        return instance
    
    def is_registered(self, name: str) -> bool:
        """检查服务是否已注册"""
        return name in self._services or name in self._factories
    
    def get_service_names(self) -> List[str]:
        """获取所有注册的服务名称"""
        return list(set(self._services.keys()) | set(self._factories.keys()))
    
    def reset(self):
        """重置容器（清除所有实例，保留注册）"""
        self._services.clear()
        self._resolved.clear()
    
    def dispose(self):
        """释放容器中的所有服务"""
        for name, service in self._services.items():
            if hasattr(service, 'dispose'):
                service.dispose()
            elif hasattr(service, '__del__'):
                service.__del__()
        
        self._services.clear()
        self._factories.clear()
        self._types.clear()
        self._dependencies.clear()
        self._resolved.clear()
        self._resolving.clear()


class IContainer(Protocol):
    """容器协议接口"""
    
    def register(self, name: str, service: Any = None, factory: callable = None, singleton: bool = True):
        """注册服务"""
        ...
    
    def register_singleton(self, name: str, service_class: Type, *args, **kwargs):
        """注册单例服务类"""
        ...
    
    def register_transient(self, name: str, service_class: Type):
        """注册瞬态服务类"""
        ...
    
    def resolve(self, name: str) -> Any:
        """解析服务实例"""
        ...
    
    def is_registered(self, name: str) -> bool:
        """检查服务是否已注册"""
        ...
    
    def reset(self):
        """重置容器"""
        ...
    
    def dispose(self):
        """释放容器中的所有服务"""
        ...


# 全局容器实例
_global_container = Container()


def get_container() -> Container:
    """获取全局容器实例"""
    return _global_container


def register_service(name: str, service: Any = None, factory: callable = None, singleton: bool = True):
    """注册服务到全局容器"""
    container = get_container()
    container.register(name, service, factory, singleton)


def resolve_service(name: str) -> Any:
    """从全局容器解析服务"""
    container = get_container()
    return container.resolve(name)