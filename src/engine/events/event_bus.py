"""
事件总线系统
实现模块间的松耦合通信
"""
import asyncio
import concurrent.futures
import weakref
from typing import Dict, List, Callable, Any, Set
from dataclasses import dataclass
from datetime import datetime
import logging


@dataclass
class Event:
    """事件类"""
    name: str
    data: Dict[str, Any]
    timestamp: float
    source: str = "system"
    correlation_id: str = None
    reply_to: str = None


class Middleware:
    """中间件基类"""
    
    async def before_emit(self, event: Event) -> Event:
        """事件发送前处理"""
        return event
    
    async def after_emit(self, event: Event) -> Event:
        """事件发送后处理"""
        return event


class LoggingMiddleware(Middleware):
    """日志中间件"""
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
    
    async def before_emit(self, event: Event) -> Event:
        self.logger.debug(f"Event '{event.name}' emitted from {event.source}")
        return event


class EventBus:
    """事件总线核心"""
    
    def __init__(self):
        self._handlers: Dict[str, List[tuple]] = {}  # {event_name: [(priority, handler), ...]}
        self._middleware: List[Middleware] = []
        self._event_history: List[Event] = []
        self._max_history_size = 1000
        self._lock = asyncio.Lock()
        self._wildcard_handlers: Dict[str, List[tuple]] = {}  # 通配符处理器
        self._pattern_handlers: Dict[str, List[tuple]] = {}  # 模式处理器
        self._thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        
    def subscribe(self, event_name: str, handler: Callable, priority: int = 0):
        """订阅事件"""
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        
        # 添加到列表并按优先级排序
        self._handlers[event_name].append((priority, handler))
        self._handlers[event_name].sort(key=lambda x: x[0])
    
    def unsubscribe(self, event_name: str, handler: Callable):
        """取消订阅事件"""
        if event_name in self._handlers:
            self._handlers[event_name] = [
                (p, h) for p, h in self._handlers[event_name] 
                if h != handler
            ]
    
    def add_middleware(self, middleware: Middleware):
        """添加中间件"""
        self._middleware.append(middleware)
    
    def remove_middleware(self, middleware: Middleware):
        """移除中间件"""
        if middleware in self._middleware:
            self._middleware.remove(middleware)
    
    async def emit(self, event_name: str, data: Dict[str, Any] = None, 
                   source: str = "system", correlation_id: str = None) -> Event:
        """发布事件"""
        # 创建事件对象
        event = Event(
            name=event_name,
            data=data or {},
            timestamp=datetime.now().timestamp(),
            source=source,
            correlation_id=correlation_id
        )
        
        # 应用中间件（发送前）
        for middleware in self._middleware:
            event = await middleware.before_emit(event)
        
        # 异步执行所有处理器
        tasks = []
        
        # 1. 执行精确匹配的处理器
        if event_name in self._handlers:
            for _, handler in self._handlers[event_name]:
                if asyncio.iscoroutinefunction(handler):
                    task = asyncio.create_task(handler(event))
                    tasks.append(task)
                else:
                    # 对于同步函数，使用线程池执行并在完成后创建完成的协程
                    loop = asyncio.get_event_loop()
                    
                    def run_handler():
                        try:
                            handler(event)
                        except Exception as e:
                            print(f"Handler error: {e}")
                    
                    # 使用 run_in_executor 来在后台运行同步函数
                    future = loop.run_in_executor(self._thread_pool, run_handler)
                    # 将future包装成task，这样我们可以等待它
                    task = asyncio.create_task(_await_future(future))
                    tasks.append(task)
        
        # 2. 执行通配符处理器
        for wildcard, handlers in self._wildcard_handlers.items():
            if self._match_wildcard(event_name, wildcard):
                for _, handler in handlers:
                    if asyncio.iscoroutinefunction(handler):
                        task = asyncio.create_task(handler(event))
                        tasks.append(task)
                    else:
                        loop = asyncio.get_event_loop()
                        
                        def run_handler():
                            try:
                                handler(event)
                            except Exception as e:
                                print(f"Handler error: {e}")
                        
                        future = loop.run_in_executor(self._thread_pool, run_handler)
                        task = asyncio.create_task(_await_future(future))
                        tasks.append(task)
        
        # 3. 执行模式处理器
        for pattern, handlers in self._pattern_handlers.items():
            if self._match_pattern(event_name, pattern):
                for _, handler in handlers:
                    if asyncio.iscoroutinefunction(handler):
                        task = asyncio.create_task(handler(event))
                        tasks.append(task)
                    else:
                        loop = asyncio.get_event_loop()
                        
                        def run_handler():
                            try:
                                handler(event)
                            except Exception as e:
                                print(f"Handler error: {e}")
                        
                        future = loop.run_in_executor(self._thread_pool, run_handler)
                        task = asyncio.create_task(_await_future(future))
                        tasks.append(task)
        
        # 等待所有处理器完成
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # 应用中间件（发送后）
        for middleware in reversed(self._middleware):
            event = await middleware.after_emit(event)
        
        # 记录事件历史
        await self._add_to_history(event)
        
        return event
    
    async def emit_with_reply(self, event_name: str, data: Dict[str, Any] = None,
                             reply_event_name: str = None, timeout: float = 30.0) -> Event:
        """发送事件并等待回复"""
        reply_event_name = reply_event_name or f"{event_name}.reply"
        correlation_id = str(datetime.now().timestamp())
        
        # 创建事件
        event = Event(
            name=event_name,
            data=data or {},
            timestamp=datetime.now().timestamp(),
            source="system",
            correlation_id=correlation_id,
            reply_to=reply_event_name
        )
        
        # 设置回复事件的Future
        future = asyncio.Future()
        reply_handler = self._create_reply_handler(reply_event_name, correlation_id, future)
        
        # 订阅回复事件
        self.subscribe(reply_event_name, reply_handler)
        
        try:
            # 发送原事件
            await self.emit(event_name, data, correlation_id=correlation_id)
            
            # 等待回复
            reply_event = await asyncio.wait_for(future, timeout=timeout)
            return reply_event
        finally:
            # 取消订阅回复事件
            self.unsubscribe(reply_event_name, reply_handler)
    
    def _create_reply_handler(self, expected_event_name: str, expected_correlation_id: str, future: asyncio.Future):
        """创建回复事件处理器"""
        def handler(event: Event):
            if (event.name == expected_event_name and 
                event.correlation_id == expected_correlation_id and 
                not future.done()):
                future.set_result(event)
        return handler
    
    def subscribe_wildcard(self, pattern: str, handler: Callable, priority: int = 0):
        """订阅通配符事件"""
        if pattern not in self._wildcard_handlers:
            self._wildcard_handlers[pattern] = []
        
        self._wildcard_handlers[pattern].append((priority, handler))
        self._wildcard_handlers[pattern].sort(key=lambda x: x[0])
    
    def subscribe_pattern(self, pattern: str, handler: Callable, priority: int = 0):
        """订阅正则表达式模式事件"""
        if pattern not in self._pattern_handlers:
            self._pattern_handlers[pattern] = []
        
        self._pattern_handlers[pattern].append((priority, handler))
        self._pattern_handlers[pattern].sort(key=lambda x: x[0])
    
    def _match_wildcard(self, event_name: str, pattern: str) -> bool:
        """检查事件名是否匹配通配符模式"""
        import fnmatch
        return fnmatch.fnmatch(event_name, pattern)
    
    def _match_pattern(self, event_name: str, pattern: str) -> bool:
        """检查事件名是否匹配正则表达式模式"""
        import re
        try:
            return re.match(pattern, event_name) is not None
        except:
            return False
    
    async def _add_to_history(self, event: Event):
        """添加事件到历史记录"""
        async with self._lock:
            self._event_history.append(event)
            if len(self._event_history) > self._max_history_size:
                self._event_history = self._event_history[-500:]  # 保留最近500个事件
    
    def get_event_history(self, limit: int = 100) -> List[Event]:
        """获取事件历史"""
        return self._event_history[-limit:]
    
    def clear_history(self):
        """清除事件历史"""
        self._event_history.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取事件总线统计信息"""
        return {
            'handlers_count': sum(len(handlers) for handlers in self._handlers.values()),
            'wildcard_handlers_count': sum(len(handlers) for handlers in self._wildcard_handlers.values()),
            'pattern_handlers_count': sum(len(handlers) for handlers in self._pattern_handlers.values()),
            'history_size': len(self._event_history),
            'max_history_size': self._max_history_size,
            'middleware_count': len(self._middleware)
        }


async def _await_future(future):
    """等待future完成的辅助函数"""
    try:
        await asyncio.wrap_future(future)
    except Exception as e:
        print(f"Future execution error: {e}")


# 全局事件总线实例
_global_event_bus = None


def get_event_bus() -> EventBus:
    """获取全局事件总线实例"""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def reset_event_bus():
    """重置全局事件总线"""
    global _global_event_bus
    _global_event_bus = EventBus()


# 预定义的事件名称常量
class Events:
    """预定义的事件名称"""
    # 系统事件
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_ERROR = "system.error"
    
    # 配置事件
    CONFIG_LOADED = "config.loaded"
    CONFIG_SAVED = "config.saved"
    CONFIG_CHANGED = "config.changed"
    
    # 工作流事件
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    WORKFLOW_PAUSED = "workflow.paused"
    WORKFLOW_RESUMED = "workflow.resumed"
    
    # 脚本事件
    SCRIPT_STARTED = "script.started"
    SCRIPT_COMPLETED = "script.completed"
    SCRIPT_FAILED = "script.failed"
    SCRIPT_TERMINATED = "script.terminated"
    
    # 进程事件
    PROCESS_STARTED = "process.started"
    PROCESS_ENDED = "process.ended"
    PROCESS_ERROR = "process.error"
    
    # 监控事件
    MONITOR_TRIGGERED = "monitor.triggered"
    CONDITION_MET = "condition.met"
    ACTION_EXECUTED = "action.executed"
    
    # UI事件
    UI_UPDATE_REQUESTED = "ui.update_requested"
    LOG_MESSAGE = "log.message"
    PROGRESS_UPDATE = "progress.update"
    
    # 状态事件
    STATE_CHANGED = "state.changed"
    HISTORY_UPDATED = "history.updated"


# 便利函数
async def emit_event(event_name: str, data: Dict[str, Any] = None, 
                    source: str = "system", correlation_id: str = None):
    """便利函数：发送事件"""
    bus = get_event_bus()
    return await bus.emit(event_name, data, source, correlation_id)


def subscribe_to_event(event_name: str, handler: Callable, priority: int = 0):
    """便利函数：订阅事件"""
    bus = get_event_bus()
    bus.subscribe(event_name, handler, priority)


# 示例用法
async def event_bus_example():
    # 获取事件总线
    bus = get_event_bus()
    
    # 添加日志中间件
    bus.add_middleware(LoggingMiddleware())
    
    # 定义事件处理器
    def handle_workflow_started(event: Event):
        print(f"工作流开始: {event.data}")
    
    def handle_script_completed(event: Event):
        print(f"脚本完成: {event.data}")
    
    # 订阅事件
    bus.subscribe(Events.WORKFLOW_STARTED, handle_workflow_started)
    bus.subscribe(Events.SCRIPT_COMPLETED, handle_script_completed)
    
    # 发送事件
    await bus.emit(Events.WORKFLOW_STARTED, {"workflow_id": "test_wf", "name": "Test Workflow"})
    await bus.emit(Events.SCRIPT_COMPLETED, {"script_id": "test_script", "result": "success"})
    
    # 获取统计信息
    stats = bus.get_statistics()
    print("事件总线统计:", stats)


if __name__ == "__main__":
    asyncio.run(event_bus_example())