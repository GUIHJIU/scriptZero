# ScriptZero 快速开始

欢迎使用 ScriptZero - 游戏自动化脚本管理框架！

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

## 快速运行

### 使用命令行

```bash
# 启动自动化任务
scriptzero start my_config.yaml

# 查看可用适配器
scriptzero list-adapters

# 配置向导
scriptzero config wizard
```

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

## 基本概念

- **适配器(Adapter)**: 与特定游戏或脚本框架交互的组件
- **配置(Configuration)**: 控制自动化行为的设置
- **任务(Task)**: 需要执行的自动化操作序列
- **模板(Template)**: 用于图像识别的参考图像

## 下一步

- 阅读 [USER_GUIDE.md](file:///E:/WORKSPACE/Python/scriptZero/docs/USER_GUIDE.md) 了解详细使用方法
- 查看 [DEVELOPER_GUIDE.md](file:///E:/WORKSPACE/Python/scriptZero/docs/DEVELOPER_GUIDE.md) 了解开发细节
- 查看适配器文档了解特定游戏的支持情况