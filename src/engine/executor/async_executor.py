"""
执行引擎核心 - 纯业务逻辑执行
与监控、UI完全解耦
"""
import asyncio
import os
import subprocess
import sys
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
import psutil
import signal


class AsyncScriptExecutor:
    """异步脚本执行器 - 纯业务逻辑执行"""
    
    def __init__(self):
        self.adapters = {}
        self.running_processes = {}  # 跟踪运行中的进程
        self._initialize_adapters()
    
    def _initialize_adapters(self):
        """初始化脚本适配器"""
        # 注册默认适配器
        self.adapters.update({
            '.py': self._prepare_python_script,
            '.exe': self._prepare_executable,
            '.bat': self._prepare_batch_script,
            '.ps1': self._prepare_powershell_script,
            '.ahk': self._prepare_autohotkey_script,
            '.js': self._prepare_nodejs_script,
            '.lua': self._prepare_lua_script,
            '.rb': self._prepare_ruby_script,
            '.jar': self._prepare_java_jar,
        })
    
    async def detect_script_type(self, script_path: str) -> str:
        """智能检测脚本类型"""
        path = Path(script_path)
        extension = path.suffix.lower()
        return extension
    
    def get_adapter(self, script_type: str):
        """获取对应类型的适配器"""
        return self.adapters.get(script_type, self._prepare_generic_script)
    
    async def _prepare_python_script(self, script_config: Dict[str, Any]) -> Tuple[List[str], dict]:
        """准备Python脚本执行命令"""
        cmd = [sys.executable, script_config['path']]
        if script_config.get('arguments'):
            cmd.extend(script_config['arguments'])
        
        env = os.environ.copy()
        if script_config.get('env_vars'):
            env.update(script_config['env_vars'])
        
        return cmd, env
    
    async def _prepare_executable(self, script_config: Dict[str, Any]) -> Tuple[List[str], dict]:
        """准备可执行文件执行命令"""
        cmd = [script_config['path']]
        if script_config.get('arguments'):
            cmd.extend(script_config['arguments'])
        
        env = os.environ.copy()
        if script_config.get('env_vars'):
            env.update(script_config['env_vars'])
        
        return cmd, env
    
    async def _prepare_batch_script(self, script_config: Dict[str, Any]) -> Tuple[List[str], dict]:
        """准备批处理脚本执行命令"""
        cmd = ['cmd', '/c', script_config['path']]
        if script_config.get('arguments'):
            cmd.extend(script_config['arguments'])
        
        env = os.environ.copy()
        if script_config.get('env_vars'):
            env.update(script_config['env_vars'])
        
        return cmd, env
    
    async def _prepare_powershell_script(self, script_config: Dict[str, Any]) -> Tuple[List[str], dict]:
        """准备PowerShell脚本执行命令"""
        cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_config['path']]
        if script_config.get('arguments'):
            cmd.extend(script_config['arguments'])
        
        env = os.environ.copy()
        if script_config.get('env_vars'):
            env.update(script_config['env_vars'])
        
        return cmd, env
    
    async def _prepare_autohotkey_script(self, script_config: Dict[str, Any]) -> Tuple[List[str], dict]:
        """准备AutoHotkey脚本执行命令"""
        # 检查AutoHotkey是否已安装
        ahk_path = self._find_autohotkey()
        if ahk_path:
            cmd = [ahk_path, script_config['path']]
        else:
            # 如果没找到，尝试直接执行
            cmd = [script_config['path']]
        
        if script_config.get('arguments'):
            cmd.extend(script_config['arguments'])
        
        env = os.environ.copy()
        if script_config.get('env_vars'):
            env.update(script_config['env_vars'])
        
        return cmd, env
    
    def _find_autohotkey(self) -> Optional[str]:
        """查找AutoHotkey可执行文件"""
        try:
            # 尝试常见安装路径
            common_paths = [
                r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
                r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
                r"C:\AutoHotkey\AutoHotkey.exe"
            ]
            
            for path in common_paths:
                if Path(path).exists():
                    return path
            
            # 尝试在PATH中查找
            import shutil
            return shutil.which("AutoHotkey.exe")
        except:
            return None
    
    async def _prepare_nodejs_script(self, script_config: Dict[str, Any]) -> Tuple[List[str], dict]:
        """准备Node.js脚本执行命令"""
        cmd = ['node', script_config['path']]
        if script_config.get('arguments'):
            cmd.extend(script_config['arguments'])
        
        env = os.environ.copy()
        if script_config.get('env_vars'):
            env.update(script_config['env_vars'])
        
        return cmd, env
    
    async def _prepare_lua_script(self, script_config: Dict[str, Any]) -> Tuple[List[str], dict]:
        """准备Lua脚本执行命令"""
        cmd = ['lua', script_config['path']]
        if script_config.get('arguments'):
            cmd.extend(script_config['arguments'])
        
        env = os.environ.copy()
        if script_config.get('env_vars'):
            env.update(script_config['env_vars'])
        
        return cmd, env
    
    async def _prepare_ruby_script(self, script_config: Dict[str, Any]) -> Tuple[List[str], dict]:
        """准备Ruby脚本执行命令"""
        cmd = ['ruby', script_config['path']]
        if script_config.get('arguments'):
            cmd.extend(script_config['arguments'])
        
        env = os.environ.copy()
        if script_config.get('env_vars'):
            env.update(script_config['env_vars'])
        
        return cmd, env
    
    async def _prepare_java_jar(self, script_config: Dict[str, Any]) -> Tuple[List[str], dict]:
        """准备Java JAR文件执行命令"""
        cmd = ['java', '-jar', script_config['path']]
        if script_config.get('arguments'):
            cmd.extend(script_config['arguments'])
        
        env = os.environ.copy()
        if script_config.get('env_vars'):
            env.update(script_config['env_vars'])
        
        return cmd, env
    
    async def _prepare_generic_script(self, script_config: Dict[str, Any]) -> Tuple[List[str], dict]:
        """通用脚本准备方法"""
        # 默认尝试使用系统默认程序执行
        cmd = [script_config['path']]
        if script_config.get('arguments'):
            cmd.extend(script_config['arguments'])
        
        env = os.environ.copy()
        if script_config.get('env_vars'):
            env.update(script_config['env_vars'])
        
        return cmd, env
    
    async def execute_script(self, script_config: Dict[str, Any]):
        """执行脚本 - 仅负责执行，不涉及监控"""
        # 1. 智能检测脚本类型
        script_type = await self.detect_script_type(script_config['path'])
        
        # 2. 应用适配器（透明转换）
        adapter = self.get_adapter(script_type)
        command, env = await adapter(script_config)
        
        # 3. 执行并返回进程对象
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE
            )
            
            # 4. 记录运行中的进程
            script_name = script_config.get('name', Path(script_config['path']).stem)
            self.running_processes[process.pid] = {
                'process': process,
                'name': script_name,
                'config': script_config,
                'start_time': asyncio.get_event_loop().time()
            }
            
            # 5. 异步收集输出（不影响脚本执行）
            asyncio.create_task(self.capture_output(process, script_name))
            
            return process
        except Exception as e:
            print(f"Failed to start process: {e}")
            raise
    
    async def capture_output(self, process, script_name: str):
        """捕获脚本输出"""
        try:
            stdout, stderr = await process.communicate()
            if stdout:
                print(f"[{script_name}] STDOUT: {stdout.decode()}")
            if stderr:
                print(f"[{script_name}] STDERR: {stderr.decode()}")
        except Exception as e:
            print(f"Error capturing output for {script_name}: {e}")
    
    async def wait_for_completion(self, process, timeout: Optional[int] = None):
        """等待进程完成"""
        try:
            if timeout:
                return await asyncio.wait_for(process.wait(), timeout=timeout)
            else:
                return await process.wait()
        except asyncio.TimeoutError:
            # 超时则终止进程
            await self.terminate_process(process.pid)
            return -1
    
    async def terminate_process(self, pid: int, force: bool = False):
        """终止进程"""
        if pid in self.running_processes:
            proc_info = self.running_processes[pid]
            process = proc_info['process']
            
            try:
                if force:
                    # 强制终止
                    process.kill()
                else:
                    # 尝试优雅终止
                    if os.name == 'nt':  # Windows
                        process.terminate()
                    else:  # Unix-like
                        process.send_signal(signal.SIGTERM)
                
                # 等待进程结束
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    # 如果进程没有响应终止信号，强制杀死
                    process.kill()
                    await process.wait()
                
                # 从运行列表中移除
                del self.running_processes[pid]
                print(f"Process {pid} terminated successfully")
            except psutil.NoSuchProcess:
                # 进程可能已经结束
                if pid in self.running_processes:
                    del self.running_processes[pid]
            except Exception as e:
                print(f"Error terminating process {pid}: {e}")
                if pid in self.running_processes:
                    del self.running_processes[pid]
    
    async def get_process_status(self, pid: int) -> Optional[dict]:
        """获取进程状态"""
        if pid not in self.running_processes:
            return None
        
        proc_info = self.running_processes[pid]
        process = proc_info['process']
        
        try:
            # 使用psutil获取更详细的进程信息
            p = psutil.Process(process.pid)
            status = {
                'pid': process.pid,
                'name': proc_info['name'],
                'status': p.status(),
                'cpu_percent': p.cpu_percent(),
                'memory_percent': p.memory_percent(),
                'running_time': asyncio.get_event_loop().time() - proc_info['start_time']
            }
            return status
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # 进程可能已经结束
            if pid in self.running_processes:
                del self.running_processes[pid]
            return None
    
    async def list_running_processes(self) -> List[dict]:
        """列出所有运行中的进程"""
        statuses = []
        for pid in list(self.running_processes.keys()):
            status = await self.get_process_status(pid)
            if status:
                statuses.append(status)
        return statuses