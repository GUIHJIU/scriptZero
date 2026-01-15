"""
简化版GUI界面
只实现核心功能：配置管理、任务控制、实时监控和结果查看
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import asyncio
import threading
import sys
import os
from pathlib import Path
import yaml
from typing import Dict, Any

try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
    HAS_TTKBOOTSTRAP = True
except ImportError:
    HAS_TTKBOOTSTRAP = False


class SimpleGUI:
    def __init__(self):
        if HAS_TTKBOOTSTRAP:
            self.root = ttkb.Window(themename="morph")
            self.style = ttkb.Style()
        else:
            self.root = tk.Tk()
        
        self.root.title("ScriptZero - 简化版GUI")
        self.root.geometry("900x700")
        
        # 当前配置和状态
        self.current_config_path = None
        self.is_running = False
        
        # 创建界面
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        if HAS_TTKBOOTSTRAP:
            main_frame = ttkb.Frame(self.root, padding="10")
        else:
            main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置管理区域
        if HAS_TTKBOOTSTRAP:
            config_frame = ttkb.Labelframe(main_frame, text="配置管理", padding="10")
        else:
            config_frame = ttk.LabelFrame(main_frame, text="配置管理", padding="10")
        config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 配置操作按钮
        if HAS_TTKBOOTSTRAP:
            ttkb.Button(config_frame, text="新建配置", command=self.new_config, bootstyle="primary").grid(row=0, column=0, padx=(0, 5))
            ttkb.Button(config_frame, text="打开配置", command=self.open_config, bootstyle="secondary").grid(row=0, column=1, padx=(0, 5))
            ttkb.Button(config_frame, text="保存配置", command=self.save_config, bootstyle="success").grid(row=0, column=2, padx=(0, 5))
            ttkb.Button(config_frame, text="配置向导", command=self.run_config_wizard, bootstyle="info").grid(row=0, column=3, padx=(0, 5))
        else:
            ttk.Button(config_frame, text="新建配置", command=self.new_config).grid(row=0, column=0, padx=(0, 5))
            ttk.Button(config_frame, text="打开配置", command=self.open_config).grid(row=0, column=1, padx=(0, 5))
            ttk.Button(config_frame, text="保存配置", command=self.save_config).grid(row=0, column=2, padx=(0, 5))
            ttk.Button(config_frame, text="配置向导", command=self.run_config_wizard).grid(row=0, column=3, padx=(0, 5))
        
        # 配置文件路径显示
        self.config_path_var = tk.StringVar()
        if HAS_TTKBOOTSTRAP:
            path_entry = ttkb.Entry(config_frame, textvariable=self.config_path_var, width=60, state="readonly")
        else:
            path_entry = ttk.Entry(config_frame, textvariable=self.config_path_var, width=60, state="readonly")
        path_entry.grid(row=0, column=4, padx=(10, 0), sticky=(tk.W, tk.E))
        
        # 配置编辑区域
        if HAS_TTKBOOTSTRAP:
            editor_frame = ttkb.Labelframe(main_frame, text="配置编辑", padding="10")
        else:
            editor_frame = ttk.LabelFrame(main_frame, text="配置编辑", padding="10")
        editor_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 配置文本编辑器
        self.config_text = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD, width=100, height=15)
        self.config_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 控制按钮区域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 任务控制按钮
        if HAS_TTKBOOTSTRAP:
            self.start_btn = ttkb.Button(control_frame, text="启动", command=self.start_task, bootstyle="success-outline")
            self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            self.stop_btn = ttkb.Button(control_frame, text="停止", command=self.stop_task, bootstyle="danger-outline")
            self.stop_btn.pack(side=tk.LEFT, padx=(0, 5))
            self.stop_btn.config(state=tk.DISABLED)  # 初始禁用停止按钮
        else:
            self.start_btn = ttk.Button(control_frame, text="启动", command=self.start_task)
            self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            self.stop_btn = ttk.Button(control_frame, text="停止", command=self.stop_task)
            self.stop_btn.pack(side=tk.LEFT, padx=(0, 5))
            self.stop_btn.config(state=tk.DISABLED)
        
        # 状态显示
        self.status_var = tk.StringVar(value="就绪")
        if HAS_TTKBOOTSTRAP:
            status_label = ttkb.Label(control_frame, textvariable=self.status_var, bootstyle="info")
        else:
            status_label = ttk.Label(control_frame, textvariable=self.status_var)
        status_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 日志区域
        if HAS_TTKBOOTSTRAP:
            log_frame = ttkb.Labelframe(main_frame, text="实时监控 - 日志", padding="10")
        else:
            log_frame = ttk.LabelFrame(main_frame, text="实时监控 - 日志", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=100, height=15)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 日志控制按钮
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.grid(row=1, column=0, pady=(5, 0), sticky=(tk.W, tk.E))
        
        if HAS_TTKBOOTSTRAP:
            ttkb.Button(log_control_frame, text="清空日志", command=self.clear_logs, bootstyle="secondary-outline").pack(side=tk.LEFT, padx=(0, 5))
            ttkb.Button(log_control_frame, text="保存日志", command=self.save_logs, bootstyle="secondary-outline").pack(side=tk.LEFT, padx=(0, 5))
        else:
            ttk.Button(log_control_frame, text="清空日志", command=self.clear_logs).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(log_control_frame, text="保存日志", command=self.save_logs).pack(side=tk.LEFT, padx=(0, 5))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def new_config(self):
        """新建配置"""
        default_config = """version: "1.0"
project_name: "ScriptZero"
core:
  log_level: "INFO"
  debug_mode: false
  max_workers: 4
  temp_dir: "./temp"
game:
  game_name: "Genshin Impact"
  genshin_path: ""
  bettergi_path: ""
  templates_path: "./templates"
  check_interval: 30
  timeout: 3600
  close_after_completion: true
  image_templates: {}
  bettergi_workflow: {}
adapters: []
"""
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(1.0, default_config)
        self.current_config_path = None
        self.config_path_var.set("未保存的新配置")
        self.status_var.set("已创建新配置")
    
    def open_config(self):
        """打开配置文件"""
        file_path = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.config_text.delete(1.0, tk.END)
                self.config_text.insert(1.0, content)
                self.current_config_path = file_path
                self.config_path_var.set(file_path)
                self.status_var.set(f"已加载配置: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"无法打开配置文件: {str(e)}")
    
    def save_config(self):
        """保存配置文件"""
        if self.current_config_path:
            try:
                content = self.config_text.get(1.0, tk.END).strip()
                with open(self.current_config_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_var.set(f"已保存配置: {os.path.basename(self.current_config_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存配置文件: {str(e)}")
        else:
            self.save_config_as()
    
    def save_config_as(self):
        """另存为配置文件"""
        file_path = filedialog.asksaveasfilename(
            title="保存配置文件",
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        if file_path:
            try:
                content = self.config_text.get(1.0, tk.END).strip()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.current_config_path = file_path
                self.config_path_var.set(file_path)
                self.status_var.set(f"已保存配置: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存配置文件: {str(e)}")
    
    def run_config_wizard(self):
        """运行配置向导"""
        # 在新线程中运行配置向导，避免阻塞GUI
        thread = threading.Thread(target=self._run_config_wizard_thread)
        thread.daemon = True
        thread.start()
    
    def _run_config_wizard_thread(self):
        """在后台线程运行配置向导"""
        try:
            from src.config.wizard import run_config_wizard
            # 这里需要以某种方式捕获向导的结果并更新GUI
            self.root.after(0, lambda: messagebox.showinfo("提示", "配置向导将在控制台中运行，请切换到控制台窗口完成配置。"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"无法启动配置向导: {str(e)}"))
    
    def start_task(self):
        """启动任务"""
        if self.is_running:
            return
        
        # 验证配置
        config_content = self.config_text.get(1.0, tk.END).strip()
        if not config_content:
            messagebox.showwarning("警告", "请先输入配置内容")
            return
        
        try:
            # 解析配置验证格式
            config = yaml.safe_load(config_content)
            if not config:
                raise ValueError("配置文件格式不正确")
        except Exception as e:
            messagebox.showerror("错误", f"配置文件格式错误: {str(e)}")
            return
        
        # 保存临时配置
        temp_config_path = "temp_gui_config.yaml"
        with open(temp_config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        # 更新状态
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_var.set("正在执行任务...")
        
        # 在新线程中运行任务
        thread = threading.Thread(target=self._run_task_thread, args=(temp_config_path,))
        thread.daemon = True
        thread.start()
    
    def _run_task_thread(self, config_path):
        """在后台线程运行任务"""
        try:
            # 导入所需的模块
            from src.config.loader import ConfigLoader
            from src.adapters.game_adapters.genshin_bettergi import GenshinBetterGIAdapter
            
            # 加载配置
            loader = ConfigLoader()
            config = loader.load_from_single_file(config_path)
            
            # 根据配置创建适配器
            adapter = None
            if config.game.game_name.lower() in ["genshin impact", "genshin", "yuanshen"]:
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
                self.root.after(0, lambda: self.add_log_message(f"错误: 不支持的游戏类型: {config.game.game_name}\n"))
                return
            
            # 执行任务
            self.root.after(0, lambda: self.add_log_message(f"启动适配器: {config.game.game_name}\n"))
            
            # 使用asyncio运行异步方法
            import subprocess
            import sys
            result = subprocess.run([
                sys.executable, '-c', f'''
import asyncio
import sys
import os
sys.path.insert(0, "{os.getcwd()}")

from src.config.loader import ConfigLoader
from src.adapters.game_adapters.genshin_bettergi import GenshinBetterGIAdapter

async def run_task():
    try:
        # 加载配置
        loader = ConfigLoader()
        config = loader.load_from_single_file("{config_path}")
        
        # 创建适配器
        adapter_config = {{
            'game_name': config.game.game_name,
            'genshin_path': config.game.genshin_path,
            'bettergi_path': config.game.bettergi_path,
            'templates_path': config.game.templates_path,
            'check_interval': config.game.check_interval,
            'timeout': config.game.timeout,
            'close_after_completion': config.game.close_after_completion,
            'image_templates': config.game.image_templates.dict() if config.game.image_templates else {{}},
            'bettergi_workflow': config.game.bettergi_workflow.dict() if config.game.bettergi_workflow else {{}}
        }}
        
        adapter = GenshinBetterGIAdapter(adapter_config)
        
        # 启动适配器
        print(f"启动适配器: {{config.game.game_name}}")
        start_success = await adapter.start()
        if not start_success:
            print("适配器启动失败")
            return
        
        # 执行主要任务
        print("执行自动化任务...")
        try:
            result = await adapter.execute()
            print(f"任务执行结果: {{result}}")
        except Exception as e:
            print(f"任务执行失败: {{str(e)}}")
        finally:
            # 停止适配器
            print("停止适配器...")
            await adapter.stop()
        
        print("自动化任务完成")

asyncio.run(run_task())
'''
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            # 处理结果
            if result.stdout:
                self.root.after(0, lambda: self.add_log_message(result.stdout))
            if result.stderr:
                self.root.after(0, lambda: self.add_log_message(f"错误: {result.stderr}\n"))
        
        except Exception as e:
            self.root.after(0, lambda: self.add_log_message(f"执行出错: {str(e)}\n"))
            import traceback
            self.root.after(0, lambda: self.add_log_message(traceback.format_exc() + "\n"))
        finally:
            # 任务完成后的清理工作
            self.root.after(0, self._task_finished)
    
    def _task_finished(self):
        """任务完成后的清理工作"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("任务已完成")
        self.add_log_message("任务执行完毕\n")
    
    def stop_task(self):
        """停止任务"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("任务已停止")
        self.add_log_message("任务已被用户停止\n")
    
    def add_log_message(self, message):
        """添加日志消息"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def clear_logs(self):
        """清空日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def save_logs(self):
        """保存日志"""
        file_path = filedialog.asksaveasfilename(
            title="保存日志",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                log_content = self.log_text.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                self.status_var.set(f"日志已保存: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存日志: {str(e)}")
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()


def main():
    """主函数"""
    app = SimpleGUI()
    app.run()


if __name__ == "__main__":
    main()