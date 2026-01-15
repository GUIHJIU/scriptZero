"""
插件接口定义
所有插件必须实现的接口
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import importlib.util
import os
from pathlib import Path


class PluginInterface(ABC):
    """所有插件必须实现的接口"""
    
    @abstractmethod
    def get_plugin_info(self) -> Dict[str, Any]:
        """返回插件元数据"""
        pass
    
    @abstractmethod
    def initialize(self, context: Dict[str, Any]) -> bool:
        """插件初始化"""
        pass
    
    @abstractmethod
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行插件逻辑"""
        pass
    
    def cleanup(self) -> bool:
        """插件清理"""
        return True


# 插件类型枚举
PLUGIN_TYPES = {
    "script_adapter": "脚本适配器插件",
    "monitor": "监控插件",
    "condition": "条件判断插件", 
    "action": "动作执行插件",
    "communicator": "通信插件",
    "scheduler": "调度插件",
    "reporter": "报告插件",
    "ui_widget": "界面组件插件",
    "logger": "日志插件",
    "storage": "存储插件"
}


class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.plugins = {}
        self.plugin_types = PLUGIN_TYPES
        self.plugin_dirs = [
            "plugins",
            "./src/plugins/custom",
            os.path.expanduser("~/.scriptzero/plugins")
        ]
        self.loaded_modules = {}
    
    def register_plugin(self, name: str, plugin: PluginInterface):
        """注册插件"""
        self.plugins[name] = plugin
    
    def unregister_plugin(self, name: str):
        """注销插件"""
        if name in self.plugins:
            # 清理插件
            try:
                self.plugins[name].cleanup()
            except:
                pass
            del self.plugins[name]
    
    def get_plugin(self, name: str) -> Optional[PluginInterface]:
        """获取插件"""
        return self.plugins.get(name)
    
    def execute_plugin(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行插件"""
        plugin = self.get_plugin(name)
        if plugin:
            return plugin.execute(data)
        else:
            raise ValueError(f"Plugin '{name}' not found")
    
    def list_plugins(self) -> Dict[str, str]:
        """列出所有插件及类型"""
        result = {}
        for name, plugin in self.plugins.items():
            info = plugin.get_plugin_info()
            result[name] = info.get('description', 'No description')
        return result
    
    def list_plugin_types(self) -> Dict[str, str]:
        """列出所有插件类型"""
        return self.plugin_types
    
    def load_plugin_from_file(self, plugin_path: str) -> Optional[PluginInterface]:
        """从文件加载插件"""
        try:
            spec = importlib.util.spec_from_file_location("plugin_module", plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找插件类（继承自PluginInterface的类）
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (hasattr(attr, '__mro__') and 
                    PluginInterface in attr.__mro__ and 
                    attr != PluginInterface):
                    plugin_instance = attr()
                    if isinstance(plugin_instance, PluginInterface):
                        plugin_name = plugin_instance.get_plugin_info()['id']
                        self.register_plugin(plugin_name, plugin_instance)
                        self.loaded_modules[plugin_path] = module
                        return plugin_instance
            
            return None
        except Exception as e:
            print(f"Error loading plugin from {plugin_path}: {e}")
            return None
    
    def discover_plugins(self, plugin_dirs: Optional[List[str]] = None) -> List[str]:
        """发现插件"""
        dirs = plugin_dirs or self.plugin_dirs
        discovered_plugins = []
        
        for plugin_dir in dirs:
            if not os.path.exists(plugin_dir):
                continue
            
            for root, dirs, files in os.walk(plugin_dir):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        plugin_path = os.path.join(root, file)
                        plugin = self.load_plugin_from_file(plugin_path)
                        if plugin:
                            discovered_plugins.append(plugin.get_plugin_info()['id'])
        
        return discovered_plugins
    
    def load_plugins_by_type(self, plugin_type: str) -> List[str]:
        """根据类型加载插件"""
        loaded_plugins = []
        for plugin_id, plugin in self.plugins.items():
            info = plugin.get_plugin_info()
            if info.get('type') == plugin_type:
                loaded_plugins.append(plugin_id)
        return loaded_plugins
    
    def get_plugins_by_type(self, plugin_type: str) -> Dict[str, PluginInterface]:
        """根据类型获取插件"""
        result = {}
        for plugin_id, plugin in self.plugins.items():
            info = plugin.get_plugin_info()
            if info.get('type') == plugin_type:
                result[plugin_id] = plugin
        return result
    
    async def execute_plugins_parallel(self, plugin_names: List[str], data: Dict[str, Any]) -> Dict[str, Any]:
        """并行执行多个插件"""
        import asyncio
        
        async def execute_single_plugin(name):
            try:
                result = self.execute_plugin(name, data)
                return name, result, None
            except Exception as e:
                return name, None, str(e)
        
        tasks = [execute_single_plugin(name) for name in plugin_names]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        final_result = {'successful': {}, 'failed': {}}
        for result in results:
            if isinstance(result, tuple):
                name, plugin_result, error = result
                if error is None:
                    final_result['successful'][name] = plugin_result
                else:
                    final_result['failed'][name] = error
            else:
                # 如果是异常
                pass
        
        return final_result


# 插件装饰器
def register_plugin(name: str, plugin_type: str, description: str = ""):
    """插件注册装饰器"""
    def decorator(cls):
        # 这里可以添加插件注册逻辑
        cls.PLUGIN_ID = name
        cls.PLUGIN_TYPE = plugin_type
        cls.PLUGIN_DESCRIPTION = description
        return cls
    return decorator


# 基础插件实现示例
class BasePlugin(PluginInterface):
    """基础插件实现"""
    
    PLUGIN_ID = ""
    PLUGIN_TYPE = ""
    PLUGIN_NAME = ""
    PLUGIN_DESCRIPTION = ""
    PLUGIN_VERSION = "1.0.0"
    
    def get_plugin_info(self) -> Dict[str, Any]:
        return {
            'id': self.PLUGIN_ID,
            'name': self.PLUGIN_NAME,
            'type': self.PLUGIN_TYPE,
            'description': self.PLUGIN_DESCRIPTION,
            'version': self.PLUGIN_VERSION
        }
    
    def initialize(self, context: Dict[str, Any]) -> bool:
        """默认初始化实现"""
        return True
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """子类需要重写此方法"""
        raise NotImplementedError("Subclasses must implement execute method")
    
    def cleanup(self) -> bool:
        """默认清理实现"""
        return True