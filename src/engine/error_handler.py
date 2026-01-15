"""
错误处理器
统一处理任务执行过程中的错误和异常
"""
import asyncio
import logging
import traceback
from typing import Dict, Any, Optional, Callable, List, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
import sys
import json


class ErrorSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    SYSTEM = "system"
    USER = "user"
    NETWORK = "network"
    IO = "io"
    VALIDATION = "validation"
    TIMEOUT = "timeout"
    RESOURCE = "resource"


@dataclass
class ErrorInfo:
    """错误信息数据类"""
    error_id: str
    exception: Exception
    severity: ErrorSeverity
    category: ErrorCategory
    timestamp: datetime
    traceback_str: str
    context: Dict[str, Any]
    handled: bool = False
    retries: int = 0
    max_retries: int = 3
    recovery_strategy: Optional[str] = None


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, log_errors: bool = True, max_error_log_size: int = 1000):
        self.log_errors = log_errors
        self.max_error_log_size = max_error_log_size
        self.error_log: List[ErrorInfo] = []
        self.recovery_strategies: Dict[str, Callable] = {}
        self.default_handlers: Dict[type, Callable] = {}
        self.logger = logging.getLogger("ErrorHandler")
        
        # 设置默认错误处理器
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """设置默认错误处理器"""
        self.default_handlers.update({
            FileNotFoundError: self._handle_file_not_found,
            PermissionError: self._handle_permission_error,
            ConnectionError: self._handle_connection_error,
            TimeoutError: self._handle_timeout_error,
            ValueError: self._handle_validation_error,
            KeyError: self._handle_key_error,
        })
    
    def register_recovery_strategy(self, strategy_name: str, handler: Callable):
        """注册恢复策略"""
        self.recovery_strategies[strategy_name] = handler
    
    def register_exception_handler(self, exc_type: type, handler: Callable):
        """注册异常处理器"""
        self.default_handlers[exc_type] = handler
    
    async def handle_error(self, 
                          exception: Exception, 
                          context: Dict[str, Any] = None,
                          severity: ErrorSeverity = ErrorSeverity.ERROR,
                          category: ErrorCategory = ErrorCategory.SYSTEM,
                          error_id: str = None) -> ErrorInfo:
        """处理错误"""
        import uuid
        error_id = error_id or str(uuid.uuid4())
        
        # 创建错误信息
        error_info = ErrorInfo(
            error_id=error_id,
            exception=exception,
            severity=severity,
            category=category,
            timestamp=datetime.now(),
            traceback_str=traceback.format_exc(),
            context=context or {}
        )
        
        # 记录错误
        if self.log_errors:
            self._log_error(error_info)
        
        # 添加到错误日志
        self.error_log.append(error_info)
        if len(self.error_log) > self.max_error_log_size:
            self.error_log.pop(0)  # 移除最老的错误
        
        # 调用默认处理器
        await self._call_default_handler(exception, context)
        
        return error_info
    
    def _log_error(self, error_info: ErrorInfo):
        """记录错误到日志"""
        level_map = {
            ErrorSeverity.INFO: logging.INFO,
            ErrorSeverity.WARNING: logging.WARNING,
            ErrorSeverity.ERROR: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }
        
        level = level_map.get(error_info.severity, logging.ERROR)
        
        self.logger.log(
            level,
            f"Error ID: {error_info.error_id}, "
            f"Type: {type(error_info.exception).__name__}, "
            f"Message: {str(error_info.exception)}, "
            f"Category: {error_info.category.value}",
            extra={
                'error_id': error_info.error_id,
                'exception_type': type(error_info.exception).__name__,
                'context': error_info.context
            }
        )
    
    async def _call_default_handler(self, exception: Exception, context: Dict[str, Any]):
        """调用默认异常处理器"""
        exc_type = type(exception)
        
        # 查找最匹配的异常处理器
        handler = None
        for cls in exc_type.__mro__:  # 检查方法解析顺序
            if cls in self.default_handlers:
                handler = self.default_handlers[cls]
                break
        
        if handler:
            try:
                await handler(exception, context)
            except Exception as e:
                self.logger.error(f"Error in default handler: {e}", exc_info=True)
    
    async def _handle_file_not_found(self, exception: FileNotFoundError, context: Dict[str, Any]):
        """处理文件未找到错误"""
        self.logger.warning(f"File not found: {exception.filename}")
    
    async def _handle_permission_error(self, exception: PermissionError, context: Dict[str, Any]):
        """处理权限错误"""
        self.logger.error(f"Permission denied: {exception}")
    
    async def _handle_connection_error(self, exception: ConnectionError, context: Dict[str, Any]):
        """处理连接错误"""
        self.logger.error(f"Connection error: {exception}")
    
    async def _handle_timeout_error(self, exception: TimeoutError, context: Dict[str, Any]):
        """处理超时错误"""
        self.logger.warning(f"Operation timed out: {exception}")
    
    async def _handle_validation_error(self, exception: ValueError, context: Dict[str, Any]):
        """处理验证错误"""
        self.logger.warning(f"Validation error: {exception}")
    
    async def _handle_key_error(self, exception: KeyError, context: Dict[str, Any]):
        """处理键错误"""
        self.logger.warning(f"Key error: {exception}")
    
    async def attempt_with_recovery(self, 
                                   operation: Callable, 
                                   recovery_strategy: str = "retry",
                                   max_retries: int = 3,
                                   retry_delay: float = 1.0,
                                   context: Dict[str, Any] = None) -> Any:
        """尝试执行操作并使用恢复策略"""
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return await operation() if asyncio.iscoroutinefunction(operation) else operation()
            except Exception as e:
                last_exception = e
                error_info = await self.handle_error(
                    e, 
                    context=context, 
                    severity=ErrorSeverity.WARNING if attempt < max_retries else ErrorSeverity.ERROR
                )
                
                if attempt < max_retries:
                    # 尝试恢复策略
                    if recovery_strategy in self.recovery_strategies:
                        recovery_func = self.recovery_strategies[recovery_strategy]
                        try:
                            await recovery_func(e, context)
                        except Exception as recovery_error:
                            self.logger.error(f"Recovery failed: {recovery_error}")
                    
                    # 等待后重试
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # 指数退避
                else:
                    # 所有重试都失败了
                    error_info.handled = True
                    error_info.retries = attempt
        
        # 如果所有尝试都失败了，抛出最后一个异常
        raise last_exception
    
    def get_error_summary(self) -> Dict[str, Any]:
        """获取错误摘要"""
        if not self.error_log:
            return {"total_errors": 0}
        
        summary = {
            "total_errors": len(self.error_log),
            "by_severity": {},
            "by_category": {},
            "recent_errors": []
        }
        
        for error in self.error_log[-10:]:  # 最近10个错误
            # 按严重程度统计
            sev = error.severity.value
            summary["by_severity"][sev] = summary["by_severity"].get(sev, 0) + 1
            
            # 按类别统计
            cat = error.category.value
            summary["by_category"][cat] = summary["by_category"].get(cat, 0) + 1
            
            # 添加到最近错误列表
            summary["recent_errors"].append({
                "error_id": error.error_id,
                "exception_type": type(error.exception).__name__,
                "message": str(error.exception),
                "timestamp": error.timestamp.isoformat(),
                "severity": error.severity.value
            })
        
        return summary
    
    def clear_error_log(self):
        """清空错误日志"""
        self.error_log.clear()
    
    def get_error_by_id(self, error_id: str) -> Optional[ErrorInfo]:
        """根据ID获取错误信息"""
        for error in self.error_log:
            if error.error_id == error_id:
                return error
        return None


# 全局错误处理器实例
_global_error_handler = ErrorHandler()


def get_error_handler() -> ErrorHandler:
    """获取全局错误处理器实例"""
    return _global_error_handler


def handle_error(exception: Exception, 
                context: Dict[str, Any] = None,
                severity: ErrorSeverity = ErrorSeverity.ERROR,
                category: ErrorCategory = ErrorCategory.SYSTEM) -> ErrorInfo:
    """处理错误的便捷函数"""
    handler = get_error_handler()
    return asyncio.run(handler.handle_error(exception, context, severity, category))


async def attempt_operation_with_recovery(operation: Callable,
                                        recovery_strategy: str = "retry",
                                        max_retries: int = 3,
                                        retry_delay: float = 1.0,
                                        context: Dict[str, Any] = None):
    """使用恢复策略尝试执行操作的便捷函数"""
    handler = get_error_handler()
    return await handler.attempt_with_recovery(
        operation, recovery_strategy, max_retries, retry_delay, context
    )