"""
任务调度器
管理任务队列、优先级和依赖关系
"""
import asyncio
import time
from typing import Dict, Any, List, Optional, Callable, Awaitable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import heapq


class TaskPriority(Enum):
    LOWEST = 0
    LOW = 1
    NORMAL = 2
    HIGH = 3
    HIGHEST = 4


class TaskStatus(Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class Task:
    """任务数据类"""
    id: str
    coroutine: Callable[[], Awaitable[Any]]
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: float = 0
    scheduled_at: Optional[float] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[Exception] = None
    dependencies: List[str] = None  # 依赖的任务ID列表
    timeout: Optional[float] = None  # 超时时间（秒）
    retry_count: int = 0  # 重试次数
    max_retries: int = 3  # 最大重试次数
    metadata: Dict[str, Any] = None  # 任务元数据

    def __post_init__(self):
        if self.created_at == 0:
            self.created_at = time.time()
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.task_queue = []  # 使用heapq实现优先级队列
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.pending_tasks: Dict[str, Task] = {}  # 等待依赖完成的任务
        self._stop_event = asyncio.Event()
        self._scheduler_task = None
        self._lock = asyncio.Lock()
        
    async def submit_task(self, task: Task) -> str:
        """提交任务到调度队列"""
        async with self._lock:
            self.pending_tasks[task.id] = task
            await self._evaluate_task(task)
            return task.id
    
    async def schedule_task(self, coro: Callable[[], Awaitable[Any]], 
                           task_id: str = None, priority: TaskPriority = TaskPriority.NORMAL,
                           dependencies: List[str] = None, timeout: Optional[float] = None,
                           max_retries: int = 3, metadata: Dict[str, Any] = None) -> str:
        """调度一个协程任务"""
        if task_id is None:
            task_id = f"task_{int(time.time() * 1000000)}"
        
        task_obj = Task(
            id=task_id,
            coroutine=coro,
            priority=priority,
            dependencies=dependencies or [],
            timeout=timeout,
            max_retries=max_retries,
            metadata=metadata or {}
        )
        
        return await self.submit_task(task_obj)
    
    async def _evaluate_task(self, task: Task):
        """评估任务是否可以运行"""
        # 检查依赖是否满足
        if await self._are_dependencies_met(task):
            # 依赖满足，可以入队
            await self._queue_task(task)
        else:
            # 依赖未满足，保持在pending状态
            pass
    
    async def _are_dependencies_met(self, task: Task) -> bool:
        """检查任务依赖是否满足"""
        for dep_id in task.dependencies:
            dep_task = self.completed_tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    async def _queue_task(self, task: Task):
        """将任务加入队列"""
        async with self._lock:
            # 更新任务状态
            task.status = TaskStatus.QUEUED
            task.scheduled_at = time.time()
            
            # 使用优先级队列
            heapq.heappush(self.task_queue, (-task.priority.value, task.created_at, task.id, task))
            
            # 尝试启动新任务
            await self._try_start_next_task()
    
    async def _try_start_next_task(self):
        """尝试启动下一个任务"""
        if len(self.running_tasks) >= self.max_concurrent:
            return  # 已达到最大并发数
        
        if not self.task_queue:
            return  # 队列为空
        
        # 获取最高优先级的任务
        _, _, task_id, task = heapq.heappop(self.task_queue)
        
        if task_id in self.running_tasks:
            # 任务已经在运行，重新放入队列
            heapq.heappush(self.task_queue, (-task.priority.value, task.created_at, task.id, task))
            return
        
        await self._start_task(task)
    
    async def _start_task(self, task: Task):
        """启动任务"""
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        
        # 创建异步任务
        async_task = asyncio.create_task(self._execute_task_with_timeout(task))
        self.running_tasks[task.id] = async_task
        
        # 附加完成回调
        async_task.add_done_callback(lambda t: asyncio.create_task(self._on_task_complete(task.id)))
    
    async def _execute_task_with_timeout(self, task: Task):
        """执行任务并处理超时"""
        try:
            if task.timeout:
                result = await asyncio.wait_for(task.coroutine(), timeout=task.timeout)
            else:
                result = await task.coroutine()
            
            task.result = result
            task.status = TaskStatus.COMPLETED
        except asyncio.TimeoutError:
            task.status = TaskStatus.TIMEOUT
            task.error = asyncio.TimeoutError(f"Task {task.id} timed out after {task.timeout} seconds")
        except Exception as e:
            task.error = e
            if task.retry_count < task.max_retries:
                # 需要重试
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                # 重新提交任务
                async with self._lock:
                    self.pending_tasks[task.id] = task
                    await self._evaluate_task(task)
                return
            else:
                task.status = TaskStatus.FAILED
        
        task.completed_at = time.time()
    
    async def _on_task_complete(self, task_id: str):
        """任务完成回调"""
        async with self._lock:
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            
            # 移动到完成任务列表
            if task_id in self.pending_tasks:
                completed_task = self.pending_tasks.pop(task_id)
                self.completed_tasks[task_id] = completed_task
                
                # 检查是否有依赖于此任务的其他任务
                await self._check_dependent_tasks(task_id)
    
    async def _check_dependent_tasks(self, completed_task_id: str):
        """检查是否有任务依赖于已完成的任务"""
        for task_id, task in self.pending_tasks.items():
            if completed_task_id in task.dependencies:
                await self._evaluate_task(task)
    
    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """等待特定任务完成"""
        start_time = time.time()
        
        while True:
            # 检查是否已完成
            completed_task = self.completed_tasks.get(task_id)
            if completed_task:
                if completed_task.status == TaskStatus.FAILED:
                    raise completed_task.error
                return completed_task.result
            
            # 检查是否正在运行
            if task_id in self.running_tasks:
                remaining_time = None
                if timeout:
                    elapsed = time.time() - start_time
                    remaining_time = max(0, timeout - elapsed)
                
                try:
                    await asyncio.wait_for(self.running_tasks[task_id], timeout=remaining_time)
                except asyncio.TimeoutError:
                    raise TimeoutError(f"Task {task_id} timed out")
                continue
            
            # 检查是否存在于待处理任务中
            if task_id in self.pending_tasks:
                # 等待一小段时间再检查
                await asyncio.sleep(0.1)
                if timeout and (time.time() - start_time) > timeout:
                    raise TimeoutError(f"Task {task_id} timed out")
                continue
            
            # 任务不存在
            raise ValueError(f"Task {task_id} not found")
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        async with self._lock:
            if task_id in self.running_tasks:
                task = self.running_tasks[task_id]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                
                # 更新任务状态
                if task_id in self.pending_tasks:
                    self.pending_tasks[task_id].status = TaskStatus.CANCELLED
                return True
            elif task_id in self.pending_tasks:
                self.pending_tasks[task_id].status = TaskStatus.CANCELLED
                return True
            elif task_id in self.completed_tasks:
                # 已完成的任务无法取消
                return False
            else:
                return False
    
    async def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        if task_id in self.running_tasks:
            return TaskStatus.RUNNING
        elif task_id in self.pending_tasks:
            return self.pending_tasks[task_id].status
        elif task_id in self.completed_tasks:
            return self.completed_tasks[task_id].status
        else:
            return None
    
    async def start(self):
        """启动调度器"""
        pass  # 当前实现不需要后台任务
    
    async def stop(self):
        """停止调度器"""
        # 取消所有正在运行的任务
        for task_id, task in list(self.running_tasks.items()):
            await self.cancel_task(task_id)
        
        # 清理资源
        self._stop_event.set()
    
    def get_queue_size(self) -> int:
        """获取队列大小"""
        return len(self.task_queue)
    
    def get_running_count(self) -> int:
        """获取运行中任务数量"""
        return len(self.running_tasks)
    
    def get_completed_count(self) -> int:
        """获取已完成任务数量"""
        return len(self.completed_tasks)