"""
执行上下文
管理任务执行的上下文信息、资源和状态
"""
import asyncio
import threading
from typing import Dict, Any, Optional, List, Callable
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from datetime import datetime
import logging
import uuid


@dataclass
class ExecutionContextData:
    """执行上下文数据"""
    task_id: str
    session_id: str
    start_time: datetime
    resources: Dict[str, Any]
    metadata: Dict[str, Any]
    parent_context: Optional['ExecutionContextData']


class ExecutionContext:
    """执行上下文管理器"""
    
    def __init__(self, task_id: str = None, session_id: str = None, 
                 metadata: Dict[str, Any] = None, parent_context: 'ExecutionContext' = None):
        self.task_id = task_id or str(uuid.uuid4())
        self.session_id = session_id or str(uuid.uuid4())
        self.metadata = metadata or {}
        self.parent_context = parent_context
        self.resources: Dict[str, Any] = {}
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.is_active = False
        self.logger = logging.getLogger(f"ExecutionContext.{self.task_id}")
        
        # 线程本地存储
        self._local = threading.local()
    
    @asynccontextmanager
    async def context(self):
        """异步上下文管理器"""
        self.is_active = True
        self._set_current_context()
        try:
            yield self
        finally:
            self.is_active = False
            self.end_time = datetime.now()
            self._clear_current_context()
    
    @contextmanager
    def sync_context(self):
        """同步上下文管理器"""
        self.is_active = True
        self._set_current_context()
        try:
            yield self
        finally:
            self.is_active = False
            self.end_time = datetime.now()
            self._clear_current_context()
    
    def _set_current_context(self):
        """设置当前上下文"""
        self._local.context = self
    
    def _clear_current_context(self):
        """清除当前上下文"""
        if hasattr(self._local, 'context'):
            delattr(self._local, 'context')
    
    @classmethod
    def get_current_context(cls) -> Optional['ExecutionContext']:
        """获取当前执行上下文"""
        thread_local = threading.local()
        if hasattr(thread_local, 'context'):
            return thread_local.context
        return None
    
    def register_resource(self, name: str, resource: Any, cleanup_func: Callable = None):
        """注册资源"""
        self.resources[name] = {
            'resource': resource,
            'cleanup_func': cleanup_func
        }
    
    def get_resource(self, name: str) -> Any:
        """获取资源"""
        if name in self.resources:
            return self.resources[name]['resource']
        return None
    
    def release_resources(self):
        """释放所有资源"""
        for name, resource_info in self.resources.items():
            cleanup_func = resource_info.get('cleanup_func')
            if cleanup_func:
                try:
                    cleanup_func(resource_info['resource'])
                except Exception as e:
                    self.logger.warning(f"Failed to clean up resource {name}: {e}")
        
        self.resources.clear()
    
    def add_metadata(self, key: str, value: Any):
        """添加元数据"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """获取元数据"""
        return self.metadata.get(key, default)
    
    def get_duration(self) -> Optional[float]:
        """获取执行持续时间（秒）"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        elif self.is_active:
            return (datetime.now() - self.start_time).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'task_id': self.task_id,
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.get_duration(),
            'is_active': self.is_active,
            'resources': list(self.resources.keys()),
            'metadata': self.metadata,
            'parent_context_id': self.parent_context.task_id if self.parent_context else None
        }


class ExecutionContextManager:
    """执行上下文管理器"""
    
    def __init__(self):
        self.active_contexts: Dict[str, ExecutionContext] = {}
        self.context_stack: List[ExecutionContext] = []
        self.lock = threading.RLock()
    
    def create_context(self, task_id: str = None, session_id: str = None,
                      metadata: Dict[str, Any] = None, 
                      parent_context: ExecutionContext = None) -> ExecutionContext:
        """创建新的执行上下文"""
        ctx = ExecutionContext(
            task_id=task_id,
            session_id=session_id,
            metadata=metadata,
            parent_context=parent_context or self.get_current_context()
        )
        
        with self.lock:
            self.active_contexts[ctx.task_id] = ctx
        
        return ctx
    
    def get_context(self, task_id: str) -> Optional[ExecutionContext]:
        """获取指定任务的上下文"""
        return self.active_contexts.get(task_id)
    
    def get_current_context(self) -> Optional[ExecutionContext]:
        """获取当前执行上下文"""
        # 首先尝试从线程本地存储获取
        thread_local = threading.local()
        if hasattr(thread_local, 'context'):
            return thread_local.context
        
        # 如果没有，尝试从上下文栈获取
        if self.context_stack:
            return self.context_stack[-1]
        
        return None
    
    def enter_context(self, context: ExecutionContext):
        """进入上下文"""
        with self.lock:
            self.context_stack.append(context)
            self.active_contexts[context.task_id] = context
    
    def exit_context(self):
        """退出上下文"""
        with self.lock:
            if self.context_stack:
                context = self.context_stack.pop()
                context.release_resources()
    
    def cleanup_context(self, task_id: str):
        """清理指定任务的上下文"""
        with self.lock:
            if task_id in self.active_contexts:
                ctx = self.active_contexts[task_id]
                ctx.release_resources()
                del self.active_contexts[task_id]


# 全局上下文管理器实例
_global_context_manager = ExecutionContextManager()


def get_context_manager() -> ExecutionContextManager:
    """获取全局上下文管理器实例"""
    return _global_context_manager


def create_execution_context(task_id: str = None, session_id: str = None,
                           metadata: Dict[str, Any] = None) -> ExecutionContext:
    """创建执行上下文"""
    manager = get_context_manager()
    return manager.create_context(task_id, session_id, metadata)


def get_current_execution_context() -> Optional[ExecutionContext]:
    """获取当前执行上下文"""
    manager = get_context_manager()
    return manager.get_current_context()


def register_resource_in_current_context(name: str, resource: Any, cleanup_func: Callable = None):
    """在当前上下文中注册资源"""
    ctx = get_current_execution_context()
    if ctx:
        ctx.register_resource(name, resource, cleanup_func)
    else:
        raise RuntimeError("No active execution context")


def get_resource_from_current_context(name: str) -> Any:
    """从当前上下文中获取资源"""
    ctx = get_current_execution_context()
    if ctx:
        return ctx.get_resource(name)
    return None