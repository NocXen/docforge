"""
插件API
供插件调用的接口

使用示例：
    # 在插件中使用
    class MyPlugin(BasePlugin):
        def execute(self, **kwargs) -> ExecutionResult:
            plugin_api = kwargs.get("plugin_api")
            
            if plugin_api:
                plugin_api.log_info("开始处理")
                content = plugin_api.read_file("input.txt")
            
            return ExecutionResult(success=True)
"""

from typing import Dict, List, Any, Optional
from pathlib import Path

from ..types import DataDict, PathLike


class PluginAPI:
    """
    插件API类
    
    提供给插件使用的功能接口
    """
    
    def __init__(self, context: Any):
        """
        初始化插件API
        
        Args:
            context: 插件上下文（包含logger、file_manager等服务）
        """
        self._context = context
        self._logger = getattr(context, 'logger', None)
        self._file_manager = getattr(context, 'file_manager', None)
        self._database = getattr(context, 'database', None)
        self._config = getattr(context, 'config', None)
        self._cache = getattr(context, 'cache', None)
        self._event_bus = getattr(context, 'event_bus', None)
    
    # ========== 日志接口 ==========
    
    def log_debug(self, message: str) -> None:
        """
        记录调试日志
        
        Args:
            message: 日志消息
        """
        if self._logger:
            self._logger.debug(message)
    
    def log_info(self, message: str) -> None:
        """
        记录信息日志
        
        Args:
            message: 日志消息
        """
        if self._logger:
            self._logger.info(message)
    
    def log_warning(self, message: str) -> None:
        """
        记录警告日志
        
        Args:
            message: 日志消息
        """
        if self._logger:
            self._logger.warning(message)
    
    def log_error(self, message: str) -> None:
        """
        记录错误日志
        
        Args:
            message: 日志消息
        """
        if self._logger:
            self._logger.error(message)
    
    # ========== 文件接口 ==========
    
    def read_file(self, file_path: PathLike) -> Optional[str]:
        """
        读取文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[str]: 文件内容，失败返回None
        """
        try:
            path = Path(file_path)
            if path.exists():
                return path.read_text(encoding='utf-8')
            return None
        except Exception as e:
            self.log_error(f"读取文件失败: {e}")
            return None
    
    def write_file(self, file_path: PathLike, content: str) -> bool:
        """
        写入文件内容
        
        Args:
            file_path: 文件路径
            content: 文件内容
            
        Returns:
            bool: 是否写入成功
        """
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            return True
        except Exception as e:
            self.log_error(f"写入文件失败: {e}")
            return False
    
    def file_exists(self, file_path: PathLike) -> bool:
        """
        检查文件是否存在
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否存在
        """
        return Path(file_path).exists()
    
    def get_file_info(self, file_path: PathLike) -> Optional[Dict[str, Any]]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[Dict[str, Any]]: 文件信息
        """
        if self._file_manager:
            return self._file_manager.get_file_info(file_path)
        return None
    
    # ========== 数据接口 ==========
    
    def get_input_data(self) -> Optional[DataDict]:
        """
        获取输入数据
        
        Returns:
            Optional[DataDict]: 输入数据
        """
        # 简化实现：从上下文获取
        return getattr(self._context, 'input_data', None)
    
    def set_output_data(self, data: DataDict) -> None:
        """
        设置输出数据
        
        Args:
            data: 输出数据
        """
        if hasattr(self._context, 'output_data'):
            self._context.output_data = data
    
    # ========== 配置接口 ==========
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        if self._config:
            return self._config.get(key, default)
        return default
    
    def get_plugin_config(self, key: str, default: Any = None) -> Any:
        """
        获取插件专用配置
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        plugin_config = getattr(self._context, 'plugin_config', {})
        return plugin_config.get(key, default)
    
    # ========== 缓存接口 ==========
    
    def cache_get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[Any]: 缓存值
        """
        if self._cache:
            return self._cache.get_memory(key)
        return None
    
    def cache_set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
            
        Returns:
            bool: 是否设置成功
        """
        if self._cache:
            return self._cache.set_memory(key, value, ttl)
        return False
    
    # ========== 数据库接口 ==========
    
    def db_query(self, sql: str, params: tuple = None) -> List[Dict]:
        """
        执行数据库查询
        
        Args:
            sql: SQL语句
            params: 参数
            
        Returns:
            List[Dict]: 查询结果
        """
        if self._database:
            # 简化实现：使用select方法
            # 实际应该支持原生SQL
            pass
        return []
    
    def db_insert(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """
        插入数据库记录
        
        Args:
            table: 表名
            data: 数据
            
        Returns:
            Optional[int]: 插入的行ID
        """
        if self._database:
            return self._database.insert(table, data)
        return None
    
    # ========== 事件接口 ==========
    
    def emit_event(self, event_name: str, data: Any = None) -> None:
        """
        发送事件
        
        Args:
            event_name: 事件名称
            data: 事件数据
        """
        if self._event_bus:
            from .event_bus import Event
            event = Event(name=event_name, data=data, source="plugin")
            self._event_bus.publish(event)
    
    def subscribe_event(self, event_name: str, callback: callable) -> str:
        """
        订阅事件
        
        Args:
            event_name: 事件名称
            callback: 回调函数
            
        Returns:
            str: 订阅ID
        """
        if self._event_bus:
            return self._event_bus.subscribe(event_name, callback)
        return ""
    
    # ========== 工具接口 ==========
    
    def get_temp_directory(self) -> str:
        """
        获取临时目录
        
        Returns:
            str: 临时目录路径
        """
        if self._cache:
            return str(self._cache.cache_dir)
        return ".temp"
    
    def create_temp_file(self, suffix: str = "") -> str:
        """
        创建临时文件
        
        Args:
            suffix: 文件后缀
            
        Returns:
            str: 临时文件路径
        """
        if self._file_manager:
            return str(self._file_manager.create_temp_file(suffix))
        
        import tempfile
        fd, path = tempfile.mkstemp(suffix=suffix)
        import os
        os.close(fd)
        return path