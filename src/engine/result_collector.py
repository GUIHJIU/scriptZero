"""
结果收集器
收集、汇总和报告任务执行结果
"""
import asyncio
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import csv
import os
from pathlib import Path


class ResultStatus(Enum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    """任务结果数据类"""
    task_id: str
    status: ResultStatus
    result: Any = None
    error: Optional[Exception] = None
    start_time: datetime = None
    end_time: datetime = None
    duration: float = 0.0
    metadata: Dict[str, Any] = None
    adapter_type: str = ""
    task_type: str = ""

    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class ResultCollector:
    """结果收集器"""
    
    def __init__(self, storage_path: str = "./results", max_results: int = 1000):
        self.storage_path = Path(storage_path)
        self.max_results = max_results
        self.results: List[TaskResult] = []
        self.lock = asyncio.Lock()
        
        # 确保存储目录存在
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def collect_result(self, task_result: TaskResult):
        """收集任务结果"""
        async with self.lock:
            # 计算持续时间
            if task_result.end_time and task_result.start_time:
                task_result.duration = (task_result.end_time - task_result.start_time).total_seconds()
            elif task_result.start_time:
                task_result.duration = (datetime.now() - task_result.start_time).total_seconds()
            
            # 添加到结果列表
            self.results.append(task_result)
            
            # 如果超出最大数量，移除最旧的结果
            if len(self.results) > self.max_results:
                self.results.pop(0)
    
    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """获取指定任务的结果"""
        for result in self.results:
            if result.task_id == task_id:
                return result
        return None
    
    def get_results_by_status(self, status: ResultStatus) -> List[TaskResult]:
        """根据状态获取结果"""
        return [result for result in self.results if result.status == status]
    
    def get_results_by_adapter(self, adapter_type: str) -> List[TaskResult]:
        """根据适配器类型获取结果"""
        return [result for result in self.results if result.adapter_type == adapter_type]
    
    def get_latest_results(self, count: int = 10) -> List[TaskResult]:
        """获取最新的结果"""
        return self.results[-count:] if len(self.results) >= count else self.results[:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取结果统计信息"""
        if not self.results:
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "timeout": 0,
                "cancelled": 0,
                "partial_success": 0,
                "average_duration": 0.0,
                "total_duration": 0.0
            }
        
        stats = {
            "total": len(self.results),
            "success": len([r for r in self.results if r.status == ResultStatus.SUCCESS]),
            "failed": len([r for r in self.results if r.status == ResultStatus.FAILED]),
            "timeout": len([r for r in self.results if r.status == ResultStatus.TIMEOUT]),
            "cancelled": len([r for r in self.results if r.status == ResultStatus.CANCELLED]),
            "partial_success": len([r for r in self.results if r.status == ResultStatus.PARTIAL_SUCCESS]),
        }
        
        durations = [r.duration for r in self.results if r.duration > 0]
        stats["total_duration"] = sum(durations)
        stats["average_duration"] = stats["total_duration"] / len(durations) if durations else 0.0
        
        return stats
    
    async def export_to_json(self, filename: str = None) -> str:
        """导出结果到JSON文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results_{timestamp}.json"
        
        filepath = self.storage_path / filename
        
        # 转换结果为可序列化的格式
        serializable_results = []
        for result in self.results:
            result_dict = {
                "task_id": result.task_id,
                "status": result.status.value,
                "result": str(result.result) if result.result is not None else None,
                "error": str(result.error) if result.error else None,
                "start_time": result.start_time.isoformat() if result.start_time else None,
                "end_time": result.end_time.isoformat() if result.end_time else None,
                "duration": result.duration,
                "metadata": result.metadata,
                "adapter_type": result.adapter_type,
                "task_type": result.task_type
            }
            serializable_results.append(result_dict)
        
        async with self.lock:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    
    async def export_to_csv(self, filename: str = None) -> str:
        """导出结果到CSV文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results_{timestamp}.csv"
        
        filepath = self.storage_path / filename
        
        async with self.lock:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'task_id', 'status', 'result', 'error', 'start_time', 
                    'end_time', 'duration', 'adapter_type', 'task_type'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for result in self.results:
                    writer.writerow({
                        'task_id': result.task_id,
                        'status': result.status.value,
                        'result': str(result.result) if result.result is not None else '',
                        'error': str(result.error) if result.error else '',
                        'start_time': result.start_time.isoformat() if result.start_time else '',
                        'end_time': result.end_time.isoformat() if result.end_time else '',
                        'duration': result.duration,
                        'adapter_type': result.adapter_type,
                        'task_type': result.task_type
                    })
        
        return str(filepath)
    
    async def export_summary_report(self, filename: str = None) -> str:
        """导出摘要报告"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"summary_{timestamp}.json"
        
        filepath = self.storage_path / filename
        
        stats = self.get_statistics()
        recent_results = self.get_latest_results(20)  # 最近20个结果
        
        summary = {
            "generated_at": datetime.now().isoformat(),
            "statistics": stats,
            "recent_results": [
                {
                    "task_id": r.task_id,
                    "status": r.status.value,
                    "duration": r.duration,
                    "adapter_type": r.adapter_type,
                    "task_type": r.task_type
                } for r in recent_results
            ]
        }
        
        async with self.lock:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    
    def clear_results(self):
        """清空结果"""
        self.results.clear()
    
    async def load_from_storage(self, filename: str) -> List[TaskResult]:
        """从存储中加载结果"""
        filepath = self.storage_path / filename
        
        if not filepath.exists():
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            results = []
            for item in data:
                result = TaskResult(
                    task_id=item['task_id'],
                    status=ResultStatus(item['status']),
                    result=item['result'],
                    error=Exception(item['error']) if item['error'] else None,
                    start_time=datetime.fromisoformat(item['start_time']) if item['start_time'] else None,
                    end_time=datetime.fromisoformat(item['end_time']) if item['end_time'] else None,
                    duration=item['duration'],
                    metadata=item['metadata'],
                    adapter_type=item['adapter_type'],
                    task_type=item['task_type']
                )
                results.append(result)
            
            return results
        except Exception as e:
            print(f"Error loading results from {filename}: {e}")
            return []
    
    def search_results(self, **criteria) -> List[TaskResult]:
        """根据条件搜索结果"""
        results = self.results[:]
        
        if 'status' in criteria:
            results = [r for r in results if r.status == criteria['status']]
        
        if 'adapter_type' in criteria:
            results = [r for r in results if r.adapter_type == criteria['adapter_type']]
        
        if 'task_type' in criteria:
            results = [r for r in results if r.task_type == criteria['task_type']]
        
        if 'min_duration' in criteria:
            results = [r for r in results if r.duration >= criteria['min_duration']]
        
        if 'max_duration' in criteria:
            results = [r for r in results if r.duration <= criteria['max_duration']]
        
        return results


class TaskResultBuilder:
    """任务结果构建器"""
    
    def __init__(self):
        self.result = TaskResult(task_id="", status=ResultStatus.SUCCESS)
    
    def with_task_id(self, task_id: str):
        """设置任务ID"""
        self.result.task_id = task_id
        return self
    
    def with_status(self, status: ResultStatus):
        """设置状态"""
        self.result.status = status
        return self
    
    def with_result(self, result: Any):
        """设置结果"""
        self.result.result = result
        return self
    
    def with_error(self, error: Exception):
        """设置错误"""
        self.result.error = error
        return self
    
    def with_times(self, start_time: datetime = None, end_time: datetime = None):
        """设置时间"""
        self.result.start_time = start_time or datetime.now()
        self.result.end_time = end_time
        return self
    
    def with_metadata(self, metadata: Dict[str, Any]):
        """设置元数据"""
        self.result.metadata = metadata
        return self
    
    def with_adapter_type(self, adapter_type: str):
        """设置适配器类型"""
        self.result.adapter_type = adapter_type
        return self
    
    def with_task_type(self, task_type: str):
        """设置任务类型"""
        self.result.task_type = task_type
        return self
    
    def build(self) -> TaskResult:
        """构建结果对象"""
        if self.result.start_time is None:
            self.result.start_time = datetime.now()
        return self.result


# 全局结果收集器实例
_global_result_collector = ResultCollector()


def get_result_collector() -> ResultCollector:
    """获取全局结果收集器实例"""
    return _global_result_collector


async def collect_result(task_result: TaskResult):
    """收集结果的便捷函数"""
    collector = get_result_collector()
    await collector.collect_result(task_result)


def get_result_statistics() -> Dict[str, Any]:
    """获取结果统计的便捷函数"""
    collector = get_result_collector()
    return collector.get_statistics()


async def export_results_to_json(filename: str = None) -> str:
    """导出结果到JSON的便捷函数"""
    collector = get_result_collector()
    return await collector.export_to_json(filename)


async def export_results_to_csv(filename: str = None) -> str:
    """导出结果到CSV的便捷函数"""
    collector = get_result_collector()
    return await collector.export_to_csv(filename)