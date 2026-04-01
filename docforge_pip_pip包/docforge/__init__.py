"""
DocForge - 办公与数据处理自动化框架

使用方法：
    from docforge import CoreAPI
    api = CoreAPI()
    api.initialize()
    # ... 使用api进行操作
"""

# ========== 版本信息 ==========
__version__ = "0.1.0"
__author__ = "Xiaomi-MiMo-V2-pro and NocXen"
__description__ = "办公与数据处理自动化框架"

# ========== 导出核心API ==========
# 这些是用户最常用的东西，直接从包级别导出
from .api.core_api import CoreAPI
from .api.plugin_api import PluginAPI
from .api.event_bus import EventBus, Event

# ========== 导出插件基类 ==========
# 插件开发者需要继承这些类
from .plugins.base import BasePlugin

# ========== 导出异常 ==========
# 用户可能需要捕获这些异常
from .exceptions import (
    DocForgeException,
    PluginException,
    PluginLoadError,
    PluginDependencyError,
    PluginExecuteError,
    WorkflowException,
    WorkflowDefinitionError,
    WorkflowExecuteError,
    FileException,
    FileNotFoundError,
    FilePermissionError,
    FileFormatError,
    DatabaseException,
    ConfigException
)

# ========== 导出常用类型 ==========
from .types import (
    FileInfo,
    WorkflowDefinition,
    WorkflowStep,
    ExecutionResult,
    PluginInfo,
    DataDict,
    JsonDict
)

# ========== 导出常量 ==========
from .constants import (
    PluginType,
    WorkflowStatus,
    LogLevel,
    FileStatus
)

# ========== 定义__all__ ==========
# 当用户写 from docforge import * 时，会导入这些
__all__ = [
    # API
    "CoreAPI",
    "PluginAPI",
    "EventBus",
    "Event",
    
    # 插件基类
    "BasePlugin",
    
    # 异常
    "DocForgeException",
    "PluginException",
    "PluginLoadError",
    "PluginDependencyError",
    "PluginExecuteError",
    "WorkflowException",
    "WorkflowDefinitionError",
    "WorkflowExecuteError",
    "FileException",
    "FileNotFoundError",
    "FilePermissionError",
    "FileFormatError",
    "DatabaseException",
    "ConfigException",
    
    # 类型
    "FileInfo",
    "WorkflowDefinition",
    "WorkflowStep",
    "ExecutionResult",
    "PluginInfo",
    "DataDict",
    "JsonDict",
    
    # 常量
    "PluginType",
    "WorkflowStatus",
    "LogLevel",
    "FileStatus",
    
    # 版本信息
    "__version__",
    "__author__",
    "__description__"
]


def get_version() -> str:
    """
    获取框架版本号
    
    Returns:
        str: 版本号字符串
        
    Example:
        >>> import docforge
        >>> docforge.get_version()
        '0.1.0'
    """
    return __version__


def print_info() -> None:
    """
    打印框架信息
    
    Example:
        >>> import docforge
        >>> docforge.print_info()
        DocForge v0.1.0
        办公与数据处理自动化框架
    """
    print(f"DocForge v{__version__}")
    print(__description__)