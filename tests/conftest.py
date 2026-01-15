"""
Pytest配置文件
定义共享的fixture和其他pytest配置
"""
import pytest
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_config():
    """提供示例配置数据"""
    return {
        "version": "1.0",
        "project_name": "ScriptZero Test",
        "core": {
            "log_level": "DEBUG",
            "debug_mode": True,
            "max_workers": 2,
            "temp_dir": "./test_temp"
        },
        "game": {
            "game_name": "Test Game",
            "genshin_path": "/path/to/test/game",
            "bettergi_path": "/path/to/test/bettergi",
            "templates_path": "./test_templates",
            "check_interval": 10,
            "timeout": 600,
            "close_after_completion": True
        },
        "adapters": []
    }


@pytest.fixture
def temp_dir(tmp_path):
    """提供临时目录"""
    return tmp_path


@pytest.fixture
def mock_adapter_config():
    """提供模拟适配器配置"""
    return {
        "name": "test_adapter",
        "type": "game",
        "enabled": True,
        "config": {
            "game_name": "Test Game",
            "test_param": "test_value"
        }
    }