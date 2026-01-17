"""
ScriptZero - 零适配游戏自动化框架主类
协调各个模块的工作
"""
import asyncio
import time
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path

import pyautogui
import pydirectinput

from .utils.config_validator import load_and_validate_config, MainConfig


class GameAutomationFramework:
    """游戏自动化框架主类"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config: Optional[MainConfig] = None
        
        # 用于GUI的回调函数
        self.log_callback: Optional[Callable[[str], None]] = None
        self.progress_callback: Optional[Callable[[int, str], None]] = None
        self.status_callback: Optional[Callable[[str], None]] = None
        
        # 设置pyautogui参数
        pyautogui.FAILSAFE = True  # 移动到角落会抛出异常
        pyautogui.PAUSE = 0.1      # 每次操作后暂停
        
        # 初始化调度器
        self._init_scheduler()
        
        # 加载并验证配置
        if config_path and Path(config_path).exists():
            self.load_and_validate_config(config_path)
    
    def _init_scheduler(self):
        """初始化调度器"""
        try:
            from .engine.scheduler.async_scheduler import AsyncScheduler
            self.scheduler = AsyncScheduler()
        except ImportError:
            # 如果调度器不可用，使用简单的执行方式
            self.scheduler = None
            print("警告: 调度器模块不可用，将使用简单执行模式")
    
    def load_and_validate_config(self, config_path: str):
        """加载并验证配置文件"""
        self.config = load_and_validate_config(config_path)
        print(f"配置验证成功: {self.config.name}")
    
    async def execute_workflow(self, workflow_name: Optional[str] = None):
        """执行工作流"""
        if not self.config:
            raise ValueError("配置未加载")
        
        workflows = self.config.workflow
        
        if workflow_name:
            # 找到特定的工作流
            target_workflow = None
            for wf in workflows:
                if wf.name == workflow_name:
                    target_workflow = wf
                    break
            if target_workflow:
                workflows = [target_workflow]
            else:
                raise ValueError(f"Workflow '{workflow_name}' not found")
        
        for workflow in workflows:
            if workflow.enabled:  # 只执行启用的工作流
                await self.execute_single_workflow(workflow)
    
    async def execute_single_workflow(self, workflow):
        """执行单个工作流"""
        workflow_type = workflow.type
        workflow_name = workflow.name
        
        print(f"开始执行工作流: {workflow_name}")
        
        if workflow_type == 'game':
            await self.execute_game_workflow(workflow)
        elif workflow_type == 'script_chain':
            await self.execute_script_chain(workflow)
        elif workflow_type == 'adapter_sequence':
            await self.execute_adapter_sequence(workflow)
        elif workflow_type == 'scheduled':
            await self.execute_scheduled_workflow(workflow)
        elif workflow_type == 'genshin_bettergi':
            await self.execute_genshin_bettergi_workflow(workflow)
        elif workflow_type == 'task_chain':
            await self.execute_task_chain(workflow)
        else:
            print(f"未知工作流类型: {workflow_type}")
    
    async def execute_genshin_bettergi_workflow(self, workflow):
        """执行原神与BetterGI适配器工作流"""
        print("执行原神与BetterGI适配器工作流...")
        
        # 导入适配器
        try:
            from ..genshin_bettergi_adapter import ConfigurableGenshinBetterGIAdapter
        except ImportError:
            print("错误: 无法导入GenshinBetterGI适配器，请确保genshin_bettergi_adapter.py文件存在")
            return
        
        # 从配置中获取参数
        config = workflow.config
        
        # 创建适配器实例
        adapter = ConfigurableGenshinBetterGIAdapter(config)
        
        # 执行自动化流程
        success = await adapter.run_automation()
        
        if success:
            print("原神与BetterGI自动化流程执行成功")
        else:
            print("原神与BetterGI自动化流程执行失败")

    async def execute_task_chain(self, workflow):
        """执行任务链"""
        print("执行任务链...")
        
        # 创建链式调度器
        from .engine.task_chain_scheduler import TaskChainScheduler, ChainTask, ChainTaskStatus
        import uuid
        
        chain_scheduler = TaskChainScheduler()
        
        # 设置回调
        def on_task_start(task):
            print(f"任务开始: {task.name}")
        
        def on_task_complete(task):
            print(f"任务完成: {task.name}, 结果: {task.result}")
        
        def on_task_fail(task):
            print(f"任务失败: {task.name}, 错误: {task.error}")
        
        chain_scheduler.on_task_start = on_task_start
        chain_scheduler.on_task_complete = on_task_complete
        chain_scheduler.on_task_fail = on_task_fail
        
        # 从工作流配置中获取任务列表
        tasks_config = workflow.config.get('tasks', [])
        task_ids = []
        
        for task_config in tasks_config:
            if not task_config.get('enabled', True):
                continue
                
            chain_task = ChainTask(
                id=task_config.get('id', f'task_{uuid.uuid4().hex[:8]}'),
                name=task_config.get('name', f'task_{len(task_ids)}'),
                game_name=task_config['game'],
                script_name=task_config['script'],
                parameters=task_config.get('parameters', {}),
                dependencies=task_config.get('dependencies', []),
                error_handling=workflow.config.get('error_handling', 'continue'),
                timeout=task_config.get('timeout'),
                enabled=task_config.get('enabled', True),
                status=ChainTaskStatus.PENDING
            )
            
            task_id = await chain_scheduler.add_chain_task(chain_task)
            task_ids.append(task_id)
        
        # 执行任务链
        await chain_scheduler.execute_chain(task_ids, workflow.config.get('error_handling', 'continue'))
    
    async def execute_scheduled_workflow(self, workflow):
        """执行计划工作流（使用调度器）"""
        if not self.scheduler:
            print("调度器不可用，回退到普通执行模式")
            await self.execute_script_chain(workflow)
            return
        
        print("使用调度器执行计划工作流...")
        
        # 启动调度器
        await self.scheduler.start()
        
        try:
            # 添加工作流中的任务到调度器
            # 从workflow.config中获取任务配置
            tasks = workflow.config.get('tasks', [])
            task_ids = []
            
            for i, task_config in enumerate(tasks):
                task_name = task_config.get('name', f'Task-{i}')
                task_func = self._get_task_function(task_config)
                task_args = task_config.get('args', ())
                task_kwargs = task_config.get('kwargs', {})
                task_priority = task_config.get('priority', 0)
                task_deps = task_config.get('dependencies', [])
                task_timeout = task_config.get('timeout')
                
                # 将依赖名称转换为实际任务ID（这里简化处理）
                actual_deps = []
                
                task_id = await self.scheduler.schedule_task(
                    lambda: task_func(*task_args, **task_kwargs),
                    task_id=f"{workflow_name}_{task_name}",
                    priority=task_priority,
                    dependencies=actual_deps
                )
                task_ids.append(task_id)
            
            # 等待所有任务完成
            await asyncio.sleep(len(tasks) * 2)  # 简单等待，实际应用中需要更好的机制
            
        finally:
            await self.scheduler.stop()
    
    def _get_task_function(self, task_config: Dict[str, Any]):
        """获取任务函数"""
        task_type = task_config.get('type', 'script')
        
        if task_type == 'script':
            return self._execute_script_task
        elif task_type == 'automation':
            return self._execute_automation_task
        elif task_type == 'game_action':
            return self._execute_game_action_task
        else:
            return self._execute_generic_task
    
    async def _execute_script_task(self, script_config: Dict[str, Any]):
        """执行脚本任务"""
        from .engine.executor.async_executor import AsyncScriptExecutor
        executor = AsyncScriptExecutor()
        return await executor.execute_script(script_config)
    
    async def _execute_automation_task(self, action_config: Dict[str, Any]):
        """执行自动化任务"""
        return await self.execute_automation_action(action_config)
    
    async def _execute_game_action_task(self, action_config: Dict[str, Any]):
        """执行游戏操作任务"""
        return await self.execute_game_action(action_config)
    
    async def _execute_generic_task(self, task_config: Dict[str, Any]):
        """执行通用任务"""
        # 根据配置执行相应的操作
        return {"status": "completed", "config": task_config}
    
    async def execute_game_workflow(self, workflow):
        """执行游戏相关工作流"""
        if not self.config:
            raise ValueError("配置未加载")
        
        game_name = workflow.config.get('game')
        if not game_name:
            print("错误: 游戏工作流缺少游戏名称")
            return
        
        game_config = self.config.games.get(game_name)
        if not game_config:
            print(f"错误: 未找到游戏配置: {game_name}")
            return
        
        actions = workflow.config.get('actions', [])
        for action in actions:
            action_type = action.get('type')
            
            if action_type == 'launch':
                await self.launch_game(game_config.dict())
            elif action_type == 'wait_for':
                condition = action.get('condition')
                timeout = action.get('timeout', 60)
                await self.wait_for_condition(condition, timeout)
            elif action_type == 'input':
                sequence = action.get('sequence', [])
                await self.execute_input_sequence(sequence)
            elif action_type in ['click', 'double_click', 'right_click', 'move_to', 'drag_to', 
                                'key_press', 'key_hold', 'type_text', 'wait_for_image', 'find_and_click']:
                # 直接执行自动化操作
                await self.execute_automation_action(action)
            else:
                print(f"未知动作类型: {action_type}")
    
    async def execute_script_chain(self, workflow):
        """执行脚本链"""
        if not self.config:
            raise ValueError("配置未加载")
        
        repeat = workflow.config.get('repeat')
        # 从scripts属性获取脚本列表（使用Pydantic模型的字段）
        scripts = [script.dict() for script in self.config.scripts]
        actions = workflow.config.get('actions', [])  # 添加对直接操作的支持
        
        # 如果有重复设置，处理重复逻辑
        if repeat == 'daily':
            # 简单的日重复逻辑
            print("按每日重复执行脚本链")
        elif repeat == 'hourly':
            print("按每小时重复执行脚本链")
        
        # 执行直接操作
        for action in actions:
            action_type = action.get('type')
            if action_type in ['click', 'double_click', 'right_click', 'move_to', 'drag_to', 
                              'key_press', 'key_hold', 'type_text', 'wait_for_image', 'find_and_click']:
                await self.execute_automation_action(action)
        
        # 执行脚本
        await self.execute_scripts_sequentially(scripts)
    
    async def execute_adapter_sequence(self, workflow):
        """执行适配器序列 - 包含启动游戏、启动脚本框架、执行自动化操作"""
        print("执行适配器序列...")
        
        # 1. 启动脚本框架（如果指定）
        script_framework_config = workflow.config.get('script_framework')
        if script_framework_config:
            await self.launch_script_framework(script_framework_config)
        
        # 2. 启动游戏（如果指定）
        game_config_name = workflow.config.get('game_config')
        if game_config_name and self.config:
            game_config = self.config.games.get(game_config_name)
            if game_config:
                await self.launch_game(game_config.dict())
        
        # 3. 执行自动化步骤
        automation_steps = workflow.config.get('automation_steps', [])
        for step in automation_steps:
            await self.execute_automation_step(step)
    
    async def launch_script_framework(self, config: Dict[str, Any]):
        """启动脚本框架"""
        import subprocess
        import sys
        
        script_path = config.get('path')
        if not script_path or not Path(script_path).exists():
            print(f"错误: 脚本框架路径不存在: {script_path}")
            return False
        
        try:
            # 启动脚本框架进程
            args = [sys.executable, script_path] + config.get('arguments', [])
            process = subprocess.Popen(args)
            
            startup_wait = config.get('startup_wait', 5)
            print(f"等待脚本框架启动 ({startup_wait}秒)...")
            await asyncio.sleep(startup_wait)
            
            print("脚本框架已启动")
            return process
        except Exception as e:
            print(f"启动脚本框架失败: {e}")
            return None
    
    async def execute_automation_step(self, step: Dict[str, Any]):
        """执行单个自动化步骤"""
        step_type = step.get('type', 'click')
        delay = step.get('delay', 1.0)
        
        print(f"执行自动化步骤: {step_type}")
        
        if step_type == 'click':
            # 尝试通过图像识别找到目标并点击
            template_key = step.get('template')
            if self.config:
                templates = self.config.dict().get('image_templates', {})
            else:
                templates = {}
            if template_key and template_key in templates:
                template_path = templates[template_key]
                if Path(template_path).exists():
                    await self.find_and_click_image(template_path)
                else:
                    print(f"模板文件不存在: {template_path}")
                    # 如果找不到图像，则使用坐标点击
                    x = step.get('x')
                    y = step.get('y')
                    if x is not None and y is not None:
                        pyautogui.click(x, y)
            else:
                # 直接使用坐标点击
                x = step.get('x')
                y = step.get('y')
                if x is not None and y is not None:
                    pyautogui.click(x, y)
                    
        elif step_type == 'double_click':
            x = step.get('x')
            y = step.get('y')
            if x is not None and y is not None:
                pyautogui.doubleClick(x, y)
                
        elif step_type == 'right_click':
            x = step.get('x')
            y = step.get('y')
            if x is not None and y is not None:
                pyautogui.rightClick(x, y)
                
        elif step_type == 'type_text':
            text = step.get('text', '')
            interval = step.get('interval', 0.0)
            pydirectinput.typewrite(text, interval=interval)
            
        elif step_type == 'key_press':
            key = step.get('key')
            if key:
                pydirectinput.press(key)
                
        elif step_type == 'wait':
            wait_time = step.get('seconds', 1.0)
            print(f"等待 {wait_time} 秒")
            await asyncio.sleep(wait_time)
        
        # 步骤间延迟
        if delay > 0:
            await asyncio.sleep(delay)
    
    async def find_and_click_image(self, template_path: str, confidence: float = 0.8):
        """查找图像并点击 - 增强版支持多种匹配方法"""
        try:
            print(f"正在查找图像: {template_path}")
            
            # 首先尝试使用pyautogui的locateOnScreen
            location = pyautogui.locateOnScreen(template_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                pyautogui.click(center)
                print(f"已点击图像位置: {center}")
                return True
            else:
                print(f"未找到图像: {template_path}")
                return False
        except Exception as e:
            print(f"图像识别失败: {e}")
            return False
    
    async def execute_scripts_sequentially(self, scripts: List[Dict[str, Any]]):
        """顺序执行脚本列表"""
        from .engine.executor.async_executor import AsyncScriptExecutor
        executor = AsyncScriptExecutor()
        
        for script_config in scripts:
            # 检查执行条件
            conditions = script_config.get('conditions')
            if conditions:
                if not await self.check_conditions(conditions):
                    print(f"跳过脚本 {script_config.get('path')}，条件不满足")
                    continue
            
            # 执行脚本
            process = await executor.execute_script(script_config)
            
            # 等待完成或检查完成条件
            completion_conditions = script_config.get('completion')
            if completion_conditions:
                await self.wait_for_completion_with_conditions(process, completion_conditions)
            else:
                # 默认等待进程结束
                await executor.wait_for_completion(process)
    
    async def launch_game(self, game_config: Dict[str, Any]):
        """启动游戏"""
        from .engine.executor.async_executor import AsyncScriptExecutor
        executor = AsyncScriptExecutor()
        
        executable = game_config.get('executable')
        arguments = game_config.get('arguments', [])
        
        script_config = {
            'path': executable,
            'arguments': arguments,
            'env_vars': {},
            'name': f"game_{game_config.get('name', 'unknown')}"
        }
        
        print(f"启动游戏: {executable}")
        process = await executor.execute_script(script_config)
        
        # 使用状态管理器记录游戏进程信息
        from .core.state_manager import StateManager
        state_manager = StateManager()
        await state_manager.update_state('current_game_process', {
            'pid': process.pid,
            'executable': executable,
            'started_at': time.time()
        })
    
    async def wait_for_condition(self, condition: str, timeout: int):
        """等待特定条件"""
        if condition == 'window_active':
            # 等待游戏窗口激活
            if not self.config:
                print("配置未加载，无法等待窗口激活")
                return
            
            game_name = self.get_current_game_name()
            game_config = self.config.games.get(game_name)
            if not game_config:
                print(f"未找到游戏配置: {game_name}")
                return
                
            window_title = game_config.window_title
            
            from .engine.monitoring import MonitoringService
            monitor_service = MonitoringService()
            conditions = [{
                'type': 'window',
                'config': {
                    'title': window_title,
                    'expected_state': 'active'
                }
            }]
            
            result = await monitor_service.start_monitoring('window_active_check', conditions, timeout=timeout)
            if result:
                print("窗口激活条件满足")
            else:
                print(f"等待窗口激活超时({timeout}秒)")
    
    def get_current_game_name(self) -> str:
        """获取当前游戏名称（简单实现）"""
        if not self.config:
            return 'unknown'
        games = self.config.games
        if games:
            return list(games.keys())[0]  # 返回第一个游戏名称
        return 'unknown'
    
    async def execute_input_sequence(self, sequence: List[Dict[str, Any]]):
        """执行输入序列"""
        for item in sequence:
            delay = item.get('delay', 0.1)
            
            if 'key' in item:
                key = item['key']
                pydirectinput.press(key)
            elif 'text' in item:
                text = item['text']
                pydirectinput.typewrite(text)
            elif 'click' in item:
                x = item.get('x')
                y = item.get('y')
                button = item.get('button', 'left')
                if x is not None and y is not None:
                    pyautogui.click(x, y, button=button)
            elif 'move_to' in item:
                x = item.get('x')
                y = item.get('y')
                if x is not None and y is not None:
                    pyautogui.moveTo(x, y)
            elif 'scroll' in item:
                clicks = item.get('clicks', 1)
                pyautogui.scroll(clicks)
            
            await asyncio.sleep(delay)

    async def execute_automation_action(self, action_config: Dict[str, Any]):
        """执行自动化操作"""
        action_type = action_config.get('type')
        
        if action_type == 'click':
            x = action_config.get('x')
            y = action_config.get('y')
            button = action_config.get('button', 'left')
            duration = action_config.get('duration', 0.0)
            
            if x is not None and y is not None:
                pyautogui.click(x, y, button=button, duration=duration)
                
        elif action_type == 'double_click':
            x = action_config.get('x')
            y = action_config.get('y')
            button = action_config.get('button', 'left')
            
            if x is not None and y is not None:
                pyautogui.doubleClick(x, y, button=button)
                
        elif action_type == 'right_click':
            x = action_config.get('x')
            y = action_config.get('y')
            
            if x is not None and y is not None:
                pyautogui.rightClick(x, y)
                
        elif action_type == 'move_to':
            x = action_config.get('x')
            y = action_config.get('y')
            duration = action_config.get('duration', 0.5)
            
            if x is not None and y is not None:
                pyautogui.moveTo(x, y, duration=duration)
                
        elif action_type == 'drag_to':
            x = action_config.get('x')
            y = action_config.get('y')
            duration = action_config.get('duration', 0.5)
            
            if x is not None and y is not None:
                pyautogui.dragTo(x, y, duration=duration)
                
        elif action_type == 'key_press':
            key = action_config.get('key')
            presses = action_config.get('presses', 1)
            interval = action_config.get('interval', 0.0)
            
            if key:
                pydirectinput.press(key, presses=presses, interval=interval)
                
        elif action_type == 'key_hold':
            key = action_config.get('key')
            duration = action_config.get('duration', 1.0)
            
            if key:
                pydirectinput.keyDown(key)
                await asyncio.sleep(duration)
                pydirectinput.keyUp(key)
                
        elif action_type == 'type_text':
            text = action_config.get('text', '')
            interval = action_config.get('interval', 0.0)
            
            pydirectinput.typewrite(text, interval=interval)
            
        elif action_type == 'wait_for_image':
            template = action_config.get('template')
            timeout = action_config.get('timeout', 30)
            threshold = action_config.get('threshold', 0.8)
            
            if template:
                # 等待图像出现
                start_time = time.time()
                while time.time() - start_time < timeout:
                    try:
                        location = pyautogui.locateOnScreen(template, confidence=threshold)
                        if location:
                            return True
                    except:
                        pass
                    await asyncio.sleep(0.5)
                return False
                
        elif action_type == 'find_and_click':
            template = action_config.get('template')
            threshold = action_config.get('threshold', 0.8)
            
            if template:
                try:
                    location = pyautogui.locateOnScreen(template, confidence=threshold)
                    if location:
                        center = pyautogui.center(location)
                        pyautogui.click(center)
                        return True
                except:
                    pass
                return False
        
        # 默认延迟
        await asyncio.sleep(action_config.get('delay', 0.1))
        return True
    
    async def execute_game_action(self, action_config: Dict[str, Any]):
        """执行游戏特定操作"""
        action_type = action_config.get('type')
        
        if action_type == 'launch_game':
            game_name = action_config.get('game')
            if game_name and self.config:
                game_config = self.config.games.get(game_name)
                if game_config:
                    await self.launch_game(game_config.dict())
        elif action_type == 'send_keys':
            keys = action_config.get('keys', '')
            pydirectinput.typewrite(keys)
        elif action_type == 'press_key_combination':
            keys = action_config.get('keys', [])
            if keys:
                pydirectinput.hotkey(*keys)
        else:
            # 默认行为：执行通用自动化操作
            await self.execute_automation_action(action_config)
    
    async def check_conditions(self, conditions: Dict[str, Any]) -> bool:
        """检查条件"""
        # 检查 all_of 条件（所有条件必须满足）
        all_conditions = conditions.get('all_of', [])
        for condition in all_conditions:
            if not await self.evaluate_single_condition(condition):
                return False
        
        # 检查 any_of 条件（任一条件满足即可）
        any_conditions = conditions.get('any_of', [])
        if any_conditions:
            for condition in any_conditions:
                if await self.evaluate_single_condition(condition):
                    break
            else:
                # 如果没有任何条件满足
                return False
        
        return True
    
    async def evaluate_single_condition(self, condition: Dict[str, Any]) -> bool:
        """评估单个条件"""
        condition_type = condition.get('type')
        
        if condition_type == 'resource_check':
            cpu_max = condition.get('cpu_max')
            memory_max = condition.get('memory_max')
            
            import psutil
            checks = {}
            if cpu_max is not None:
                if psutil.cpu_percent(interval=1) > cpu_max:
                    return False
            if memory_max is not None:
                if psutil.virtual_memory().percent > memory_max:
                    return False
        
        elif condition_type == 'time_window':
            import time
            start_time = condition.get('start')
            end_time = condition.get('end')
            
            # 简单的时间窗口检查
            current_hour = time.strftime('%H:%M')
            return start_time <= current_hour <= end_time
        
        elif condition_type == 'process_running':
            import psutil
            process_name = condition.get('process_name')
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == process_name:
                    return True
            return False
        
        elif condition_type == 'window_exists':
            import pygetwindow as gw
            window_title = condition.get('window_title')
            windows = gw.getWindowsWithTitle(window_title)
            return len(windows) > 0
        
        return True  # 默认返回True，表示条件满足
    
    async def wait_for_completion_with_conditions(self, process, completion_conditions: Dict[str, Any]):
        """等待进程完成或满足完成条件"""
        from .engine.executor.async_executor import AsyncScriptExecutor
        executor = AsyncScriptExecutor()
        
        # 检查 any_of 完成条件
        any_conditions = completion_conditions.get('any_of', [])
        
        # 创建一个任务来监视进程
        process_task = asyncio.create_task(executor.wait_for_completion(process))
        
        # 创建任务来监视完成条件
        condition_tasks = []
        for condition in any_conditions:
            condition_type = condition.get('type')
            
            if condition_type == 'timeout':
                seconds = condition.get('seconds', 60)
                timeout_task = asyncio.create_task(asyncio.sleep(seconds))
                condition_tasks.append(timeout_task)
            elif condition_type == 'image_detected':
                template = condition.get('template')
                from .engine.monitoring import MonitoringService
                monitor_service = MonitoringService()
                # 创建一个模拟的监控任务
                async def image_monitor_task():
                    # 这里需要实际的图像监控实现
                    start_time = time.time()
                    timeout = condition.get('timeout', 3600)
                    while time.time() - start_time < timeout:
                        # 模拟图像检测
                        await asyncio.sleep(1)
                    return False
                    
                image_task = asyncio.create_task(image_monitor_task())
                condition_tasks.append(image_task)
        
        # 等待任一条件满足
        done, pending = await asyncio.wait(
            [process_task] + condition_tasks,
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # 取消未完成的任务
        for task in pending:
            task.cancel()
        
        print("完成条件满足或进程结束")
    
    def set_callbacks(self, log_callback: Optional[Callable[[str], None]] = None,
                     progress_callback: Optional[Callable[[int, str], None]] = None,
                     status_callback: Optional[Callable[[str], None]] = None):
        """设置GUI回调函数"""
        self.log_callback = log_callback
        self.progress_callback = progress_callback
        self.status_callback = status_callback
    
    def log_message(self, message: str):
        """记录日志消息"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
    
    def update_status(self, status: str):
        """更新状态"""
        if self.status_callback:
            self.status_callback(status)
    
    def update_progress(self, percentage: int, message: str):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(percentage, message)
    
    async def run(self, workflow_name: Optional[str] = None):
        """运行框架"""
        self.log_message("启动ScriptZero - 零适配游戏自动化框架...")
        self.update_status("正在运行")
        try:
            await self.execute_workflow(workflow_name)
            self.log_message("工作流执行完成")
            self.update_status("已完成")
        except Exception as e:
            self.log_message(f"执行出错: {str(e)}")
            self.update_status("错误")
            raise


# 示例用法
async def main():
    # 创建示例配置文件
    example_config = """
version: 1.0
name: "示例自动化任务"

variables:
  game_path: "C:/Games/ExampleGame/game.exe"
  account: "player123"

games:
  example_game:
    executable: "${variables.game_path}"
    arguments: ["-windowed"]
    window_title: "ExampleGame"

workflow:
  - name: "启动游戏"
    type: "game"
    game: "example_game"
    actions:
      - type: "launch"
      - type: "wait_for"
        condition: "window_active"
        timeout: 30
"""
    
    with open("example_config.yaml", "w", encoding="utf-8") as f:
        f.write(example_config)
    
    # 创建框架实例并运行
    framework = GameAutomationFramework("example_config.yaml")
    await framework.run()


if __name__ == "__main__":
    asyncio.run(main())