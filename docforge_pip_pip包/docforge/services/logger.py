"""
日志服务
提供分级日志记录功能

使用示例：
    from docforge.services.logger import Logger
    
    logger = Logger()
    logger.info("程序启动")
    logger.error("出错了", details="文件不存在")
"""

import logging
import os
from typing import Optional, Callable, List
from datetime import datetime
from pathlib import Path

from ..constants import LogLevel


class Logger:
    """
    日志管理器
    
    支持：
    - 分级日志（DEBUG/INFO/WARNING/ERROR/CRITICAL）
    - 输出到控制台
    - 输出到文件
    - 回调函数通知
    
    Attributes:
        name: 日志器名称
        level: 日志级别
    """
    
    def __init__(self, name: str = "docforge"):
        """
        初始化日志器
        
        Args:
            name: 日志器名称
        """
        self.name = name
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        
        # 避免重复添加处理器
        if not self._logger.handlers:
            self._setup_console_handler()
        
        # 回调函数列表
        self._callbacks: List[Callable[[str, str], None]] = []
    
    def _setup_console_handler(self) -> None:
        """设置控制台处理器"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        # 格式：时间 - 级别 - 消息
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        self._logger.addHandler(console_handler)
    
    def set_level(self, level: LogLevel) -> None:
        """
        设置日志级别
        
        Args:
            level: 日志级别
        """
        level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL
        }
        
        log_level = level_map.get(level, logging.INFO)
        self._logger.setLevel(log_level)
        
        # 同时更新所有处理器的级别
        for handler in self._logger.handlers:
            handler.setLevel(log_level)
    
    def add_file_handler(
        self,
        file_path: str,
        max_size: int = 10485760,  # 10MB
        backup_count: int = 5
    ) -> bool:
        """
        添加文件处理器
        
        Args:
            file_path: 日志文件路径
            max_size: 单个文件最大字节数
            backup_count: 备份文件数量
            
        Returns:
            bool: 是否添加成功
        """
        try:
            # 确保目录存在
            log_dir = os.path.dirname(file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # 使用RotatingFileHandler实现日志轮转
            from logging.handlers import RotatingFileHandler
            
            file_handler = RotatingFileHandler(
                file_path,
                maxBytes=max_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            
            # 格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            
            self._logger.addHandler(file_handler)
            
            self.info(f"日志文件处理器已添加: {file_path}")
            return True
            
        except Exception as e:
            self.error(f"添加文件处理器失败: {e}")
            return False
    
    def add_callback(self, callback: Callable[[str, str], None]) -> str:
        """
        添加日志回调函数
        
        当有新日志时，会调用所有注册的回调函数
        
        Args:
            callback: 回调函数，参数为 (level, message)
            
        Returns:
            str: 回调ID（用于移除）
        """
        callback_id = f"callback_{len(self._callbacks)}"
        self._callbacks.append(callback)
        return callback_id
    
    def remove_callback(self, callback: Callable[[str, str], None]) -> bool:
        """
        移除回调函数
        
        Args:
            callback: 要移除的回调函数
            
        Returns:
            bool: 是否移除成功
        """
        try:
            self._callbacks.remove(callback)
            return True
        except ValueError:
            return False
    
    def _notify_callbacks(self, level: str, message: str) -> None:
        """通知所有回调函数"""
        for callback in self._callbacks:
            try:
                callback(level, message)
            except Exception:
                pass  # 忽略回调函数中的错误
    
    def debug(self, message: str, **kwargs) -> None:
        """
        记录DEBUG级别日志
        
        Args:
            message: 日志消息
            **kwargs: 额外数据（会附加到消息中）
        """
        full_message = self._format_message(message, kwargs)
        self._logger.debug(full_message)
        self._notify_callbacks(LogLevel.DEBUG, full_message)
    
    def info(self, message: str, **kwargs) -> None:
        """
        记录INFO级别日志
        
        Args:
            message: 日志消息
            **kwargs: 额外数据
        """
        full_message = self._format_message(message, kwargs)
        self._logger.info(full_message)
        self._notify_callbacks(LogLevel.INFO, full_message)
    
    def warning(self, message: str, **kwargs) -> None:
        """
        记录WARNING级别日志
        
        Args:
            message: 日志消息
            **kwargs: 额外数据
        """
        full_message = self._format_message(message, kwargs)
        self._logger.warning(full_message)
        self._notify_callbacks(LogLevel.WARNING, full_message)
    
    def error(self, message: str, **kwargs) -> None:
        """
        记录ERROR级别日志
        
        Args:
            message: 日志消息
            **kwargs: 额外数据
        """
        full_message = self._format_message(message, kwargs)
        self._logger.error(full_message)
        self._notify_callbacks(LogLevel.ERROR, full_message)
    
    def critical(self, message: str, **kwargs) -> None:
        """
        记录CRITICAL级别日志
        
        Args:
            message: 日志消息
            **kwargs: 额外数据
        """
        full_message = self._format_message(message, kwargs)
        self._logger.critical(full_message)
        self._notify_callbacks(LogLevel.CRITICAL, full_message)
    
    def _format_message(self, message: str, kwargs: dict) -> str:
        """
        格式化消息，将kwargs附加到消息后面
        
        Args:
            message: 原始消息
            kwargs: 额外数据
            
        Returns:
            str: 格式化后的消息
        """
        if not kwargs:
            return message
        
        extras = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        return f"{message} [{extras}]"
    
    def get_logs(
        self,
        level: Optional[LogLevel] = None,
        limit: int = 100
    ) -> List[dict]:
        """
        获取日志记录（需要配置文件处理器）
        
        注意：这个方法只能读取文件中的日志，不能读取内存中的
        
        Args:
            level: 过滤的日志级别
            limit: 返回数量限制
            
        Returns:
            List[dict]: 日志记录列表
        """
        # 这个功能需要从日志文件中读取
        # 简化实现，返回空列表
        return []
    
    def clear(self) -> None:
        """清空所有处理器"""
        for handler in self._logger.handlers[:]:
            self._logger.removeHandler(handler)
        
        self._setup_console_handler()
        self.info("日志处理器已清空")