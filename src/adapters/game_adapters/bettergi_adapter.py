"""
BetterGI通用游戏适配器
适用于使用BetterGI框架的各类游戏
"""
import asyncio
from typing import Any, Dict, Optional
from .base_game_adapter import BaseGameAdapter


class BetterGIAdapter(BaseGameAdapter):
    """BetterGI通用游戏适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化BetterGI适配器
        
        Args:
            config: 配置字典，包含bettergi_path, game_specific_config等
        """
        super().__init__(config)
        self.bettergi_path = config.get('bettergi_path', '')
        self.bettergi_process = None
        self.game_specific_config = config.get('game_specific_config', {})
        
        # 设置默认支持的功能
        self.supported_features.extend([
            'image_recognition',
            'auto_script_execution',
            'process_management',
            'window_control'
        ])
    
    async def start(self):
        """启动BetterGI框架"""
        print(f"启动BetterGI框架 for {self.game_name}...")
        self.is_running = True
        
        # 这里会实现BetterGI框架的启动逻辑
        # 具体实现将在子类中完成
        print(f"BetterGI框架已为 {self.game_name} 启动")
        return True
    
    async def stop(self):
        """停止BetterGI框架"""
        print(f"停止BetterGI框架 for {self.game_name}...")
        self.is_running = False
        
        # 停止相关进程
        if self.bettergi_process:
            try:
                self.bettergi_process.terminate()
                self.bettergi_process = None
            except:
                pass
        
        print(f"BetterGI框架已为 {self.game_name} 停止")
        return True
    
    async def execute(self, *args, **kwargs):
        """执行主要功能"""
        # 具体的执行逻辑由子类实现
        raise NotImplementedError("execute方法必须被子类重写")
    
    def load_game_config(self, game_name: str) -> Dict[str, Any]:
        """加载特定游戏的配置"""
        # 这里可以根据游戏名称加载不同的配置
        game_configs = {
            'genshin': {
                'workflow_steps': [
                    {'name': '启动游戏', 'action': 'launch_game'},
                    {'name': '启动脚本框架', 'action': 'launch_framework'},
                    {'name': '执行自动化', 'action': 'execute_automation'}
                ],
                'templates_path': 'templates/genshin',
                'click_positions': {}
            },
            'honkai': {
                'workflow_steps': [
                    {'name': '启动游戏', 'action': 'launch_game'},
                    {'name': '启动脚本框架', 'action': 'launch_framework'},
                    {'name': '执行自动化', 'action': 'execute_automation'}
                ],
                'templates_path': 'templates/honkai',
                'click_positions': {}
            }
        }
        
        return game_configs.get(game_name.lower(), {})