"""
现代化游戏自动化框架UI
使用ttkbootstrap提供现代化外观
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import asyncio
import threading
import sys
from pathlib import Path
import yaml
import json
import datetime
from typing import Dict, Any, List, Optional

try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
    HAS_TTKBOOTSTRAP = True
except ImportError:
    HAS_TTKBOOTSTRAP = False

from ..game_automation_framework import GameAutomationFramework


class ModernUI:
    def __init__(self):
        if HAS_TTKBOOTSTRAP:
            # 初始化多种主题供用户选择
            self.root = ttkb.Window(themename="morph")  # 使用更现代的主题
            self.style = ttkb.Style()
            
            # 添加主题切换菜单
            self.available_themes = [
                "cosmo", "flatly", "journal", "litera", "lumen", "minty", "pulse", "sandstone",
                "united", "yeti", "cerulean", "morph", "simplex", "superhero", "darkly", "vapor"
            ]
        else:
            self.root = tk.Tk()
        
        self.root.title("游戏自动化框架 - 现代化界面")
        self.root.geometry("1400x900")
        
        # 当前配置文件路径
        self.current_config_path = None
        self.framework = None
        self.current_config = {}
        
        # 预定义的配置选项
        self.predefined_configs = {
            "game_types": ["script_chain", "game", "mixed"],
            "action_types": ["launch", "wait_for", "click", "key_press", "type_text", "wait_for_image"],
            "buttons": ["left", "right", "middle"],
            "condition_types": ["timeout", "image_detected", "process_exit", "window_active"]
        }
        
        # 创建界面
        self.create_widgets()
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建配置", command=self.new_config, accelerator="Ctrl+N")
        file_menu.add_command(label="打开配置", command=self.open_config, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="保存配置", command=self.save_config, accelerator="Ctrl+S")
        file_menu.add_command(label="另存为", command=self.save_config_as)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 视图菜单
        if HAS_TTKBOOTSTRAP:
            view_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="视图", menu=view_menu)
            
            # 主题子菜单
            theme_submenu = tk.Menu(view_menu, tearoff=0)
            view_menu.add_cascade(label="主题", menu=theme_submenu)
            for theme in self.available_themes:
                theme_submenu.add_command(label=theme, command=lambda t=theme: self.change_theme_direct(t))
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def change_theme(self, event=None):
        """更改应用程序主题"""
        if HAS_TTKBOOTSTRAP:
            selected_theme = self.theme_var.get()
            self.style.theme_use(selected_theme)
            
    def change_theme_direct(self, theme_name):
        """直接更改主题"""
        if HAS_TTKBOOTSTRAP:
            self.style.theme_use(theme_name)
            self.theme_var.set(theme_name)
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """游戏自动化框架 - 现代化UI

版本: 1.0
使用ttkbootstrap提供现代化界面体验
支持多种主题切换

作者: Assistant"""
        messagebox.showinfo("关于", about_text)
        
    def create_widgets(self):
        """创建现代化界面组件"""
        # 创建菜单栏
        self.create_menu()
        
        # 主框架
        if HAS_TTKBOOTSTRAP:
            main_frame = ttkb.Frame(self.root, padding="10")
        else:
            main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置区域
        if HAS_TTKBOOTSTRAP:
            config_frame = ttkb.Labelframe(main_frame, text="配置管理", padding="10")
        else:
            config_frame = ttk.LabelFrame(main_frame, text="配置管理", padding="10")
        config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 配置文件选择和操作
        if HAS_TTKBOOTSTRAP:
            ttkb.Button(config_frame, text="新建配置", command=self.new_config, bootstyle="primary").grid(row=0, column=0, padx=(0, 5))
            ttkb.Button(config_frame, text="打开配置", command=self.open_config, bootstyle="secondary").grid(row=0, column=1, padx=(0, 5))
            ttkb.Button(config_frame, text="保存配置", command=self.save_config, bootstyle="success").grid(row=0, column=2, padx=(0, 5))
            ttkb.Button(config_frame, text="保存配置为", command=self.save_config_as, bootstyle="info").grid(row=0, column=3, padx=(0, 5))
            
            # 主题选择下拉菜单
            theme_label = ttkb.Label(config_frame, text="主题:")
            theme_label.grid(row=0, column=5, padx=(20, 5))
            
            self.theme_var = tk.StringVar(value="morph")
            theme_selector = ttkb.Combobox(
                config_frame, 
                textvariable=self.theme_var, 
                values=self.available_themes,
                state="readonly",
                width=12
            )
            theme_selector.grid(row=0, column=6, padx=(0, 5))
            theme_selector.bind('<<ComboboxSelected>>', self.change_theme)
        else:
            ttk.Button(config_frame, text="新建配置", command=self.new_config).grid(row=0, column=0, padx=(0, 5))
            ttk.Button(config_frame, text="打开配置", command=self.open_config).grid(row=0, column=1, padx=(0, 5))
            ttk.Button(config_frame, text="保存配置", command=self.save_config).grid(row=0, column=2, padx=(0, 5))
            ttk.Button(config_frame, text="保存配置为", command=self.save_config_as).grid(row=0, column=3, padx=(0, 5))
        
        # 配置文件路径显示
        self.config_path_var = tk.StringVar()
        if HAS_TTKBOOTSTRAP:
            path_entry = ttkb.Entry(config_frame, textvariable=self.config_path_var, width=60, state="readonly")
        else:
            path_entry = ttk.Entry(config_frame, textvariable=self.config_path_var, width=60, state="readonly")
        path_entry.grid(row=0, column=4, padx=(10, 0), sticky=(tk.W, tk.E))
        
        # 创建笔记本控件用于不同配置部分
        if HAS_TTKBOOTSTRAP:
            self.notebook = ttkb.Notebook(main_frame)
        else:
            self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 基本配置标签页
        self.create_basic_config_tab()
        
        # 游戏配置标签页
        self.create_game_config_tab()
        
        # 工作流配置标签页
        self.create_workflow_config_tab()
        
        # 脚本配置标签页
        self.create_script_config_tab()
        
        # 控制按钮区域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 执行控制
        if HAS_TTKBOOTSTRAP:
            # 使用现代化按钮样式
            exec_btn = ttkb.Button(control_frame, text="执行", command=self.start_execution, bootstyle="success-outline")
            exec_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            stop_btn = ttkb.Button(control_frame, text="停止", command=self.stop_execution, bootstyle="danger-outline")
            stop_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            pause_btn = ttkb.Button(control_frame, text="暂停", command=self.pause_execution, bootstyle="warning-outline")
            pause_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            preview_btn = ttkb.Button(control_frame, text="预览配置", command=self.preview_config, bootstyle="info-outline")
            preview_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            # 添加高级控制按钮
            reset_btn = ttkb.Button(control_frame, text="重置", command=self.reset_config, bootstyle="secondary-outline")
            reset_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            export_btn = ttkb.Button(control_frame, text="导出执行报告", command=self.export_report, bootstyle="primary-outline")
            export_btn.pack(side=tk.LEFT, padx=(0, 5))
        else:
            ttk.Button(control_frame, text="执行", command=self.start_execution).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(control_frame, text="停止", command=self.stop_execution).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(control_frame, text="暂停", command=self.pause_execution).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(control_frame, text="预览配置", command=self.preview_config).pack(side=tk.LEFT, padx=(0, 5))
        
        # 日志区域
        if HAS_TTKBOOTSTRAP:
            log_frame = ttkb.Labelframe(main_frame, text="执行日志", padding="10")
        else:
            log_frame = ttk.LabelFrame(main_frame, text="执行日志", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 日志文本框
        if HAS_TTKBOOTSTRAP:
            # ttkbootstrap的Text组件不支持bootstyle，使用原生Text
            self.log_area = tk.Text(log_frame, wrap=tk.WORD, width=120, height=15)
            self.log_scrollbar = ttkb.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_area.yview)
        else:
            self.log_area = tk.Text(log_frame, wrap=tk.WORD, width=120, height=15)
            self.log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_area.yview)
        
        self.log_area.configure(yscrollcommand=self.log_scrollbar.set)
        self.log_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 添加日志控制按钮
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky=(tk.W, tk.E))
        
        if HAS_TTKBOOTSTRAP:
            ttkb.Button(log_control_frame, text="清空日志", command=self.clear_logs, bootstyle="secondary-outline").pack(side=tk.LEFT, padx=(0, 5))
            ttkb.Button(log_control_frame, text="保存日志", command=self.save_logs, bootstyle="secondary-outline").pack(side=tk.LEFT, padx=(0, 5))
            ttkb.Button(log_control_frame, text="自动滚动", command=self.toggle_auto_scroll, bootstyle="secondary").pack(side=tk.RIGHT)
        else:
            ttk.Button(log_control_frame, text="清空日志", command=self.clear_logs).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(log_control_frame, text="保存日志", command=self.save_logs).pack(side=tk.LEFT, padx=(0, 5))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        if HAS_TTKBOOTSTRAP:
            status_bar = ttkb.Label(main_frame, textvariable=self.status_var, bootstyle="info")
        else:
            status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def create_basic_config_tab(self):
        """创建基本配置标签页"""
        if HAS_TTKBOOTSTRAP:
            basic_frame = ttkb.Frame(self.notebook)
        else:
            basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(basic_frame, text="基本配置")
        
        # 版本和名称
        if HAS_TTKBOOTSTRAP:
            basic_info_frame = ttkb.Labelframe(basic_frame, text="基本信息", padding="10")
        else:
            basic_info_frame = ttk.LabelFrame(basic_frame, text="基本信息", padding="10")
        basic_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 版本
        version_frame = ttk.Frame(basic_info_frame)
        version_frame.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        if HAS_TTKBOOTSTRAP:
            ttkb.Label(version_frame, text="版本:").pack(side=tk.LEFT, padx=(0, 5))
            self.version_var = tk.StringVar(value="1.0")
            version_combo = ttkb.Combobox(version_frame, textvariable=self.version_var, 
                                         values=["1.0", "1.1", "2.0"], state="readonly", width=10, bootstyle="success")
        else:
            ttk.Label(version_frame, text="版本:").pack(side=tk.LEFT)
            self.version_var = tk.StringVar(value="1.0")
            version_combo = ttk.Combobox(version_frame, textvariable=self.version_var, 
                                         values=["1.0", "1.1", "2.0"], state="readonly", width=10)
        version_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # 名称
        name_frame = ttk.Frame(basic_info_frame)
        name_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        if HAS_TTKBOOTSTRAP:
            ttkb.Label(name_frame, text="名称:").pack(side=tk.LEFT, padx=(0, 5))
            self.name_var = tk.StringVar(value="新自动化任务")
            name_entry = ttkb.Entry(name_frame, textvariable=self.name_var, width=50, bootstyle="success")
        else:
            ttk.Label(name_frame, text="名称:").pack(side=tk.LEFT)
            self.name_var = tk.StringVar(value="新自动化任务")
            name_entry = ttk.Entry(name_frame, textvariable=self.name_var, width=50)
        name_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # 变量配置
        if HAS_TTKBOOTSTRAP:
            variables_frame = ttkb.Labelframe(basic_frame, text="变量配置", padding="10")
        else:
            variables_frame = ttk.LabelFrame(basic_frame, text="变量配置", padding="10")
        variables_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 变量表格
        columns = ('name', 'value', 'description')
        if HAS_TTKBOOTSTRAP:
            self.variables_tree = ttkb.Treeview(variables_frame, columns=columns, show='headings', height=8)
            # 添加样式
            self.variables_tree.configure(selectmode='browse')
        else:
            self.variables_tree = ttk.Treeview(variables_frame, columns=columns, show='headings', height=8)
        
        self.variables_tree.heading('name', text='变量名')
        self.variables_tree.heading('value', text='值')
        self.variables_tree.heading('description', text='描述')
        
        # 设置列宽
        self.variables_tree.column('name', width=150)
        self.variables_tree.column('value', width=300)
        self.variables_tree.column('description', width=200)
        
        # 滚动条
        if HAS_TTKBOOTSTRAP:
            variables_scrollbar = ttkb.Scrollbar(variables_frame, orient=tk.VERTICAL, command=self.variables_tree.yview)
        else:
            variables_scrollbar = ttk.Scrollbar(variables_frame, orient=tk.VERTICAL, command=self.variables_tree.yview)
        
        self.variables_tree.configure(yscrollcommand=variables_scrollbar.set)
        
        # 布局
        self.variables_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        variables_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 变量操作按钮
        var_button_frame = ttk.Frame(variables_frame)
        var_button_frame.pack(fill=tk.X, pady=(5, 0))
        
        if HAS_TTKBOOTSTRAP:
            ttkb.Button(var_button_frame, text="添加变量", command=self.add_variable, bootstyle="outline-success").pack(side=tk.LEFT, padx=(0, 5))
            ttkb.Button(var_button_frame, text="编辑变量", command=self.edit_variable, bootstyle="outline-warning").pack(side=tk.LEFT, padx=(0, 5))
            ttkb.Button(var_button_frame, text="删除变量", command=self.delete_variable, bootstyle="outline-danger").pack(side=tk.LEFT, padx=(0, 5))
            
            # 添加导入/导出按钮
            ttkb.Button(var_button_frame, text="导入变量", command=self.import_variables, bootstyle="outline-info").pack(side=tk.RIGHT, padx=(0, 5))
            ttkb.Button(var_button_frame, text="导出变量", command=self.export_variables, bootstyle="outline-info").pack(side=tk.RIGHT, padx=(0, 5))
        else:
            ttk.Button(var_button_frame, text="添加变量", command=self.add_variable).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(var_button_frame, text="编辑变量", command=self.edit_variable).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(var_button_frame, text="删除变量", command=self.delete_variable).pack(side=tk.LEFT, padx=(0, 5))
    
    def create_game_config_tab(self):
        """创建游戏配置标签页"""
        if HAS_TTKBOOTSTRAP:
            game_frame = ttkb.Frame(self.notebook)
        else:
            game_frame = ttk.Frame(self.notebook)
        self.notebook.add(game_frame, text="游戏配置")
        
        # 游戏配置表格
        columns = ('name', 'executable', 'window_title', 'arguments')
        if HAS_TTKBOOTSTRAP:
            self.games_tree = ttkb.Treeview(game_frame, columns=columns, show='headings', height=15)
            # 添加样式
            self.games_tree.configure(selectmode='browse')
        else:
            self.games_tree = ttk.Treeview(game_frame, columns=columns, show='headings', height=15)
        
        self.games_tree.heading('name', text='游戏名称')
        self.games_tree.heading('executable', text='可执行文件')
        self.games_tree.heading('window_title', text='窗口标题')
        self.games_tree.heading('arguments', text='启动参数')
        
        # 设置列宽
        self.games_tree.column('name', width=100)
        self.games_tree.column('executable', width=250)
        self.games_tree.column('window_title', width=150)
        self.games_tree.column('arguments', width=200)
        
        # 滚动条
        if HAS_TTKBOOTSTRAP:
            games_scrollbar = ttkb.Scrollbar(game_frame, orient=tk.VERTICAL, command=self.games_tree.yview)
        else:
            games_scrollbar = ttk.Scrollbar(game_frame, orient=tk.VERTICAL, command=self.games_tree.yview)
        
        self.games_tree.configure(yscrollcommand=games_scrollbar.set)
        
        # 布局
        self.games_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        games_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 游戏操作按钮
        game_button_frame = ttk.Frame(game_frame)
        game_button_frame.pack(fill=tk.X, pady=(5, 0))
        
        if HAS_TTKBOOTSTRAP:
            ttkb.Button(game_button_frame, text="添加游戏", command=self.add_game, bootstyle="outline-success").pack(side=tk.LEFT, padx=(0, 5))
            ttkb.Button(game_button_frame, text="编辑游戏", command=self.edit_game, bootstyle="outline-warning").pack(side=tk.LEFT, padx=(0, 5))
            ttkb.Button(game_button_frame, text="删除游戏", command=self.delete_game, bootstyle="outline-danger").pack(side=tk.LEFT, padx=(0, 5))
            
            # 添加测试连接按钮
            ttkb.Button(game_button_frame, text="测试游戏", command=self.test_game_launch, bootstyle="outline-primary").pack(side=tk.RIGHT, padx=(0, 5))
        else:
            ttk.Button(game_button_frame, text="添加游戏", command=self.add_game).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(game_button_frame, text="编辑游戏", command=self.edit_game).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(game_button_frame, text="删除游戏", command=self.delete_game).pack(side=tk.LEFT, padx=(0, 5))
    
    def create_workflow_config_tab(self):
        """创建工作流配置标签页"""
        if HAS_TTKBOOTSTRAP:
            workflow_frame = ttkb.Frame(self.notebook)
        else:
            workflow_frame = ttk.Frame(self.notebook)
        self.notebook.add(workflow_frame, text="工作流")
        
        # 工作流配置表格
        columns = ('name', 'type', 'description', 'enabled')
        if HAS_TTKBOOTSTRAP:
            self.workflow_tree = ttkb.Treeview(workflow_frame, columns=columns, show='headings', height=15)
            # 添加样式
            self.workflow_tree.configure(selectmode='browse')
        else:
            self.workflow_tree = ttk.Treeview(workflow_frame, columns=columns, show='headings', height=15)
        
        self.workflow_tree.heading('name', text='名称')
        self.workflow_tree.heading('type', text='类型')
        self.workflow_tree.heading('description', text='描述')
        self.workflow_tree.heading('enabled', text='启用')
        
        # 设置列宽
        self.workflow_tree.column('name', width=150)
        self.workflow_tree.column('type', width=100)
        self.workflow_tree.column('description', width=300)
        self.workflow_tree.column('enabled', width=50)
        
        # 滚动条
        if HAS_TTKBOOTSTRAP:
            workflow_scrollbar = ttkb.Scrollbar(workflow_frame, orient=tk.VERTICAL, command=self.workflow_tree.yview)
        else:
            workflow_scrollbar = ttk.Scrollbar(workflow_frame, orient=tk.VERTICAL, command=self.workflow_tree.yview)
        
        self.workflow_tree.configure(yscrollcommand=workflow_scrollbar.set)
        
        # 布局
        self.workflow_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        workflow_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 工作流操作按钮
        workflow_button_frame = ttk.Frame(workflow_frame)
        workflow_button_frame.pack(fill=tk.X, pady=(5, 0))
        
        if HAS_TTKBOOTSTRAP:
            ttkb.Button(workflow_button_frame, text="添加工作流", command=self.add_workflow, bootstyle="outline-success").pack(side=tk.LEFT, padx=(0, 5))
            ttkb.Button(workflow_button_frame, text="编辑工作流", command=self.edit_workflow, bootstyle="outline-warning").pack(side=tk.LEFT, padx=(0, 5))
            ttkb.Button(workflow_button_frame, text="删除工作流", command=self.delete_workflow, bootstyle="outline-danger").pack(side=tk.LEFT, padx=(0, 5))
            
            # 添加执行顺序调整按钮
            ttkb.Button(workflow_button_frame, text="上移", command=self.move_workflow_up, bootstyle="outline-secondary").pack(side=tk.LEFT, padx=(0, 5))
            ttkb.Button(workflow_button_frame, text="下移", command=self.move_workflow_down, bootstyle="outline-secondary").pack(side=tk.LEFT, padx=(0, 5))
        else:
            ttk.Button(workflow_button_frame, text="添加工作流", command=self.add_workflow).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(workflow_button_frame, text="编辑工作流", command=self.edit_workflow).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(workflow_button_frame, text="删除工作流", command=self.delete_workflow).pack(side=tk.LEFT, padx=(0, 5))
    
    def create_script_config_tab(self):
        """创建脚本配置标签页"""
        if HAS_TTKBOOTSTRAP:
            script_frame = ttkb.Frame(self.notebook)
        else:
            script_frame = ttk.Frame(self.notebook)
        self.notebook.add(script_frame, text="脚本配置")
        
        # 脚本配置表格
        columns = ('path', 'type', 'arguments', 'timeout')
        if HAS_TTKBOOTSTRAP:
            self.scripts_tree = ttkb.Treeview(script_frame, columns=columns, show='headings', height=15)
            # 添加样式
            self.scripts_tree.configure(selectmode='browse')
        else:
            self.scripts_tree = ttk.Treeview(script_frame, columns=columns, show='headings', height=15)
        
        self.scripts_tree.heading('path', text='脚本路径')
        self.scripts_tree.heading('type', text='类型')
        self.scripts_tree.heading('arguments', text='参数')
        self.scripts_tree.heading('timeout', text='超时(秒)')
        
        # 设置列宽
        self.scripts_tree.column('path', width=250)
        self.scripts_tree.column('type', width=100)
        self.scripts_tree.column('arguments', width=200)
        self.scripts_tree.column('timeout', width=100)
        
        # 滚动条
        if HAS_TTKBOOTSTRAP:
            scripts_scrollbar = ttkb.Scrollbar(script_frame, orient=tk.VERTICAL, command=self.scripts_tree.yview)
        else:
            scripts_scrollbar = ttk.Scrollbar(script_frame, orient=tk.VERTICAL, command=self.scripts_tree.yview)
        
        self.scripts_tree.configure(yscrollcommand=scripts_scrollbar.set)
        
        # 布局
        self.scripts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        scripts_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 脚本操作按钮
        script_button_frame = ttk.Frame(script_frame)
        script_button_frame.pack(fill=tk.X, pady=(5, 0))
        
        if HAS_TTKBOOTSTRAP:
            ttkb.Button(script_button_frame, text="添加脚本", command=self.add_script, bootstyle="outline-success").pack(side=tk.LEFT, padx=(0, 5))
            ttkb.Button(script_button_frame, text="编辑脚本", command=self.edit_script, bootstyle="outline-warning").pack(side=tk.LEFT, padx=(0, 5))
            ttkb.Button(script_button_frame, text="删除脚本", command=self.delete_script, bootstyle="outline-danger").pack(side=tk.LEFT, padx=(0, 5))
            
            # 添加测试脚本按钮
            ttkb.Button(script_button_frame, text="测试脚本", command=self.test_script, bootstyle="outline-primary").pack(side=tk.LEFT, padx=(0, 5))
        else:
            ttk.Button(script_button_frame, text="添加脚本", command=self.add_script).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(script_button_frame, text="编辑脚本", command=self.edit_script).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(script_button_frame, text="删除脚本", command=self.delete_script).pack(side=tk.LEFT, padx=(0, 5))
    
    def new_config(self):
        """新建配置文件"""
        self.current_config_path = None
        self.config_path_var.set("")
        self.current_config = {
            'version': '1.0',
            'name': '新自动化任务',
            'variables': {},
            'games': {},
            'workflow': [],
            'scripts': []
        }
        self.refresh_ui_from_config()
        self.status_var.set("已创建新配置")
    
    def open_config(self):
        """打开配置文件"""
        file_path = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("YAML files", "*.yaml *.yml"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    if file_path.endswith('.json'):
                        self.current_config = json.load(f)
                    else:
                        self.current_config = yaml.safe_load(f)
                
                self.current_config_path = file_path
                self.config_path_var.set(file_path)
                self.refresh_ui_from_config()
                self.status_var.set(f"已打开配置文件: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"无法打开配置文件: {str(e)}")
    
    def save_config(self):
        """保存配置文件"""
        if self.current_config_path:
            try:
                config_to_save = self.build_config_from_ui()
                with open(self.current_config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config_to_save, f, default_flow_style=False, allow_unicode=True)
                self.status_var.set(f"已保存配置文件: {self.current_config_path}")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存配置文件: {str(e)}")
        else:
            self.save_config_as()
    
    def save_config_as(self):
        """另存为配置文件"""
        file_path = filedialog.asksaveasfilename(
            title="保存配置文件",
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                config_to_save = self.build_config_from_ui()
                with open(file_path, 'w', encoding='utf-8') as f:
                    if file_path.endswith('.json'):
                        json.dump(config_to_save, f, indent=2, ensure_ascii=False)
                    else:
                        yaml.dump(config_to_save, f, default_flow_style=False, allow_unicode=True)
                self.current_config_path = file_path
                self.config_path_var.set(file_path)
                self.status_var.set(f"已保存配置文件: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存配置文件: {str(e)}")
    
    def refresh_ui_from_config(self):
        """从配置刷新UI"""
        # 刷新基本信息
        self.version_var.set(str(self.current_config.get('version', '1.0')))
        self.name_var.set(self.current_config.get('name', '新自动化任务'))
        
        # 刷新变量表
        for item in self.variables_tree.get_children():
            self.variables_tree.delete(item)
        for name, value in self.current_config.get('variables', {}).items():
            self.variables_tree.insert('', tk.END, values=(name, str(value), ''))
        
        # 刷新游戏表
        for item in self.games_tree.get_children():
            self.games_tree.delete(item)
        for name, game_config in self.current_config.get('games', {}).items():
            args_str = ' '.join(game_config.get('arguments', []))
            self.games_tree.insert('', tk.END, values=(
                name, 
                game_config.get('executable', ''), 
                game_config.get('window_title', ''),
                args_str
            ))
        
        # 刷新工作流表
        for item in self.workflow_tree.get_children():
            self.workflow_tree.delete(item)
        for wf in self.current_config.get('workflow', []):
            enabled_str = "是" if wf.get('enabled', True) else "否"
            self.workflow_tree.insert('', tk.END, values=(
                wf.get('name', ''),
                wf.get('type', ''),
                wf.get('description', ''),
                enabled_str
            ))
        
        # 刷新脚本表
        for item in self.scripts_tree.get_children():
            self.scripts_tree.delete(item)
        for script in self.current_config.get('scripts', []):
            args_str = ' '.join(script.get('arguments', []))
            timeout = script.get('completion', {}).get('any_of', [{}])[0].get('seconds', 3600) if script.get('completion') else 3600
            self.scripts_tree.insert('', tk.END, values=(
                script.get('path', ''),
                script.get('type', 'python'),  # 默认类型
                args_str,
                timeout
            ))
    
    def build_config_from_ui(self) -> Dict[str, Any]:
        """从界面构建配置字典"""
        config = {
            'version': self.version_var.get(),
            'name': self.name_var.get(),
            'variables': {},
            'games': {},
            'workflow': [],
            'scripts': []
        }
        
        # 添加变量
        for child in self.variables_tree.get_children():
            values = self.variables_tree.item(child)['values']
            config['variables'][values[0]] = values[1]
        
        # 添加游戏配置
        for child in self.games_tree.get_children():
            values = self.games_tree.item(child)['values']
            config['games'][values[0]] = {
                'executable': values[1],
                'window_title': values[2],
                'arguments': values[3].split() if values[3] else []
            }
        
        # 添加工作流
        for child in self.workflow_tree.get_children():
            values = self.workflow_tree.item(child)['values']
            workflow_item = {
                'name': values[0],
                'type': values[1],
                'enabled': values[3] == "是"
            }
            if values[2]:  # 添加描述
                workflow_item['description'] = values[2]
            config['workflow'].append(workflow_item)
        
        # 添加脚本
        for child in self.scripts_tree.get_children():
            values = self.scripts_tree.item(child)['values']
            script_item = {
                'path': values[0],
                'type': values[1],
                'arguments': values[2].split() if values[2] else [],
                'completion': {
                    'any_of': [
                        {
                            'type': 'timeout',
                            'seconds': int(values[3]) if values[3].isdigit() else 3600
                        }
                    ]
                }
            }
            config['scripts'].append(script_item)
        
        return config
    
    def add_variable(self):
        """添加变量"""
        dialog = VariableDialog(self.root, "添加变量", predefined_configs=self.predefined_configs)
        if dialog.result:
            self.variables_tree.insert('', tk.END, values=(
                dialog.result['name'], 
                dialog.result['value'], 
                dialog.result.get('description', '')))
    
    def edit_variable(self):
        """编辑选中的变量"""
        selected = self.variables_tree.selection()
        if selected:
            item = self.variables_tree.item(selected)
            values = item['values']
            dialog = VariableDialog(
                self.root, 
                "编辑变量", 
                existing_values={
                    'name': values[0],
                    'value': values[1],
                    'description': values[2]
                },
                predefined_configs=self.predefined_configs
            )
            if dialog.result:
                self.variables_tree.item(selected, values=(
                    dialog.result['name'], 
                    dialog.result['value'], 
                    dialog.result.get('description', '')))
        else:
            messagebox.showwarning("警告", "请选择要编辑的变量")
    
    def delete_variable(self):
        """删除选中的变量"""
        selected = self.variables_tree.selection()
        if selected:
            self.variables_tree.delete(selected)
        else:
            messagebox.showwarning("警告", "请选择要删除的变量")
    
    def add_game(self):
        """添加游戏配置"""
        dialog = GameConfigDialog(self.root, "添加游戏", predefined_configs=self.predefined_configs)
        if dialog.result:
            args_str = ' '.join(dialog.result.get('arguments', []))
            self.games_tree.insert('', tk.END, values=(
                dialog.result['name'], 
                dialog.result['executable'], 
                dialog.result['window_title'],
                args_str))
    
    def edit_game(self):
        """编辑选中的游戏配置"""
        selected = self.games_tree.selection()
        if selected:
            item = self.games_tree.item(selected)
            values = item['values']
            dialog = GameConfigDialog(
                self.root, 
                "编辑游戏", 
                existing_values={
                    'name': values[0],
                    'executable': values[1],
                    'window_title': values[2],
                    'arguments': values[3].split() if values[3] else []
                },
                predefined_configs=self.predefined_configs
            )
            if dialog.result:
                args_str = ' '.join(dialog.result.get('arguments', []))
                self.games_tree.item(selected, values=(
                    dialog.result['name'], 
                    dialog.result['executable'], 
                    dialog.result['window_title'],
                    args_str))
        else:
            messagebox.showwarning("警告", "请选择要编辑的游戏配置")
    
    def delete_game(self):
        """删除选中的游戏配置"""
        selected = self.games_tree.selection()
        if selected:
            self.games_tree.delete(selected)
        else:
            messagebox.showwarning("警告", "请选择要删除的游戏配置")
    
    def add_workflow(self):
        """添加工作流"""
        dialog = WorkflowDialog(self.root, "添加工作流", predefined_configs=self.predefined_configs)
        if dialog.result:
            enabled_str = "是" if dialog.result.get('enabled', True) else "否"
            self.workflow_tree.insert('', tk.END, values=(
                dialog.result['name'], 
                dialog.result['type'], 
                dialog.result.get('description', ''),
                enabled_str))
    
    def edit_workflow(self):
        """编辑选中的工作流"""
        selected = self.workflow_tree.selection()
        if selected:
            item = self.workflow_tree.item(selected)
            values = item['values']
            dialog = WorkflowDialog(
                self.root, 
                "编辑工作流", 
                existing_values={
                    'name': values[0],
                    'type': values[1],
                    'description': values[2],
                    'enabled': values[3] == "是"
                },
                predefined_configs=self.predefined_configs
            )
            if dialog.result:
                enabled_str = "是" if dialog.result.get('enabled', True) else "否"
                self.workflow_tree.item(selected, values=(
                    dialog.result['name'], 
                    dialog.result['type'], 
                    dialog.result.get('description', ''),
                    enabled_str))
        else:
            messagebox.showwarning("警告", "请选择要编辑的工作流")
    
    def delete_workflow(self):
        """删除选中的工作流"""
        selected = self.workflow_tree.selection()
        if selected:
            self.workflow_tree.delete(selected)
        else:
            messagebox.showwarning("警告", "请选择要删除的工作流")
    
    def add_script(self):
        """添加脚本"""
        dialog = ScriptConfigDialog(self.root, "添加脚本", predefined_configs=self.predefined_configs)
        if dialog.result:
            args_str = ' '.join(dialog.result.get('arguments', []))
            timeout = dialog.result.get('timeout', 3600)
            self.scripts_tree.insert('', tk.END, values=(
                dialog.result['path'], 
                dialog.result['type'], 
                args_str,
                timeout))
    
    def edit_script(self):
        """编辑选中的脚本"""
        selected = self.scripts_tree.selection()
        if selected:
            item = self.scripts_tree.item(selected)
            values = item['values']
            dialog = ScriptConfigDialog(
                self.root, 
                "编辑脚本", 
                existing_values={
                    'path': values[0],
                    'type': values[1],
                    'arguments': values[2].split() if values[2] else [],
                    'timeout': int(values[3]) if values[3].isdigit() else 3600
                },
                predefined_configs=self.predefined_configs
            )
            if dialog.result:
                args_str = ' '.join(dialog.result.get('arguments', []))
                timeout = dialog.result.get('timeout', 3600)
                self.scripts_tree.item(selected, values=(
                    dialog.result['path'], 
                    dialog.result['type'], 
                    args_str,
                    timeout))
        else:
            messagebox.showwarning("警告", "请选择要编辑的脚本")
    
    def delete_script(self):
        """删除选中的脚本"""
        selected = self.scripts_tree.selection()
        if selected:
            self.scripts_tree.delete(selected)
        else:
            messagebox.showwarning("警告", "请选择要删除的脚本")
    
    def preview_config(self):
        """预览配置"""
        config = self.build_config_from_ui()
        config_yaml = yaml.dump(config, default_flow_style=False, allow_unicode=True)
        
        # 创建预览窗口
        preview_window = tk.Toplevel(self.root)
        preview_window.title("配置预览")
        preview_window.geometry("800x600")
        
        text_area = tk.Text(preview_window, wrap=tk.NONE)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_area.insert(tk.END, config_yaml)
        text_area.config(state=tk.DISABLED)
    
    def start_execution(self):
        """开始执行自动化任务"""
        # 获取当前配置
        config_to_run = self.build_config_from_ui()
        
        # 临时保存配置到文件
        temp_config_path = "temp_config.yaml"
        with open(temp_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_to_run, f, default_flow_style=False, allow_unicode=True)
        
        # 在新线程中运行异步执行
        thread = threading.Thread(target=self._run_async_execution, args=(temp_config_path,))
        thread.daemon = True
        thread.start()
        
        self.status_var.set("正在执行自动化任务...")
    
    def _run_async_execution(self, config_path):
        """在后台线程中运行异步执行"""
        async def run_framework():
            try:
                self.framework = GameAutomationFramework(config_path)
                # 设置回调函数
                self.framework.set_callbacks(
                    log_callback=self.add_log_message,
                    status_callback=lambda status: self.status_var.set(status)
                )
                
                await self.framework.run()
                
            except Exception as e:
                self.add_log_message(f"执行出错: {str(e)}\n")
            finally:
                self.status_var.set("执行完成")
        
        # 运行异步函数
        asyncio.run(run_framework())
    
    def stop_execution(self):
        """停止执行"""
        if self.framework:
            self.status_var.set("执行已停止")
            self.add_log_message("执行已被用户停止\n")
        else:
            messagebox.showinfo("提示", "没有正在执行的任务")
    
    def pause_execution(self):
        """暂停执行"""
        self.status_var.set("执行已暂停")
        self.add_log_message("执行已暂停\n")
    
    def add_log_message(self, message):
        """添加日志消息"""
        def update_log():
            self.log_area.config(state=tk.NORMAL)
            self.log_area.insert(tk.END, message)
            # 如果启用了自动滚动，则滚动到底部
            if getattr(self, 'auto_scroll_enabled', True):
                self.log_area.see(tk.END)
            self.log_area.config(state=tk.DISABLED)
            self.root.update_idletasks()
        
        # 使用after方法在主线程中更新GUI
        self.root.after(0, update_log)
    
    # 新增功能方法
    def import_variables(self):
        """导入变量配置"""
        file_path = filedialog.askopenfilename(
            title="导入变量配置",
            filetypes=[("YAML files", "*.yaml *.yml"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    if file_path.endswith('.json'):
                        imported_vars = json.load(f)
                    else:
                        imported_vars = yaml.safe_load(f)
                
                # 清空现有变量
                for item in self.variables_tree.get_children():
                    self.variables_tree.delete(item)
                
                # 添加导入的变量
                for name, value in imported_vars.items():
                    self.variables_tree.insert('', tk.END, values=(name, str(value), ''))
                
                self.status_var.set(f"已导入变量配置: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"无法导入变量配置: {str(e)}")
    
    def export_variables(self):
        """导出变量配置"""
        file_path = filedialog.asksaveasfilename(
            title="导出变量配置",
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                # 从表格中收集变量
                exported_vars = {}
                for child in self.variables_tree.get_children():
                    values = self.variables_tree.item(child)['values']
                    exported_vars[values[0]] = values[1]
                
                # 写入文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    if file_path.endswith('.json'):
                        json.dump(exported_vars, f, indent=2, ensure_ascii=False)
                    else:
                        yaml.dump(exported_vars, f, default_flow_style=False, allow_unicode=True)
                
                self.status_var.set(f"已导出变量配置: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"无法导出变量配置: {str(e)}")
    
    def test_game_launch(self):
        """测试游戏启动"""
        selected = self.games_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请选择要测试的游戏")
            return
        
        item = self.games_tree.item(selected)
        values = item['values']
        executable_path = values[1]
        
        if not executable_path or not Path(executable_path).exists():
            messagebox.showerror("错误", f"可执行文件不存在: {executable_path}")
            return
        
        try:
            import subprocess
            # 尝试启动进程（但不等待它完成）
            proc = subprocess.Popen([executable_path])
            self.add_log_message(f"已启动游戏测试: {values[0]} (PID: {proc.pid})\n")
            self.status_var.set(f"已启动游戏测试: {values[0]}")
        except Exception as e:
            messagebox.showerror("错误", f"无法启动游戏: {str(e)}")
    
    def move_workflow_up(self):
        """向上移动选中的工作流"""
        selected = self.workflow_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请选择要移动的工作流")
            return
        
        item_id = selected[0]
        item_idx = self.workflow_tree.index(item_id)
        
        if item_idx > 0:
            # 获取当前项的值
            values = self.workflow_tree.item(item_id)['values']
            # 删除当前项
            self.workflow_tree.delete(item_id)
            # 在新位置插入
            self.workflow_tree.insert('', item_idx - 1, values=values)
            # 重新选择该项
            self.workflow_tree.selection_set(f'{item_idx - 1}')
    
    def move_workflow_down(self):
        """向下移动选中的工作流"""
        selected = self.workflow_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请选择要移动的工作流")
            return
        
        item_id = selected[0]
        item_idx = self.workflow_tree.index(item_id)
        total_items = len(self.workflow_tree.get_children())
        
        if item_idx < total_items - 1:
            # 获取当前项的值
            values = self.workflow_tree.item(item_id)['values']
            # 删除当前项
            self.workflow_tree.delete(item_id)
            # 在新位置插入
            self.workflow_tree.insert('', item_idx + 1, values=values)
            # 重新选择该项
            self.workflow_tree.selection_set(f'{item_idx + 1}')
    
    def test_script(self):
        """测试脚本"""
        selected = self.scripts_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请选择要测试的脚本")
            return
        
        item = self.scripts_tree.item(selected)
        values = item['values']
        script_path = values[0]
        script_type = values[1]
        
        if not script_path or not Path(script_path).exists():
            messagebox.showerror("错误", f"脚本文件不存在: {script_path}")
            return
        
        try:
            import subprocess
            import os
            
            # 准备命令
            if script_type == "python":
                cmd = [sys.executable, script_path]
            elif script_type == "exe":
                cmd = [script_path]
            elif script_type == "bat":
                cmd = ["cmd", "/c", script_path]
            elif script_type == "ps1":
                cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path]
            elif script_type == "ahk":
                cmd = ["AutoHotkey.exe", script_path]
            else:
                messagebox.showerror("错误", f"不支持的脚本类型: {script_type}")
                return
            
            # 添加参数
            args = values[2].split() if values[2] else []
            cmd.extend(args)
            
            # 启动脚本
            proc = subprocess.Popen(cmd)
            self.add_log_message(f"已启动脚本测试: {os.path.basename(script_path)} (PID: {proc.pid})\n")
            self.status_var.set(f"已启动脚本测试: {os.path.basename(script_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"无法启动脚本: {str(e)}")
    
    def reset_config(self):
        """重置配置"""
        if messagebox.askyesno("确认", "确定要重置当前配置吗？未保存的更改将丢失。"):
            self.current_config = {}
            self.current_config_path = None
            self.config_path_var.set("")
            
            # 清空所有表格
            for item in self.variables_tree.get_children():
                self.variables_tree.delete(item)
            for item in self.games_tree.get_children():
                self.games_tree.delete(item)
            for item in self.workflow_tree.get_children():
                self.workflow_tree.delete(item)
            for item in self.scripts_tree.get_children():
                self.scripts_tree.delete(item)
            
            self.status_var.set("配置已重置")
    
    def export_report(self):
        """导出执行报告"""
        import datetime
        # 获取日志内容
        log_content = self.log_area.get(1.0, tk.END)
        
        file_path = filedialog.asksaveasfilename(
            title="导出执行报告",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Log files", "*.log"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"游戏自动化框架执行报告\n")
                    f.write(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"配置文件: {self.current_config_path or '未指定'}\n")
                    f.write("-" * 50 + "\n")
                    f.write(log_content)
                
                self.status_var.set(f"已导出执行报告: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"无法导出执行报告: {str(e)}")
    
    def clear_logs(self):
        """清空日志"""
        if messagebox.askyesno("确认", "确定要清空日志吗？"):
            self.log_area.config(state=tk.NORMAL)
            self.log_area.delete(1.0, tk.END)
            self.log_area.config(state=tk.DISABLED)
            self.status_var.set("日志已清空")
    
    def save_logs(self):
        """保存日志"""
        log_content = self.log_area.get(1.0, tk.END)
        
        file_path = filedialog.asksaveasfilename(
            title="保存日志",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                
                self.status_var.set(f"已保存日志: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存日志: {str(e)}")
    
    def toggle_auto_scroll(self):
        """切换自动滚动"""
        self.auto_scroll_enabled = not getattr(self, 'auto_scroll_enabled', True)
        status = "开启" if self.auto_scroll_enabled else "关闭"
        self.status_var.set(f"自动滚动已{status}")
    
    def run(self):
        """运行主窗口"""
        # 设置默认自动滚动状态
        self.auto_scroll_enabled = True
        self.root.mainloop()


class VariableDialog:
    """变量编辑对话框 - 现代化样式"""
    def __init__(self, parent, title, existing_values=None, predefined_configs=None):
        self.parent = parent
        self.result = None
        self.predefined_configs = predefined_configs or {}
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets(existing_values)
        
        # 居中显示
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
    def create_widgets(self, existing_values):
        """创建对话框组件"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 变量名
        ttk.Label(main_frame, text="变量名:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.name_var = tk.StringVar(value=existing_values['name'] if existing_values else "")
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 变量值
        ttk.Label(main_frame, text="变量值:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.value_var = tk.StringVar(value=existing_values['value'] if existing_values else "")
        ttk.Entry(main_frame, textvariable=self.value_var, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 描述
        ttk.Label(main_frame, text="描述:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.desc_var = tk.StringVar(value=existing_values.get('description', '') if existing_values else "")
        ttk.Entry(main_frame, textvariable=self.desc_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        if HAS_TTKBOOTSTRAP:
            ttkb.Button(button_frame, text="确定", command=self.ok_clicked, bootstyle="success").pack(side=tk.LEFT, padx=5)
            ttkb.Button(button_frame, text="取消", command=self.cancel_clicked, bootstyle="secondary").pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(button_frame, text="确定", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # 绑定回车键
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
        
        # 使对话框可见
        self.dialog.focus_set()
        
    def ok_clicked(self):
        """确定按钮点击"""
        if not self.name_var.get().strip():
            messagebox.showwarning("警告", "请输入变量名")
            return
            
        self.result = {
            'name': self.name_var.get(),
            'value': self.value_var.get(),
            'description': self.desc_var.get()
        }
        self.dialog.destroy()
        
    def cancel_clicked(self):
        """取消按钮点击"""
        self.result = None
        self.dialog.destroy()


class GameConfigDialog:
    """游戏配置对话框 - 现代化样式"""
    def __init__(self, parent, title, existing_values=None, predefined_configs=None):
        self.parent = parent
        self.result = None
        self.predefined_configs = predefined_configs or {}
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets(existing_values)
        
        # 居中显示
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
    def create_widgets(self, existing_values):
        """创建对话框组件"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 游戏名称
        ttk.Label(main_frame, text="游戏名称:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.name_var = tk.StringVar(value=existing_values.get('name', '') if existing_values else "")
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 可执行文件路径
        ttk.Label(main_frame, text="可执行文件:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.executable_var = tk.StringVar(value=existing_values.get('executable', '') if existing_values else "")
        executable_frame = ttk.Frame(main_frame)
        executable_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Entry(executable_frame, textvariable=self.executable_var, width=25).pack(side=tk.LEFT)
        ttk.Button(executable_frame, text="浏览", command=self.browse_executable).pack(side=tk.LEFT, padx=(5, 0))
        
        # 窗口标题
        ttk.Label(main_frame, text="窗口标题:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.window_title_var = tk.StringVar(value=existing_values.get('window_title', '') if existing_values else "")
        ttk.Entry(main_frame, textvariable=self.window_title_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 启动参数
        ttk.Label(main_frame, text="启动参数:").grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.arguments_var = tk.StringVar(value=' '.join(existing_values.get('arguments', [])) if existing_values else "")
        ttk.Entry(main_frame, textvariable=self.arguments_var, width=30).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        if HAS_TTKBOOTSTRAP:
            ttkb.Button(button_frame, text="确定", command=self.ok_clicked, bootstyle="success").pack(side=tk.LEFT, padx=5)
            ttkb.Button(button_frame, text="取消", command=self.cancel_clicked, bootstyle="secondary").pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(button_frame, text="确定", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # 绑定回车键
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
        
        # 使对话框可见
        self.dialog.focus_set()
        
    def browse_executable(self):
        """浏览可执行文件"""
        file_path = filedialog.askopenfilename(
            title="选择游戏可执行文件",
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
        )
        if file_path:
            self.executable_var.set(file_path)
            
    def ok_clicked(self):
        """确定按钮点击"""
        if not self.name_var.get().strip():
            messagebox.showwarning("警告", "请输入游戏名称")
            return
        if not self.executable_var.get().strip():
            messagebox.showwarning("警告", "请选择可执行文件")
            return
            
        self.result = {
            'name': self.name_var.get(),
            'executable': self.executable_var.get(),
            'window_title': self.window_title_var.get(),
            'arguments': self.arguments_var.get().split()
        }
        self.dialog.destroy()
        
    def cancel_clicked(self):
        """取消按钮点击"""
        self.result = None
        self.dialog.destroy()


class WorkflowDialog:
    """工作流配置对话框 - 现代化样式"""
    def __init__(self, parent, title, existing_values=None, predefined_configs=None):
        self.parent = parent
        self.result = None
        self.predefined_configs = predefined_configs or {}
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x280")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets(existing_values)
        
        # 居中显示
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
    def create_widgets(self, existing_values):
        """创建对话框组件"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 工作流名称
        ttk.Label(main_frame, text="名称:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.name_var = tk.StringVar(value=existing_values.get('name', '') if existing_values else "")
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 类型
        ttk.Label(main_frame, text="类型:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.type_var = tk.StringVar(value=existing_values.get('type', 'script_chain') if existing_values else "script_chain")
        type_combo = ttk.Combobox(main_frame, textvariable=self.type_var, 
                                  values=self.predefined_configs.get("game_types", ["script_chain", "game", "mixed"]), state="readonly")
        type_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 描述
        ttk.Label(main_frame, text="描述:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.desc_var = tk.StringVar(value=existing_values.get('description', '') if existing_values else "")
        ttk.Entry(main_frame, textvariable=self.desc_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 启用状态
        self.enabled_var = tk.BooleanVar(value=existing_values.get('enabled', True) if existing_values else True)
        ttk.Checkbutton(main_frame, text="启用", variable=self.enabled_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        if HAS_TTKBOOTSTRAP:
            ttkb.Button(button_frame, text="确定", command=self.ok_clicked, bootstyle="success").pack(side=tk.LEFT, padx=5)
            ttkb.Button(button_frame, text="取消", command=self.cancel_clicked, bootstyle="secondary").pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(button_frame, text="确定", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # 绑定回车键
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
        
        # 使对话框可见
        self.dialog.focus_set()
        
    def ok_clicked(self):
        """确定按钮点击"""
        if not self.name_var.get().strip():
            messagebox.showwarning("警告", "请输入工作流名称")
            return
            
        self.result = {
            'name': self.name_var.get(),
            'type': self.type_var.get(),
            'description': self.desc_var.get(),
            'enabled': self.enabled_var.get()
        }
        self.dialog.destroy()
        
    def cancel_clicked(self):
        """取消按钮点击"""
        self.result = None
        self.dialog.destroy()


class ScriptConfigDialog:
    """脚本配置对话框 - 现代化样式"""
    def __init__(self, parent, title, existing_values=None, predefined_configs=None):
        self.parent = parent
        self.result = None
        self.predefined_configs = predefined_configs or {}
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x320")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets(existing_values)
        
        # 居中显示
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
    def create_widgets(self, existing_values):
        """创建对话框组件"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 脚本路径
        ttk.Label(main_frame, text="脚本路径:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.path_var = tk.StringVar(value=existing_values.get('path', '') if existing_values else "")
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Entry(path_frame, textvariable=self.path_var, width=25).pack(side=tk.LEFT)
        ttk.Button(path_frame, text="浏览", command=self.browse_script).pack(side=tk.LEFT, padx=(5, 0))
        
        # 脚本类型
        ttk.Label(main_frame, text="类型:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.type_var = tk.StringVar(value=existing_values.get('type', 'python') if existing_values else "python")
        type_combo = ttk.Combobox(main_frame, textvariable=self.type_var, 
                                  values=["python", "exe", "bat", "ps1", "ahk"], state="readonly")
        type_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 参数
        ttk.Label(main_frame, text="参数:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.args_var = tk.StringVar(value=' '.join(existing_values.get('arguments', [])) if existing_values else "")
        ttk.Entry(main_frame, textvariable=self.args_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 超时时间
        ttk.Label(main_frame, text="超时(秒):").grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.timeout_var = tk.IntVar(value=existing_values.get('timeout', 3600) if existing_values else 3600)
        timeout_spinbox = ttk.Spinbox(main_frame, from_=1, to=86400, textvariable=self.timeout_var, width=10)
        timeout_spinbox.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        if HAS_TTKBOOTSTRAP:
            ttkb.Button(button_frame, text="确定", command=self.ok_clicked, bootstyle="success").pack(side=tk.LEFT, padx=5)
            ttkb.Button(button_frame, text="取消", command=self.cancel_clicked, bootstyle="secondary").pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(button_frame, text="确定", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # 绑定回车键
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
        
        # 使对话框可见
        self.dialog.focus_set()
        
    def browse_script(self):
        """浏览脚本文件"""
        file_types = [
            ("Python files", "*.py"),
            ("Executable files", "*.exe"),
            ("Batch files", "*.bat"),
            ("PowerShell files", "*.ps1"),
            ("AutoHotkey files", "*.ahk"),
            ("All files", "*.*")
        ]
        file_path = filedialog.askopenfilename(title="选择脚本文件", filetypes=file_types)
        if file_path:
            self.path_var.set(file_path)
            
    def ok_clicked(self):
        """确定按钮点击"""
        if not self.path_var.get().strip():
            messagebox.showwarning("警告", "请选择脚本文件")
            return
            
        self.result = {
            'path': self.path_var.get(),
            'type': self.type_var.get(),
            'arguments': self.args_var.get().split(),
            'timeout': self.timeout_var.get()
        }
        self.dialog.destroy()
        
    def cancel_clicked(self):
        """取消按钮点击"""
        self.result = None
        self.dialog.destroy()


if __name__ == "__main__":
    app = ModernUI()
    app.run()