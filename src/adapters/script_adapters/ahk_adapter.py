"""
AutoHotKey脚本适配器
"""
import subprocess
import os
from typing import Any, Dict, Optional
from ..base import BaseAdapter


class AhkAdapter(BaseAdapter):
    """AutoHotKey脚本执行适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.script_path = config.get('script_path', '')
        self.ahk_executable = config.get('ahk_executable', 'AutoHotkey.exe')
        self.arguments = config.get('arguments', [])
    
    async def start(self):
        """启动AHK脚本"""
        self.is_running = True
        print(f"Starting AHK adapter for {self.script_path}")
    
    async def stop(self):
        """停止AHK脚本"""
        self.is_running = False
        print("Stopping AHK adapter")
    
    async def execute(self, *args, **kwargs):
        """执行AHK脚本"""
        if not self.script_path:
            raise ValueError("AHK script path not specified in config")
        
        if not os.path.exists(self.script_path):
            raise FileNotFoundError(f"AHK script not found: {self.script_path}")
        
        cmd = [self.ahk_executable, self.script_path] + self.arguments
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            'return_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }