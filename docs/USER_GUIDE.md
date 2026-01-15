# ScriptZero 用户指南

## 概述

ScriptZero 是一个灵活的游戏自动化脚本管理框架，支持多种游戏和自动化脚本框架。

## 安装与环境准备

### 系统要求

- Python 3.8 或更高版本
- Windows 10/11 (部分功能依赖Windows特定API)
- 管理员权限 (某些游戏需要)

### 依赖安装

```bash
pip install -r requirements.txt
```

### 可选依赖

如需使用高级图像识别功能，安装 OpenCV:

```bash
pip install opencv-python
```

## 配置系统

### 配置文件格式

ScriptZero 使用 YAML 格式的配置文件，支持三级配置系统：

1. **基础配置**(base_config.yaml) - 通用设置
2. **游戏特定配置**(game_config.yaml) - 特定游戏设置
3. **用户覆盖配置**(user_config.yaml) - 个人偏好设置

### 配置向导

使用配置向导快速生成配置文件：

```bash
scriptzero config wizard
```

### 主要配置项

#### 核心配置
```yaml
core:
  log_level: "INFO"           # 日志级别
  log_file: "app.log"         # 日志文件路径
  debug_mode: false           # 调试模式
  max_workers: 4             # 最大工作线程数
  temp_dir: "./temp"         # 临时文件目录
```

#### 游戏配置
```yaml
game:
  game_name: "Genshin Impact"  # 游戏名称
  genshin_path: "path/to/game" # 游戏路径
  bettergi_path: "path/to/bettergi" # 脚本框架路径
  templates_path: "./templates" # 模板文件路径
  check_interval: 30           # 检查间隔(秒)
  timeout: 3600               # 超时时间(秒)
  close_after_completion: true # 完成后关闭
```

## 适配器系统

ScriptZero 使用适配器模式支持不同游戏和脚本框架：

### 可用适配器

- **GenshinBetterGIAdapter**: 原神与BetterGI框架
- **PythonAdapter**: Python脚本执行
- **ExeAdapter**: 可执行文件执行
- **AhkAdapter**: AutoHotKey脚本执行

### 适配器配置

```yaml
adapters:
  - name: "genshin_bettergi"
    type: "game"
    enabled: true
    config:
      genshin_path: "path/to/genshin.exe"
      bettergi_path: "path/to/bettergi.exe"
```

## 命令行使用

### 基本命令

```bash
# 启动自动化任务
scriptzero start config.yaml

# 停止任务
scriptzero stop <task_id>

# 查看状态
scriptzero status

# 列出可用适配器
scriptzero list-adapters

# 验证配置
scriptzero config validate config.yaml
```

### 任务管理

```bash
# 查看所有任务
scriptzero list-tasks

# 获取任务详情
scriptzero task-info <task_id>

# 重启任务
scriptzero restart <task_id>
```

## 图像识别

ScriptZero 支持基于图像模板的识别功能：

### 模板制作

1. 使用截图工具截取目标元素
2. 保存为PNG格式
3. 确保模板清晰且背景简单

### 模板配置

```yaml
image_templates:
  start_button: "templates/start_button.png"
  complete_flag: "templates/complete_flag.png"
```

## 故障排除

### 常见问题

1. **权限错误**
   - 确保以管理员身份运行
   - 检查游戏和脚本框架的权限设置

2. **图像识别失败**
   - 检查模板文件是否存在
   - 确认游戏分辨率与模板匹配
   - 调整图像识别置信度

3. **窗口激活失败**
   - 检查游戏是否正常运行
   - 确认窗口标题与预期一致

### 调试模式

启用调试模式获取更多信息：

```bash
scriptzero start --debug config.yaml
```

## 最佳实践

1. **配置管理**
   - 使用版本控制管理配置文件
   - 为不同环境创建不同的配置

2. **模板优化**
   - 定期更新图像模板
   - 为不同界面状态准备模板

3. **安全性**
   - 遵守游戏使用条款
   - 合理设置操作间隔