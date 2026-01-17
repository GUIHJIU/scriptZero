"""
现代化GUI应用
使用PySide6实现现代化界面
"""
import sys
import asyncio
from pathlib import Path

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QTextEdit, QLabel, QTabWidget, QFileDialog, 
                              QMessageBox, QSplitter, QListWidget, QTreeWidget, QTreeWidgetItem,
                              QGroupBox, QFormLayout, QLineEdit, QSpinBox, QCheckBox, QComboBox,
                              QMenuBar, QStatusBar, QToolBar, QDialog, QGridLayout, QHeaderView,
                              QListWidgetItem, QAbstractItemView)
from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer
from PySide6.QtGui import QAction, QIcon

from src.game_automation_framework import GameAutomationFramework
from src.utils.config_validator import create_sample_config


class LogSignal(QObject):
    """日志信号类"""
    message_logged = Signal(str)


class ExecutionThread(QThread):
    """执行工作线程"""
    def __init__(self, framework, workflow_name=None):
        super().__init__()
        self.framework = framework
        self.workflow_name = workflow_name
        
    def run(self):
        """运行框架"""
        try:
            asyncio.run(self.framework.run(self.workflow_name))
        except Exception as e:
            print(f"执行出错: {e}")


class ModernMainWindow(QMainWindow):
    """现代化主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ScriptZero - 现代化游戏自动化框架")
        self.setGeometry(100, 100, 1400, 900)
        
        # 日志信号
        self.log_signal = LogSignal()
        self.log_signal.message_logged.connect(self.append_log)
        
        # 框架实例
        self.framework = None
        self.execution_thread = None
        
        # 初始化界面
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建中央分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧配置面板
        config_panel = self.create_config_panel()
        splitter.addWidget(config_panel)
        
        # 右侧面板（日志和控制）
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([700, 700])  # 设置初始大小
        
        main_layout.addWidget(splitter)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
    def create_menu(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        new_action = QAction("新建配置", self)
        new_action.triggered.connect(self.new_config)
        file_menu.addAction(new_action)
        
        open_action = QAction("打开配置", self)
        open_action.triggered.connect(self.open_config)
        file_menu.addAction(open_action)
        
        save_action = QAction("保存配置", self)
        save_action.triggered.connect(self.save_config)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("另存为", self)
        save_as_action.triggered.connect(self.save_config_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 执行菜单
        exec_menu = menubar.addMenu("执行")
        
        start_action = QAction("开始执行", self)
        start_action.triggered.connect(self.start_execution)
        exec_menu.addAction(start_action)
        
        stop_action = QAction("停止执行", self)
        stop_action.triggered.connect(self.stop_execution)
        exec_menu.addAction(stop_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = self.addToolBar("主工具栏")
        
        # 添加按钮到工具栏
        new_btn = QPushButton("新建")
        new_btn.clicked.connect(self.new_config)
        toolbar.addWidget(new_btn)
        
        open_btn = QPushButton("打开")
        open_btn.clicked.connect(self.open_config)
        toolbar.addWidget(open_btn)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_config)
        toolbar.addWidget(save_btn)
        
        toolbar.addSeparator()
        
        start_btn = QPushButton("执行")
        start_btn.clicked.connect(self.start_execution)
        toolbar.addWidget(start_btn)
        
        stop_btn = QPushButton("停止")
        stop_btn.clicked.connect(self.stop_execution)
        toolbar.addWidget(stop_btn)
        
    def create_config_panel(self):
        """创建配置面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 配置标签页
        tab_widget = QTabWidget()
        
        # 基本配置标签页
        basic_tab = self.create_basic_config_tab()
        tab_widget.addTab(basic_tab, "基本配置")
        
        # 游戏配置标签页
        game_tab = self.create_game_config_tab()
        tab_widget.addTab(game_tab, "游戏配置")
        
        # 脚本配置标签页
        script_tab = self.create_script_config_tab()
        tab_widget.addTab(script_tab, "脚本配置")
        
        # 任务链配置标签页
        task_chain_tab = self.create_task_chain_config_tab()
        tab_widget.addTab(task_chain_tab, "任务链配置")
        
        # 工作流配置标签页
        workflow_tab = self.create_workflow_config_tab()
        tab_widget.addTab(workflow_tab, "工作流")
        
        layout.addWidget(tab_widget)
        
        return panel
    
    def create_basic_config_tab(self):
        """创建基本配置标签页"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # 版本
        self.version_combo = QComboBox()
        self.version_combo.addItems(["1.0", "1.1", "2.0"])
        self.version_combo.setCurrentText("1.0")
        layout.addRow("版本:", self.version_combo)
        
        # 名称
        self.name_edit = QLineEdit()
        self.name_edit.setText("新自动化任务")
        layout.addRow("名称:", self.name_edit)
        
        # 变量配置
        variables_group = QGroupBox("变量配置")
        vars_layout = QVBoxLayout(variables_group)
        
        self.variables_tree = QTreeWidget()
        self.variables_tree.setHeaderLabels(["变量名", "值", "描述"])
        self.variables_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.variables_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.variables_tree.header().setSectionResizeMode(2, QHeaderView.Stretch)
        
        vars_buttons_layout = QHBoxLayout()
        
        add_var_btn = QPushButton("添加变量")
        add_var_btn.clicked.connect(self.add_variable)
        vars_buttons_layout.addWidget(add_var_btn)
        
        edit_var_btn = QPushButton("编辑变量")
        edit_var_btn.clicked.connect(self.edit_variable)
        vars_buttons_layout.addWidget(edit_var_btn)
        
        del_var_btn = QPushButton("删除变量")
        del_var_btn.clicked.connect(self.delete_variable)
        vars_buttons_layout.addWidget(del_var_btn)
        
        vars_layout.addWidget(self.variables_tree)
        vars_layout.addLayout(vars_buttons_layout)
        
        layout.addRow(variables_group)
        
        return widget
    
    def create_game_config_tab(self):
        """创建游戏配置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.games_list = QListWidget()
        layout.addWidget(self.games_list)
        
        buttons_layout = QHBoxLayout()
        
        add_game_btn = QPushButton("添加游戏")
        add_game_btn.clicked.connect(self.add_game)
        buttons_layout.addWidget(add_game_btn)
        
        edit_game_btn = QPushButton("编辑游戏")
        edit_game_btn.clicked.connect(self.edit_game)
        buttons_layout.addWidget(edit_game_btn)
        
        del_game_btn = QPushButton("删除游戏")
        del_game_btn.clicked.connect(self.delete_game)
        buttons_layout.addWidget(del_game_btn)
        
        layout.addLayout(buttons_layout)
        
        return widget
    
    def create_script_config_tab(self):
        """创建脚本配置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.scripts_list = QListWidget()
        layout.addWidget(self.scripts_list)
        
        buttons_layout = QHBoxLayout()
        
        add_script_btn = QPushButton("添加脚本")
        add_script_btn.clicked.connect(self.add_script)
        buttons_layout.addWidget(add_script_btn)
        
        edit_script_btn = QPushButton("编辑脚本")
        edit_script_btn.clicked.connect(self.edit_script)
        buttons_layout.addWidget(edit_script_btn)
        
        del_script_btn = QPushButton("删除脚本")
        del_script_btn.clicked.connect(self.delete_script)
        buttons_layout.addWidget(del_script_btn)
        
        # 添加测试脚本按钮
        test_script_btn = QPushButton("测试脚本")
        test_script_btn.clicked.connect(self.test_script)
        buttons_layout.addWidget(test_script_btn)
        
        layout.addLayout(buttons_layout)
        
        return widget
    
    def create_task_chain_config_tab(self):
        """创建任务链配置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.task_chain_tree = QTreeWidget()
        self.task_chain_tree.setHeaderLabels(["ID", "名称", "游戏", "脚本", "依赖项", "启用"])
        self.task_chain_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.task_chain_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.task_chain_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.task_chain_tree.header().setSectionResizeMode(3, QHeaderView.Stretch)
        self.task_chain_tree.header().setSectionResizeMode(4, QHeaderView.Stretch)
        self.task_chain_tree.header().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        layout.addWidget(self.task_chain_tree)
        
        buttons_layout = QHBoxLayout()
        
        add_task_btn = QPushButton("添加任务")
        add_task_btn.clicked.connect(self.add_task)
        buttons_layout.addWidget(add_task_btn)
        
        edit_task_btn = QPushButton("编辑任务")
        edit_task_btn.clicked.connect(self.edit_task)
        buttons_layout.addWidget(edit_task_btn)
        
        del_task_btn = QPushButton("删除任务")
        del_task_btn.clicked.connect(self.delete_task)
        buttons_layout.addWidget(del_task_btn)
        
        # 添加上移下移按钮
        move_up_btn = QPushButton("上移")
        move_up_btn.clicked.connect(self.move_task_up)
        buttons_layout.addWidget(move_up_btn)
        
        move_down_btn = QPushButton("下移")
        move_down_btn.clicked.connect(self.move_task_down)
        buttons_layout.addWidget(move_down_btn)
        
        layout.addLayout(buttons_layout)
        
        return widget
    
    def create_workflow_config_tab(self):
        """创建工作流配置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.workflow_tree = QTreeWidget()
        self.workflow_tree.setHeaderLabels(["名称", "类型", "描述", "启用"])
        self.workflow_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.workflow_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.workflow_tree.header().setSectionResizeMode(2, QHeaderView.Stretch)
        self.workflow_tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        layout.addWidget(self.workflow_tree)
        
        buttons_layout = QHBoxLayout()
        
        add_wf_btn = QPushButton("添加工作流")
        add_wf_btn.clicked.connect(self.add_workflow)
        buttons_layout.addWidget(add_wf_btn)
        
        edit_wf_btn = QPushButton("编辑工作流")
        edit_wf_btn.clicked.connect(self.edit_workflow)
        buttons_layout.addWidget(edit_wf_btn)
        
        del_wf_btn = QPushButton("删除工作流")
        del_wf_btn.clicked.connect(self.delete_workflow)
        buttons_layout.addWidget(del_wf_btn)
        
        # 添加上移下移按钮
        move_up_btn = QPushButton("上移")
        move_up_btn.clicked.connect(self.move_workflow_up)
        buttons_layout.addWidget(move_up_btn)
        
        move_down_btn = QPushButton("下移")
        move_down_btn.clicked.connect(self.move_workflow_down)
        buttons_layout.addWidget(move_down_btn)
        
        layout.addLayout(buttons_layout)
        
        return widget
    
    def create_right_panel(self):
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 控制按钮
        control_group = QGroupBox("执行控制")
        control_layout = QHBoxLayout(control_group)
        
        start_btn = QPushButton("开始执行")
        start_btn.clicked.connect(self.start_execution)
        control_layout.addWidget(start_btn)
        
        stop_btn = QPushButton("停止执行")
        stop_btn.clicked.connect(self.stop_execution)
        control_layout.addWidget(stop_btn)
        
        pause_btn = QPushButton("暂停")
        pause_btn.clicked.connect(self.pause_execution)
        control_layout.addWidget(pause_btn)
        
        preview_btn = QPushButton("预览配置")
        preview_btn.clicked.connect(self.preview_config)
        control_layout.addWidget(preview_btn)
        
        # 添加重置和导出报告按钮
        reset_btn = QPushButton("重置配置")
        reset_btn.clicked.connect(self.reset_config)
        control_layout.addWidget(reset_btn)
        
        export_btn = QPushButton("导出报告")
        export_btn.clicked.connect(self.export_report)
        control_layout.addWidget(export_btn)
        
        layout.addWidget(control_group)
        
        # 日志区域
        log_group = QGroupBox("执行日志")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        # 日志控制按钮
        log_buttons_layout = QHBoxLayout()
        
        clear_log_btn = QPushButton("清空日志")
        clear_log_btn.clicked.connect(self.clear_logs)
        log_buttons_layout.addWidget(clear_log_btn)
        
        save_log_btn = QPushButton("保存日志")
        save_log_btn.clicked.connect(self.save_logs)
        log_buttons_layout.addWidget(save_log_btn)
        
        auto_scroll_btn = QPushButton("自动滚动")
        auto_scroll_btn.setCheckable(True)
        auto_scroll_btn.setChecked(True)
        auto_scroll_btn.clicked.connect(self.toggle_auto_scroll)
        log_buttons_layout.addWidget(auto_scroll_btn)
        
        log_layout.addLayout(log_buttons_layout)
        
        layout.addWidget(log_group)
        
        return panel
    
    def new_config(self):
        """新建配置"""
        # 创建示例配置
        config = create_sample_config()
        
        # 更新界面
        self.name_edit.setText(config.name)
        
        # 清空变量列表并添加新变量
        self.variables_tree.clear()
        for name, value in config.variables.items():
            item = QTreeWidgetItem([name, str(value), ""])
            self.variables_tree.addTopLevelItem(item)
        
        # 清空游戏列表并添加新游戏
        self.games_list.clear()
        for name, game_config in config.games.items():
            self.games_list.addItem(f"{name}: {game_config.executable}")
        
        # 清空工作流列表并添加新工作流
        self.workflow_tree.clear()
        for wf in config.workflow:
            item = QTreeWidgetItem([wf.name, wf.type, wf.config.get('description', ''), 
                                   "是" if wf.enabled else "否"])
            self.workflow_tree.addTopLevelItem(item)
        
        # 清空脚本列表并添加新脚本
        self.scripts_list.clear()
        for script in config.scripts:
            self.scripts_list.addItem(f"{script.path} ({script.type})")
        
        self.statusBar().showMessage("已创建新配置")
    
    def open_config(self):
        """打开配置文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择配置文件", "", "配置文件 (*.yaml *.yml *.json);;所有文件 (*)"
        )
        if file_path:
            try:
                # 加载并验证配置
                from src.utils.config_validator import load_and_validate_config
                config = load_and_validate_config(file_path)
                
                # 更新界面
                self.name_edit.setText(config.name)
                
                # 更新变量列表
                self.variables_tree.clear()
                for name, value in config.variables.items():
                    item = QTreeWidgetItem([name, str(value), ""])
                    self.variables_tree.addTopLevelItem(item)
                
                # 更新游戏列表
                self.games_list.clear()
                for name, game_config in config.games.items():
                    self.games_list.addItem(f"{name}: {game_config.executable}")
                
                # 更新工作流列表
                self.workflow_tree.clear()
                for wf in config.workflow:
                    item = QTreeWidgetItem([wf.name, wf.type, wf.config.get('description', ''), 
                                           "是" if wf.enabled else "否"])
                    self.workflow_tree.addTopLevelItem(item)
                
                # 更新脚本列表
                self.scripts_list.clear()
                for script in config.scripts:
                    self.scripts_list.addItem(f"{script.path} ({script.type})")
                
                self.statusBar().showMessage(f"已加载配置: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法加载配置文件:\n{str(e)}")
    
    def save_config(self):
        """保存配置"""
        # 创建一个临时配置对象
        config_data = {
            'version': self.version_combo.currentText(),
            'name': self.name_edit.text(),
            'variables': {},
            'games': {},
            'workflow': [],
            'scripts': []
        }
        
        # 从界面收集变量
        for i in range(self.variables_tree.topLevelItemCount()):
            item = self.variables_tree.topLevelItem(i)
            config_data['variables'][item.text(0)] = item.text(1)
        
        # 从界面收集游戏
        for i in range(self.games_list.count()):
            item_text = self.games_list.item(i).text()
            name, path = item_text.split(': ', 1)
            config_data['games'][name] = {'executable': path}
        
        # 从界面收集工作流
        for i in range(self.workflow_tree.topLevelItemCount()):
            item = self.workflow_tree.topLevelItem(i)
            config_data['workflow'].append({
                'name': item.text(0),
                'type': item.text(1),
                'description': item.text(2),
                'enabled': item.text(3) == '是'
            })
        
        # 从界面收集脚本
        for i in range(self.scripts_list.count()):
            item_text = self.scripts_list.item(i).text()
            parts = item_text.split(' (')
            path = parts[0]
            script_type = parts[1][:-1] if len(parts) > 1 else 'python'
            config_data['scripts'].append({
                'path': path,
                'type': script_type
            })
        
        # 保存配置文件
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存配置文件", "", "YAML文件 (*.yaml);;JSON文件 (*.json);;所有文件 (*)"
        )
        
        if file_path:
            import yaml
            import json
            
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, indent=2, ensure_ascii=False)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
                
                self.statusBar().showMessage(f"已保存配置: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法保存配置文件:\n{str(e)}")
    
    def save_config_as(self):
        """另存为配置"""
        self.save_config()
    
    def start_execution(self):
        """开始执行"""
        if self.framework is None:
            # 创建框架实例
            # 由于GameAutomationFramework需要配置文件路径，我们需要先保存配置
            temp_config_path = "temp_config.yaml"
            
            # 创建临时配置文件
            config_data = {
                'version': self.version_combo.currentText(),
                'name': self.name_edit.text(),
                'variables': {},
                'games': {},
                'workflow': [],
                'scripts': []
            }
            
            # 从界面收集变量
            for i in range(self.variables_tree.topLevelItemCount()):
                item = self.variables_tree.topLevelItem(i)
                config_data['variables'][item.text(0)] = item.text(1)
            
            # 从界面收集游戏
            for i in range(self.games_list.count()):
                item_text = self.games_list.item(i).text()
                name, path = item_text.split(': ', 1)
                config_data['games'][name] = {'executable': path}
            
            # 从界面收集工作流
            for i in range(self.workflow_tree.topLevelItemCount()):
                item = self.workflow_tree.topLevelItem(i)
                config_data['workflow'].append({
                    'name': item.text(0),
                    'type': item.text(1),
                    'description': item.text(2),
                    'enabled': item.text(3) == '是'
                })
            
            # 从界面收集脚本
            for i in range(self.scripts_list.count()):
                item_text = self.scripts_list.item(i).text()
                parts = item_text.split(' (')
                path = parts[0]
                script_type = parts[1][:-1] if len(parts) > 1 else 'python'
                config_data['scripts'].append({
                    'path': path,
                    'type': script_type
                })
            
            import yaml
            with open(temp_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            
            self.framework = GameAutomationFramework(temp_config_path)
            
            # 设置回调
            self.framework.set_callbacks(
                log_callback=self.log_message,
                status_callback=self.update_status
            )
        
        # 在单独线程中执行
        self.execution_thread = ExecutionThread(self.framework)
        self.execution_thread.start()
        
        self.statusBar().showMessage("正在执行自动化任务...")
    
    def stop_execution(self):
        """停止执行"""
        if self.execution_thread and self.execution_thread.isRunning():
            self.execution_thread.terminate()
            self.execution_thread.wait()
            self.statusBar().showMessage("执行已停止")
    
    def pause_execution(self):
        """暂停执行"""
        self.statusBar().showMessage("执行已暂停（功能待实现）")
    
    def preview_config(self):
        """预览配置"""
        # 创建预览对话框
        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle("配置预览")
        preview_dialog.resize(800, 600)
        
        layout = QVBoxLayout(preview_dialog)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        # 创建临时配置数据
        config_data = {
            'version': self.version_combo.currentText(),
            'name': self.name_edit.text(),
            'variables': {},
            'games': {},
            'workflow': [],
            'scripts': []
        }
        
        # 从界面收集变量
        for i in range(self.variables_tree.topLevelItemCount()):
            item = self.variables_tree.topLevelItem(i)
            config_data['variables'][item.text(0)] = item.text(1)
        
        # 从界面收集游戏
        for i in range(self.games_list.count()):
            item_text = self.games_list.item(i).text()
            name, path = item_text.split(': ', 1)
            config_data['games'][name] = {'executable': path}
        
        # 从界面收集工作流
        for i in range(self.workflow_tree.topLevelItemCount()):
            item = self.workflow_tree.topLevelItem(i)
            config_data['workflow'].append({
                'name': item.text(0),
                'type': item.text(1),
                'description': item.text(2),
                'enabled': item.text(3) == '是'
            })
        
        # 从界面收集脚本
        for i in range(self.scripts_list.count()):
            item_text = self.scripts_list.item(i).text()
            parts = item_text.split(' (')
            path = parts[0]
            script_type = parts[1][:-1] if len(parts) > 1 else 'python'
            config_data['scripts'].append({
                'path': path,
                'type': script_type
            })
        
        import yaml
        config_yaml = yaml.dump(config_data, default_flow_style=False, allow_unicode=True)
        text_edit.setPlainText(config_yaml)
        
        layout.addWidget(text_edit)
        
        preview_dialog.exec_()
    
    def clear_logs(self):
        """清空日志"""
        self.log_text.clear()
    
    def save_logs(self):
        """保存日志"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志", "execution_log.txt", "文本文件 (*.txt);;所有文件 (*)"
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.log_text.toPlainText())
    
    def add_variable(self):
        """添加变量"""
        dialog = VariableDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name, value, desc = dialog.get_values()
            item = QTreeWidgetItem([name, value, desc])
            self.variables_tree.addTopLevelItem(item)
    
    def edit_variable(self):
        """编辑变量"""
        selected = self.variables_tree.currentItem()
        if selected:
            current_name = selected.text(0)
            current_value = selected.text(1)
            current_desc = selected.text(2)
            
            dialog = VariableDialog(self, current_name, current_value, current_desc)
            if dialog.exec_() == QDialog.Accepted:
                name, value, desc = dialog.get_values()
                selected.setText(0, name)
                selected.setText(1, value)
                selected.setText(2, desc)
        else:
            QMessageBox.warning(self, "警告", "请选择要编辑的变量")
    
    def delete_variable(self):
        """删除变量"""
        selected = self.variables_tree.currentItem()
        if selected:
            self.variables_tree.takeTopLevelItem(self.variables_tree.indexOfTopLevelItem(selected))
        else:
            QMessageBox.warning(self, "警告", "请选择要删除的变量")
    
    def add_game(self):
        """添加游戏"""
        dialog = GameDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name, executable, window_title, arguments, working_dir, priority, env_vars, timeout, close_after_completion = dialog.get_values()
            self.games_list.addItem(f"{name}: {executable}")
    
    def edit_game(self):
        """编辑游戏"""
        selected_row = self.games_list.currentRow()
        if selected_row >= 0:
            current_text = self.games_list.item(selected_row).text()
            parts = current_text.split(': ', 1)
            if len(parts) == 2:
                current_name, current_path = parts[0], parts[1]
                
                dialog = GameDialog(self, current_name, current_path, "", "", "", "normal", "", 3600, True)
                if dialog.exec_() == QDialog.Accepted:
                    name, executable, window_title, arguments, working_dir, priority, env_vars, timeout, close_after_completion = dialog.get_values()
                    self.games_list.item(selected_row).setText(f"{name}: {executable}")
        else:
            QMessageBox.warning(self, "警告", "请选择要编辑的游戏")
    
    def delete_game(self):
        """删除游戏"""
        selected_row = self.games_list.currentRow()
        if selected_row >= 0:
            self.games_list.takeItem(selected_row)
        else:
            QMessageBox.warning(self, "警告", "请选择要删除的游戏")
    
    def add_task(self):
        """添加任务链项"""
        dialog = TaskChainDialog(self, self.get_available_games(), self.get_available_scripts())
        if dialog.exec_() == QDialog.Accepted:
            task_id, name, game, script, depends_on, enabled = dialog.get_values()
            item = QTreeWidgetItem([task_id, name, game, script, ", ".join(depends_on) if depends_on else "", "是" if enabled else "否"])
            self.task_chain_tree.addTopLevelItem(item)

    def edit_task(self):
        """编辑任务链项"""
        selected = self.task_chain_tree.currentItem()
        if selected:
            task_id = selected.text(0)
            name = selected.text(1)
            game = selected.text(2)
            script = selected.text(3)
            depends_on = [x.strip() for x in selected.text(4).split(",")] if selected.text(4) != "" else []
            enabled = selected.text(5) == "是"

            dialog = TaskChainDialog(self, self.get_available_games(), self.get_available_scripts(), 
                                   task_id, name, game, script, depends_on, enabled)
            if dialog.exec_() == QDialog.Accepted:
                task_id, name, game, script, depends_on, enabled = dialog.get_values()
                selected.setText(0, task_id)
                selected.setText(1, name)
                selected.setText(2, game)
                selected.setText(3, script)
                selected.setText(4, ", ".join(depends_on) if depends_on else "")
                selected.setText(5, "是" if enabled else "否")
        else:
            QMessageBox.warning(self, "警告", "请选择要编辑的任务")

    def delete_task(self):
        """删除任务链项"""
        selected = self.task_chain_tree.currentItem()
        if selected:
            self.task_chain_tree.takeTopLevelItem(self.task_chain_tree.indexOfTopLevelItem(selected))
        else:
            QMessageBox.warning(self, "警告", "请选择要删除的任务")

    def move_task_up(self):
        """上移任务"""
        selected = self.task_chain_tree.currentItem()
        if selected:
            index = self.task_chain_tree.indexOfTopLevelItem(selected)
            if index > 0:
                # 获取当前项的值
                values = [selected.text(i) for i in range(selected.columnCount())]

                # 删除当前项
                self.task_chain_tree.takeTopLevelItem(index)

                # 在新位置插入
                new_item = QTreeWidgetItem(values)
                self.task_chain_tree.insertTopLevelItem(index - 1, new_item)

                # 重新选择该项
                self.task_chain_tree.setCurrentItem(new_item)

    def move_task_down(self):
        """下移任务"""
        selected = self.task_chain_tree.currentItem()
        if selected:
            index = self.task_chain_tree.indexOfTopLevelItem(selected)
            total_items = self.task_chain_tree.topLevelItemCount()

            if index < total_items - 1:
                # 获取当前项的值
                values = [selected.text(i) for i in range(selected.columnCount())]

                # 删除当前项
                self.task_chain_tree.takeTopLevelItem(index)

                # 在新位置插入
                new_item = QTreeWidgetItem(values)
                self.task_chain_tree.insertTopLevelItem(index + 1, new_item)

                # 重新选择该项
                self.task_chain_tree.setCurrentItem(new_item)

    def add_workflow(self):
        """添加工作流"""
        dialog = WorkflowDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name, wf_type, description, enabled = dialog.get_values()
            enabled_text = "是" if enabled else "否"
            item = QTreeWidgetItem([name, wf_type, description, enabled_text])
            self.workflow_tree.addTopLevelItem(item)
    
    def edit_workflow(self):
        """编辑工作流"""
        selected = self.workflow_tree.currentItem()
        if selected:
            current_name = selected.text(0)
            current_type = selected.text(1)
            current_desc = selected.text(2)
            current_enabled = selected.text(3) == "是"
            
            dialog = WorkflowDialog(self, current_name, current_type, current_desc, current_enabled)
            if dialog.exec_() == QDialog.Accepted:
                name, wf_type, description, enabled = dialog.get_values()
                enabled_text = "是" if enabled else "否"
                selected.setText(0, name)
                selected.setText(1, wf_type)
                selected.setText(2, description)
                selected.setText(3, enabled_text)
        else:
            QMessageBox.warning(self, "警告", "请选择要编辑的工作流")
    
    def delete_workflow(self):
        """删除工作流"""
        selected = self.workflow_tree.currentItem()
        if selected:
            self.workflow_tree.takeTopLevelItem(self.workflow_tree.indexOfTopLevelItem(selected))
        else:
            QMessageBox.warning(self, "警告", "请选择要删除的工作流")
    
    def add_script(self):
        """添加脚本"""
        dialog = ScriptDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            path, script_type, arguments, working_dir, environment_vars, timeout, completion_condition, dependencies = dialog.get_values()
            self.scripts_list.addItem(f"{path} ({script_type})")
    
    def edit_script(self):
        """编辑脚本"""
        selected_row = self.scripts_list.currentRow()
        if selected_row >= 0:
            current_text = self.scripts_list.item(selected_row).text()
            parts = current_text.split(' (')
            if len(parts) == 2:
                current_path = parts[0]
                current_type = parts[1][:-1]  # 移除末尾的 ')'
                
                dialog = ScriptDialog(self, current_path, current_type, "", "", "", 3600, "", "")
                if dialog.exec_() == QDialog.Accepted:
                    path, script_type, arguments, working_dir, environment_vars, timeout, completion_condition, dependencies = dialog.get_values()
                    self.scripts_list.item(selected_row).setText(f"{path} ({script_type})")
        else:
            QMessageBox.warning(self, "警告", "请选择要编辑的脚本")
    
    def delete_script(self):
        """删除脚本"""
        selected_row = self.scripts_list.currentRow()
        if selected_row >= 0:
            self.scripts_list.takeItem(selected_row)
        else:
            QMessageBox.warning(self, "警告", "请选择要删除的脚本")
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, 
            "关于 ScriptZero", 
            "ScriptZero - 现代化游戏自动化框架\n\n版本: 1.0\n\n使用PySide6实现现代化界面"
        )
    
    def log_message(self, message):
        """接收日志消息"""
        self.log_signal.message_logged.emit(message)
    
    def append_log(self, message):
        """追加日志到文本框"""
        self.log_text.append(message)
        
        # 如果启用了自动滚动，则滚动到底部
        if hasattr(self, '_auto_scroll_enabled') and self._auto_scroll_enabled:
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.End)
            self.log_text.setTextCursor(cursor)
    
    def update_status(self, status):
        """更新状态栏"""
        self.statusBar().showMessage(status)
    
    def move_workflow_up(self):
        """上移工作流"""
        selected = self.workflow_tree.currentItem()
        if selected:
            index = self.workflow_tree.indexOfTopLevelItem(selected)
            if index > 0:
                # 获取当前项的值
                values = [selected.text(i) for i in range(selected.columnCount())]
                
                # 删除当前项
                self.workflow_tree.takeTopLevelItem(index)
                
                # 在新位置插入
                new_item = QTreeWidgetItem(values)
                self.workflow_tree.insertTopLevelItem(index - 1, new_item)
                
                # 重新选择该项
                self.workflow_tree.setCurrentItem(new_item)
    
    def move_workflow_down(self):
        """下移工作流"""
        selected = self.workflow_tree.currentItem()
        if selected:
            index = self.workflow_tree.indexOfTopLevelItem(selected)
            total_items = self.workflow_tree.topLevelItemCount()
            
            if index < total_items - 1:
                # 获取当前项的值
                values = [selected.text(i) for i in range(selected.columnCount())]
                
                # 删除当前项
                self.workflow_tree.takeTopLevelItem(index)
                
                # 在新位置插入
                new_item = QTreeWidgetItem(values)
                self.workflow_tree.insertTopLevelItem(index + 1, new_item)
                
                # 重新选择该项
                self.workflow_tree.setCurrentItem(new_item)
    
    def test_script(self):
        """测试脚本"""
        selected_row = self.scripts_list.currentRow()
        if selected_row >= 0:
            item_text = self.scripts_list.item(selected_row).text()
            parts = item_text.split(' (')
            if len(parts) == 2:
                script_path = parts[0]
                script_type = parts[1][:-1]  # 移除末尾的 ')'
                
                # 这里可以实现脚本测试逻辑
                QMessageBox.information(self, "测试脚本", f"正在测试脚本: {script_path} ({script_type})")
        else:
            QMessageBox.warning(self, "警告", "请选择要测试的脚本")
    
    def reset_config(self):
        """重置配置"""
        reply = QMessageBox.question(self, "确认", "确定要重置配置吗？所有未保存的更改将丢失。", 
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 清空所有配置
            self.variables_tree.clear()
            self.games_list.clear()
            self.workflow_tree.clear()
            self.scripts_list.clear()
            self.name_edit.setText("新自动化任务")
            self.version_combo.setCurrentText("1.0")
            self.statusBar().showMessage("配置已重置")

    def get_available_games(self):
        """获取可用的游戏列表"""
        games = []
        for i in range(self.games_list.count()):
            item_text = self.games_list.item(i).text()
            parts = item_text.split(': ', 1)
            if len(parts) == 2:
                game_name = parts[0]
                games.append(game_name)
        return games

    def get_available_scripts(self):
        """获取可用的脚本列表"""
        scripts = []
        for i in range(self.scripts_list.count()):
            item_text = self.scripts_list.item(i).text()
            parts = item_text.split(' (')
            if len(parts) == 2:
                script_path = parts[0]
                scripts.append(script_path)
        return scripts

    def get_game_config_details(self, game_name):
        """获取游戏配置详细信息"""
        # 遍历游戏列表找到匹配的游戏并返回其详细信息
        for i in range(self.games_list.count()):
            item_text = self.games_list.item(i).text()
            parts = item_text.split(': ', 1)
            if len(parts) == 2 and parts[0] == game_name:
                # 这里我们简单地返回整个文本，实际应用中可以解析更多细节
                return f"游戏名称: {parts[0]}\n可执行文件: {parts[1]}"
        return f"未找到游戏: {game_name}"

    def get_script_config_details(self, script_path):
        """获取脚本配置详细信息"""
        # 遍历脚本列表找到匹配的脚本并返回其详细信息
        for i in range(self.scripts_list.count()):
            item_text = self.scripts_list.item(i).text()
            parts = item_text.split(' (')
            if len(parts) == 2 and parts[0] == script_path:
                script_type = parts[1][:-1]  # 移除末尾的 ')'
                return f"脚本路径: {parts[0]}\n类型: {script_type}"
        return f"未找到脚本: {script_path}"

    def export_report(self):
        """导出报告"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出执行报告", "report.txt", "文本文件 (*.txt);;所有文件 (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("ScriptZero 执行报告\n")
                    f.write(f"生成时间: {__import__('datetime').datetime.now()}\n")
                    f.write("-" * 50 + "\n")
                    f.write(self.log_text.toPlainText())
                
                QMessageBox.information(self, "成功", f"报告已导出到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法导出报告:\n{str(e)}")
    
    def toggle_auto_scroll(self, checked):
        """切换自动滚动"""
        self._auto_scroll_enabled = checked
        status = "开启" if checked else "关闭"
        self.statusBar().showMessage(f"自动滚动已{status}")


class VariableDialog(QDialog):
    """变量编辑对话框"""
    def __init__(self, parent=None, name="", value="", description=""):
        super().__init__(parent)
        self.setWindowTitle("编辑变量")
        self.resize(400, 200)
        
        layout = QFormLayout(self)
        
        self.name_edit = QLineEdit(name)
        self.value_edit = QLineEdit(value)
        self.desc_edit = QLineEdit(description)
        
        layout.addRow("变量名:", self.name_edit)
        layout.addRow("值:", self.value_edit)
        layout.addRow("描述:", self.desc_edit)
        
        # 按钮
        buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addRow(buttons_layout)
    
    def get_values(self):
        """获取输入的值"""
        return self.name_edit.text(), self.value_edit.text(), self.desc_edit.text()


class GameDialog(QDialog):
    """游戏配置对话框"""
    def __init__(self, parent=None, name="", executable="", window_title="", arguments="", working_dir="", priority="normal", environment_vars="", timeout=3600, close_after_completion=True):
        super().__init__(parent)
        self.setWindowTitle("编辑游戏")
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # 基本配置组
        basic_group = QGroupBox("基本配置")
        basic_layout = QFormLayout(basic_group)
        
        self.name_edit = QLineEdit(name)
        self.executable_edit = QLineEdit(executable)
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self.browse_executable)
        
        executable_layout = QHBoxLayout()
        executable_layout.addWidget(self.executable_edit)
        executable_layout.addWidget(browse_btn)
        
        self.window_title_edit = QLineEdit(window_title)
        
        basic_layout.addRow("游戏名称:", self.name_edit)
        basic_layout.addRow("可执行文件:", executable_layout)
        basic_layout.addRow("窗口标题:", self.window_title_edit)
        
        layout.addWidget(basic_group)
        
        # 高级选项组
        advanced_group = QGroupBox("高级选项")
        advanced_group.setCheckable(True)  # 可折叠
        advanced_group.setChecked(False)   # 默认折叠
        advanced_layout = QFormLayout(advanced_group)
        
        # 启动参数
        self.arguments_edit = QLineEdit(arguments)
        advanced_layout.addRow("启动参数:", self.arguments_edit)
        
        # 工作目录
        self.working_dir_edit = QLineEdit(working_dir)
        working_dir_btn = QPushButton("浏览")
        working_dir_btn.clicked.connect(self.browse_working_dir)
        
        working_dir_layout = QHBoxLayout()
        working_dir_layout.addWidget(self.working_dir_edit)
        working_dir_layout.addWidget(working_dir_btn)
        advanced_layout.addRow("工作目录:", working_dir_layout)
        
        # 优先级
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["low", "normal", "high", "realtime"])
        self.priority_combo.setCurrentText(priority)
        advanced_layout.addRow("进程优先级:", self.priority_combo)
        
        # 环境变量
        self.environment_vars_edit = QLineEdit(environment_vars)
        advanced_layout.addRow("环境变量:", self.environment_vars_edit)
        
        # 超时设置
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(1, 86400)  # 1秒到24小时
        self.timeout_spinbox.setValue(timeout)
        advanced_layout.addRow("超时时间(秒):", self.timeout_spinbox)
        
        # 完成后关闭
        self.close_after_completion_check = QCheckBox()
        self.close_after_completion_check.setChecked(close_after_completion)
        advanced_layout.addRow("完成后关闭:", self.close_after_completion_check)
        
        layout.addWidget(advanced_group)
        
        # 按钮
        buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def browse_executable(self):
        """浏览可执行文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择可执行文件", "", "可执行文件 (*.exe);;所有文件 (*)"
        )
        if file_path:
            self.executable_edit.setText(file_path)
    
    def browse_working_dir(self):
        """浏览工作目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择工作目录", "")
        if dir_path:
            self.working_dir_edit.setText(dir_path)
    
    def get_values(self):
        """获取输入的值"""
        return (
            self.name_edit.text(),
            self.executable_edit.text(),
            self.window_title_edit.text(),
            self.arguments_edit.text(),
            self.working_dir_edit.text(),
            self.priority_combo.currentText(),
            self.environment_vars_edit.text(),
            self.timeout_spinbox.value(),
            self.close_after_completion_check.isChecked()
        )


class WorkflowDialog(QDialog):
    """工作流配置对话框"""
    def __init__(self, parent=None, name="", wf_type="", description="", enabled=True, error_handling="continue", tasks=None):
        super().__init__(parent)
        self.setWindowTitle("编辑工作流")
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # 基本配置组
        basic_group = QGroupBox("基本配置")
        basic_layout = QFormLayout(basic_group)
        
        self.name_edit = QLineEdit(name)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["script_chain", "game", "task_chain", "mixed"])
        self.type_combo.setCurrentText(wf_type)
        self.desc_edit = QLineEdit(description)
        self.enabled_check = QCheckBox()
        self.enabled_check.setChecked(enabled)
        
        basic_layout.addRow("名称:", self.name_edit)
        basic_layout.addRow("类型:", self.type_combo)
        basic_layout.addRow("描述:", self.desc_edit)
        basic_layout.addRow("启用:", self.enabled_check)
        
        layout.addWidget(basic_group)
        
        # 任务链配置组 - 仅在类型为task_chain时显示
        self.task_chain_group = QGroupBox("任务链配置")
        self.task_chain_group.setVisible(wf_type == "task_chain")
        task_chain_layout = QVBoxLayout(self.task_chain_group)
        
        # 错误处理策略
        error_handling_layout = QHBoxLayout()
        error_handling_layout.addWidget(QLabel("错误处理:"))
        self.error_handling_combo = QComboBox()
        self.error_handling_combo.addItems(["continue", "stop", "retry"])
        self.error_handling_combo.setCurrentText(error_handling)
        error_handling_layout.addWidget(self.error_handling_combo)
        error_handling_layout.addStretch()
        task_chain_layout.addLayout(error_handling_layout)
        
        # 任务列表
        self.tasks_tree = QTreeWidget()
        self.tasks_tree.setHeaderLabels(["ID", "名称", "游戏", "脚本", "依赖项", "启用"])
        self.tasks_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tasks_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tasks_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tasks_tree.header().setSectionResizeMode(3, QHeaderView.Stretch)
        
        task_chain_layout.addWidget(self.tasks_tree)
        
        # 任务操作按钮
        task_buttons_layout = QHBoxLayout()
        self.add_task_btn = QPushButton("添加任务")
        self.add_task_btn.clicked.connect(self.add_task)
        self.edit_task_btn = QPushButton("编辑任务")
        self.edit_task_btn.clicked.connect(self.edit_task)
        self.delete_task_btn = QPushButton("删除任务")
        self.delete_task_btn.clicked.connect(self.delete_task)
        self.move_up_btn = QPushButton("上移")
        self.move_up_btn.clicked.connect(self.move_task_up)
        self.move_down_btn = QPushButton("下移")
        self.move_down_btn.clicked.connect(self.move_task_down)
        
        task_buttons_layout.addWidget(self.add_task_btn)
        task_buttons_layout.addWidget(self.edit_task_btn)
        task_buttons_layout.addWidget(self.delete_task_btn)
        task_buttons_layout.addWidget(self.move_up_btn)
        task_buttons_layout.addWidget(self.move_down_btn)
        task_buttons_layout.addStretch()
        
        task_chain_layout.addLayout(task_buttons_layout)
        
        layout.addWidget(self.task_chain_group)
        
        # 连接类型变化信号
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        
        # 按钮
        buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def on_type_changed(self, current_type):
        """当工作流类型改变时"""
        is_task_chain = current_type == "task_chain"
        self.task_chain_group.setVisible(is_task_chain)
    
    def add_task(self):
        """添加任务"""
        dialog = TaskChainDialog(self, self.get_available_games(), self.get_available_scripts())
        if dialog.exec_() == QDialog.Accepted:
            task_id, name, game, script, depends_on, enabled = dialog.get_values()
            item = QTreeWidgetItem([task_id, name, game, script, ", ".join(depends_on) if depends_on else "", "是" if enabled else "否"])
            self.tasks_tree.addTopLevelItem(item)
    
    def edit_task(self):
        """编辑任务"""
        selected = self.tasks_tree.currentItem()
        if selected:
            task_id = selected.text(0)
            name = selected.text(1)
            game = selected.text(2)
            script = selected.text(3)
            depends_on = [x.strip() for x in selected.text(4).split(",")] if selected.text(4) != "" else []
            enabled = selected.text(5) == "是"
            
            dialog = TaskChainDialog(self, self.get_available_games(), self.get_available_scripts(), 
                                   task_id, name, game, script, depends_on, enabled)
            if dialog.exec_() == QDialog.Accepted:
                task_id, name, game, script, depends_on, enabled = dialog.get_values()
                selected.setText(0, task_id)
                selected.setText(1, name)
                selected.setText(2, game)
                selected.setText(3, script)
                selected.setText(4, ", ".join(depends_on) if depends_on else "")
                selected.setText(5, "是" if enabled else "否")
        else:
            QMessageBox.warning(self, "警告", "请选择要编辑的任务")
    
    def delete_task(self):
        """删除任务"""
        selected = self.tasks_tree.currentItem()
        if selected:
            self.tasks_tree.takeTopLevelItem(self.tasks_tree.indexOfTopLevelItem(selected))
        else:
            QMessageBox.warning(self, "警告", "请选择要删除的任务")
    
    def move_task_up(self):
        """上移任务"""
        selected = self.tasks_tree.currentItem()
        if selected:
            index = self.tasks_tree.indexOfTopLevelItem(selected)
            if index > 0:
                # 获取当前项的值
                values = [selected.text(i) for i in range(selected.columnCount())]
                
                # 删除当前项
                self.tasks_tree.takeTopLevelItem(index)
                
                # 在新位置插入
                new_item = QTreeWidgetItem(values)
                self.tasks_tree.insertTopLevelItem(index - 1, new_item)
                
                # 重新选择该项
                self.tasks_tree.setCurrentItem(new_item)
    
    def move_task_down(self):
        """下移任务"""
        selected = self.tasks_tree.currentItem()
        if selected:
            index = self.tasks_tree.indexOfTopLevelItem(selected)
            total_items = self.tasks_tree.topLevelItemCount()
            
            if index < total_items - 1:
                # 获取当前项的值
                values = [selected.text(i) for i in range(selected.columnCount())]
                
                # 删除当前项
                self.tasks_tree.takeTopLevelItem(index)
                
                # 在新位置插入
                new_item = QTreeWidgetItem(values)
                self.tasks_tree.insertTopLevelItem(index + 1, new_item)
                
                # 重新选择该项
                self.tasks_tree.setCurrentItem(new_item)
    
    def get_available_games(self):
        """获取可用的游戏列表 - 需要从父窗口获取"""
        if hasattr(self.parent(), 'get_available_games'):
            return self.parent().get_available_games()
        return []
    
    def get_available_scripts(self):
        """获取可用的脚本列表 - 需要从父窗口获取"""
        if hasattr(self.parent(), 'get_available_scripts'):
            return self.parent().get_available_scripts()
        return []
    
    def get_values(self):
        """获取输入的值"""
        tasks = []
        for i in range(self.tasks_tree.topLevelItemCount()):
            item = self.tasks_tree.topLevelItem(i)
            depends_on = [x.strip() for x in item.text(4).split(",")] if item.text(4) != "" else []
            task = {
                'id': item.text(0),
                'name': item.text(1),
                'game': item.text(2),
                'script': item.text(3),
                'depends_on': depends_on,
                'enabled': item.text(5) == "是"
            }
            tasks.append(task)
        
        return (
            self.name_edit.text(), 
            self.type_combo.currentText(), 
            self.desc_edit.text(), 
            self.enabled_check.isChecked(),
            self.error_handling_combo.currentText(),
            tasks
        )


class ScriptDialog(QDialog):
    """脚本配置对话框"""
    def __init__(self, parent=None, path="", script_type="python", arguments="", working_dir="", environment_vars="", timeout=3600, completion_condition="", dependencies=None):
        super().__init__(parent)
        self.setWindowTitle("编辑脚本")
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # 基本配置组
        basic_group = QGroupBox("基本配置")
        basic_layout = QFormLayout(basic_group)
        
        self.path_edit = QLineEdit(path)
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self.browse_script)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_btn)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["python", "exe", "bat", "ps1", "ahk"])
        self.type_combo.setCurrentText(script_type)
        
        basic_layout.addRow("脚本路径:", path_layout)
        basic_layout.addRow("类型:", self.type_combo)
        
        layout.addWidget(basic_group)
        
        # 高级选项组
        advanced_group = QGroupBox("高级选项")
        advanced_group.setCheckable(True)  # 可折叠
        advanced_group.setChecked(False)   # 默认折叠
        advanced_layout = QFormLayout(advanced_group)
        
        # 参数
        self.arguments_edit = QLineEdit(arguments)
        advanced_layout.addRow("参数:", self.arguments_edit)
        
        # 工作目录
        self.working_dir_edit = QLineEdit(working_dir)
        working_dir_btn = QPushButton("浏览")
        working_dir_btn.clicked.connect(self.browse_working_dir)
        
        working_dir_layout = QHBoxLayout()
        working_dir_layout.addWidget(self.working_dir_edit)
        working_dir_layout.addWidget(working_dir_btn)
        advanced_layout.addRow("工作目录:", working_dir_layout)
        
        # 环境变量
        self.environment_vars_edit = QLineEdit(environment_vars)
        advanced_layout.addRow("环境变量:", self.environment_vars_edit)
        
        # 超时设置
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(1, 86400)  # 1秒到24小时
        self.timeout_spinbox.setValue(timeout)
        advanced_layout.addRow("超时时间(秒):", self.timeout_spinbox)
        
        # 完成条件
        self.completion_condition_edit = QLineEdit(completion_condition)
        advanced_layout.addRow("完成条件:", self.completion_condition_edit)
        
        # 依赖项
        self.dependencies_edit = QLineEdit(dependencies if dependencies else "")
        advanced_layout.addRow("依赖项:", self.dependencies_edit)
        
        layout.addWidget(advanced_group)
        
        # 按钮
        buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def browse_script(self):
        """浏览脚本文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择脚本文件", "", 
            "Python文件 (*.py);;可执行文件 (*.exe);;批处理文件 (*.bat);;PowerShell文件 (*.ps1);;AutoHotkey文件 (*.ahk);;所有文件 (*)"
        )
        if file_path:
            self.path_edit.setText(file_path)
    
    def browse_working_dir(self):
        """浏览工作目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择工作目录", "")
        if dir_path:
            self.working_dir_edit.setText(dir_path)
    
    def get_values(self):
        """获取输入的值"""
        return (
            self.path_edit.text(),
            self.type_combo.currentText(),
            self.arguments_edit.text(),
            self.working_dir_edit.text(),
            self.environment_vars_edit.text(),
            self.timeout_spinbox.value(),
            self.completion_condition_edit.text(),
            self.dependencies_edit.text()
        )


class TaskChainDialog(QDialog):
    """任务链配置对话框"""
    def __init__(self, parent=None, available_games=None, available_scripts=None, task_id="", name="", game="", script="", depends_on=None, enabled=True):
        super().__init__(parent)
        self.setWindowTitle("编辑任务链项")
        self.resize(800, 600)
        
        available_games = available_games or []
        available_scripts = available_scripts or []
        depends_on = depends_on or []
        
        layout = QVBoxLayout(self)
        
        # 任务配置表单
        form_layout = QFormLayout()
        
        self.id_edit = QLineEdit(task_id)
        self.name_edit = QLineEdit(name)
        
        # 游戏下拉列表
        self.game_combo = QComboBox()
        for game in available_games:
            self.game_combo.addItem(game)
        if game:
            self.game_combo.setCurrentText(game)
        
        # 脚本下拉列表
        self.script_combo = QComboBox()
        for script in available_scripts:
            self.script_combo.addItem(script)
        if script:
            self.script_combo.setCurrentText(script)
        
        # 依赖项配置
        self.depends_list = QListWidget()
        self.depends_list.setSelectionMode(QAbstractItemView.MultiSelection)
        
        # 添加所有可用任务到依赖项列表（游戏和脚本）
        all_tasks = list(set(available_games + available_scripts))  # 合并并去重
        for task in all_tasks:
            self.depends_list.addItem(QListWidgetItem(task))
        
        # 查找当前依赖项并选中
        for i in range(self.depends_list.count()):
            item = self.depends_list.item(i)
            if item.text() in depends_on:
                item.setSelected(True)
        
        self.enabled_check = QCheckBox()
        self.enabled_check.setChecked(enabled)
        
        form_layout.addRow("任务ID:", self.id_edit)
        form_layout.addRow("名称:", self.name_edit)
        form_layout.addRow("游戏:", self.game_combo)
        form_layout.addRow("脚本:", self.script_combo)
        form_layout.addRow("依赖项:", self.depends_list)
        form_layout.addRow("启用:", self.enabled_check)
        
        layout.addLayout(form_layout)
        
        # 游戏和脚本详细信息显示区域
        details_group = QGroupBox("配置详情")
        details_layout = QVBoxLayout(details_group)
        
        # 游戏详情
        game_details_label = QLabel("游戏详情:")
        self.game_details_text = QTextEdit()
        self.game_details_text.setMaximumHeight(100)
        self.game_details_text.setReadOnly(True)
        
        # 脚本详情
        script_details_label = QLabel("脚本详情:")
        self.script_details_text = QTextEdit()
        self.script_details_text.setMaximumHeight(100)
        self.script_details_text.setReadOnly(True)
        
        details_layout.addWidget(game_details_label)
        details_layout.addWidget(self.game_details_text)
        details_layout.addWidget(script_details_label)
        details_layout.addWidget(self.script_details_text)
        
        layout.addWidget(details_group)
        
        # 连接信号以显示详情
        self.game_combo.currentTextChanged.connect(self.show_game_details)
        self.script_combo.currentTextChanged.connect(self.show_script_details)
        
        # 按钮
        buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        # 显示初始详情
        if game:
            self.show_game_details(game)
        if script:
            self.show_script_details(script)
    
    def show_game_details(self, game_name):
        """显示游戏详细信息"""
        if game_name and hasattr(self.parent(), 'get_game_config_details'):
            details = self.parent().get_game_config_details(game_name)
            self.game_details_text.setPlainText(details)
        else:
            # 尝试从父窗口获取游戏列表，然后显示相关信息
            games_list = self.parent().get_available_games() if hasattr(self.parent(), 'get_available_games') else []
            if game_name in games_list:
                # 显示简单的占位符信息
                self.game_details_text.setPlainText(f"游戏: {game_name}\n状态: 已配置")
            else:
                self.game_details_text.setPlainText("未选择或未找到该游戏配置")
    
    def show_script_details(self, script_path):
        """显示脚本详细信息"""
        if script_path and hasattr(self.parent(), 'get_script_config_details'):
            details = self.parent().get_script_config_details(script_path)
            self.script_details_text.setPlainText(details)
        else:
            # 尝试从父窗口获取脚本列表，然后显示相关信息
            scripts_list = self.parent().get_available_scripts() if hasattr(self.parent(), 'get_available_scripts') else []
            if script_path in scripts_list:
                # 显示简单的占位符信息
                self.script_details_text.setPlainText(f"脚本: {script_path}\n状态: 已配置")
            else:
                self.script_details_text.setPlainText("未选择或未找到该脚本配置")
    
    def get_values(self):
        """获取输入的值"""
        # 获取选中的依赖项
        selected_deps = []
        for i in range(self.depends_list.count()):
            item = self.depends_list.item(i)
            if item.isSelected():
                selected_deps.append(item.text())
        
        return (
            self.id_edit.text(),
            self.name_edit.text(),
            self.game_combo.currentText(),
            self.script_combo.currentText(),
            selected_deps,
            self.enabled_check.isChecked()
        )


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用属性
    app.setApplicationName("ScriptZero")
    app.setApplicationVersion("1.0")
    
    # 创建并显示主窗口
    window = ModernMainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()