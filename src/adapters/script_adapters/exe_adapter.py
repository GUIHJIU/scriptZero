"""
可执行文件适配器
"""
import subprocess
from typing import Any, Dict, Optional
from ..base import BaseAdapter


class ExeAdapter(BaseAdapter):
    """可执行文件执行适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.exe_path = config.get('exe_path', '')
        self.arguments = config.get('arguments', [])
    
    async def start(self):
        """启动可执行文件"""
        self.is_running = True
        print(f"Starting EXE adapter for {self.exe_path}")
    
    async def stop(self):
        """停止可执行文件"""
        self.is_running = False
        print("Stopping EXE adapter")
    
    async def execute(self, *args, **kwargs):
        """执行可执行文件"""
        if not self.exe_path:
            raise ValueError("Executable path not specified in config")
        
        cmd = [self.exe_path] + self.arguments
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            'return_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }