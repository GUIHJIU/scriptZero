# 创建新适配器

## 适配器概述

适配器是 ScriptZero 框架的核心扩展点，用于与不同的游戏、脚本框架或其他外部系统交互。所有适配器都应该继承自基础适配器类以确保一致性。

## 适配器类型

ScriptZero 支持多种类型的适配器：

- **游戏适配器**(Game Adapters): 与特定游戏交互
- **脚本适配器**(Script Adapters): 执行外部脚本
- **通信适配器**(Communication Adapters): 处理外部通信
- **协议适配器**(Protocol Adapters): 处理特定协议

## 基础适配器结构

所有适配器都应继承自以下基类之一：

- [BaseAdapter](file:///E:/WORKSPACE/Python/scriptZero/src/adapters/base.py#L10-L32): 所有适配器的通用基类
- [BaseGameAdapter](file:///E:/WORKSPACE/Python/scriptZero/src/adapters/game_adapters/base_game_adapter.py#L11-L35): 游戏适配器的基类

## 创建游戏适配器

### 1. 继承基类

```python
from src.adapters.game_adapters.base_game_adapter import BaseGameAdapter

class MyGameAdapter(BaseGameAdapter):
    def __init__(self, config):
        super().__init__(config)
        # 初始化特定属性
        self.game_path = config.get('game_path', '')
        self.script_path = config.get('script_path', '')
```

### 2. 实现抽象方法

每个适配器必须实现以下方法：

```python
import asyncio

class MyGameAdapter(BaseGameAdapter):
    # ... 初始化代码 ...
    
    async def start(self):
        """启动适配器"""
        self.is_running = True
        # 启动游戏和相关服务的逻辑
        print(f"Starting {self.game_name}")
        # 实现具体的启动逻辑
        return True
    
    async def stop(self):
        """停止适配器"""
        self.is_running = False
        # 停止游戏和相关服务的逻辑
        print(f"Stopping {self.game_name}")
        # 实现具体的停止逻辑
        return True
    
    async def execute(self, *args, **kwargs):
        """执行适配器的主要功能"""
        # 实现主要功能逻辑
        # 例如：启动自动化脚本、执行游戏任务等
        return {"status": "success", "details": "Execution completed"}
```

### 3. 添加特定功能

```python
class MyGameAdapter(BaseGameAdapter):
    # ... 之前的方法 ...
    
    async def find_game_window(self):
        """查找游戏窗口"""
        # 实现窗口查找逻辑
        pass
    
    async def send_command(self, command):
        """发送命令到游戏"""
        # 实现命令发送逻辑
        pass
```

## 创建脚本适配器

脚本适配器用于执行外部脚本：

```python
from src.adapters.base import BaseAdapter
import subprocess
import sys

class CustomScriptAdapter(BaseAdapter):
    def __init__(self, config):
        super().__init__(config)
        self.script_path = config.get('script_path', '')
        self.arguments = config.get('arguments', [])
    
    async def start(self):
        self.is_running = True
        print(f"Starting script adapter for {self.script_path}")
        return True
    
    async def stop(self):
        self.is_running = False
        print("Stopping script adapter")
        return True
    
    async def execute(self, *args, **kwargs):
        """执行外部脚本"""
        if not self.script_path:
            raise ValueError("Script path not specified in config")
        
        cmd = [sys.executable, self.script_path] + self.arguments
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            'return_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
```

## 配置集成

### 1. 定义配置模型

为适配器创建对应的配置模型：

```python
# 在 src/config/models.py 中添加
from pydantic import BaseModel, Field

class MyGameAdapterConfig(BaseModel):
    game_path: str = Field(..., description="游戏可执行文件路径")
    script_path: str = Field(..., description="脚本路径")
    window_title: str = Field("MyGame", description="游戏窗口标题")
    custom_setting: int = Field(100, description="自定义设置")
```

### 2. 在适配器中使用配置

```python
class MyGameAdapter(BaseGameAdapter):
    def __init__(self, config):
        super().__init__(config)
        # 从配置中提取值
        adapter_config = MyGameAdapterConfig(**config)
        self.game_path = adapter_config.game_path
        self.script_path = adapter_config.script_path
        self.window_title = adapter_config.window_title
        self.custom_setting = adapter_config.custom_setting
```

## 错误处理

适配器应该妥善处理各种错误情况：

```python
import logging

class MyGameAdapter(BaseGameAdapter):
    def __init__(self, config):
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def start(self):
        try:
            # 尝试启动逻辑
            if not self._validate_paths():
                raise ValueError("Invalid paths in configuration")
            
            # 启动游戏
            self._launch_game()
            self.is_running = True
            return True
        except FileNotFoundError as e:
            self.logger.error(f"File not found: {e}")
            return False
        except PermissionError as e:
            self.logger.error(f"Permission denied: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during start: {e}")
            return False
    
    def _validate_paths(self):
        """验证路径是否存在"""
        import os
        return os.path.exists(self.game_path)
    
    def _launch_game(self):
        """启动游戏的私有方法"""
        # 实现启动逻辑
        pass
```

## 注册适配器

### 1. 更新适配器工厂

在适配器包的 [__init__.py](file:///E:/WORKSPACE/Python/scriptZero/src/adapters/__init__.py) 文件中注册新适配器：

```python
# src/adapters/__init__.py
from .base import BaseAdapter
from .game_adapters.my_game_adapter import MyGameAdapter
from .game_adapters.genshin_bettergi import GenshinBetterGIAdapter
from .script_adapters.python_adapter import PythonAdapter
from .script_adapters.exe_adapter import ExeAdapter
from .script_adapters.ahk_adapter import AhkAdapter

__all__ = [
    'BaseAdapter',
    'GenshinBetterGIAdapter',
    'MyGameAdapter',
    'PythonAdapter',
    'ExeAdapter',
    'AhkAdapter'
]
```

### 2. 配置文件中使用适配器

```yaml
adapters:
  - name: "my_game"
    type: "game"
    enabled: true
    config:
      game_path: "/path/to/mygame.exe"
      script_path: "/path/to/script.py"
      window_title: "My Game Window"
      custom_setting: 200
```

## 测试适配器

### 1. 单元测试

为适配器编写单元测试：

```python
# tests/unit/adapters/test_my_game_adapter.py
import pytest
from src.adapters.game_adapters.my_game_adapter import MyGameAdapter

@pytest.mark.asyncio
async def test_adapter_initialization():
    config = {
        'game_name': 'Test Game',
        'game_path': '/fake/path.exe',
        'window_title': 'Test Window'
    }
    
    adapter = MyGameAdapter(config)
    assert adapter.game_name == 'Test Game'
    assert adapter.game_path == '/fake/path.exe'

@pytest.mark.asyncio
async def test_adapter_start_stop():
    config = {
        'game_name': 'Test Game',
        'game_path': '/fake/path.exe'
    }
    
    adapter = MyGameAdapter(config)
    
    # 测试启动
    result = await adapter.start()
    assert result is True
    assert adapter.is_running is True
    
    # 测试停止
    result = await adapter.stop()
    assert result is True
    assert adapter.is_running is False
```

### 2. 集成测试

```python
# tests/integration/test_my_game_workflow.py
import pytest
from src.adapters.game_adapters.my_game_adapter import MyGameAdapter

@pytest.mark.asyncio
async def test_full_adapter_workflow():
    config = {
        'game_name': 'Test Game',
        'game_path': '/fake/path.exe'
    }
    
    adapter = MyGameAdapter(config)
    
    # 测试完整工作流程
    start_result = await adapter.start()
    assert start_result is True
    
    execute_result = await adapter.execute()
    assert execute_result is not None
    
    stop_result = await adapter.stop()
    assert stop_result is True
```

## 最佳实践

### 1. 遵循接口契约

始终实现基类定义的所有抽象方法，并遵循方法签名。

### 2. 异步编程

使用 `async`/`await` 进行异步编程，特别是在 I/O 操作中。

### 3. 错误处理

提供有意义的错误信息，并记录适当的日志。

### 4. 配置验证

在初始化时验证配置的有效性。

### 5. 文档注释

为类和方法提供清晰的文档字符串。

### 6. 资源清理

确保在停止适配器时正确清理所有资源。

## 调试适配器

### 1. 启用调试日志

在配置中启用调试模式：

```yaml
core:
  debug_mode: true
  log_level: "DEBUG"
```

### 2. 使用调试方法

在适配器中添加调试辅助方法：

```python
class MyGameAdapter(BaseGameAdapter):
    # ... 其他代码 ...
    
    def debug_info(self):
        """返回调试信息"""
        return {
            "game_name": self.game_name,
            "is_running": self.is_running,
            "window_title": self.window_title,
            "process_status": self._get_process_status()
        }
    
    def _get_process_status(self):
        """获取进程状态（私有方法）"""
        # 实现进程状态检查
        pass
```

通过遵循这些指导原则，您可以创建功能完善、易于维护的适配器，无缝集成到 ScriptZero 框架中。