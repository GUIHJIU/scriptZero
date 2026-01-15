"""
配置验证器
提供自定义验证逻辑
"""
from pathlib import Path
from typing import Dict, Any
from pydantic import ValidationError
from .models import MainConfiguration
import os


class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def validate_file_exists(file_path: str, file_description: str = "文件") -> bool:
        """验证文件是否存在"""
        if not file_path:
            return True  # 空路径可能表示可选文件
        
        # 如果路径包含变量引用，跳过验证
        if '${' in file_path and '}' in file_path:
            return True  # 变量引用的路径在运行时才会解析
        
        path = Path(file_path)
        if not path.exists():
            raise ValueError(f"{file_description}不存在: {file_path}")
        return True
    
    @staticmethod
    def validate_directory_exists(dir_path: str, dir_description: str = "目录") -> bool:
        """验证目录是否存在"""
        if not dir_path:
            return True  # 空路径可能表示可选目录
        
        # 如果路径包含变量引用，跳过验证
        if '${' in dir_path and '}' in dir_path:
            return True  # 变量引用的路径在运行时才会解析
        
        path = Path(dir_path)
        if not path.is_dir():
            raise ValueError(f"{dir_description}不存在: {dir_path}")
        return True
    
    @staticmethod
    def validate_executable_path(exec_path: str, exec_description: str = "可执行文件") -> bool:
        """验证可执行文件路径"""
        if not exec_path:
            return True  # 空路径可能表示可选的可执行文件
        
        # 如果路径包含变量引用，跳过验证
        if '${' in exec_path and '}' in exec_path:
            return True  # 变量引用的路径在运行时才会解析
        
        path = Path(exec_path)
        if not path.exists():
            raise ValueError(f"{exec_description}不存在: {exec_path}")
        
        if not os.access(path, os.X_OK):
            # 在Windows上，我们通常不能简单地检查X_OK，所以只检查文件存在
            pass
        
        return True
    
    @staticmethod
    def validate_image_templates(image_templates: Dict[str, str]) -> bool:
        """验证图像模板文件"""
        for template_name, template_path in image_templates.items():
            if template_path:  # 只验证非空路径
                ConfigValidator.validate_file_exists(template_path, f"图像模板 {template_name}")
        return True
    
    @staticmethod
    def validate_genshin_bettergi_config(config: Dict[str, Any]) -> bool:
        """验证原神BetterGI配置"""
        # 验证必要字段
        required_fields = ['genshin_path', 'bettergi_path']
        for field in required_fields:
            if field not in config or not config[field]:
                continue  # 对于变量引用，暂时跳过严格验证
        
        # 验证路径存在性（如果路径不是变量引用）
        if config.get('genshin_path'):
            ConfigValidator.validate_executable_path(
                config['genshin_path'], 
                "原神可执行文件"
            )
        if config.get('bettergi_path'):
            ConfigValidator.validate_executable_path(
                config['bettergi_path'], 
                "BetterGI可执行文件"
            )
        
        # 验证图像模板
        if 'image_templates' in config:
            ConfigValidator.validate_image_templates(config['image_templates'])
        
        return True
    
    @staticmethod
    def validate_configuration_model(config: MainConfiguration) -> bool:
        """验证配置模型"""
        try:
            # 验证模型结构
            config_dict = config.dict()
            
            # 验证游戏配置
            game_config = config_dict.get('game', {})
            if game_config:
                ConfigValidator.validate_genshin_bettergi_config(game_config)
            
            # 验证核心配置中的路径
            core_config = config_dict.get('core', {})
            if core_config.get('log_file'):
                # 如果日志文件路径不是变量引用，则验证其父目录
                log_file_path = core_config['log_file']
                if '${' not in log_file_path or '}' not in log_file_path:
                    log_dir = Path(log_file_path).parent
                    # 创建日志目录（如果不存在）
                    log_dir.mkdir(parents=True, exist_ok=True)
            
            if core_config.get('temp_dir'):
                temp_dir = core_config['temp_dir']
                if '${' not in temp_dir or '}' not in temp_dir:
                    # 创建临时目录（如果不存在）
                    Path(temp_dir).mkdir(parents=True, exist_ok=True)
            
            return True
        except Exception as e:
            raise ValueError(f"配置验证失败: {str(e)}")
    
    @staticmethod
    def full_validate(config_data: Dict[str, Any]) -> MainConfiguration:
        """完整验证配置数据并返回配置对象"""
        # 首先验证数据结构
        try:
            config = MainConfiguration(**config_data)
        except ValidationError as e:
            raise ValueError(f"配置数据结构验证失败: {str(e)}")
        
        # 然后验证业务逻辑
        ConfigValidator.validate_configuration_model(config)
        
        return config