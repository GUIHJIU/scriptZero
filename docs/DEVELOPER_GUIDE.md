# ScriptZero 开发者指南

## 架构概览

ScriptZero 采用模块化架构，主要包括以下几个核心组件：

- **核心引擎**(Core Engine): 任务调度和执行
- **适配器系统**(Adapters): 与外部系统交互
- **配置系统**(Configuration): 配置管理和验证
- **UI系统**(UI): 用户界面
- **实用工具**(Utilities): 通用功能

## 项目结构

```
src/
├── adapters/          # 适配器模块
│   ├── base.py        # 适配器基类
│   ├── script_adapters/ # 脚本适配器
│   └── game_adapters/ # 游戏适配器
├── config/            # 配置系统
│   ├── models.py      # 配置模型
│   ├── validators.py  # 配置验证器
│   └── loader.py      # 配置加载器
├── core/              # 核心模块
│   ├── interfaces/    # 接口定义
│   ├── container.py   # 依赖注入容器
│   └── engine/        # 核心引擎
├── ui/                # 用户界面
└── utils/             # 实用工具
```

## 开发环境设置

### 环境要求

- Python 3.8+
- pip 包管理器
- Git 版本控制

### 开发依赖

安装开发依赖：

```bash
pip install -r requirements-dev.txt
```

### 代码风格

遵循 PEP 8 编码规范，使用 black 进行代码格式化：

```bash
black .
```

## 核心概念

### 适配器模式

适配器是 ScriptZero 的核心扩展点，所有外部系统交互都通过适配器实现。

#### 创建新适配器

1. 继承 [BaseAdapter](file:///E:/WORKSPACE/Python/scriptZero/src/adapters/base.py#L10-L32) 或 [BaseGameAdapter](file:///E:/WORKSPACE/Python/scriptZero/src/adapters/game_adapters/base_game_adapter.py#L11-L35)
2. 实现必要的抽象方法
3. 在适配器注册表中注册

示例：

```python
from src.adapters.base import BaseAdapter

class MyCustomAdapter(BaseAdapter):
    def __init__(self, config):
        super().__init__(config)
        self.custom_param = config.get('custom_param', 'default')

    async def start(self):
        # 启动逻辑
        pass

    async def stop(self):
        # 停止逻辑
        pass

    async def execute(self, *args, **kwargs):
        # 执行逻辑
        pass
```

### 配置系统

配置系统使用 Pydantic 进行数据验证和模型定义。

#### 创建配置模型

```python
from pydantic import BaseModel, Field

class MyAdapterConfig(BaseModel):
    param1: str = Field(..., description="参数1描述")
    param2: int = Field(10, description="参数2描述")
```

### 依赖注入

ScriptZero 使用依赖注入容器管理组件生命周期：

```python
from src.core.container import Container

container = Container()
container.register('my_service', MyService)
service = container.resolve('my_service')
```

## 扩展开发

### 添加新功能

1. 在对应模块中创建新类或函数
2. 更新接口定义（如适用）
3. 添加单元测试
4. 更新文档

### 添加新适配器

1. 在 `src/adapters/` 相应子目录中创建适配器
2. 继承适当的基类
3. 实现接口方法
4. 在适配器工厂中注册

### 添加新配置选项

1. 在 `src/config/models.py` 中扩展配置模型
2. 添加相应的验证逻辑
3. 更新文档

## 测试

### 单元测试

运行单元测试：

```bash
pytest tests/unit/
```

### 集成测试

运行集成测试：

```bash
pytest tests/integration/
```

### 测试覆盖率

检查测试覆盖率：

```bash
pytest --cov=src tests/
```

## 发布流程

### 版本管理

使用语义化版本控制 (SemVer)：

- 主版本号：重大变更，不向后兼容
- 次版本号：新增功能，向后兼容
- 修订号：修复bug，向后兼容

### 发布步骤

1. 更新版本号
2. 更新 CHANGELOG.md
3. 运行完整测试套件
4. 创建发布分支
5. 合并到主分支
6. 创建 Git 标签
7. 构建发布包

## 贡献指南

### 代码提交

- 提交信息应清晰描述更改内容
- 遵循约定式提交规范
- 确保代码通过所有测试

### 分支管理

- `main`: 生产就绪代码
- `develop`: 开发主线
- `feature/*`: 功能分支
- `hotfix/*`: 紧急修复分支

### 代码审查

所有 PR 都需要经过代码审查，重点关注：

- 代码质量和可读性
- 测试覆盖率
- 文档完整性
- 性能影响
- 安全性考虑