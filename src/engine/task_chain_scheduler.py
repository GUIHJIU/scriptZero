"""
链式任务调度器
按顺序执行多个脚本-游戏配对，并监控每个任务的执行状态
"""
import asyncio
import time
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from .task_scheduler import TaskScheduler, Task, TaskStatus, TaskPriority


class ChainTaskStatus(Enum):
    """链式任务状态"""
    PENDING = "pending"
    WAITING_DEPENDENCIES = "waiting_dependencies"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ChainTask:
    """链式任务数据类"""
    id: str
    name: str
    game_name: str
    script_name: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    error_handling: str  # continue, stop, retry
    timeout: Optional[int] = None
    enabled: bool = True
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: ChainTaskStatus = ChainTaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[Exception] = None


class TaskChainScheduler:
    """任务链调度器 - 按顺序执行多个脚本-游戏配对"""
    
    def __init__(self, max_concurrent: int = 1):
        # 只允许单个任务运行（按顺序执行）
        self.max_concurrent = max_concurrent
        self.chain_tasks: Dict[str, ChainTask] = {}
        self.completed_chain_tasks: Dict[str, ChainTask] = {}
        self.scheduler = TaskScheduler(max_concurrent=1)
        self._stop_event = asyncio.Event()
        self._running_chain = False
        self._current_task_id: Optional[str] = None
        
        # 回调函数
        self.on_chain_start: Optional[Callable] = None
        self.on_task_start: Optional[Callable] = None
        self.on_task_complete: Optional[Callable] = None
        self.on_task_fail: Optional[Callable] = None
        self.on_chain_complete: Optional[Callable] = None
        self.on_chain_fail: Optional[Callable] = None
    
    async def add_chain_task(self, chain_task: ChainTask) -> str:
        """添加链式任务"""
        self.chain_tasks[chain_task.id] = chain_task
        return chain_task.id
    
    async def execute_chain(self, task_ids: List[str], error_handling: str = "continue"):
        """执行任务链"""
        if self._running_chain:
            raise RuntimeError("链已在运行中")
        
        self._running_chain = True
        print(f"开始执行任务链，共 {len(task_ids)} 个任务")
        
        if self.on_chain_start:
            self.on_chain_start()
        
        try:
            for task_id in task_ids:
                if self._stop_event.is_set():
                    print("链执行被停止")
                    break
                
                chain_task = self.chain_tasks.get(task_id)
                if not chain_task or not chain_task.enabled:
                    continue
                
                print(f"执行任务: {chain_task.name}")
                
                # 检查依赖是否满足
                if not await self._check_dependencies_satisfied(chain_task):
                    print(f"任务 {chain_task.name} 的依赖未满足，跳过")
                    chain_task.status = ChainTaskStatus.SKIPPED
                    continue
                
                # 执行单个任务
                success = await self._execute_single_chain_task(chain_task, error_handling)
                
                # 根据错误处理策略决定是否继续
                if not success and error_handling == "stop":
                    print(f"任务 {chain_task.name} 失败，停止执行链")
                    if self.on_chain_fail:
                        self.on_chain_fail(chain_task)
                    break
                
                # 检查是否有依赖此任务的其他任务可以运行
                await self._check_dependent_tasks(task_id)
        
        finally:
            self._running_chain = False
            if self.on_chain_complete:
                self.on_chain_complete()
    
    async def _check_dependencies_satisfied(self, chain_task: ChainTask) -> bool:
        """检查任务的依赖是否满足"""
        for dep_id in chain_task.dependencies:
            dep_task = self.completed_chain_tasks.get(dep_id)
            if not dep_task or dep_task.status != ChainTaskStatus.COMPLETED:
                return False
        return True
    
    async def _execute_single_chain_task(self, chain_task: ChainTask, error_handling: str) -> bool:
        """执行单个链式任务"""
        chain_task.status = ChainTaskStatus.RUNNING
        chain_task.started_at = time.time()
        self._current_task_id = chain_task.id
        
        if self.on_task_start:
            self.on_task_start(chain_task)
        
        try:
            # 根据游戏和脚本名称执行对应的自动化任务
            result = await self._execute_game_script_pair(
                chain_task.game_name,
                chain_task.script_name,
                chain_task.parameters
            )
            
            chain_task.result = result
            chain_task.status = ChainTaskStatus.COMPLETED
            chain_task.completed_at = time.time()
            
            # 将完成的任务移动到完成列表
            self.completed_chain_tasks[chain_task.id] = chain_task
            del self.chain_tasks[chain_task.id]
            
            if self.on_task_complete:
                self.on_task_complete(chain_task)
            
            return True
            
        except Exception as e:
            chain_task.error = e
            chain_task.status = ChainTaskStatus.FAILED
            chain_task.completed_at = time.time()
            
            print(f"任务 {chain_task.name} 执行失败: {str(e)}")
            
            if self.on_task_fail:
                self.on_task_fail(chain_task)
            
            return False
    
    async def _execute_game_script_pair(self, game_name: str, script_name: str, parameters: Dict[str, Any]):
        """执行游戏-脚本对"""
        from .executor.async_executor import AsyncScriptExecutor
        from ..adapters.game_adapters.genshin_bettergi import ConfigurableGenshinBetterGIAdapter
        
        # 获取游戏和脚本配置
        # 为了实现这个功能，我们需要从外部传入配置信息
        # 这里我们暂时使用模拟实现
        print(f"执行游戏-脚本对: {game_name} - {script_name}")
        
        # 根据游戏类型创建相应的适配器
        if game_name.lower() in ["genshin", "原神", "genshin impact", "yuanshen"]:
            # 使用原神适配器
            adapter_config = parameters.copy()
            adapter_config['game_name'] = game_name
            adapter = ConfigurableGenshinBetterGIAdapter(adapter_config)
            # 这里需要适配器的实际方法，我们使用模拟
            print(f"启动原神BetterGI适配器，参数: {parameters}")
            await asyncio.sleep(2)  # 模拟执行时间
            result = {"status": "success", "game": game_name, "script": script_name}
        else:
            # 使用通用脚本执行器
            print(f"执行脚本: {script_name}，参数: {parameters}")
            await asyncio.sleep(2)  # 模拟执行时间
            result = {"status": "success", "game": game_name, "script": script_name}
        
        return result
    
    async def _check_dependent_tasks(self, completed_task_id: str):
        """检查是否有依赖于已完成任务的其他任务"""
        for task_id, task in self.chain_tasks.items():
            if completed_task_id in task.dependencies:
                # 检查所有依赖是否都已完成
                all_deps_completed = all(
                    dep_id in self.completed_chain_tasks and 
                    self.completed_chain_tasks[dep_id].status == ChainTaskStatus.COMPLETED
                    for dep_id in task.dependencies
                )
                
                if all_deps_completed:
                    # 依赖已满足，可以准备执行此任务
                    task.status = ChainTaskStatus.READY
                    print(f"任务 {task.name} 的依赖已满足，状态变为就绪")
    
    async def stop_chain(self):
        """停止链式执行"""
        self._stop_event.set()
        await self.scheduler.stop()
    
    def get_chain_status(self) -> Dict[str, Any]:
        """获取链的整体状态"""
        total_tasks = len(self.chain_tasks) + len(self.completed_chain_tasks)
        completed_tasks = len(self.completed_chain_tasks)
        running_tasks = sum(1 for task in self.chain_tasks.values() 
                          if task.status == ChainTaskStatus.RUNNING)
        failed_tasks = sum(1 for task in self.chain_tasks.values() 
                         if task.status == ChainTaskStatus.FAILED)
        skipped_tasks = sum(1 for task in self.chain_tasks.values() 
                          if task.status == ChainTaskStatus.SKIPPED)
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'running_tasks': running_tasks,
            'failed_tasks': failed_tasks,
            'skipped_tasks': skipped_tasks,
            'pending_tasks': len(self.chain_tasks) - running_tasks - failed_tasks - skipped_tasks,
            'progress': completed_tasks / total_tasks if total_tasks > 0 else 0
        }

    def get_current_task(self) -> Optional[ChainTask]:
        """获取当前正在执行的任务"""
        if self._current_task_id:
            return self.chain_tasks.get(self._current_task_id) or self.completed_chain_tasks.get(self._current_task_id)
        return None