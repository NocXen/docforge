"""
常量定义模块
定义框架中使用的所有常量和枚举

使用示例：
    from docforge.constants import PluginType, WorkflowStatus
    
    # 检查插件类型
    if plugin.plugin_type == PluginType.EXTRACTOR:
        print("这是一个提取器插件")
    
    # 检查工作流状态
    if status == WorkflowStatus.RUNNING:
        print("工作流正在运行")
"""

from enum import Enum


# ========== 插件类型 ==========

class PluginType(str, Enum):
    """
    插件类型枚举
    
    说明：
    - EXTRACTOR: 数据提取器，从文件中提取数据
    - TRANSFORMER: 数据转换器，处理和转换数据
    - REPLACER: 模板替换器，将数据填入模板
    - POST_PROCESSOR: 后处理器，处理生成的文件
    """
    EXTRACTOR = "extractor"
    TRANSFORMER = "transformer"
    REPLACER = "replacer"
    POST_PROCESSOR = "post_processor"


# ========== 工作流状态 ==========

class WorkflowStatus(str, Enum):
    """
    工作流执行状态
    
    状态转换：
    IDLE → RUNNING → COMPLETED
                → FAILED
                → CANCELLED
                → PAUSED → RUNNING
    """
    IDLE = "idle"               # 空闲，未执行
    RUNNING = "running"         # 运行中
    PAUSED = "paused"           # 暂停
    COMPLETED = "completed"     # 完成
    FAILED = "failed"           # 失败
    CANCELLED = "cancelled"     # 已取消


# ========== 日志级别 ==========

class LogLevel(str, Enum):
    """
    日志级别
    
    从低到高：
    DEBUG < INFO < WARNING < ERROR < CRITICAL
    
    设置某个级别后，只会记录该级别及以上的日志
    """
    DEBUG = "DEBUG"         # 调试信息，最详细
    INFO = "INFO"           # 一般信息
    WARNING = "WARNING"     # 警告
    ERROR = "ERROR"         # 错误
    CRITICAL = "CRITICAL"   # 严重错误


# ========== 文件状态 ==========

class FileStatus(str, Enum):
    """
    文件处理状态
    
    状态转换：
    PENDING → PROCESSING → COMPLETED
                       → FAILED
                       → SKIPPED
    """
    PENDING = "pending"         # 待处理
    PROCESSING = "processing"   # 处理中
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"           # 失败
    SKIPPED = "skipped"         # 已跳过


# ========== 配置键名 ==========

class ConfigKeys:
    """
    配置键名常量
    
    用于访问配置字典中的特定配置项
    
    使用示例：
        from docforge.constants import ConfigKeys
        
        # 获取数据库路径
        db_path = config.get(ConfigKeys.DB_PATH)
    """
    
    # ========== 项目配置 ==========
    PROJECT_NAME = "project.name"
    PROJECT_VERSION = "project.version"
    PROJECT_PATH = "project.path"
    
    # ========== 插件配置 ==========
    PLUGIN_DIR = "plugins.directory"        # 插件目录
    PLUGIN_AUTO_LOAD = "plugins.auto_load"  # 是否自动加载插件
    
    # ========== 数据库配置 ==========
    DB_PATH = "database.path"               # 数据库文件路径
    DB_AUTO_BACKUP = "database.auto_backup" # 是否自动备份
    
    # ========== 日志配置 ==========
    LOG_LEVEL = "logging.level"             # 日志级别
    LOG_FILE = "logging.file"               # 日志文件路径
    LOG_MAX_SIZE = "logging.max_size"       # 日志文件最大大小
    
    # ========== 文件配置 ==========
    TEMP_DIR = "files.temp_directory"       # 临时目录
    BACKUP_DIR = "files.backup_directory"   # 备份目录
    MAX_FILE_SIZE = "files.max_size"        # 最大文件大小


# ========== 文件扩展名 ==========

class FileExtensions:
    """
    支持的文件扩展名
    
    使用示例：
        from docforge.constants import FileExtensions
        
        # 检查是否是Excel文件
        if ext in FileExtensions.EXCEL:
            print("这是Excel文件")
        
        # 获取所有支持的扩展名
        all_exts = FileExtensions.get_all()
    """
    
    # Excel文件（支持pandas可读取的所有格式）
    EXCEL = [".xlsx", ".xls", ".xlsm", ".xlsb", ".odf", ".ods", ".odt"]
    
    # Word文件
    WORD = [".docx", ".doc"]
    
    # CSV文件
    CSV = [".csv"]
    
    # JSON文件
    JSON = [".json"]
    
    # XML文件
    XML = [".xml"]
    
    # 文本文件
    TEXT = [".txt", ".md"]
    
    # HTML文件
    HTML = [".html", ".htm"]
    
    @classmethod
    def get_all(cls) -> list:
        """
        获取所有支持的扩展名
        
        Returns:
            list: 所有扩展名的列表
        """
        all_ext = []
        for attr in dir(cls):
            if not attr.startswith('_'):
                value = getattr(cls, attr)
                if isinstance(value, list):
                    all_ext.extend(value)
        return all_ext
    
    @classmethod
    def get_type(cls, extension: str) -> str:
        """
        根据扩展名获取文件类型
        
        Args:
            extension: 文件扩展名（如 ".xlsx"）
            
        Returns:
            str: 文件类型名称，如果不支持返回 "unknown"
        """
        extension = extension.lower()
        
        if extension in cls.EXCEL:
            return "excel"
        elif extension in cls.WORD:
            return "word"
        elif extension in cls.CSV:
            return "csv"
        elif extension in cls.JSON:
            return "json"
        elif extension in cls.XML:
            return "xml"
        elif extension in cls.TEXT:
            return "text"
        elif extension in cls.HTML:
            return "html"
        else:
            return "unknown"


# ========== 默认值 ==========

class Defaults:
    """
    默认值常量
    
    框架使用的各种默认配置值
    """
    
    # 数据库
    DB_PATH = "docforge.db"
    
    # 插件
    PLUGIN_DIR = "plugins"
    
    # 日志
    LOG_LEVEL = LogLevel.INFO
    LOG_FILE = "docforge.log"
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    
    # 文件
    TEMP_DIR = ".temp"
    BACKUP_DIR = ".backup"
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    
    # 项目
    PROJECT_VERSION = "1.0.0"


# ========== 错误消息 ==========

class ErrorMessages:
    """
    错误消息常量
    
    统一管理错误消息，便于维护和国际化
    """
    
    # 文件相关
    FILE_NOT_FOUND = "文件不存在: {path}"
    FILE_PERMISSION_DENIED = "没有文件访问权限: {path}"
    FILE_FORMAT_INVALID = "文件格式无效: {path}"
    
    # 插件相关
    PLUGIN_LOAD_FAILED = "插件加载失败: {name}"
    PLUGIN_NOT_FOUND = "插件不存在: {name}"
    PLUGIN_DEPENDENCY_MISSING = "插件依赖缺失: {dependency}"
    
    # 工作流相关
    WORKFLOW_INVALID = "工作流定义无效"
    WORKFLOW_STEP_FAILED = "工作流步骤执行失败: {step}"
    
    # 数据库相关
    DB_CONNECTION_FAILED = "数据库连接失败"
    DB_QUERY_FAILED = "数据库查询失败"
    
    # 配置相关
    CONFIG_NOT_FOUND = "配置文件不存在: {path}"
    CONFIG_INVALID = "配置无效: {reason}"


# ========== 成功消息 ==========

class SuccessMessages:
    """
    成功消息常量
    """
    
    FILE_SAVED = "文件保存成功: {path}"
    PLUGIN_LOADED = "插件加载成功: {name}"
    WORKFLOW_COMPLETED = "工作流执行完成"
    PROJECT_SAVED = "项目保存成功"