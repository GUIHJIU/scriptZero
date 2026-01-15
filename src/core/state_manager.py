"""
全局状态管理器
实现跨脚本状态共享和执行历史跟踪
"""
import asyncio
import json
import time
from typing import Any, Dict, List, Optional
from pathlib import Path
import sqlite3
import threading


class StateManager:
    """全局状态管理器"""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "state.json"
        self.db_path = "state.db"  # SQLite数据库用于持久化存储
        self.state = {
            'scripts': {},      # 脚本执行状态
            'games': {},        # 游戏进程状态
            'variables': {},    # 用户定义变量
            'resources': {},    # 系统资源状态
            'history': [],      # 执行历史
            'config': {}        # 全局配置
        }
        self.lock = asyncio.Lock()
        self.event_handlers = {}
        self.auto_save = True
        
        # 初始化SQLite数据库
        self._init_db()
        
        # 初始化时加载已保存的状态
        self.load_state()
    
    def _init_db(self):
        """初始化SQLite数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建表用于存储状态和历史记录
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT,
                timestamp REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS execution_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_name TEXT,
                start_time REAL,
                end_time REAL,
                status TEXT,
                result TEXT,
                timestamp REAL DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_event_handler(self, event_type: str, handler):
        """注册事件处理器"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def emit_event(self, event_type: str, data: Dict[str, Any]):
        """触发事件"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    print(f"Event handler error for {event_type}: {e}")
    
    async def update_state(self, key: str, value: Any):
        """更新状态"""
        async with self.lock:
            # 状态更新
            self.state[key] = value
            
            # 触发状态变更事件
            await self.emit_event('state_changed', {key: value})
            
            # 持久化（可选）
            if self.auto_save:
                await self.save_state()
    
    async def get_state(self, key: str, default: Any = None):
        """获取状态值"""
        async with self.lock:
            return self.state.get(key, default)
    
    async def update_nested_state(self, keys: List[str], value: Any):
        """更新嵌套状态值"""
        async with self.lock:
            current = self.state
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            current[keys[-1]] = value
            
            # 触发状态变更事件
            await self.emit_event('state_changed', {'keys': keys, 'value': value})
            
            # 持久化
            if self.auto_save:
                await self.save_state()
    
    async def increment_counter(self, counter_key: str, amount: int = 1):
        """递增计数器"""
        current_value = await self.get_state(counter_key, 0)
        new_value = current_value + amount
        await self.update_state(counter_key, new_value)
        return new_value
    
    async def add_execution_history(self, entry: Dict[str, Any]):
        """添加执行历史到数据库"""
        # 存储到SQLite数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO execution_history 
            (workflow_name, start_time, end_time, status, result)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            entry.get('workflow_name', ''),
            entry.get('start_time'),
            entry.get('end_time'),
            entry.get('status', ''),
            json.dumps(entry.get('result', {}))
        ))
        
        conn.commit()
        conn.close()
        
        # 同时更新内存中的历史记录
        async with self.lock:
            # 限制历史记录数量，避免无限增长
            if len(self.state['history']) > 1000:
                self.state['history'] = self.state['history'][-500:]  # 保留最近500条
            
            self.state['history'].append({
                'timestamp': time.time(),
                'entry': entry
            })
            
            # 触发历史更新事件
            await self.emit_event('history_updated', entry)
            
            # 持久化
            if self.auto_save:
                await self.save_state()
    
    async def get_execution_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """从数据库获取执行历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT workflow_name, start_time, end_time, status, result, timestamp
            FROM execution_history
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'workflow_name': row[0],
                'start_time': row[1],
                'end_time': row[2],
                'status': row[3],
                'result': json.loads(row[4]) if row[4] else {},
                'timestamp': row[5]
            })
        
        return history
    
    async def save_state(self):
        """保存状态到文件和数据库"""
        try:
            # 保存到JSON文件（主要用于快速访问）
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2, default=str)
            
            # 保存到SQLite数据库（主要用于持久化）
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for key, value in self.state.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO state (key, value, timestamp)
                    VALUES (?, ?, ?)
                ''', (key, json.dumps(value, default=str), time.time()))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving state: {e}")
    
    def load_state(self):
        """从文件和数据库加载状态"""
        try:
            # 从SQLite数据库加载
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT key, value FROM state')
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                key = row[0]
                try:
                    value = json.loads(row[1])
                    self.state[key] = value
                except json.JSONDecodeError:
                    # 如果不是有效的JSON，直接使用字符串
                    self.state[key] = row[1]
        except Exception as e:
            print(f"Error loading state from database: {e}")
        
        # 从JSON文件加载（覆盖数据库内容，因为可能是更新的）
        try:
            if Path(self.storage_path).exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    loaded_state = json.load(f)
                    # 合并加载的状态，保留内存中的最新状态
                    self.state.update(loaded_state)
        except Exception as e:
            print(f"Error loading state from file: {e}")
    
    async def reset_state(self):
        """重置状态"""
        async with self.lock:
            self.state = {
                'scripts': {},
                'games': {},
                'variables': {},
                'resources': {},
                'history': [],
                'config': {}
            }
            await self.save_state()
    
    async def set_variable(self, name: str, value: Any):
        """设置变量"""
        variables = await self.get_state('variables', {})
        variables[name] = value
        await self.update_state('variables', variables)
    
    async def get_variable(self, name: str, default: Any = None):
        """获取变量"""
        variables = await self.get_state('variables', {})
        return variables.get(name, default)
    
    async def delete_variable(self, name: str):
        """删除变量"""
        variables = await self.get_state('variables', {})
        if name in variables:
            del variables[name]
            await self.update_state('variables', variables)
    
    async def get_recent_executions(self, workflow_name: Optional[str] = None, 
                                   status_filter: Optional[str] = None, 
                                   limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的执行记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT workflow_name, start_time, end_time, status, result, timestamp
            FROM execution_history
            WHERE 1=1
        '''
        params = []
        
        if workflow_name:
            query += ' AND workflow_name = ?'
            params.append(workflow_name)
        
        if status_filter:
            query += ' AND status = ?'
            params.append(status_filter)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'workflow_name': row[0],
                'start_time': row[1],
                'end_time': row[2],
                'status': row[3],
                'result': json.loads(row[4]) if row[4] else {},
                'timestamp': row[5]
            })
        
        return history
    
    async def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取总执行次数
        cursor.execute('SELECT COUNT(*) FROM execution_history')
        total_executions = cursor.fetchone()[0]
        
        # 获取成功/失败次数
        cursor.execute('SELECT status, COUNT(*) FROM execution_history GROUP BY status')
        status_counts = dict(cursor.fetchall())
        
        # 获取最近执行时间
        cursor.execute('SELECT MAX(timestamp) FROM execution_history')
        last_execution = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_executions': total_executions,
            'status_counts': status_counts,
            'last_execution': last_execution,
            'success_rate': status_counts.get('success', 0) / max(total_executions, 1) * 100
        }