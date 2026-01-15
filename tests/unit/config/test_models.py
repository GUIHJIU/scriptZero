"""
配置模型单元测试
"""
import pytest
from pydantic import ValidationError
from src.config.models import (
    MainConfiguration, GameSpecificConfig, CoreConfig, 
    AdapterConfig, ImageTemplateConfig, BetterGIWorkflowConfig
)


class TestMainConfiguration:
    """主配置模型测试"""
    
    def test_valid_main_configuration(self):
        """测试有效的主配置"""
        config_data = {
            "version": "1.0",
            "project_name": "ScriptZero Test",
            "core": {
                "log_level": "INFO",
                "debug_mode": False,
                "max_workers": 4,
                "temp_dir": "./temp"
            },
            "game": {
                "game_name": "Genshin Impact",
                "genshin_path": "/path/to/genshin.exe",
                "bettergi_path": "/path/to/bettergi.exe",
                "templates_path": "./templates",
                "check_interval": 30,
                "timeout": 3600,
                "close_after_completion": True
            },
            "adapters": []
        }
        
        config = MainConfiguration(**config_data)
        
        assert config.version == "1.0"
        assert config.project_name == "ScriptZero Test"
        assert config.core.log_level == "INFO"
        assert config.game.game_name == "Genshin Impact"
        assert len(config.adapters) == 0
    
    def test_invalid_version_format(self):
        """测试无效的版本格式"""
        config_data = {
            "version": "",  # 空版本号
            "project_name": "ScriptZero Test",
            "core": {
                "log_level": "INFO",
                "debug_mode": False,
                "max_workers": 4,
                "temp_dir": "./temp"
            },
            "game": {
                "game_name": "Genshin Impact",
                "check_interval": 30,
                "timeout": 3600,
                "close_after_completion": True
            },
            "adapters": []
        }
        
        with pytest.raises(ValidationError):
            MainConfiguration(**config_data)
    
    def test_invalid_game_name(self):
        """测试无效的游戏名称"""
        config_data = {
            "version": "1.0",
            "project_name": "ScriptZero Test",
            "core": {
                "log_level": "INFO",
                "debug_mode": False,
                "max_workers": 4,
                "temp_dir": "./temp"
            },
            "game": {
                "game_name": "",  # 空游戏名称
                "check_interval": 30,
                "timeout": 3600,
                "close_after_completion": True
            },
            "adapters": []
        }
        
        with pytest.raises(ValidationError):
            MainConfiguration(**config_data)
    
    def test_create_default_configuration(self):
        """测试创建默认配置"""
        config = MainConfiguration.create_default(game_name="Test Game")
        
        assert config.version == "1.0"
        assert config.project_name == "ScriptZero"
        assert config.game.game_name == "Test Game"
        assert config.core.log_level == "INFO"
        assert len(config.adapters) == 0


class TestGameSpecificConfig:
    """游戏特定配置测试"""
    
    def test_valid_game_config(self):
        """测试有效的游戏配置"""
        config = GameSpecificConfig(
            game_name="Genshin Impact",
            genshin_path="/path/to/genshin.exe",
            bettergi_path="/path/to/bettergi.exe",
            templates_path="./templates",
            check_interval=30,
            timeout=3600,
            close_after_completion=True
        )
        
        assert config.game_name == "Genshin Impact"
        assert config.genshin_path == "/path/to/genshin.exe"
        assert config.check_interval == 30
        assert config.timeout == 3600
        assert config.close_after_completion is True
    
    def test_default_values(self):
        """测试默认值"""
        config = GameSpecificConfig(game_name="Test Game")
        
        assert config.templates_path == "templates"
        assert config.check_interval == 30
        assert config.timeout == 3600
        assert config.close_after_completion is True


class TestCoreConfig:
    """核心配置测试"""
    
    def test_valid_core_config(self):
        """测试有效的核心配置"""
        config = CoreConfig(
            log_level="DEBUG",
            log_file="app.log",
            debug_mode=True,
            max_workers=8,
            temp_dir="/tmp"
        )
        
        assert config.log_level == "DEBUG"
        assert config.log_file == "app.log"
        assert config.debug_mode is True
        assert config.max_workers == 8
        assert config.temp_dir == "/tmp"
    
    def test_default_core_config(self):
        """测试默认核心配置"""
        config = CoreConfig()
        
        assert config.log_level == "INFO"
        assert config.debug_mode is False
        assert config.max_workers == 4
        assert config.temp_dir == "./temp"


class TestAdapterConfig:
    """适配器配置测试"""
    
    def test_valid_adapter_config(self):
        """测试有效的适配器配置"""
        config = AdapterConfig(
            name="test_adapter",
            type="game",
            enabled=True,
            config={"param": "value"}
        )
        
        assert config.name == "test_adapter"
        assert config.type == "game"
        assert config.enabled is True
        assert config.config == {"param": "value"}
    
    def test_default_adapter_config(self):
        """测试默认适配器配置"""
        config = AdapterConfig(
            name="test_adapter",
            type="script"
        )
        
        assert config.enabled is True  # 默认启用
        assert config.config == {}  # 默认空配置


class TestImageTemplateConfig:
    """图像模板配置测试"""
    
    def test_image_template_config(self):
        """测试图像模板配置"""
        config = ImageTemplateConfig(
            initial_start_btn="templates/start.png",
            dragon_btn_before="templates/dragon_before.png",
            blue_play_btn="templates/blue_play.png"
        )
        
        assert config.initial_start_btn == "templates/start.png"
        assert config.dragon_btn_before == "templates/dragon_before.png"
        assert config.blue_play_btn == "templates/blue_play.png"
        assert config.automation_complete is None  # 未设置的字段应该是None


class TestBetterGIWorkflowConfig:
    """BetterGI工作流配置测试"""
    
    def test_empty_workflow_config(self):
        """测试空工作流配置"""
        config = BetterGIWorkflowConfig()
        
        assert config.steps == []
    
    def test_workflow_config_with_steps(self):
        """测试带有步骤的工作流配置"""
        from src.config.models import WorkflowStepConfig
        
        step = WorkflowStepConfig(
            name="Test Step",
            templates=["template1.png", "template2.png"],
            fallback_coords=[100, 200],
            delay_after=2.5
        )
        
        config = BetterGIWorkflowConfig(steps=[step])
        
        assert len(config.steps) == 1
        assert config.steps[0].name == "Test Step"
        assert config.steps[0].templates == ["template1.png", "template2.png"]
        assert config.steps[0].fallback_coords == [100, 200]
        assert config.steps[0].delay_after == 2.5