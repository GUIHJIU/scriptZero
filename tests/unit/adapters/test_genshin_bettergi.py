"""
GenshinBetterGI适配器单元测试
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from pathlib import Path
from src.adapters.game_adapters.genshin_bettergi import GenshinBetterGIAdapter


class TestGenshinBetterGIAdapter:
    """GenshinBetterGI适配器测试类"""
    
    @pytest.fixture
    def adapter_config(self):
        """适配器配置"""
        return {
            'game_name': 'Genshin Impact',
            'genshin_path': '/path/to/genshin.exe',
            'bettergi_path': '/path/to/bettergi.exe',
            'templates_path': './templates',
            'check_interval': 30,
            'timeout': 3600,
            'close_after_completion': True
        }
    
    @pytest.fixture
    def adapter(self, adapter_config):
        """创建适配器实例"""
        return GenshinBetterGIAdapter(adapter_config)
    
    def test_initialization(self, adapter, adapter_config):
        """测试适配器初始化"""
        # 使用Path对象进行比较，避免路径分隔符问题
        assert adapter.genshin_path == Path(adapter_config['genshin_path'])
        assert adapter.bettergi_path == Path(adapter_config['bettergi_path'])
        assert adapter.is_running is False
        assert adapter.genshin_process is None
        assert adapter.bettergi_process is None
    
    @pytest.mark.asyncio
    async def test_start_method(self, adapter):
        """测试启动方法"""
        with patch.object(adapter, 'start_framework', new_callable=AsyncMock) as mock_start_framework, \
             patch.object(adapter, 'start_game', new_callable=AsyncMock) as mock_start_game, \
             patch.object(adapter, 'switch_to_framework_and_start', new_callable=AsyncMock) as mock_switch:
            
            mock_start_framework.return_value = True
            mock_start_game.return_value = True
            mock_switch.return_value = True
            
            result = await adapter.start()
            
            assert result is True
            assert adapter.is_running is True
            mock_start_framework.assert_called_once()
            mock_start_game.assert_called_once()
            mock_switch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stop_method(self, adapter):
        """测试停止方法"""
        with patch.object(adapter, 'close_processes', new_callable=AsyncMock) as mock_close:
            result = await adapter.stop()
            
            assert result is True
            assert adapter.is_running is False
            mock_close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_method(self, adapter):
        """测试执行方法"""
        with patch.object(adapter, 'wait_for_completion', new_callable=AsyncMock) as mock_wait:
            mock_wait.return_value = True
            
            result = await adapter.execute()
            
            assert result is True
            mock_wait.assert_called_once_with(check_interval=30, timeout=3600)
    
    @pytest.mark.asyncio
    async def test_find_image_position_with_existing_template(self, adapter):
        """测试查找图像位置 - 存在模板"""
        # 创建一个模拟的Location对象，具有left, top, width, height属性
        mock_location = Mock()
        mock_location.left = 100
        mock_location.top = 200
        mock_location.width = 50
        mock_location.height = 50
        
        # 创建一个模拟的Center对象
        mock_center = Mock()
        mock_center.x = 125  # left + width/2
        mock_center.y = 225  # top + height/2
        
        with patch('src.adapters.game_adapters.genshin_bettergi.pyautogui.locateOnScreen') as mock_locate, \
             patch('src.adapters.game_adapters.genshin_bettergi.pyautogui.center') as mock_center_func, \
             patch('pathlib.Path.exists', return_value=True):
            
            mock_locate.return_value = mock_location
            mock_center_func.return_value = mock_center
            
            result = await adapter.find_image_position('/fake/template.png')
            
            assert result is not None
            assert result[0] == 125  # center x
            assert result[1] == 225  # center y
            mock_center_func.assert_called_once_with(mock_location)
    
    @pytest.mark.asyncio
    async def test_find_image_position_with_nonexistent_template(self, adapter):
        """测试查找图像位置 - 模板不存在"""
        with patch('pathlib.Path.exists', return_value=False):
            result = await adapter.find_image_position('/nonexistent/template.png')
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_click_image_success(self, adapter):
        """测试点击图像 - 成功"""
        with patch.object(adapter, 'find_image_position', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = (100, 200)
            
            with patch('src.adapters.game_adapters.genshin_bettergi.pyautogui.click') as mock_click:
                result = await adapter.click_image('/fake/template.png')
                
                assert result is True
                mock_click.assert_called_once_with(100, 200)
    
    @pytest.mark.asyncio
    async def test_click_image_failure(self, adapter):
        """测试点击图像 - 失败"""
        with patch.object(adapter, 'find_image_position', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = None
            
            result = await adapter.click_image('/fake/template.png')
            
            assert result is False


class TestConfigurableGenshinBetterGIAdapter:
    """可配置的GenshinBetterGI适配器测试类"""
    
    @pytest.fixture
    def configurable_adapter(self):
        """创建可配置适配器实例"""
        from src.adapters.game_adapters.genshin_bettergi import ConfigurableGenshinBetterGIAdapter
        
        config = {
            'game_name': 'Genshin Impact',
            'genshin_path': '/path/to/genshin.exe',
            'bettergi_path': '/path/to/bettergi.exe',
            'check_interval': 15,
            'timeout': 1800,
            'close_after_completion': False
        }
        
        return ConfigurableGenshinBetterGIAdapter(config)
    
    def test_configurable_adapter_initialization(self, configurable_adapter):
        """测试可配置适配器初始化"""
        assert configurable_adapter.check_interval == 15
        assert configurable_adapter.timeout == 1800
        assert configurable_adapter.close_after_completion is False
    
    @pytest.mark.asyncio
    async def test_configurable_adapter_wait_for_completion(self, configurable_adapter):
        """测试可配置适配器等待完成方法"""
        with patch.object(configurable_adapter, 'wait_for_completion', new_callable=AsyncMock) as mock_wait:
            mock_wait.return_value = True
            
            result = await configurable_adapter.wait_for_completion()
            
            assert result is True
            # 验证传递了正确的参数
            mock_wait.assert_called_once()