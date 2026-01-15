"""
ScriptZero 命令行接口
统一管理所有功能入口
"""
import typer
import asyncio
import sys
from typing import Optional
from pathlib import Path
import yaml
import os

# 导入必要的模块
from src.config.loader import ConfigLoader
from src.config.wizard import ConfigWizard
from src.adapters.game_adapters.genshin_bettergi import GenshinBetterGIAdapter
from src.engine.task_scheduler import TaskScheduler, Task, TaskPriority
from src.engine.execution_context import ExecutionContextManager, create_execution_context
from src.engine.error_handler import ErrorHandler, ErrorSeverity, ErrorCategory
from src.engine.result_collector import ResultCollector, TaskResult, ResultStatus

# 创建Typer应用
app = typer.Typer(
    name="scriptzero",
    help="ScriptZero - 游戏自动化脚本管理框架",
    epilog="使用 'scriptzero COMMAND --help' 获取特定命令的帮助信息"
)


@app.command()
def start(config_path: str = typer.Argument(..., help="配置文件路径"),
          debug: bool = typer.Option(False, "--debug", "-d", help="启用调试模式")):
    """
    启动自动化任务
    """
    print(f"启动自动化任务，配置文件: {config_path}")
    
    try:
        # 加载配置
        loader = ConfigLoader()
        config = loader.load_from_single_file(config_path)
        
        # 设置调试模式
        if debug:
            config.core.debug_mode = True
            config.core.log_level = "DEBUG"
        
        print(f"已加载配置: {config.project_name} (版本 {config.version})")
        print(f"游戏: {config.game.game_name}")
        
        # 根据配置创建并运行适配器
        asyncio.run(_run_adapter_from_config(config))
        
    except FileNotFoundError:
        print(f"错误: 配置文件不存在 - {config_path}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@app.command()
def stop(task_id: str = typer.Argument(..., help="任务ID")):
    """
    停止指定任务
    """
    print(f"停止任务: {task_id}")
    # 实现任务停止逻辑
    print("任务停止功能待实现")


@app.command()
def status():
    """
    查看当前状态
    """
    print("当前状态:")
    print("- 任务调度器: 待实现")
    print("- 运行中任务: 待实现")
    print("- 系统资源: 待实现")


@app.command()
def list_adapters():
    """
    列出可用适配器
    """
    print("可用适配器:")
    print("- GenshinBetterGIAdapter: 原神与BetterGI框架适配器")
    print("- PythonAdapter: Python脚本执行适配器")
    print("- ExeAdapter: 可执行文件执行适配器")
    print("- AhkAdapter: AutoHotKey脚本执行适配器")
    print("- BetterGIAdapter: BetterGI通用游戏适配器")


@app.command()
def config(subcommand: str = typer.Argument(..., help="配置子命令: wizard, validate, create-default"),
          config_path: Optional[str] = typer.Option(None, "--config", "-c", help="配置文件路径")):
    """
    配置管理命令
    """
    if subcommand == "wizard":
        print("启动配置向导...")
        run_config_wizard()
    elif subcommand == "validate":
        if not config_path:
            print("错误: 验证配置需要指定配置文件路径")
            return
        
        try:
            loader = ConfigLoader()
            config = loader.load_from_single_file(config_path)
            print(f"配置验证成功: {config_path}")
            print(f"项目: {config.project_name}")
            print(f"游戏: {config.game.game_name}")
        except Exception as e:
            print(f"配置验证失败: {str(e)}")
    elif subcommand == "create-default":
        game_name = typer.prompt("请输入游戏名称", default="Genshin Impact")
        loader = ConfigLoader()
        config = loader.create_default_config(game_name)
        
        output_path = typer.prompt("请输入输出配置文件路径", default="default_config.yaml")
        loader.save_config(config, output_path)
        print(f"默认配置已创建: {output_path}")
    else:
        print(f"未知的配置子命令: {subcommand}")
        print("可用子命令: wizard, validate, create-default")


@app.command()
def plugin(subcommand: str = typer.Argument(..., help="插件子命令: install, list, uninstall")):
    """
    插件管理命令
    """
    if subcommand == "install":
        print("插件安装功能待实现")
    elif subcommand == "list":
        print("当前没有可列出的插件")
    elif subcommand == "uninstall":
        print("插件卸载功能待实现")
    else:
        print(f"未知的插件子命令: {subcommand}")
        print("可用子命令: install, list, uninstall")


@app.command()
def task_info(task_id: str = typer.Argument(..., help="任务ID")):
    """
    获取任务详细信息
    """
    print(f"任务 {task_id} 信息: 待实现")


@app.command()
def list_tasks():
    """
    列出所有任务
    """
    print("任务列表: 待实现")


@app.command()
def version():
    """
    显示版本信息
    """
    print("ScriptZero v1.0.0")
    print("游戏自动化脚本管理框架")


def run_config_wizard():
    """运行配置向导"""
    wizard = ConfigWizard()
    config = wizard.run_interactive_setup()
    
    # 询问保存位置
    print(f"\n配置生成完成!")
    save_path = input("请输入配置文件保存路径 (默认: config.yaml): ").strip()
    if not save_path:
        save_path = "config.yaml"
    
    wizard.save_config(config, save_path)
    
    print(f"\n配置向导完成! 您可以使用以下命令启动自动化:")
    print(f"scriptzero start {save_path}")


async def _run_adapter_from_config(config):
    """根据配置运行适配器"""
    print("初始化适配器...")
    
    # 创建任务调度器
    scheduler = TaskScheduler(max_concurrent=1)  # 适配器通常串行执行
    
    # 根据配置创建适配器
    adapter = None
    if config.game.game_name.lower() in ["genshin impact", "genshin", "yuanshen"]:
        # 创建原神BetterGI适配器
        adapter_config = {
            'game_name': config.game.game_name,
            'genshin_path': config.game.genshin_path,
            'bettergi_path': config.game.bettergi_path,
            'templates_path': config.game.templates_path,
            'check_interval': config.game.check_interval,
            'timeout': config.game.timeout,
            'close_after_completion': config.game.close_after_completion,
            'image_templates': config.game.image_templates.dict() if config.game.image_templates else {},
            'bettergi_workflow': config.game.bettergi_workflow.dict() if config.game.bettergi_workflow else {}
        }
        
        adapter = GenshinBetterGIAdapter(adapter_config)
    
    if adapter is None:
        print(f"错误: 不支持的游戏类型: {config.game.game_name}")
        return False
    
    print("启动适配器...")
    
    # 创建执行上下文
    ctx = create_execution_context(metadata={
        "game": config.game.game_name,
        "adapter_type": "GenshinBetterGIAdapter",
        "config_path": str(Path.cwd())
    })
    
    async with ctx.context():
        # 启动适配器
        start_success = await adapter.start()
        if not start_success:
            print("适配器启动失败")
            return False
        
        print("执行自动化任务...")
        
        # 执行主要任务
        try:
            result = await adapter.execute()
            print(f"任务执行结果: {result}")
        except Exception as e:
            print(f"任务执行失败: {str(e)}")
            return False
        finally:
            # 停止适配器
            print("停止适配器...")
            await adapter.stop()
    
    print("自动化任务完成")
    return True


def main():
    """主入口函数"""
    app()


if __name__ == "__main__":
    main()