"""
配置编辑器 - 提供可视化配置编辑功能
"""
import tkinter as tk
from tkinter import ttk, messagebox
import yaml
from typing import Dict, Any, Callable


class ConfigEditor:
    def __init__(self, parent, on_save_callback: Callable[[Dict[str, Any]], None] = None):
        self.parent = parent
        self.on_save_callback = on_save_callback
        self.config_data = {}
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 配置类型选择
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(top_frame, text="配置类型:").pack(side=tk.LEFT, padx=(0, 5))
        self.config_type = tk.StringVar(value="basic")
        type_combo = ttk.Combobox(top_frame, textvariable=self.config_type, 
                                  values=["basic", "advanced"], state="readonly")
        type_combo.pack(side=tk.LEFT, padx=(0, 10))
        type_combo.bind("<<ComboboxSelected>>", self.on_config_type_changed)
        
        ttk.Button(top_frame, text="保存配置", command=self.save_config).pack(side=tk.RIGHT)
        ttk.Button(top_frame, text="加载配置", command=self.load_config).pack(side=tk.RIGHT, padx=(0, 5))
        
        # 创建笔记本控件用于不同配置部分
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本配置页面
        self.basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.basic_frame, text="基本配置")
        self.create_basic_config_tab()
        
        # 游戏配置页面
        self.game_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.game_frame, text="游戏配置")
        self.create_game_config_tab()
        
        # 工作流配置页面
        self.workflow_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.workflow_frame, text="工作流")
        self.create_workflow_config_tab()
        
    def create_basic_config_tab(self):
        """创建基本配置标签页"""
        # 版本和名称
        basic_info_frame = ttk.LabelFrame(self.basic_frame, text="基本信息", padding="10")
        basic_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(basic_info_frame, text="版本:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.version_var = tk.StringVar(value="1.0")
        ttk.Entry(basic_info_frame, textvariable=self.version_var, width=20).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(basic_info_frame, text="名称:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.name_var = tk.StringVar(value="新自动化任务")
        ttk.Entry(basic_info_frame, textvariable=self.name_var, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 变量配置
        variables_frame = ttk.LabelFrame(self.basic_frame, text="变量配置", padding="10")
        variables_frame.pack(fill=tk.BOTH, expand=True)
        
        # 变量表格
        columns = ('name', 'value', 'description')
        self.variables_tree = ttk.Treeview(variables_frame, columns=columns, show='headings', height=8)
        self.variables_tree.heading('name', text='变量名')
        self.variables_tree.heading('value', text='值')
        self.variables_tree.heading('description', text='描述')
        
        # 设置列宽
        self.variables_tree.column('name', width=150)
        self.variables_tree.column('value', width=300)
        self.variables_tree.column('description', width=200)
        
        # 滚动条
        variables_scrollbar = ttk.Scrollbar(variables_frame, orient=tk.VERTICAL, command=self.variables_tree.yview)
        self.variables_tree.configure(yscrollcommand=variables_scrollbar.set)
        
        # 布局
        self.variables_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        variables_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 变量操作按钮
        var_button_frame = ttk.Frame(variables_frame)
        var_button_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(var_button_frame, text="添加变量", command=self.add_variable).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(var_button_frame, text="删除变量", command=self.delete_variable).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(var_button_frame, text="编辑变量", command=self.edit_variable).pack(side=tk.LEFT, padx=(0, 5))
        
    def create_game_config_tab(self):
        """创建游戏配置标签页"""
        # 游戏配置表格
        columns = ('name', 'executable', 'window_title', 'arguments')
        self.games_tree = ttk.Treeview(self.game_frame, columns=columns, show='headings', height=15)
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
        games_scrollbar = ttk.Scrollbar(self.game_frame, orient=tk.VERTICAL, command=self.games_tree.yview)
        self.games_tree.configure(yscrollcommand=games_scrollbar.set)
        
        # 布局
        self.games_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        games_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 游戏操作按钮
        game_button_frame = ttk.Frame(self.game_frame)
        game_button_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(game_button_frame, text="添加游戏", command=self.add_game).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(game_button_frame, text="删除游戏", command=self.delete_game).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(game_button_frame, text="编辑游戏", command=self.edit_game).pack(side=tk.LEFT, padx=(0, 5))
        
    def create_workflow_config_tab(self):
        """创建工作流配置标签页"""
        # 工作流配置表格
        columns = ('name', 'type', 'description', 'enabled')
        self.workflow_tree = ttk.Treeview(self.workflow_frame, columns=columns, show='headings', height=15)
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
        workflow_scrollbar = ttk.Scrollbar(self.workflow_frame, orient=tk.VERTICAL, command=self.workflow_tree.yview)
        self.workflow_tree.configure(yscrollcommand=workflow_scrollbar.set)
        
        # 布局
        self.workflow_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        workflow_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 工作流操作按钮
        workflow_button_frame = ttk.Frame(self.workflow_frame)
        workflow_button_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(workflow_button_frame, text="添加工作流", command=self.add_workflow).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(workflow_button_frame, text="删除工作流", command=self.delete_workflow).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(workflow_button_frame, text="编辑工作流", command=self.edit_workflow).pack(side=tk.LEFT, padx=(0, 5))
        
    def on_config_type_changed(self, event=None):
        """配置类型改变事件"""
        pass
        
    def add_variable(self):
        """添加变量"""
        dialog = VariableDialog(self.parent, "添加变量")
        if dialog.result:
            self.variables_tree.insert('', tk.END, values=(dialog.result['name'], 
                                                          dialog.result['value'], 
                                                          dialog.result['description']))
            
    def delete_variable(self):
        """删除选中的变量"""
        selected = self.variables_tree.selection()
        if selected:
            self.variables_tree.delete(selected)
        else:
            messagebox.showwarning("警告", "请选择要删除的变量")
            
    def edit_variable(self):
        """编辑选中的变量"""
        selected = self.variables_tree.selection()
        if selected:
            item = self.variables_tree.item(selected)
            values = item['values']
            dialog = VariableDialog(self.parent, "编辑变量", values)
            if dialog.result:
                self.variables_tree.item(selected, values=(dialog.result['name'], 
                                                           dialog.result['value'], 
                                                           dialog.result['description']))
        else:
            messagebox.showwarning("警告", "请选择要编辑的变量")
            
    def add_game(self):
        """添加游戏配置"""
        dialog = GameConfigDialog(self.parent, "添加游戏")
        if dialog.result:
            args_str = ' '.join(dialog.result.get('arguments', []))
            self.games_tree.insert('', tk.END, values=(dialog.result['name'], 
                                                       dialog.result['executable'], 
                                                       dialog.result['window_title'],
                                                       args_str))
                                                       
    def delete_game(self):
        """删除选中的游戏配置"""
        selected = self.games_tree.selection()
        if selected:
            self.games_tree.delete(selected)
        else:
            messagebox.showwarning("警告", "请选择要删除的游戏配置")
            
    def edit_game(self):
        """编辑选中的游戏配置"""
        selected = self.games_tree.selection()
        if selected:
            item = self.games_tree.item(selected)
            values = item['values']
            dialog = GameConfigDialog(self.parent, "编辑游戏", {
                'name': values[0],
                'executable': values[1],
                'window_title': values[2],
                'arguments': values[3].split() if values[3] else []
            })
            if dialog.result:
                args_str = ' '.join(dialog.result.get('arguments', []))
                self.games_tree.item(selected, values=(dialog.result['name'], 
                                                       dialog.result['executable'], 
                                                       dialog.result['window_title'],
                                                       args_str))
        else:
            messagebox.showwarning("警告", "请选择要编辑的游戏配置")
            
    def add_workflow(self):
        """添加工作流"""
        dialog = WorkflowDialog(self.parent, "添加工作流")
        if dialog.result:
            enabled_str = "是" if dialog.result.get('enabled', True) else "否"
            self.workflow_tree.insert('', tk.END, values=(dialog.result['name'], 
                                                          dialog.result['type'], 
                                                          dialog.result.get('description', ''),
                                                          enabled_str))
                                                          
    def delete_workflow(self):
        """删除选中的工作流"""
        selected = self.workflow_tree.selection()
        if selected:
            self.workflow_tree.delete(selected)
        else:
            messagebox.showwarning("警告", "请选择要删除的工作流")
            
    def edit_workflow(self):
        """编辑选中的工作流"""
        selected = self.workflow_tree.selection()
        if selected:
            item = self.workflow_tree.item(selected)
            values = item['values']
            dialog = WorkflowDialog(self.parent, "编辑工作流", {
                'name': values[0],
                'type': values[1],
                'description': values[2],
                'enabled': values[3] == "是"
            })
            if dialog.result:
                enabled_str = "是" if dialog.result.get('enabled', True) else "否"
                self.workflow_tree.item(selected, values=(dialog.result['name'], 
                                                          dialog.result['type'], 
                                                          dialog.result.get('description', ''),
                                                          enabled_str))
        else:
            messagebox.showwarning("警告", "请选择要编辑的工作流")
            
    def save_config(self):
        """保存配置"""
        # 将界面数据转换为配置字典
        config = self.build_config_from_ui()
        
        # 调用回调函数保存配置
        if self.on_save_callback:
            self.on_save_callback(config)
        else:
            # 如果没有回调函数，则直接显示配置内容
            yaml_content = yaml.dump(config, default_flow_style=False, allow_unicode=True)
            messagebox.showinfo("配置内容", f"配置已生成:\n\n{yaml_content}")
            
    def load_config(self):
        """加载配置到界面"""
        # 这里应该从外部加载配置数据到界面
        # 暂时留空，具体实现取决于如何获取配置数据
        pass
        
    def build_config_from_ui(self) -> Dict[str, Any]:
        """从界面构建配置字典"""
        config = {
            'version': self.version_var.get(),
            'name': self.name_var.get(),
            'variables': {},
            'games': {},
            'workflow': []
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
            
        return config


class VariableDialog:
    """变量编辑对话框"""
    def __init__(self, parent, title, existing_values=None):
        self.parent = parent
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")
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
        # 变量名
        ttk.Label(self.dialog, text="变量名:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.name_var = tk.StringVar(value=existing_values[0] if existing_values else "")
        ttk.Entry(self.dialog, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # 变量值
        ttk.Label(self.dialog, text="变量值:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.value_var = tk.StringVar(value=existing_values[1] if existing_values else "")
        ttk.Entry(self.dialog, textvariable=self.value_var, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # 描述
        ttk.Label(self.dialog, text="描述:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.desc_var = tk.StringVar(value=existing_values[2] if existing_values else "")
        ttk.Entry(self.dialog, textvariable=self.desc_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
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
    """游戏配置对话框"""
    def __init__(self, parent, title, existing_values=None):
        self.parent = parent
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x300")
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
        # 游戏名称
        ttk.Label(self.dialog, text="游戏名称:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.name_var = tk.StringVar(value=existing_values.get('name', '') if existing_values else "")
        ttk.Entry(self.dialog, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # 可执行文件路径
        ttk.Label(self.dialog, text="可执行文件:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.executable_var = tk.StringVar(value=existing_values.get('executable', '') if existing_values else "")
        executable_frame = ttk.Frame(self.dialog)
        executable_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        ttk.Entry(executable_frame, textvariable=self.executable_var, width=25).pack(side=tk.LEFT)
        ttk.Button(executable_frame, text="浏览", command=self.browse_executable).pack(side=tk.LEFT, padx=(5, 0))
        
        # 窗口标题
        ttk.Label(self.dialog, text="窗口标题:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.window_title_var = tk.StringVar(value=existing_values.get('window_title', '') if existing_values else "")
        ttk.Entry(self.dialog, textvariable=self.window_title_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # 启动参数
        ttk.Label(self.dialog, text="启动参数:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        self.arguments_var = tk.StringVar(value=' '.join(existing_values.get('arguments', [])) if existing_values else "")
        ttk.Entry(self.dialog, textvariable=self.arguments_var, width=30).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # 绑定回车键
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
        
        # 使对话框可见
        self.dialog.focus_set()
        
    def browse_executable(self):
        """浏览可执行文件"""
        from tkinter import filedialog
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
    """工作流配置对话框"""
    def __init__(self, parent, title, existing_values=None):
        self.parent = parent
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x250")
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
        # 工作流名称
        ttk.Label(self.dialog, text="名称:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.name_var = tk.StringVar(value=existing_values.get('name', '') if existing_values else "")
        ttk.Entry(self.dialog, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # 类型
        ttk.Label(self.dialog, text="类型:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.type_var = tk.StringVar(value=existing_values.get('type', 'script_chain') if existing_values else "script_chain")
        type_combo = ttk.Combobox(self.dialog, textvariable=self.type_var, 
                                  values=["script_chain", "game", "mixed"], state="readonly")
        type_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # 描述
        ttk.Label(self.dialog, text="描述:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.desc_var = tk.StringVar(value=existing_values.get('description', '') if existing_values else "")
        ttk.Entry(self.dialog, textvariable=self.desc_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # 启用状态
        self.enabled_var = tk.BooleanVar(value=existing_values.get('enabled', True) if existing_values else True)
        ttk.Checkbutton(self.dialog, text="启用", variable=self.enabled_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
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