# ScriptZero 项目结构说明

## 概述
ScriptZero 是一个现代化的游戏自动化脚本管理框架，经过重构后采用了清晰的模块化架构。

## 当前根目录结构

### 核心入口文件
- [main.py](file:///E:/WORKSPACE/Python/scriptZero/main.py) - 主程序入口
- [start_gui.py](file:///E:/WORKSPACE/Python/scriptZero/start_gui.py) - GUI启动器
- [scriptzero.py](file:///E:/WORKSPACE/Python/scriptZero/scriptzero.py) - CLI入口

### 配置文件
- [requirements.txt](file:///E:/WORKSPACE/Python/scriptZero/requirements.txt) - 项目依赖配置
- [example_full_config.yaml](file:///E:/WORKSPACE/Python/scriptZero/example_full_config.yaml) - 示例配置文件
- [genshin_bettergi_config.yaml](file:///E:/WORKSPACE/Python/scriptZero/genshin_bettergi_config.yaml) - 原神适配器配置文件

### 文档文件
- [README.md](file:///E:/WORKSPACE/Python/scriptZero/README.md) - 主要项目说明文档
- [CHANGES_SUMMARY.md](file:///E:/WORKSPACE/Python/scriptZero/CHANGES_SUMMARY.md) - 重构与优化总结
- [GENSHIN_BETTERGI_ADAPTER.md](file:///E:/WORKSPACE/Python/scriptZero/GENSHIN_BETTERGI_ADAPTER.md) - 原神BetterGI适配器详细说明

### 工具脚本
- [image_template_generator.py](file:///E:/WORKSPACE/Python/scriptZero/image_template_generator.py) - 图像模板生成工具
- [install_deps.py](file:///E:/WORKSPACE/Python/scriptZero/install_deps.py) - 依赖安装脚本

### 项目目录
- [src/](file:///E:/WORKSPACE/Python/scriptZero/src/) - 源代码目录（采用分层架构）
- [docs/](file:///E:/WORKSPACE/Python/scriptZero/docs/) - 项目文档
- [templates/](file:///E:/WORKSPACE/Python/scriptZero/templates/) - 图像识别模板
- [tests/](file:///E:/WORKSPACE/Python/scriptZero/tests/) - 测试文件
- [legacy_scripts/](file:///E:/WORKSPACE/Python/scriptZero/legacy_scripts/) - 历史脚本文件（已迁移）
- [coverage_report/](file:///E:/WORKSPACE/Python/scriptZero/coverage_report/) - 代码覆盖率报告

## 项目架构

### src/ 目录结构
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

## 重构说明

根据项目重构计划，以下文件已被迁移至 [legacy_scripts/](file:///E:/WORKSPACE/Python/scriptZero/legacy_scripts/) 目录：
- 旧的适配器文件
- 旧的启动脚本
- 临时测试文件
- 调试脚本

这些文件保留用于参考和向后兼容，但不再是主要的实现方式。

## 使用方法

### 启动CLI
```bash
python -m src.cli
```

### 启动GUI
```bash
python start_gui.py
```

### 安装依赖
```bash
python install_deps.py
```