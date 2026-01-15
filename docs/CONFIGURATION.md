# ScriptZero 配置说明

## 配置系统概述

ScriptZero 采用三级配置系统，允许灵活的配置管理和覆盖：

1. **基础配置**(Base Config) - 默认系统配置
2. **特定配置**(Specific Config) - 游戏或适配器特定配置  
3. **用户覆盖**(User Override) - 用户个性化配置

配置按优先级从低到高依次加载，高优先级配置会覆盖低优先级配置的相同项。

## 配置文件格式

ScriptZero 支持 YAML 和 JSON 格式的配置文件，默认使用 YAML。

### 配置文件位置

- 基础配置: `src/config/base_config.yaml`
- 游戏配置: `src/config/game_config.yaml` 
- 用户配置: `src/config/user_config.yaml`

## 主配置结构

```yaml
version: "1.0"                    # 配置版本
project_name: "ScriptZero"        # 项目名称
core:                             # 核心配置
  log_level: "INFO"               # 日志级别
  log_file: "logs/app.log"        # 日志文件路径
  debug_mode: false               # 调试模式
  max_workers: 4                  # 最大工作线程数
  temp_dir: "./temp"              # 临时文件目录
game:                             # 游戏配置
  game_name: "Genshin Impact"     # 游戏名称
  genshin_path: ""                # 原神路径
  bettergi_path: ""               # BetterGI路径
  templates_path: "templates"     # 模板路径
  check_interval: 30              # 检查间隔(秒)
  timeout: 3600                   # 超时时间(秒)
  close_after_completion: true    # 完成后关闭
  image_templates:                # 图像模板配置
    initial_start_btn: "templates/bettergi_initial_start_btn.png"
    dragon_btn_before: "templates/bettergi_dragon_btn_before.png"
    blue_play_btn: "templates/bettergi_blue_play_btn.png"
    automation_complete: "templates/automation_complete.png"
  bettergi_workflow:              # BetterGI工作流配置
    steps:
      - name: "点击初始启动按钮"
        templates: ["templates/bettergi_initial_start_btn.png"]
        fallback_coords: [150, 200]
        delay_after: 3
adapters:                         # 适配器配置
  - name: "genshin_bettergi"
    type: "game"
    enabled: true
    config:
      genshin_path: "F:/Genshin Impact/Genshin Impact Game/YuanShen.exe"
      bettergi_path: "F:/better/BetterGI.exe"
```

## 核心配置项

### 日志配置

```yaml
core:
  log_level: "DEBUG|INFO|WARNING|ERROR|CRITICAL"  # 日志级别
  log_file: "path/to/logfile.log"                 # 日志文件路径
  debug_mode: true|false                         # 是否启用调试模式
```

### 性能配置

```yaml
core:
  max_workers: 1-16                              # 最大工作线程数
  temp_dir: "path/to/temp/dir"                   # 临时文件目录
```

## 游戏配置项

### 基本信息

```yaml
game:
  game_name: "游戏名称"                          # 游戏名称
  genshin_path: "path/to/genshin.exe"           # 游戏可执行文件路径
  bettergi_path: "path/to/bettergi.exe"         # 脚本框架可执行文件路径
```

### 时间配置

```yaml
game:
  check_interval: 10-300                        # 检查间隔(秒)，建议30-60
  timeout: 1800-14400                           # 超时时间(秒)，建议1-4小时
  close_after_completion: true|false            # 完成后是否关闭程序
```

### 图像模板配置

```yaml
game:
  templates_path: "path/to/templates"            # 模板文件根目录
  image_templates:                               # 图像模板映射
    initial_start_btn: "templates/initial_start.png"
    dragon_btn_before: "templates/dragon_before.png"
    blue_play_btn: "templates/blue_play.png"
    automation_complete: "templates/complete.png"
```

## 适配器配置

### 适配器结构

```yaml
adapters:
  - name: "适配器名称"                           # 适配器唯一标识
    type: "game|script|communication"           # 适配器类型
    enabled: true|false                         # 是否启用
    config:                                     # 适配器特定配置
      param1: "value1"
      param2: 123
```

### 游戏适配器配置示例

```yaml
adapters:
  - name: "genshin_bettergi"
    type: "game"
    enabled: true
    config:
      game_name: "Genshin Impact"
      genshin_path: "F:/Genshin Impact/Genshin Impact Game/YuanShen.exe"
      bettergi_path: "F:/better/BetterGI.exe"
      templates_path: "./templates"
      check_interval: 30
      timeout: 7200
      close_after_completion: true
```

### 脚本适配器配置示例

```yaml
adapters:
  - name: "python_script"
    type: "script"
    enabled: true
    config:
      script_path: "scripts/my_script.py"
      arguments: ["--arg1", "value1"]
```

## 工作流配置

### BetterGI工作流

```yaml
game:
  bettergi_workflow:
    steps:
      - name: "步骤名称"
        action: "click|wait_for_image|activate_window"  # 动作类型
        templates: ["templates/template1.png"]          # 使用的模板列表
        fallback_coords: [x, y]                        # 备用坐标
        delay_after: 2.5                              # 执行后延迟(秒)
        timeout: 10                                    # 步骤超时(秒)
```

## 验证规则

### 必填项

- `version`: 配置版本号
- `game.game_name`: 游戏名称
- `game.genshin_path`: 游戏可执行文件路径（如适用）
- `game.bettergi_path`: 脚本框架可执行文件路径（如适用）

### 路径验证

- 所有可执行文件路径必须存在且可访问
- 模板文件路径必须存在
- 日志目录必须存在或可创建

### 数值范围

- `check_interval`: 1-3600秒
- `timeout`: 60-86400秒（1天）
- `max_workers`: 1-32

## 配置验证

### 命令行验证

```bash
scriptzero config validate config.yaml
```

### 程序化验证

```python
from src.config.loader import ConfigLoader
from src.config.validators import ConfigValidator

loader = ConfigLoader()
config = loader.load_from_single_file('config.yaml')
# 验证已在加载过程中自动完成
```

## 配置最佳实践

### 安全性

- 不要在配置中存储敏感信息（密码、密钥等）
- 使用环境变量或安全存储替代敏感配置

### 可维护性

- 使用有意义的配置键名
- 添加注释说明复杂配置项
- 按功能模块组织配置

### 性能优化

- 合理设置检查间隔，避免过于频繁
- 优化图像模板大小和数量
- 启用必要的日志级别，避免过度日志

### 版本控制

- 将基础配置加入版本控制
- 使用 .gitignore 排除用户特定配置
- 为不同环境维护不同配置分支