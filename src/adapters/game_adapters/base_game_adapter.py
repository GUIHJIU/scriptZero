"""
游戏适配器基类
"""
from typing import Any, Dict, Optional, List
from ..base import BaseAdapter


class BaseGameAdapter(BaseAdapter):
    """游戏适配器的基类"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.game_name = config.get('game_name', 'Unknown Game')
        self.window_title = config.get('window_title', '')
        self.process_name = config.get('process_name', '')
        self.supported_features = config.get('supported_features', [])
    
    async def find_game_window(self) -> Optional[int]:
        """查找游戏窗口句柄"""
        # 这里需要实现窗口查找逻辑
        pass
    
    async def activate_game_window(self):
        """激活游戏窗口"""
        # 这里需要实现窗口激活逻辑
        pass
    
    async def send_input_to_game(self, input_type: str, input_data: Any):
        """向游戏发送输入"""
        # 这里需要实现输入发送逻辑
        pass
    
    def is_feature_supported(self, feature: str) -> bool:
        """检查是否支持特定功能"""
        return feature in self.supported_features