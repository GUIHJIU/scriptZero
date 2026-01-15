"""
配置加载器
负责加载、解析和合并配置文件
"""
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from .models import MainConfiguration, ConfigSimplifier
from .validators import ConfigValidator
import re


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self):
        self.base_config_path = None
        self.game_specific_config_path = None
        self.user_override_config_path = None
    
    def load_yaml_config(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """加载YAML配置文件"""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                return yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                raise ValueError(f"YAML配置文件格式错误: {e}")
    
    def load_json_config(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """加载JSON配置文件"""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f) or {}
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON配置文件格式错误: {e}")
    
    def merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """合并基础配置和覆盖配置"""
        merged = base_config.copy()
        
        def deep_merge(base: Dict, override: Dict) -> Dict:
            """深度合并两个字典"""
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        return deep_merge(merged, override_config)
    
    def resolve_variables(self, config: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """解析配置中的变量引用"""
        def replace_vars(obj):
            if isinstance(obj, str):
                # 查找并替换 ${variable} 格式的变量
                pattern = r'\$\{([^}]+)\}'
                result = obj
                # 持续替换直到不再有变量引用
                max_iterations = 10  # 防止无限循环
                iteration = 0
                while True:
                    iteration += 1
                    if iteration > max_iterations:
                        break  # 防止无限循环
                    matches = re.findall(pattern, result)
                    if not matches:
                        break
                    for var_name in matches:
                        # 支持两种格式的变量引用：直接变量名或 variables.变量名
                        value = None
                        if var_name in variables:
                            value = variables[var_name]
                        elif var_name.startswith('variables.') and var_name[10:] in variables:  # 10是'variables.'的长度
                            actual_var_name = var_name[10:]
                            value = variables[actual_var_name]
                        elif var_name.startswith('image_templates.') and var_name in config.get('image_templates', {}):
                            # 处理 image_templates 引用
                            value = config.get('image_templates', {}).get(var_name, var_name)
                        
                        if value is not None:
                            # 保持原始值的类型
                            if isinstance(value, str):
                                result = result.replace(f"${{{var_name}}}", value)
                            else:
                                result = str(value)  # 将非字符串值转换为字符串
                        else:
                            # 如果变量未找到，保留原字符串
                            break
                    else:
                        continue
                    break
                return result
            elif isinstance(obj, dict):
                new_dict = {}
                for k, v in obj.items():
                    new_dict[k] = replace_vars(v)
                return new_dict
            elif isinstance(obj, list):
                return [replace_vars(item) for item in obj]
            else:
                return obj
        
        return replace_vars(config)
    
    def convert_legacy_config_to_new_format(self, legacy_config: Dict[str, Any]) -> Dict[str, Any]:
        """将旧格式配置转换为新格式"""
        # 提取变量部分
        variables = legacy_config.get('variables', {})
        
        # 解析整个配置中的变量引用
        resolved_config = self.resolve_variables(legacy_config, variables)
        
        # 从解析后的配置中获取实际值
        version = resolved_config.get('version', '1.0')
        name = resolved_config.get('name', 'ScriptZero')
        logging_config = resolved_config.get('logging', {})
        variables_resolved = resolved_config.get('variables', {})
        
        # 初始化新格式配置
        new_config = {
            "version": str(version),
            "project_name": name,
            "core": {
                "log_level": logging_config.get('level', 'INFO'),
                "log_file": logging_config.get('file', None),
                "debug_mode": False,
                "max_workers": 4,
                "temp_dir": "./temp"
            },
            "game": {
                "game_name": "Genshin Impact",  # 从配置中推断
                "genshin_path": variables_resolved.get('genshin_path', ''),
                "bettergi_path": variables_resolved.get('bettergi_path', ''),
                "templates_path": "./templates",
                "check_interval": int(variables_resolved.get('check_interval', 30)),
                "timeout": int(variables_resolved.get('timeout', 3600)),
                "close_after_completion": bool(variables_resolved.get('close_after_completion', True)),
                "image_templates": {
                    "initial_start_btn": resolved_config.get('image_templates', {}).get('bettergi_initial_start_btn', ''),
                    "dragon_btn_before": resolved_config.get('image_templates', {}).get('bettergi_dragon_btn_before', ''),
                    "blue_play_btn": resolved_config.get('image_templates', {}).get('bettergi_blue_play_btn', ''),
                    "dragon_btn_after": resolved_config.get('image_templates', {}).get('bettergi_dragon_btn_after', ''),
                    "general_start_btn": resolved_config.get('image_templates', {}).get('bettergi_start_btn', ''),
                    "general_dragon_btn": resolved_config.get('image_templates', {}).get('bettergi_dragon_btn', ''),
                    "general_play_btn": resolved_config.get('image_templates', {}).get('bettergi_play_btn', ''),
                    "automation_complete": resolved_config.get('image_templates', {}).get('automation_complete', ''),
                }
            },
            "adapters": []
        }
        
        # 如果有工作流配置，将其转换为适配器配置
        # 重要：使用resolved_config而不是原始的legacy_config
        workflow = resolved_config.get('workflow', [])
        for wf_item in workflow:
            if wf_item.get('enabled', True) and wf_item.get('type') == 'adapter_sequence' and wf_item.get('adapter_type') == 'genshin_bettergi':
                adapter_config = wf_item.get('config', {})
                
                # 注意：这里adapter_config已经通过resolve_variables解析过了
                # 创建适配器配置时，使用解析后的值
                new_config["adapters"].append({
                    "name": "genshin_bettergi_adapter",
                    "type": "genshin_bettergi",
                    "enabled": True,
                    "config": adapter_config
                })
                
                # 更新game配置中的模板路径
                if 'image_templates' in adapter_config:
                    new_config["game"]["image_templates"].update(adapter_config['image_templates'])
                
                # 更新其他游戏配置参数
                if 'genshin_path' in adapter_config:
                    new_config["game"]["genshin_path"] = adapter_config['genshin_path']
                if 'bettergi_path' in adapter_config:
                    new_config["game"]["bettergi_path"] = adapter_config['bettergi_path']
                if 'check_interval' in adapter_config:
                    new_config["game"]["check_interval"] = int(adapter_config['check_interval'])
                if 'timeout' in adapter_config:
                    new_config["game"]["timeout"] = int(adapter_config['timeout'])
                if 'close_after_completion' in adapter_config:
                    new_config["game"]["close_after_completion"] = bool(adapter_config['close_after_completion'])
                break
        
        return new_config
    
    def load_configuration(self, 
                          base_config_path: Optional[Union[str, Path]] = None,
                          game_specific_config_path: Optional[Union[str, Path]] = None,
                          user_override_config_path: Optional[Union[str, Path]] = None) -> MainConfiguration:
        """
        加载配置文件（支持三层配置系统）
        
        Args:
            base_config_path: 基础配置路径
            game_specific_config_path: 游戏特定配置路径
            user_override_config_path: 用户覆盖配置路径
        
        Returns:
            MainConfiguration: 验证后的配置对象
        """
        # 默认路径设置
        if base_config_path is None:
            base_config_path = Path(__file__).parent.parent / "config" / "base_config.yaml"
        
        if game_specific_config_path is None:
            game_specific_config_path = Path(__file__).parent.parent / "config" / "game_config.yaml"
        
        if user_override_config_path is None:
            user_override_config_path = Path(__file__).parent.parent / "config" / "user_config.yaml"
        
        # 存储配置路径
        self.base_config_path = Path(base_config_path)
        self.game_specific_config_path = Path(game_specific_config_path)
        self.user_override_config_path = Path(user_override_config_path)
        
        # 加载基础配置
        base_config = {}
        if self.base_config_path.exists():
            base_config = self.load_yaml_config(self.base_config_path)
        
        # 加载游戏特定配置
        game_specific_config = {}
        if self.game_specific_config_path.exists():
            game_specific_config = self.load_yaml_config(self.game_specific_config_path)
        
        # 加载用户覆盖配置
        user_override_config = {}
        if self.user_override_config_path.exists():
            user_override_config = self.load_yaml_config(self.user_override_config_path)
        
        # 合并配置：基础配置 <- 游戏特定配置 <- 用户覆盖配置
        merged_config = self.merge_configs(base_config, game_specific_config)
        final_config = self.merge_configs(merged_config, user_override_config)
        
        # 验证最终配置
        validated_config = ConfigValidator.full_validate(final_config)
        
        return validated_config
    
    def load_from_single_file(self, config_path: Union[str, Path]) -> MainConfiguration:
        """从单个配置文件加载配置"""
        config_path = Path(config_path)
        
        if config_path.suffix.lower() in ['.yaml', '.yml']:
            raw_config = self.load_yaml_config(config_path)
        elif config_path.suffix.lower() == '.json':
            raw_config = self.load_json_config(config_path)
        else:
            raise ValueError(f"不支持的配置文件格式: {config_path.suffix}")
        
        # 检查是否是旧格式配置，如果是则转换
        if self._is_legacy_format(raw_config):
            raw_config = self.convert_legacy_config_to_new_format(raw_config)
        
        # 验证配置
        validated_config = ConfigValidator.full_validate(raw_config)
        
        return validated_config
    
    def _is_legacy_format(self, config: Dict[str, Any]) -> bool:
        """判断是否为旧格式配置"""
        # 旧格式特征：包含 variables, games, script_frameworks, workflow 等字段
        legacy_keys = {'variables', 'games', 'script_frameworks', 'workflow', 'monitors', 'plugins'}
        config_keys = set(config.keys())
        
        # 如果配置包含至少一半的旧格式键，则认为是旧格式
        common_keys = legacy_keys.intersection(config_keys)
        return len(common_keys) >= len(legacy_keys) // 2
    
    def save_config(self, config: MainConfiguration, file_path: Union[str, Path]):
        """保存配置到文件"""
        file_path = Path(file_path)
        config.save_to_file(str(file_path))
    
    def create_default_config(self, game_name: str = "Genshin Impact") -> MainConfiguration:
        """创建默认配置"""
        return MainConfiguration.create_default(game_name=game_name)
    
    def validate_and_fix_paths(self, config: MainConfiguration) -> MainConfiguration:
        """验证并修正配置中的路径"""
        # 这里可以添加路径修正逻辑
        # 例如：将相对路径转换为绝对路径
        config_dict = config.dict()
        
        # 修正游戏配置中的路径
        if 'game' in config_dict:
            game_config = config_dict['game']
            if 'genshin_path' in game_config and game_config['genshin_path']:
                game_config['genshin_path'] = str(Path(game_config['genshin_path']).resolve())
            if 'bettergi_path' in game_config and game_config['bettergi_path']:
                game_config['bettergi_path'] = str(Path(game_config['bettergi_path']).resolve())
            if 'templates_path' in game_config and game_config['templates_path']:
                game_config['templates_path'] = str(Path(game_config['templates_path']).resolve())
        
        # 返回修正后的配置
        return MainConfiguration(**config_dict)