"""
配置向导
提供交互式配置生成界面
"""
import os
import sys
from typing import Dict, Any, Optional
from pathlib import Path
import yaml
from .models import ConfigSimplifier, MainConfiguration


class ConfigWizard:
    """配置向导"""
    
    def __init__(self):
        self.config_data: Dict[str, Any] = {}
        self.supported_games = [
            "Genshin Impact",
            "Honkai Impact 3rd",
            "Blue Archive",
            "Other"
        ]
        
        self.supported_adapters = [
            "BetterGI (Genshin)",
            "Python Script",
            "Executable",
            "AutoHotKey",
            "Custom"
        ]
    
    def run_interactive_setup(self) -> MainConfiguration:
        """运行交互式设置"""
        print("=" * 50)
        print("ScriptZero 配置向导")
        print("=" * 50)
        
        # 询问游戏类型
        print("\n请选择您要自动化的游戏:")
        for i, game in enumerate(self.supported_games, 1):
            print(f"{i}. {game}")
        
        while True:
            try:
                choice = input(f"\n请输入选项 (1-{len(self.supported_games)}): ").strip()
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(self.supported_games):
                    selected_game = self.supported_games[choice_idx]
                    break
                else:
                    print("无效选择，请重试。")
            except (ValueError, IndexError):
                print("请输入有效数字。")
        
        # 根据游戏类型进行特定设置
        if selected_game.lower() in ["genshin impact", "genshin", "yuanshen"]:
            return self._setup_genshin_config(selected_game)
        else:
            return self._setup_generic_config(selected_game)
    
    def _setup_genshin_config(self, game_name: str) -> MainConfiguration:
        """设置原神配置"""
        print(f"\n正在为 {game_name} 设置配置...")
        
        # 获取原神路径
        print("\n请输入原神游戏客户端路径 (例如: C:/Genshin Impact/Genshin Impact Game/YuanShen.exe):")
        genshin_path = input("路径: ").strip()
        if not genshin_path:
            genshin_path = self._find_genshin_installation()
        
        # 获取BetterGI路径
        print("\n请输入BetterGI路径 (例如: C:/BetterGI/BetterGI.exe):")
        bettergi_path = input("路径: ").strip()
        
        # 验证路径
        if genshin_path and not Path(genshin_path).exists():
            print(f"警告: 原神路径不存在: {genshin_path}")
        
        if bettergi_path and not Path(bettergi_path).exists():
            print(f"警告: BetterGI路径不存在: {bettergi_path}")
        
        # 获取模板路径
        templates_path = input(f"\n模板文件路径 (默认: ./templates): ").strip()
        if not templates_path:
            templates_path = "./templates"
        
        # 获取执行参数
        print("\n设置执行参数:")
        check_interval = input("检查间隔 (秒, 默认30): ").strip()
        check_interval = int(check_interval) if check_interval.isdigit() else 30
        
        timeout = input("超时时间 (秒, 默认3600): ").strip()
        timeout = int(timeout) if timeout.isdigit() else 3600
        
        close_after = input("完成后关闭游戏和脚本框架? (y/N): ").strip().lower()
        close_after_completion = close_after in ['y', 'yes', '是']
        
        # 构建配置
        basic_config = {
            "game": game_name,
            "adapter": "bettergi",
            "script": ""
        }
        
        full_config = ConfigSimplifier.expand_basic_to_full(basic_config)
        
        # 更新具体配置
        full_config.game.genshin_path = genshin_path
        full_config.game.bettergi_path = bettergi_path
        full_config.game.templates_path = templates_path
        full_config.game.check_interval = check_interval
        full_config.game.timeout = timeout
        full_config.game.close_after_completion = close_after_completion
        
        return full_config
    
    def _setup_generic_config(self, game_name: str) -> MainConfiguration:
        """设置通用配置"""
        print(f"\n正在为 {game_name} 设置通用配置...")
        
        # 让用户选择适配器类型
        print("\n请选择适配器类型:")
        for i, adapter in enumerate(self.supported_adapters, 1):
            print(f"{i}. {adapter}")
        
        while True:
            try:
                choice = input(f"\n请输入选项 (1-{len(self.supported_adapters)}): ").strip()
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(self.supported_adapters):
                    selected_adapter = self.supported_adapters[choice_idx]
                    break
                else:
                    print("无效选择，请重试。")
            except (ValueError, IndexError):
                print("请输入有效数字。")
        
        # 根据适配器类型进行设置
        if "BetterGI" in selected_adapter:
            return self._setup_genshin_config(game_name)
        elif "Python Script" in selected_adapter:
            return self._setup_python_adapter_config(game_name)
        elif "Executable" in selected_adapter:
            return self._setup_exe_adapter_config(game_name)
        elif "AutoHotKey" in selected_adapter:
            return self._setup_ahk_adapter_config(game_name)
        else:
            # 自定义配置
            return self._setup_custom_config(game_name)
    
    def _setup_python_adapter_config(self, game_name: str) -> MainConfiguration:
        """设置Python适配器配置"""
        script_path = input("\nPython脚本路径: ").strip()
        arguments = input("脚本参数 (空格分隔): ").strip().split()
        
        basic_config = {
            "game": game_name,
            "adapter": "python",
            "script": script_path
        }
        
        full_config = ConfigSimplifier.expand_basic_to_full(basic_config)
        
        # 添加适配器特定配置
        adapter_config = {
            "script_path": script_path,
            "arguments": arguments
        }
        
        # 查找或创建Python适配器配置
        python_adapter_exists = False
        for adapter in full_config.adapters:
            if adapter.name == "python_adapter":
                adapter.config.update(adapter_config)
                python_adapter_exists = True
                break
        
        if not python_adapter_exists:
            from .models import AdapterConfig
            full_config.adapters.append(AdapterConfig(
                name="python_adapter",
                type="script",
                enabled=True,
                config=adapter_config
            ))
        
        return full_config
    
    def _setup_exe_adapter_config(self, game_name: str) -> MainConfiguration:
        """设置可执行文件适配器配置"""
        exe_path = input("\n可执行文件路径: ").strip()
        arguments = input("启动参数 (空格分隔): ").strip().split()
        
        basic_config = {
            "game": game_name,
            "adapter": "exe",
            "script": exe_path
        }
        
        full_config = ConfigSimplifier.expand_basic_to_full(basic_config)
        
        # 添加适配器特定配置
        adapter_config = {
            "exe_path": exe_path,
            "arguments": arguments
        }
        
        # 查找或创建EXE适配器配置
        exe_adapter_exists = False
        for adapter in full_config.adapters:
            if adapter.name == "exe_adapter":
                adapter.config.update(adapter_config)
                exe_adapter_exists = True
                break
        
        if not exe_adapter_exists:
            from .models import AdapterConfig
            full_config.adapters.append(AdapterConfig(
                name="exe_adapter",
                type="script",
                enabled=True,
                config=adapter_config
            ))
        
        return full_config
    
    def _setup_ahk_adapter_config(self, game_name: str) -> MainConfiguration:
        """设置AutoHotKey适配器配置"""
        script_path = input("\nAHK脚本路径: ").strip()
        ahk_executable = input("AHK可执行文件路径 (默认: AutoHotkey.exe): ").strip()
        if not ahk_executable:
            ahk_executable = "AutoHotkey.exe"
        arguments = input("脚本参数 (空格分隔): ").strip().split()
        
        basic_config = {
            "game": game_name,
            "adapter": "ahk",
            "script": script_path
        }
        
        full_config = ConfigSimplifier.expand_basic_to_full(basic_config)
        
        # 添加适配器特定配置
        adapter_config = {
            "script_path": script_path,
            "ahk_executable": ahk_executable,
            "arguments": arguments
        }
        
        # 查找或创建AHK适配器配置
        ahk_adapter_exists = False
        for adapter in full_config.adapters:
            if adapter.name == "ahk_adapter":
                adapter.config.update(adapter_config)
                ahk_adapter_exists = True
                break
        
        if not ahk_adapter_exists:
            from .models import AdapterConfig
            full_config.adapters.append(AdapterConfig(
                name="ahk_adapter",
                type="script",
                enabled=True,
                config=adapter_config
            ))
        
        return full_config
    
    def _setup_custom_config(self, game_name: str) -> MainConfiguration:
        """设置自定义配置"""
        print("\n请输入自定义配置参数:")
        
        basic_config = {
            "game": game_name,
            "adapter": "custom",
            "script": ""
        }
        
        return ConfigSimplifier.expand_basic_to_full(basic_config)
    
    def _find_genshin_installation(self) -> str:
        """尝试自动查找原神安装位置"""
        common_paths = [
            "C:/Genshin Impact/Genshin Impact Game/YuanShen.exe",
            "C:/Genshin Impact/Genshin Impact Game/GenshinImpact.exe",
            "D:/Genshin Impact/Genshin Impact Game/YuanShen.exe",
            "D:/Genshin Impact/Genshin Impact Game/GenshinImpact.exe",
            os.path.expanduser("~/AppData/Local/Genshin Impact Game/YuanShen.exe"),
            os.path.expanduser("~/AppData/Local/Genshin Impact Game/GenshinImpact.exe")
        ]
        
        for path in common_paths:
            if Path(path).exists():
                print(f"找到原神安装: {path}")
                return path
        
        print("未找到原神安装，请手动指定路径")
        return ""
    
    def save_config(self, config: MainConfiguration, file_path: str):
        """保存配置到文件"""
        config.save_to_file(file_path)
        print(f"配置已保存到: {file_path}")


def run_config_wizard():
    """运行配置向导的便捷函数"""
    wizard = ConfigWizard()
    config = wizard.run_interactive_setup()
    
    # 询问保存位置
    print(f"\n配置生成完成!")
    save_path = input("请输入配置文件保存路径 (默认: config.yaml): ").strip()
    if not save_path:
        save_path = "config.yaml"
    
    wizard.save_config(config, save_path)
    
    print("\n配置向导完成! 您可以使用以下命令启动自动化:")
    print(f"scriptzero start {save_path}")
    
    return config


if __name__ == "__main__":
    run_config_wizard()