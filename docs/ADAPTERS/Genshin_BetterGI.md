# 原神与BetterGI自动化适配器

这是一个为《原神》游戏和BetterGI自动化脚本框架设计的适配器，能够自动处理游戏启动、脚本框架启动、自动化操作以及完成判断的完整流程。

## 功能特性

- **自动启动游戏**: 自动启动原神游戏客户端
- **自动启动脚本框架**: 自动启动BetterGI脚本框架
- **智能窗口管理**: 自动切换窗口焦点并执行相应操作
- **自动化启动**: 按照预设流程启动自动化脚本
- **多状态图像识别支持**: 支持不同界面状态的按钮识别
- **完成检测**: 监控自动化操作的完成状态
- **自动关闭**: 可选择在完成后自动关闭游戏和脚本框架

## 权限要求

⚠️ **重要**: 由于原神游戏需要特殊权限，建议以管理员身份运行自动化脚本：

1. **以管理员身份运行命令提示符/PowerShell**
2. **确保BetterGI和原神也以兼容的权限级别运行**

如果遇到"拒绝访问"错误，请检查权限设置。

## BetterGI界面状态说明

BetterGI具有多个界面状态，需要针对不同状态制作模板：

### 1. 初始状态
- **启动按钮**: 灰色按钮，白色字体，带三角形图标和"启动"字样
- **一条龙按钮**: 初始状态（未点击）
- **蓝色三角形启动按钮**: 不存在

### 2. 点击一条龙后状态
- **一条龙按钮**: 变为点击后状态
- **蓝色三角形启动按钮**: 出现

## 图像识别功能详解

### 图像识别优先级策略

适配器采用"多模板匹配优先，坐标点击备选"的策略：

1. **多模板匹配**: 系统尝试匹配多个可能的模板，使用第一个匹配成功的
2. **状态感知**: 针对不同界面状态提供相应的模板
3. **备选坐标点击**: 如果所有模板都匹配失败，则使用配置的坐标进行点击

### 图像模板配置

在配置文件中定义不同状态的图像模板：

```
image_templates:
  # BetterGI初始状态
  bettergi_initial_start_btn: "templates/bettergi_initial_start_btn.png"
  bettergi_dragon_btn_before: "templates/bettergi_dragon_btn_before.png"
  # BetterGI点击一条龙后状态
  bettergi_blue_play_btn: "templates/bettergi_blue_play_btn.png"
  bettergi_dragon_btn_after: "templates/bettergi_dragon_btn_after.png"
  # 通用模板（备用）
  bettergi_start_btn: "templates/bettergi_start_btn.png"
  bettergi_dragon_btn: "templates/bettergi_dragon_btn.png"
  bettergi_play_btn: "templates/bettergi_play_btn.png"
```

### 图像识别参数

- `image_match_confidence`: 图像匹配置信度（默认0.7，范围0.0-1.0）
- `max_retry_attempts`: 最大重试次数（默认3次）
- `retry_delay`: 重试间隔（默认1.0秒）

## 如何制作图像模板

### 方法一：使用图像模板生成工具（推荐）

```
python image_template_generator.py
```

### 方法二：手动制作模板

#### 1. 初始启动按钮模板
1. 打开BetterGI，确保显示灰色启动按钮
2. 截取启动按钮区域（灰色按钮，白色字体，三角形图标+"启动"字样）
3. 保存为`bettergi_initial_start_btn.png`

#### 2. 一条龙按钮模板（点击前）
1. 在BetterGI界面找到一条龙按钮
2. 截取按钮区域（点击前状态）
3. 保存为`bettergi_dragon_btn_before.png`

#### 3. 蓝色三角形启动按钮模板
1. 点击一条龙按钮后，等待蓝色三角形启动按钮出现
2. 截取蓝色三角形启动按钮区域
3. 保存为`bettergi_blue_play_btn.png`

### 模板制作要点

1. **清晰度**: 确保图像清晰，避免模糊
2. **大小适中**: 模板不宜过大或过小，一般50x50到200x200像素为宜
3. **背景简单**: 尽量选择背景相对简单的元素
4. **多角度准备**: 为同一元素准备多个角度的模板提高识别率
5. **状态覆盖**: 确保覆盖所有可能的界面状态

## 使用方法

### 1. 基本使用

```
python genshin_automation_starter.py
```

### 2. 交互式设置

```
python genshin_automation_starter.py --setup
```

### 3. 使用自定义配置文件

```
python genshin_automation_starter.py path/to/your/config.yaml
```

## 配置说明

### 基本配置参数

- `genshin_path`: 原神游戏可执行文件路径
- `bettergi_path`: BetterGI脚本框架可执行文件路径
- `check_interval`: 检查自动化完成状态的间隔（秒）
- `timeout`: 最大执行时间（秒）
- `close_after_completion`: 完成后是否自动关闭游戏和脚本框架
- `image_confidence`: 图像识别置信度
- `click_positions`: 各个按钮在界面的坐标（备用）

### BetterGI工作流配置

```
bettergi_workflow:
  steps:
    - name: "点击初始启动按钮"
      action: "click"
      templates: ["templates/bettergi_initial_start_btn.png", "templates/bettergi_start_btn.png"]
      fallback_coords: [150, 200]
      delay_after: 3
    - name: "点击一条龙按钮"
      action: "click"
      templates: ["templates/bettergi_dragon_btn_before.png", "templates/bettergi_dragon_btn.png"]
      fallback_coords: [250, 150]
      delay_after: 5
    - name: "等待蓝色启动按钮出现"
      action: "wait_for_image"
      template: "templates/bettergi_blue_play_btn.png"
      timeout: 10
      delay_after: 2
    - name: "点击蓝色启动按钮"
      action: "click"
      templates: ["templates/bettergi_blue_play_btn.png", "templates/bettergi_play_btn.png"]
      fallback_coords: [350, 150]
      delay_after: 2
```

## 工作流程

1. **启动脚本框架**: 启动BetterGI脚本框架并等待其完全加载
2. **启动游戏**: 启动原神游戏并等待其完全加载
3. **激活脚本框架**: 切换焦点到脚本框架
4. **多状态识别启动按钮**: 尝试匹配初始启动按钮（灰色）或通用启动按钮
5. **等待焦点切换**: 等待脚本框架将焦点切换至原神游戏
6. **重新激活脚本框架**: 再次切换焦点回脚本框架
7. **多状态识别一条龙按钮**: 尝试匹配不同状态的一条龙按钮
8. **等待蓝色启动按钮出现**: 监控界面变化，等待蓝色启动按钮出现
9. **多状态识别启动按钮**: 尝试匹配蓝色启动按钮或通用播放按钮
10. **监控完成**: 使用图像识别监控自动化操作的完成状态
11. **清理**: 根据配置决定是否关闭游戏和脚本框架

## 完成判断机制

自动化操作的完成可以通过以下几种方式判断：

1. **进程监控**: 监控BetterGI或原神进程是否退出
2. **时间超时**: 达到预设的最大执行时间
3. **图像识别**: 通过图像识别检测特定完成标志

## 注意事项

1. **图像模板质量**: 高质量的图像模板是成功识别的关键
2. **置信度设置**: 过高的置信度可能导致识别失败，过低可能导致误识别
3. **分辨率适配**: 图像模板应与游戏运行时的分辨率匹配
4. **权限问题**: 确保脚本有足够的权限操作游戏和脚本框架窗口
5. **防封策略**: 建议合理设置操作间隔，避免过于频繁的操作
6. **界面状态**: 确保为所有可能的界面状态准备了模板

## 故障排除

### 图像识别常见问题

1. **识别失败**:
   - 检查图像模板是否清晰
   - 调低置信度阈值
   - 确认游戏分辨率与模板匹配
   - 确保覆盖所有可能的界面状态

2. **误识别**:
   - 提高置信度阈值
   - 优化图像模板，减少背景干扰

3. **性能问题**:
   - 增加重试间隔
   - 优化图像模板大小

### 调试方法

1. 降低[PAUSE](file:///E:/WORKSPACE/Python/scriptZero/src/game_automation_framework.py#L28-L28)值以便观察操作过程
2. 启用详细日志记录
3. 使用截图验证当前屏幕状态
4. 逐步执行各个阶段以定位问题

## 扩展性

该适配器设计具有良好的扩展性，您可以：

1. **自定义完成判断**: 继承适配器类并重写`check_completion_indicators`方法
2. **添加图像识别**: 集成OpenCV进行更精确的图像识别
3. **多游戏支持**: 修改适配器以支持其他游戏和脚本框架组合
4. **高级图像处理**: 实现颜色识别、OCR文字识别等高级功能

## 安全声明

请遵守游戏使用条款，合理使用自动化工具，避免违反游戏规则导致账号风险。