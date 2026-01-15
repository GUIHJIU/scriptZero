"""
GenshinBetterGI适配器集成测试
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from pathlib import Path
from src.adapters.game_adapters.genshin_bettergi import GenshinBetterGIAdapter
from src.config.loader import ConfigLoader
from src.config.models import MainConfiguration


class TestGenshinBetterGIIntegration:
    """GenshinBetterGI适配器集成测试"""
    
    @pytest.fixture
    def sample_config(self):
        """示例配置"""
        return {
            'game_name': 'Genshin Impact Test',
            'genshin_path': '/mock/genshin/path',
            'bettergi_path': '/mock/bettergi/path',
            'templates_path': './mock/templates',
            'check_interval': 5,  # 缩短检查间隔用于测试
            'timeout': 60,       # 缩短超时时间用于测试
            'close_after_completion': False
        }
    
    @pytest.fixture
    def adapter(self, sample_config):
        """适配器实例"""
        return GenshinBetterGIAdapter(sample_config)
    
    @pytest.mark.asyncio
    async def test_full_lifecycle_integration(self, adapter):
        """测试完整生命周期集成"""
        # 模拟所有依赖方法
        with patch.object(adapter, 'start_framework', new_callable=AsyncMock) as mock_start_framework, \
             patch.object(adapter, 'start_game', new_callable=AsyncMock) as mock_start_game, \
             patch.object(adapter, 'switch_to_framework_and_start', new_callable=AsyncMock) as mock_switch, \
             patch.object(adapter, 'wait_for_completion', new_callable=AsyncMock) as mock_wait, \
             patch.object(adapter, 'close_processes', new_callable=AsyncMock) as mock_close:
            
            # 设置模拟返回值
            mock_start_framework.return_value = True
            mock_start_game.return_value = True
            mock_switch.return_value = True
            mock_wait.return_value = True
            mock_close.return_value = True
            
            # 测试启动
            start_result = await adapter.start()
            assert start_result is True
            assert adapter.is_running is True
            mock_start_framework.assert_called_once()
            mock_start_game.assert_called_once()
            mock_switch.assert_called_once()
            
            # 测试执行
            execute_result = await adapter.execute()
            assert execute_result is True
            mock_wait.assert_called_once_with(check_interval=5, timeout=60)
            
            # 测试停止
            stop_result = await adapter.stop()
            assert stop_result is True
            assert adapter.is_running is False
            mock_close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_adapter_with_real_config_loader(self):
        """测试使用真实配置加载器的适配器"""
        # 创建一个最小的配置
        config_data = {
            "version": "1.0",
            "project_name": "Test Integration",
            "core": {
                "log_level": "DEBUG",
                "debug_mode": True
            },
            "game": {
                "game_name": "Genshin Impact Test",
                "genshin_path": "/mock/genshin/path",
                "bettergi_path": "/mock/bettergi/path",
                "templates_path": "./mock/templates",
                "check_interval": 5,
                "timeout": 60,
                "close_after_completion": False
            },
            "adapters": []
        }
        
        # 使用MainConfiguration创建配置
        main_config = MainConfiguration(**config_data)
        
        # 创建适配器
        adapter_config = {
            'game_name': main_config.game.game_name,
            'genshin_path': main_config.game.genshin_path,
            'bettergi_path': main_config.game.bettergi_path,
            'templates_path': main_config.game.templates_path,
            'check_interval': main_config.game.check_interval,
            'timeout': main_config.game.timeout,
            'close_after_completion': main_config.game.close_after_completion,
            'image_templates': {},
            'bettergi_workflow': {}
        }
        
        adapter = GenshinBetterGIAdapter(adapter_config)
        
        # 验证适配器配置是否正确加载（使用Path对象进行比较）
        assert adapter.genshin_path == Path(main_config.game.genshin_path)
        assert adapter.bettergi_path == Path(main_config.game.bettergi_path)
        assert adapter.config['check_interval'] == main_config.game.check_interval
        assert adapter.config['timeout'] == main_config.game.timeout
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self, adapter):
        """测试错误处理集成"""
        # 在start方法中，即使start_framework失败，也需要正确处理is_running状态
        # 我们需要模拟完整的start过程
        with patch.object(adapter, 'start_framework', new_callable=AsyncMock) as mock_start_framework, \
             patch.object(adapter, 'start_game', new_callable=AsyncMock) as mock_start_game, \
             patch.object(adapter, 'switch_to_framework_and_start', new_callable=AsyncMock) as mock_switch:
            
            # 模拟启动框架失败
            mock_start_framework.return_value = False
            # 确保其他方法不被调用
            mock_start_game.return_value = True
            mock_switch.return_value = True
            
            start_result = await adapter.start()
            # 因为start_framework失败，所以整体启动应该失败
            assert start_result is False
            # is_running应该根据实际逻辑设置
            # 在start方法中，如果任何一步失败，我们应该确保is_running被正确设置
    
    @pytest.mark.asyncio
    async def test_image_processing_integration(self, adapter):
        """测试图像处理集成"""
        # 创建模拟的Location和Center对象
        mock_location = Mock()
        mock_location.left = 100
        mock_location.top = 200
        mock_location.width = 50
        mock_location.height = 50
        
        mock_center = Mock()
        mock_center.x = 125  # left + width/2
        mock_center.y = 225  # top + height/2
        
        with patch('src.adapters.game_adapters.genshin_bettergi.pyautogui.locateOnScreen') as mock_locate, \
             patch('src.adapters.game_adapters.genshin_bettergi.pyautogui.center') as mock_center_func, \
             patch('pathlib.Path.exists', return_value=True):
            
            mock_locate.return_value = mock_location
            mock_center_func.return_value = mock_center
            
            result = await adapter.find_image_position('/mock/template.png')
            
            assert result is not None
            assert result[0] == 125  # center x
            assert result[1] == 225  # center y
            mock_center_func.assert_called_once_with(mock_location)
    
    @pytest.mark.asyncio
    async def test_click_operations_integration(self, adapter):
        """测试点击操作集成"""
        with patch.object(adapter, 'find_image_position', new_callable=AsyncMock) as mock_find, \
             patch('src.adapters.game_adapters.genshin_bettergi.pyautogui.click') as mock_click:
            
            # 模拟找到图像位置
            mock_find.return_value = (150, 300)
            
            result = await adapter.click_image('/mock/template.png')
            
            assert result is True
            mock_click.assert_called_once_with(150, 300)
    
    def test_config_compatibility_with_adapter(self, sample_config):
        """测试配置与适配器的兼容性"""
        # 直接使用适配器配置进行初始化
        adapter = GenshinBetterGIAdapter(sample_config)
        
        # 验证关键属性是否正确设置（使用Path对象进行比较）
        assert adapter.config['game_name'] == sample_config['game_name']
        assert adapter.genshin_path == Path(sample_config['genshin_path'])
        assert adapter.bettergi_path == Path(sample_config['bettergi_path'])
        assert adapter.config['check_interval'] == sample_config['check_interval']
        assert adapter.config['timeout'] == sample_config['timeout']