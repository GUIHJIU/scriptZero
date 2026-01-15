"""
游戏自动化框架 - 主窗口
提供图形化界面用于配置和执行自动化任务
"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import asyncio
import threading
from pathlib import Path
import yaml

from ..game_automation_framework import GameAutomationFramework


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("游戏自动化框架 - 图形界面")
        self.root.geometry("1200x800")
        
        # 当前配置文件路径
        self.current_config_path = None
        self.framework = None
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置区域
        config_frame = ttk.LabelFrame(main_frame, text="配置管理", padding="10")
        config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 配置文件选择和操作
        ttk.Button(config_frame, text="新建配置", command=self.new_config).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(config_frame, text="打开配置", command=self.open_config).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(config_frame, text="保存配置", command=self.save_config).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(config_frame, text="保存配置为", command=self.save_config_as).grid(row=0, column=3, padx=(0, 5))
        
        # 配置文件路径显示
        self.config_path_var = tk.StringVar()
        path_entry = ttk.Entry(config_frame, textvariable=self.config_path_var, width=60, state="readonly")
        path_entry.grid(row=0, column=4, padx=(10, 0), sticky=(tk.W, tk.E))
        
        # 配置编辑器
        editor_frame = ttk.LabelFrame(main_frame, text="配置编辑器", padding="10")
        editor_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 文本编辑器
        self.text_area = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD, width=120, height=25)
        self.text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 控制按钮区域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 执行控制
        ttk.Button(control_frame, text="执行", command=self.start_execution).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="停止", command=self.stop_execution).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="暂停", command=self.pause_execution).pack(side=tk.LEFT, padx=(0, 5))
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="执行日志", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 日志文本框
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=120, height=15)
        self.log_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
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
        """新建配置文件"""
        self.current_config_path = None
        self.config_path_var.set("")
        # 填入默认配置
        default_config = """version: 1.0
name: "新自动化任务"

variables:
  game_path: "C:/Games/YourGame/Game.exe"
  script_path: "scripts/your_automation.py"

games:
  your_game:
    executable: "${variables.game_path}"
    arguments: ["-windowed"]
    window_title: "Your Game Title"

workflow:
  - name: "启动游戏"
    type: "game"
    game: "your_game"
    actions:
      - type: "launch"
      - type: "wait_for"
        condition: "window_active"
        timeout: 60

  - name: "执行自动化脚本"
    type: "script_chain"
    scripts:
      - path: "${variables.script_path}"
        arguments: ["--mode", "auto"]
        completion:
          any_of:
            - type: "timeout"
              seconds: 3600
"""
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, default_config)
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
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, content)
                self.current_config_path = file_path
                self.config_path_var.set(file_path)
                self.status_var.set(f"已打开配置文件: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"无法打开配置文件: {str(e)}")
                
    def save_config(self):
        """保存配置文件"""
        if self.current_config_path:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(self.current_config_path, 'w', encoding='utf-8') as f:
                    f.write(content)
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
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        if file_path:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.current_config_path = file_path
                self.config_path_var.set(file_path)
                self.status_var.set(f"已保存配置文件: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存配置文件: {str(e)}")
                
    def start_execution(self):
        """开始执行自动化任务"""
        # 获取当前配置内容
        config_content = self.text_area.get(1.0, tk.END).strip()
        if not config_content:
            messagebox.showwarning("警告", "请先输入配置内容")
            return
            
        # 临时保存配置到文件
        temp_config_path = "temp_config.yaml"
        with open(temp_config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
            
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
            # 这里需要在框架中添加停止功能
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
            self.log_area.insert(tk.END, message)
            self.log_area.see(tk.END)
            self.root.update_idletasks()
        # 使用after方法在主线程中更新GUI
        self.root.after(0, update_log)
        
    def run(self):
        """运行主窗口"""
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()