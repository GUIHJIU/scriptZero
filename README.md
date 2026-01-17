# ScriptZero - 游戏自动化脚本管理框架

ScriptZero 是一个现代化的游戏自动化脚本管理框架，支持多种游戏和自动化脚本框架。它提供了一个统一的接口来管理和执行各种自动化任务。

经过重构，项目现在具有更清晰的模块化架构，实现了核心框架与适配器的完全解耦。

## 特性

- **模块化架构**：使用适配器模式支持多种游戏和脚本框架
- **统一配置**：使用Pydantic进行强类型配置验证
- **命令行接口**：提供统一的命令行工具
- **GUI界面**：提供现代化图形界面（基于PySide6）
- **任务调度**：内置任务调度和执行引擎
- **错误处理**：统一的错误处理和恢复机制
- **结果收集**：完整的执行结果收集和报告

## 安装

1. 克隆项目：
   ```bash
   git clone <repository-url>
   cd scriptzero
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 快速开始

### 使用命令行

```bash
# 启动配置向导
scriptzero config wizard

# 使用配置文件启动自动化
scriptzero start my_config.yaml

# 查看可用适配器
scriptzero list-adapters

# 查看状态
scriptzero status
```

### 使用GUI界面

```bash
# 启动图形界面
python start_gui.py
```

GUI界面提供了完整的配置管理、执行控制和日志查看功能，包括：
- 配置管理（变量、游戏、工作流、脚本配置）
- 主题切换功能
- 执行控制（开始、停止、暂停）
- 日志管理（清空、保存、自动滚动）
- 报告导出功能
- 工作流排序功能

### 使用配置文件

创建一个基本配置文件 `my_config.yaml`：

```yaml
version: "1.0"
project_name: "ScriptZero"
core:
  log_level: "INFO"
  debug_mode: false
game:
  game_name: "Genshin Impact"
  genshin_path: "path/to/YuanShen.exe"
  bettergi_path: "path/to/BetterGI.exe"
  templates_path: "./templates"
  check_interval: 30
  timeout: 3600
  close_after_completion: true
```

## 架构

### 适配器系统

ScriptZero 使用适配器模式来支持不同的游戏和脚本框架：

- **GenshinBetterGIAdapter**: 原神与BetterGI框架适配器
- **PythonAdapter**: Python脚本执行适配器
- **ExeAdapter**: 可执行文件执行适配器
- **AhkAdapter**: AutoHotKey脚本执行适配器

### 配置系统

配置系统使用Pydantic进行数据验证，支持三级配置：

1. **基础配置** (base_config.yaml) - 通用设置
2. **游戏特定配置** (game_config.yaml) - 特定游戏设置
3. **用户覆盖配置** (user_config.yaml) - 个性化设置

### 任务执行引擎

- **任务调度器**: 管理任务队列、优先级和依赖关系
- **执行上下文**: 管理任务执行的上下文信息
- **错误处理器**: 统一处理执行过程中的错误
- **结果收集器**: 收集和报告任务执行结果
- **链式任务调度器**: 支持按顺序执行多个脚本-游戏配对，具有依赖管理和错误处理策略

## 使用方法

### 1. 配置向导

使用交互式配置向导创建配置文件：

```bash
scriptzero config wizard
```

### 2. 启动自动化

```bash
scriptzero start config.yaml
```

### 2.1 执行特定任务链

```bash
scriptzero start config.yaml --chain "链名称"
```

### 3. 管理任务

```bash
# 查看任务状态
scriptzero status

# 停止任务
scriptzero stop <task_id>

# 列出所有任务
scriptzero list-tasks
```

## GUI界面

项目提供现代化的GUI界面，基于PySide6实现：

- **现代化界面**: 使用PySide6提供专业级界面
- **配置管理**: 完整的配置编辑功能
- **执行控制**: 直观的执行控制界面
- **日志查看**: 实时日志显示和管理
- **主题支持**: 支持多种主题切换

启动GUI界面:
```bash
python start_gui.py
```

## 开发

### 项目结构

```
src/
├── adapters/              # 适配器模块
│   ├── base.py           # 适配器基类
│   ├── script_adapters/  # 脚本适配器
│   └── game_adapters/    # 游戏适配器
├── config/               # 配置系统
│   ├── models.py         # 配置模型
│   ├── validators.py     # 配置验证器
│   ├── loader.py         # 配置加载器
│   └── wizard.py         # 配置向导
├── core/                 # 核心模块
│   ├── interfaces/       # 接口定义
│   ├── container.py      # 依赖注入容器
│   └── engine/           # 核心引擎
├── apps/                 # 应用层
│   └── gui/             # GUI应用
├── ui/                   # 用户界面
└── utils/                # 实用工具
```

### 重构说明

根据项目重构计划，旧的脚本文件已被迁移至 `legacy_scripts/` 目录，以保持根目录的整洁。这些文件保留用于参考和向后兼容，但不再是主要的实现方式。

当前架构实现了：
- 核心框架与适配器的完全解耦
- 统一的命令行接口
- 强类型的配置验证系统
- 模块化的架构设计

### 使用方法

#### 启动CLI
```bash
python -m src.cli
```

#### 启动GUI
```bash
python start_gui.py
```

#### 安装依赖
```bash
python install_deps.py
```

### 创建新适配器

1. 继承 `BaseAdapter` 或 `BaseGameAdapter`
2. 实现必要的抽象方法
3. 在适配器注册表中注册新适配器

## 文档

- [快速开始](docs/QUICK_START.md)
- [用户指南](docs/USER_GUIDE.md)
- [开发者指南](docs/DEVELOPER_GUIDE.md)
- [配置说明](docs/CONFIGURATION.md)
- [常见问题](docs/FAQ.md)

## 贡献

欢迎提交Issue和Pull Request来改进项目。

## 许可证

[MIT License](LICENSE)

## 注意事项

- 请遵守游戏使用条款
- 合理使用自动化工具
- 注意账号安全