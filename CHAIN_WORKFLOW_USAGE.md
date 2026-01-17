# 链式任务执行功能使用指南

## 概述

ScriptZero 支持链式任务执行功能，允许用户按顺序执行多个脚本-游戏配对，并支持依赖关系管理、错误处理策略等功能。

## 配置文件结构

在配置文件中，通过 `workflow` 部分定义任务链：

```yaml
version: "1.0"
name: "ScriptZero链式任务示例"

variables:
  game_path: "C:/Games/Genshin Impact/YuanShen.exe"
  scripts_dir: "./scripts"

games:
  genshin:
    executable: "${variables.game_path}"
    arguments: ["-fullscreen"]
    window_title: "原神"
  honkai_star_rail:
    executable: "C:/Games/Honkai Star Rail/HonkaiStarRail.exe"
    arguments: ["-windowed"]
    window_title: "崩坏：星穹铁道"

scripts:
  - path: "${variables.scripts_dir}/genshin_daily.py"
    type: "python"
    arguments: ["--mode", "daily"]
    completion:
      timeout: 3600
  - path: "${variables.scripts_dir}/hsr_daily.py"
    type: "python"
    arguments: ["--mode", "daily"]
    completion:
      timeout: 3600

workflow:
  - name: "日常任务链"
    type: "task_chain"
    config:
      error_handling: "continue"  # 可选: continue, stop, retry
      tasks:
        - id: "task_genshin_daily"
          name: "原神日常任务"
          game: "genshin"
          script: "${variables.scripts_dir}/genshin_daily.py"
          parameters:
            start_time: "09:00"
            timeout: 3600
            script_path: "${variables.scripts_dir}/genshin_daily.py"
            arguments: ["--mode", "daily"]
          enabled: true
        - id: "task_hsr_daily"
          name: "星穹铁道日常任务"
          game: "honkai_star_rail"
          script: "${variables.scripts_dir}/hsr_daily.py"
          parameters:
            start_time: "10:00"
            timeout: 3600
            script_path: "${variables.scripts_dir}/hsr_daily.py"
            arguments: ["--mode", "daily"]
          enabled: true
          depends_on: ["task_genshin_daily"]  # 依赖于原神日常任务完成
    enabled: true
```

## 配置说明

### 任务链配置 (`task_chain`)

- `error_handling`: 错误处理策略
  - `continue`: 遇到错误时继续执行后续任务
  - `stop`: 遇到错误时停止整个链
  - `retry`: 遇到错误时重试

### 任务配置

- `id`: 任务唯一标识符
- `name`: 任务名称（用于显示）
- `game`: 游戏配置名称（对应 `games` 部分的键）
- `script`: 脚本路径（对应 `scripts` 部分的路径）
- `parameters`: 传递给脚本的参数
- `enabled`: 是否启用此任务
- `depends_on`: 依赖的任务ID列表（只有在依赖任务完成后才会执行）

## 命令行使用

### 执行指定的任务链

```bash
python -m src.cli start config.yaml --chain "链名称"
```

例如：
```bash
python -m src.cli start example_chain_config.yaml --chain "日常任务链"
```

## 功能特点

### 1. 顺序执行
任务严格按照配置顺序执行，确保执行时序的可靠性。

### 2. 依赖管理
支持任务间的依赖关系，只有在依赖任务完成后才会执行当前任务。

### 3. 错误处理
支持多种错误处理策略：
- 继续执行
- 停止链
- 重试机制

### 4. 状态监控
实时监控任务执行状态，包括：
- 待执行
- 运行中
- 已完成
- 失败
- 跳过

### 5. 资源管理
控制并发执行数量，避免系统资源冲突。

## 使用场景

1. **多游戏日常任务**: 按顺序执行多个游戏的日常任务
2. **复杂自动化流程**: 需要按特定顺序执行的复杂自动化任务
3. **依赖任务执行**: 存在依赖关系的任务序列
4. **批处理作业**: 需要顺序执行的批处理任务

## 注意事项

1. 确保配置文件格式正确
2. 依赖关系不能形成循环
3. 合理设置超时时间，避免长时间等待
4. 监控系统资源使用情况
5. 测试配置文件后再正式运行