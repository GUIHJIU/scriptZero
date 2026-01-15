"""
配置数据模型
使用Pydantic定义配置的数据结构和验证规则
"""
from typing import Dict, List, Optional, Union, Any  # 添加 Any 到导入
from pathlib import Path
from pydantic import BaseModel, Field, validator
import yaml


class AdapterConfig(BaseModel):
    """适配器配置"""
    name: str = Field(..., description="适配器名称")
    type: str = Field(..., description="适配器类型")
    enabled: bool = Field(True, description="是否启用")
    config: Dict[str, Union[str, int, float, bool, List, Dict]] = Field(default_factory=dict, description="适配器特定配置")


class ImageTemplateConfig(BaseModel):
    """图像模板配置"""
    initial_start_btn: Optional[str] = Field(None, description="初始启动按钮模板路径")
    dragon_btn_before: Optional[str] = Field(None, description="一条龙按钮模板路径（点击前）")
    blue_play_btn: Optional[str] = Field(None, description="蓝色播放按钮模板路径")
    dragon_btn_after: Optional[str] = Field(None, description="一条龙按钮模板路径（点击后）")
    general_start_btn: Optional[str] = Field(None, description="通用启动按钮模板路径")
    general_dragon_btn: Optional[str] = Field(None, description="通用一条龙按钮模板路径")
    general_play_btn: Optional[str] = Field(None, description="通用播放按钮模板路径")
    automation_complete: Optional[str] = Field(None, description="自动化完成标志模板路径")


class WorkflowStepConfig(BaseModel):
    """工作流步骤配置"""
    name: str = Field(..., description="步骤名称")
    templates: List[str] = Field(default_factory=list, description="该步骤使用的模板列表")
    fallback_coords: Optional[List[int]] = Field(None, description="备用坐标")
    delay_after: float = Field(2.0, description="执行后延迟时间")
    timeout: Optional[int] = Field(None, description="步骤超时时间")


class BetterGIWorkflowConfig(BaseModel):
    """BetterGI工作流配置"""
    steps: List[WorkflowStepConfig] = Field(default_factory=list, description="工作流步骤列表")


class GameSpecificConfig(BaseModel):
    """游戏特定配置"""
    game_name: str = Field(..., description="游戏名称")
    genshin_path: Optional[str] = Field(None, description="原神游戏路径")
    bettergi_path: Optional[str] = Field(None, description="BetterGI路径")
    templates_path: str = Field("templates", description="模板文件路径")
    check_interval: int = Field(30, description="检查间隔（秒）")
    timeout: int = Field(3600, description="超时时间（秒）")
    close_after_completion: bool = Field(True, description="完成后是否关闭")
    image_templates: ImageTemplateConfig = Field(default_factory=ImageTemplateConfig, description="图像模板配置")
    bettergi_workflow: BetterGIWorkflowConfig = Field(default_factory=BetterGIWorkflowConfig, description="BetterGI工作流配置")


class CoreConfig(BaseModel):
    """核心配置"""
    log_level: str = Field("INFO", description="日志级别")
    log_file: Optional[str] = Field(None, description="日志文件路径")
    debug_mode: bool = Field(False, description="调试模式")
    max_workers: int = Field(4, description="最大工作线程数")
    temp_dir: str = Field("./temp", description="临时文件目录")


class MainConfiguration(BaseModel):
    """主配置模型"""
    version: str = Field("1.0", description="配置版本")
    project_name: str = Field("ScriptZero", description="项目名称")
    core: CoreConfig = Field(default_factory=CoreConfig, description="核心配置")
    game: GameSpecificConfig = Field(..., description="游戏特定配置")
    adapters: List[AdapterConfig] = Field(default_factory=list, description="适配器列表")
    
    @validator('version')
    def validate_version(cls, v):
        """验证版本格式"""
        if not isinstance(v, str) or len(v.strip()) == 0:
            raise ValueError('版本号不能为空')
        return v
    
    @validator('game')
    def validate_game_config(cls, v):
        """验证游戏配置"""
        if not v.game_name or len(v.game_name.strip()) == 0:
            raise ValueError('游戏名称不能为空')
        return v
    
    def save_to_file(self, file_path: str):
        """保存配置到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.dict(), f, default_flow_style=False, allow_unicode=True)
    
    @classmethod
    def load_from_file(cls, file_path: str):
        """从文件加载配置"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls(**data)
    
    @classmethod
    def create_default(cls, game_name: str = "Genshin Impact"):
        """创建默认配置"""
        return cls(
            version="1.0",
            project_name="ScriptZero",
            core=CoreConfig(),
            game=GameSpecificConfig(
                game_name=game_name
            ),
            adapters=[]
        )


class ConfigSimplifier:
    """配置简化器 - 提供分层配置方案"""
    
    @staticmethod
    def create_basic_config(game: str = "Genshin Impact", adapter: str = "bettergi", script: str = "") -> Dict[str, Any]:
        """创建基础配置（新手友好）"""
        basic_config = {
            "game": game,
            "adapter": adapter,
            "script": script
        }
        return basic_config
    
    @staticmethod
    def expand_basic_to_full(basic_config: Dict[str, Any]) -> MainConfiguration:
        """将基础配置扩展为完整配置"""
        game = basic_config.get("game", "Genshin Impact")
        adapter = basic_config.get("adapter", "bettergi")
        
        # 根据游戏类型生成默认配置
        if game.lower() in ["genshin impact", "genshin", "yuanshen"]:
            full_config = MainConfiguration(
                version="1.0",
                project_name="ScriptZero",
                core=CoreConfig(),
                game=GameSpecificConfig(
                    game_name=game,
                    templates_path="./templates",
                    check_interval=30,
                    timeout=3600,
                    close_after_completion=True
                ),
                adapters=[
                    AdapterConfig(
                        name=f"{adapter}_adapter",
                        type="game",
                        enabled=True,
                        config={}
                    )
                ]
            )
        else:
            # 默认配置
            full_config = MainConfiguration.create_default(game_name=game)
        
        return full_config
    
    @staticmethod
    def create_adapter_specific_config(adapter_type: str, **kwargs) -> Dict[str, Any]:
        """创建适配器特定配置"""
        config_map = {
            "bettergi": {
                "game_name": kwargs.get("game_name", "Genshin Impact"),
                "genshin_path": kwargs.get("genshin_path", ""),
                "bettergi_path": kwargs.get("bettergi_path", ""),
                "templates_path": kwargs.get("templates_path", "./templates"),
                "check_interval": kwargs.get("check_interval", 30),
                "timeout": kwargs.get("timeout", 3600),
                "close_after_completion": kwargs.get("close_after_completion", True)
            },
            "python": {
                "script_path": kwargs.get("script_path", ""),
                "arguments": kwargs.get("arguments", [])
            },
            "exe": {
                "exe_path": kwargs.get("exe_path", ""),
                "arguments": kwargs.get("arguments", [])
            },
            "ahk": {
                "script_path": kwargs.get("script_path", ""),
                "ahk_executable": kwargs.get("ahk_executable", "AutoHotkey.exe"),
                "arguments": kwargs.get("arguments", [])
            }
        }
        
        return config_map.get(adapter_type, {})
    
    @staticmethod
    def apply_template(base_config: MainConfiguration, template_name: str) -> MainConfiguration:
        """应用配置模板"""
        templates = {
            "genshin_daily": {
                "game": {
                    "check_interval": 60,
                    "timeout": 7200,  # 2小时
                    "close_after_completion": True
                }
            },
            "genshin_weekly": {
                "game": {
                    "check_interval": 120,
                    "timeout": 14400,  # 4小时
                    "close_after_completion": True
                }
            },
            "performance_optimized": {
                "core": {
                    "max_workers": 2,
                    "log_level": "WARNING"
                }
            },
            "debug_mode": {
                "core": {
                    "debug_mode": True,
                    "log_level": "DEBUG"
                }
            }
        }
        
        template = templates.get(template_name, {})
        config_dict = base_config.dict()
        
        # 深度合并配置
        ConfigSimplifier._deep_update(config_dict, template)
        
        return MainConfiguration(**config_dict)
    
    @staticmethod
    def _deep_update(source: Dict, updates: Dict) -> Dict:
        """深度更新字典"""
        for key, value in updates.items():
            if key in source and isinstance(source[key], dict) and isinstance(value, dict):
                ConfigSimplifier._deep_update(source[key], value)
            else:
                source[key] = value
        return source