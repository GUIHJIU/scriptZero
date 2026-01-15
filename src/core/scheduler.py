"""
智能调度器
实现工作流调度、资源管理和任务优化
"""
import asyncio
import heapq
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import time
import uuid
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task:
    """任务类"""
    
    def __init__(self, 
                 task_id: str,
                 name: str,
                 func: Callable,
                 args: tuple = (),
                 kwargs: dict = None,
                 priority: int = 0,
                 dependencies: List[str] = None,
                 timeout: Optional[int] = None,
                 created_at: float = None):
        self.task_id = task_id
        self.name = name
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.priority = priority  # 优先级，数值越小优先级越高
        self.dependencies = dependencies or []
        self.timeout = timeout
        self.created_at = created_at or time.time()
        self.status = TaskStatus.PENDING
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
        
        # 用于堆排序：(优先级, 创建时间, 任务ID)
        self.heap_key = (priority, self.created_at, self.task_id)
    
    def __lt__(self, other):
        """用于堆排序"""
        return self.heap_key < other.heap_key
    
    def __eq__(self, other):
        return self.task_id == other.task_id


class ResourcePool:
    """资源池管理"""
    
    def __init__(self, max_cpu: float = 80.0, max_memory: float = 80.0, max_concurrent: int = 10):
        self.max_cpu = max_cpu
        self.max_memory = max_memory
        self.max_concurrent = max_concurrent
        self.current_tasks = 0
        
    async def check_availability(self) -> bool:
        """检查资源是否可用"""
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        if cpu_percent > self.max_cpu or memory_percent > self.max_memory:
            return False
        
        if self.current_tasks >= self.max_concurrent:
            return False
        
        return True
    
    def acquire(self):
        """获取资源"""
        self.current_tasks += 1
    
    def release(self):
        """释放资源"""
        self.current_tasks = max(0, self.current_tasks - 1)


class IntelligentScheduler:
    """智能调度器"""
    
    def __init__(self):
        self.task_queue = []  # 优先级队列
        self.tasks = {}  # 任务映射
        self.running_tasks = set()  # 运行中的任务ID
        self.completed_tasks = {}  # 已完成任务
        self.failed_tasks = {}  # 失败任务
        self.resource_pool = ResourcePool()
        self.task_lock = asyncio.Lock()
        self.scheduler_running = False
        self.scheduler_task = None
        
        # 事件回调
        self.on_task_start = None
        self.on_task_complete = None
        self.on_task_fail = None
    
    async def add_task(self, 
                      name: str,
                      func: Callable,
                      args: tuple = (),
                      kwargs: dict = None,
                      priority: int = 0,
                      dependencies: List[str] = None,
                      timeout: Optional[int] = None) -> str:
        """添加任务到调度器"""
        task_id = str(uuid.uuid4())
        
        task = Task(
            task_id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            dependencies=dependencies or [],
            timeout=timeout
        )
        
        async with self.task_lock:
            self.tasks[task_id] = task
            # 只有当所有依赖都满足时才添加到队列
            if await self._are_dependencies_satisfied(task_id):
                heapq.heappush(self.task_queue, task)
        
        return task_id
    
    async def _are_dependencies_satisfied(self, task_id: str) -> bool:
        """检查任务的依赖是否都已完成"""
        task = self.tasks[task_id]
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                return False
            dep_task = self.tasks[dep_id]
            if dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    async def _execute_task(self, task: Task):
        """执行单个任务"""
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        
        if self.on_task_start:
            self.on_task_start(task)
        
        try:
            # 获取资源
            self.resource_pool.acquire()
            
            # 执行任务
            if asyncio.iscoroutinefunction(task.func):
                if task.timeout:
                    task.result = await asyncio.wait_for(
                        task.func(*task.args, **task.kwargs), 
                        timeout=task.timeout
                    )
                else:
                    task.result = await task.func(*task.args, **task.kwargs)
            else:
                # 对于同步函数，在线程池中执行
                loop = asyncio.get_event_loop()
                if task.timeout:
                    task.result = await asyncio.wait_for(
                        loop.run_in_executor(None, task.func, *task.args, **task.kwargs),
                        timeout=task.timeout
                    )
                else:
                    task.result = await loop.run_in_executor(None, task.func, *task.args, **task.kwargs)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            
            if self.on_task_complete:
                self.on_task_complete(task)
                
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = time.time()
            
            if self.on_task_fail:
                self.on_task_fail(task)
        
        finally:
            # 释放资源
            self.resource_pool.release()
            
            # 将任务移到相应集合
            async with self.task_lock:
                self.running_tasks.discard(task.task_id)
                if task.status == TaskStatus.COMPLETED:
                    self.completed_tasks[task.task_id] = task
                else:
                    self.failed_tasks[task.task_id] = task
            
            # 检查是否有依赖此任务的其他任务可以加入队列
            await self._check_dependent_tasks(task.task_id)
    
    async def _check_dependent_tasks(self, completed_task_id: str):
        """检查依赖于已完成任务的其他任务"""
        async with self.task_lock:
            for task_id, task in self.tasks.items():
                if task.status == TaskStatus.PENDING and completed_task_id in task.dependencies:
                    # 检查该任务的所有依赖是否都已完成
                    if await self._are_dependencies_satisfied(task_id):
                        heapq.heappush(self.task_queue, task)
    
    async def _scheduler_loop(self):
        """调度器主循环"""
        while self.scheduler_running:
            async with self.task_lock:
                # 检查是否有可运行的任务
                runnable_tasks = []
                remaining_tasks = []
                
                while self.task_queue:
                    task = heapq.heappop(self.task_queue)
                    if task.task_id not in self.running_tasks:
                        # 检查资源可用性
                        if await self.resource_pool.check_availability():
                            runnable_tasks.append(task)
                            self.running_tasks.add(task.task_id)
                        else:
                            remaining_tasks.append(task)
                    else:
                        remaining_tasks.append(task)
                
                # 将未使用的任务放回队列
                for task in remaining_tasks:
                    heapq.heappush(self.task_queue, task)
            
            # 执行可运行的任务
            for task in runnable_tasks:
                asyncio.create_task(self._execute_task(task))
            
            # 等待一段时间再检查
            await asyncio.sleep(0.1)
    
    async def start(self):
        """启动调度器"""
        if not self.scheduler_running:
            self.scheduler_running = True
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
    
    async def stop(self):
        """停止调度器"""
        self.scheduler_running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
    
    async def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        if task_id in self.tasks:
            return self.tasks[task_id].status
        return None
    
    async def get_task_result(self, task_id: str) -> Any:
        """获取任务结果"""
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id].result
        elif task_id in self.failed_tasks:
            raise self.failed_tasks[task_id].error
        else:
            raise ValueError(f"Task {task_id} not completed")
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        async with self.task_lock:
            if task_id in self.tasks and self.tasks[task_id].status == TaskStatus.PENDING:
                task = self.tasks[task_id]
                task.status = TaskStatus.CANCELLED
                return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取调度器统计信息"""
        return {
            'pending_tasks': len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
            'running_tasks': len(self.running_tasks),
            'completed_tasks': len(self.completed_tasks),
            'failed_tasks': len(self.failed_tasks),
            'queue_size': len(self.task_queue),
            'resource_usage': {
                'cpu_percent': self.resource_pool.current_tasks,
                'max_concurrent': self.resource_pool.max_concurrent
            }
        }


class WorkflowScheduler(IntelligentScheduler):
    """工作流调度器 - 扩展智能调度器以支持工作流"""
    
    async def add_workflow(self, workflow_config: Dict[str, Any]) -> str:
        """添加工作流"""
        workflow_id = str(uuid.uuid4())
        
        # 解析工作流配置并创建任务
        tasks = workflow_config.get('tasks', [])
        task_mapping = {}  # 任务名称到ID的映射
        
        for task_config in tasks:
            task_name = task_config['name']
            task_func = task_config['func']  # 实际应该是某种可调用的执行函数
            task_args = task_config.get('args', ())
            task_kwargs = task_config.get('kwargs', {})
            task_priority = task_config.get('priority', 0)
            task_deps = task_config.get('dependencies', [])
            task_timeout = task_config.get('timeout')
            
            # 替换依赖名称为实际的任务ID
            actual_deps = []
            for dep_name in task_deps:
                if dep_name in task_mapping:
                    actual_deps.append(task_mapping[dep_name])
            
            task_id = await self.add_task(
                name=f"{workflow_id}:{task_name}",
                func=task_func,
                args=task_args,
                kwargs=task_kwargs,
                priority=task_priority,
                dependencies=actual_deps,
                timeout=task_timeout
            )
            
            task_mapping[task_name] = task_id
        
        return workflow_id


# 示例用法
async def example_task(name: str, duration: float):
    """示例任务函数"""
    print(f"开始执行任务: {name}")
    await asyncio.sleep(duration)
    print(f"任务完成: {name}")
    return f"Result from {name}"


async def scheduler_example():
    scheduler = IntelligentScheduler()
    
    # 设置回调
    def on_start(task):
        print(f"任务开始: {task.name} (ID: {task.task_id})")
    
    def on_complete(task):
        print(f"任务完成: {task.name}, 结果: {task.result}")
    
    def on_fail(task):
        print(f"任务失败: {task.name}, 错误: {task.error}")
    
    scheduler.on_task_start = on_start
    scheduler.on_task_complete = on_complete
    scheduler.on_task_fail = on_fail
    
    # 启动调度器
    await scheduler.start()
    
    # 添加一些任务
    task1_id = await scheduler.add_task("任务1", example_task, ("任务1", 2), priority=1)
    task2_id = await scheduler.add_task("任务2", example_task, ("任务2", 1), priority=2)
    task3_id = await scheduler.add_task("任务3", example_task, ("任务3", 3), 
                                       dependencies=[task1_id], priority=0)
    
    # 等待一段时间让任务执行
    await asyncio.sleep(10)
    
    # 停止调度器
    await scheduler.stop()
    
    # 输出统计信息
    stats = scheduler.get_statistics()
    print("调度器统计:", stats)


if __name__ == "__main__":
    asyncio.run(scheduler_example())