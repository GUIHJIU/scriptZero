"""
配置验证模型
使用Pydantic实现强类型配置验证
"""
from pydantic import BaseModel, Field, validator, FilePath, DirectoryPath
from typing import List, Dict, Optional, Union
from pathlib import Path
import yaml


class GameConfig(BaseModel):
    """游戏配置模型"""
    executable: Union[FilePath, str] = Field(..., description="游戏可执行文件路径")
    arguments: List[str] = Field(default_factory=list, description="启动参数")
    window_title: str = Field(..., min_length=1, description="游戏窗口标题")
    detection_timeout: int = Field(30, ge=1, le=300, description="检测超时时间(秒)")
    
    @validator('arguments', pre=True)
    def validate_arguments(cls, v):
        """验证参数列表"""
        if isinstance(v, str):
            return v.split()
        return v


class MonitorConfig(BaseModel):
    """监控配置模型"""
    type: str = Field(..., description="监控类型")
    config: Dict[str, str] = Field(default_factory=dict, description="监控配置参数")
    timeout: int = Field(60, ge=1, le=3600, description="监控超时时间")


class ScriptConfig(BaseModel):
    """脚本配置模型"""
    path: Union[FilePath, str] = Field(..., description="脚本路径")
    type: str = Field(default="python", description="脚本类型")
    arguments: List[str] = Field(default_factory=list, description="脚本参数")
    completion: Optional[Dict] = Field(None, description="完成条件")
    
    @validator('arguments', pre=True)
    def validate_script_arguments(cls, v):
        """验证脚本参数"""
        if isinstance(v, str):
            return v.split()
        return v


class WorkflowStep(BaseModel):
    """工作流步骤模型"""
    name: str = Field(..., min_length=1, description="步骤名称")
    type: str = Field(..., description="步骤类型")
    config: Dict = Field(default_factory=dict, description="步骤配置")
    enabled: bool = Field(True, description="是否启用")
    depends_on: List[str] = Field(default_factory=list, description="依赖的步骤")


class MainConfig(BaseModel):
    """主配置模型"""
    version: str = Field("1.0", description="配置版本")
    name: str = Field(..., min_length=1, max_length=100, description="配置名称")
    variables: Dict[str, Union[str, int, float, bool]] = Field(default_factory=dict, description="变量配置")
    games: Dict[str, GameConfig] = Field(default_factory=dict, description="游戏配置")
    workflow: List[WorkflowStep] = Field(default_factory=list, description="工作流配置")
    scripts: List[ScriptConfig] = Field(default_factory=list, description="脚本配置")
    monitors: List[MonitorConfig] = Field(default_factory=list, description="监控配置")
    
    @validator('variables', pre=True)
    def validate_variables(cls, v):
        """验证变量配置"""
        if isinstance(v, list):
            # 如果是列表形式，转换为字典
            result = {}
            for item in v:
                if isinstance(item, dict) and 'name' in item and 'value' in item:
                    result[item['name']] = item['value']
                elif isinstance(item, str):
                    # 假设格式为 "name=value"
                    if '=' in item:
                        name, value = item.split('=', 1)
                        result[name.strip()] = value.strip()
            return result
        return v


def load_and_validate_config(config_path: Union[str, Path]) -> MainConfig:
    """
    加载并验证配置文件
    """
    config_path = Path(config_path)
    
    if config_path.suffix.lower() in ['.yaml', '.yml']:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
    elif config_path.suffix.lower() == '.json':
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
    else:
        raise ValueError(f"Unsupported config file format: {config_path.suffix}")
    
    # 验证并创建配置对象
    validated_config = MainConfig(**config_dict)
    return validated_config


def validate_config_dict(config_dict: Dict) -> MainConfig:
    """
    验证配置字典
    """
    return MainConfig(**config_dict)


def create_sample_config() -> MainConfig:
    """
    创建示例配置
    """
    sample_config = MainConfig(
        version="1.0",
        name="示例配置",
        variables={
            "GAME_PATH": "C:/Games/MyGame",
            "PLAYER_NAME": "Player1"
        },
        games={
            "my_game": GameConfig(
                executable="C:/Games/MyGame/game.exe",
                arguments=["-fullscreen", "-player", "Player1"],
                window_title="My Game",
                detection_timeout=45
            )
        },
        workflow=[
            WorkflowStep(
                name="启动游戏",
                type="launch_game",
                config={"game": "my_game"},
                enabled=True
            ),
            WorkflowStep(
                name="等待游戏加载",
                type="wait_for_condition",
                config={"monitor": "window_active", "timeout": 60},
                enabled=True,
                depends_on=["启动游戏"]
            )
        ],
        scripts=[
            ScriptConfig(
                path="./scripts/init.py",
                type="python",
                arguments=["--mode", "init"],
                completion={
                    "any_of": [
                        {"type": "timeout", "seconds": 180}
                    ]
                }
            )
        ],
        monitors=[
            MonitorConfig(
                type="window",
                config={"title": "My Game", "expected_state": "active"},
                timeout=30
            )
        ]
    )
    return sample_config


if __name__ == "__main__":
    # 示例用法
    try:
        # 创建示例配置
        config = create_sample_config()
        print("示例配置创建成功!")
        print(f"配置名称: {config.name}")
        print(f"游戏数量: {len(config.games)}")
        print(f"工作流步骤: {len(config.workflow)}")
        
        # 验证配置
        config.validate()
        print("配置验证通过!")
        
    except Exception as e:
        print(f"配置验证失败: {e}")