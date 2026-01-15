"""
异步调度器
实现高效的异步任务调度和管理
"""
import asyncio
import time
from typing import Dict, Any, List, Optional, Callable, Awaitable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """任务数据类"""
    id: str
    coroutine: Callable[[], Awaitable[Any]]
    priority: int = 0
    created_at: float = 0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[Exception] = None
    dependencies: List[str] = None  # 依赖的任务ID列表

    def __post_init__(self):
        if self.created_at == 0:
            self.created_at = time.time()
        if self.dependencies is None:
            self.dependencies = []


class AsyncScheduler:
    """异步调度器"""
    
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.task_queue = asyncio.PriorityQueue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self._stop_event = asyncio.Event()
        self._scheduler_task = None
        
    async def submit_task(self, task: Task) -> str:
        """提交任务到调度队列"""
        # 将任务放入优先级队列 (优先级, 任务ID, 任务对象)
        await self.task_queue.put((-task.priority, task.id, task))
        return task.id
    
    async def schedule_task(self, coro: Callable[[], Awaitable[Any]], 
                           task_id: str = None, priority: int = 0,
                           dependencies: List[str] = None) -> str:
        """调度一个协程任务"""
        if task_id is None:
            task_id = f"task_{int(time.time() * 1000000)}"
        
        task_obj = Task(
            id=task_id,
            coroutine=coro,
            priority=priority,
            dependencies=dependencies or []
        )
        
        return await self.submit_task(task_obj)
    
    async def run_scheduler(self):
        """运行调度器主循环"""
        while not self._stop_event.is_set():
            try:
                # 检查是否有可运行的任务
                await self._process_ready_tasks()
                
                # 等待一段时间或直到停止事件被设置
                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(), 
                        timeout=0.1  # 100ms检查间隔
                    )
                    break
                except asyncio.TimeoutError:
                    continue
            except Exception as e:
                print(f"Scheduler error: {e}")
                await asyncio.sleep(0.1)
    
    async def _process_ready_tasks(self):
        """处理准备好运行的任务"""
        # 检查队列中的任务
        pending_items = []
        queue_size = self.task_queue.qsize()
        
        for _ in range(queue_size):
            try:
                priority, task_id, task = self.task_queue.get_nowait()
                pending_items.append((priority, task_id, task))
            except asyncio.QueueEmpty:
                break
        
        # 重新评估哪些任务可以运行
        for priority, task_id, task in pending_items:
            if await self._can_run_task(task):
                await self._start_task(task)
            else:
                # 如果不能运行，放回队列
                await self.task_queue.put((priority, task_id, task))
    
    async def _can_run_task(self, task: Task) -> bool:
        """检查任务是否可以运行（依赖是否满足）"""
        # 检查依赖
        for dep_id in task.dependencies:
            dep_task = self.completed_tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        
        # 检查是否已经在运行
        if task.id in self.running_tasks:
            return False
        
        # 检查并发限制
        if len(self.running_tasks) >= self.max_concurrent:
            return False
        
        return True
    
    async def _start_task(self, task: Task):
        """启动任务"""
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        
        # 创建异步任务
        async_task = asyncio.create_task(self._execute_task(task))
        self.running_tasks[task.id] = async_task
        
        # 附加完成回调
        async_task.add_done_callback(lambda t: self._on_task_complete(task.id))
    
    async def _execute_task(self, task: Task):
        """执行任务"""
        try:
            result = await task.coroutine()
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
        except Exception as e:
            task.error = e
            task.status = TaskStatus.FAILED
            task.completed_at = time.time()
            print(f"Task {task.id} failed: {e}")
    
    def _on_task_complete(self, task_id: str):
        """任务完成回调"""
        if task_id in self.running_tasks:
            del self.running_tasks[task_id]
        
        # 移动到完成任务列表
        # 注意：这里需要从队列中获取完整的task对象
        # 实际实现中可能需要不同的机制来追踪任务状态
    
    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """等待特定任务完成"""
        # 如果任务正在运行，等待其完成
        if task_id in self.running_tasks:
            try:
                await asyncio.wait_for(self.running_tasks[task_id], timeout=timeout)
            except asyncio.TimeoutError:
                raise TimeoutError(f"Task {task_id} timed out")
        
        # 返回任务结果
        completed_task = self.completed_tasks.get(task_id)
        if not completed_task:
            raise ValueError(f"Task {task_id} not found in completed tasks")
        
        if completed_task.status == TaskStatus.FAILED:
            raise completed_task.error
        
        return completed_task.result
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            return True
        return False
    
    async def start(self):
        """启动调度器"""
        if self._scheduler_task is None:
            self._scheduler_task = asyncio.create_task(self.run_scheduler())
    
    async def stop(self):
        """停止调度器"""
        self._stop_event.set()
        if self._scheduler_task:
            await self._scheduler_task
        self.executor.shutdown(wait=True)


class EfficientExecutor:
    """高效的异步执行器 - 根据改进建议实现进程池和协程池"""
    
    def __init__(self, max_processes: int = 4, max_coroutines: int = 10):
        from concurrent.futures import ProcessPoolExecutor
        self.process_pool = ProcessPoolExecutor(max_workers=max_processes)
        self.coroutine_semaphore = asyncio.Semaphore(max_coroutines)  # 限制并发协程数
        self.scheduler = AsyncScheduler(max_concurrent=max_coroutines)
    
    async def execute_many(self, tasks_config: List[Dict[str, Any]]):
        """批量执行多个任务"""
        async with self.coroutine_semaphore:
            tasks = []
            for task_config in tasks_config:
                if task_config.get('type') == "cpu_intensive":
                    # CPU密集型任务使用进程池
                    task = asyncio.create_task(self._run_cpu_intensive(task_config))
                else:
                    # I/O密集型任务使用协程
                    task = asyncio.create_task(self._run_io_intensive(task_config))
                
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
    
    async def _run_cpu_intensive(self, config: Dict[str, Any]):
        """运行CPU密集型任务"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.process_pool, 
            self._execute_cpu_task_sync, 
            config
        )
    
    def _execute_cpu_task_sync(self, config: Dict[str, Any]):
        """同步执行CPU密集型任务"""
        # 这里执行实际的CPU密集型工作
        import subprocess
        import sys
        
        script_path = config.get('path')
        args = config.get('arguments', [])
        
        result = subprocess.run([sys.executable, script_path] + args, 
                               capture_output=True, text=True)
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    
    async def _run_io_intensive(self, config: Dict[str, Any]):
        """运行I/O密集型任务"""
        # 使用调度器来管理I/O密集型任务
        async with self.coroutine_semaphore:
            # 这里执行实际的I/O密集型工作
            import subprocess
            import sys
            
            script_path = config.get('path')
            args = config.get('arguments', [])
            
            process = await asyncio.create_subprocess_exec(
                sys.executable, script_path, *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            return {
                'returncode': process.returncode,
                'stdout': stdout.decode(),
                'stderr': stderr.decode()
            }
    
    async def close(self):
        """关闭执行器"""
        await self.scheduler.stop()
        self.process_pool.shutdown(wait=True)


# 使用示例
async def example_usage():
    executor = EfficientExecutor()
    
    # 示例任务配置
    tasks = [
        {'type': 'io_intensive', 'path': 'script1.py', 'arguments': ['arg1']},
        {'type': 'cpu_intensive', 'path': 'script2.py', 'arguments': ['arg2']},
    ]
    
    try:
        results = await executor.execute_many(tasks)
        print("Results:", results)
    finally:
        await executor.close()


if __name__ == "__main__":
    asyncio.run(example_usage())