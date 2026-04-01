"""
异常定义模块
定义框架中使用的所有异常类型

异常层次结构：
    DocForgeException (基础异常)
    ├── PluginException (插件相关)
    │   ├── PluginLoadError (加载失败)
    │   ├── PluginDependencyError (依赖缺失)
    │   ├── PluginExecuteError (执行失败)
    │   └── PluginSecurityError (安全违规)
    ├── WorkflowException (工作流相关)
    │   ├── WorkflowDefinitionError (定义错误)
    │   ├── WorkflowExecuteError (执行失败)
    │   └── WorkflowCancelledError (被取消)
    ├── FileException (文件相关)
    │   ├── FileNotFoundError (文件不存在)
    │   ├── FilePermissionError (权限错误)
    │   └── FileFormatError (格式错误)
    ├── DatabaseException (数据库相关)
    │   ├── DatabaseConnectionError (连接失败)
    │   └── DatabaseQueryError (查询失败)
    └── ConfigException (配置相关)
        ├── ConfigParseError (解析错误)
        └── ConfigValidationError (验证失败)

使用示例：
    from docforge.exceptions import FileNotFoundError
    
    try:
        with open("不存在的文件.txt") as f:
            pass
    except FileNotFoundError as e:
        print(f"文件不存在: {e}")
"""


class DocForgeException(Exception):
    """
    DocForge基础异常类
    所有框架异常都继承自这个类
    
    Attributes:
        message: 错误消息
        details: 详细信息（可选）
    """
    
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - {self.details}"
        return self.message


# ========== 插件相关异常 ==========

class PluginException(DocForgeException):
    """
    插件基础异常
    所有插件相关的异常都继承自这个类
    """
    pass


class PluginLoadError(PluginException):
    """
    插件加载失败
    
    常见原因：
    - 插件文件语法错误
    - 插件类没有继承正确的基类
    - 插件文件路径不存在
    
    Example:
        raise PluginLoadError("无法加载插件", "文件语法错误在第10行")
    """
    pass


class PluginDependencyError(PluginException):
    """
    插件依赖缺失
    
    常见原因：
    - 缺少pip包（如pandas、openpyxl等）
    - 依赖的其他插件不存在
    
    Example:
        raise PluginDependencyError("缺少依赖", "需要安装 pandas: pip install pandas")
    """
    pass


class PluginExecuteError(PluginException):
    """
    插件执行失败
    
    常见原因：
    - 插件内部逻辑错误
    - 输入数据格式不正确
    - 文件读写失败
    
    Example:
        raise PluginExecuteError("插件执行失败", "Excel文件格式不支持")
    """
    pass


class PluginSecurityError(PluginException):
    """
    插件安全违规
    
    常见原因：
    - 尝试访问禁止的路径
    - 尝试导入禁止的模块
    - 超出资源限制
    
    Example:
        raise PluginSecurityError("安全违规", "禁止访问系统目录")
    """
    pass


# ========== 工作流相关异常 ==========

class WorkflowException(DocForgeException):
    """
    工作流基础异常
    所有工作流相关的异常都继承自这个类
    """
    pass


class WorkflowDefinitionError(WorkflowException):
    """
    工作流定义错误
    
    常见原因：
    - JSON格式错误
    - 缺少必需字段
    - 引用的插件不存在
    
    Example:
        raise WorkflowDefinitionError("工作流定义错误", "缺少 'steps' 字段")
    """
    pass


class WorkflowExecuteError(WorkflowException):
    """
    工作流执行失败
    
    常见原因：
    - 某个步骤执行失败
    - 数据传递错误
    - 超时
    
    Example:
        raise WorkflowExecuteError("工作流执行失败", "步骤2执行超时")
    """
    pass


class WorkflowCancelledError(WorkflowException):
    """
    工作流被取消
    
    用户主动取消工作流执行时抛出
    
    Example:
        raise WorkflowCancelledError("工作流已取消")
    """
    pass


# ========== 文件相关异常 ==========

class FileException(DocForgeException):
    """
    文件操作基础异常
    所有文件相关的异常都继承自这个类
    """
    pass


class FileNotFoundError(FileException):
    """
    文件不存在
    
    尝试访问不存在的文件时抛出
    
    Example:
        raise FileNotFoundError("文件不存在", "/path/to/file.xlsx")
    """
    pass


class FilePermissionError(FileException):
    """
    文件权限错误
    
    常见原因：
    - 没有读取权限
    - 没有写入权限
    - 文件被其他程序占用
    
    Example:
        raise FilePermissionError("没有写入权限", "/path/to/readonly.txt")
    """
    pass


class FileFormatError(FileException):
    """
    文件格式错误
    
    常见原因：
    - Excel文件损坏
    - JSON格式错误
    - 文件扩展名与内容不匹配
    
    Example:
        raise FileFormatError("文件格式错误", "不是有效的Excel文件")
    """
    pass


# ========== 数据库相关异常 ==========

class DatabaseException(DocForgeException):
    """
    数据库基础异常
    所有数据库相关的异常都继承自这个类
    """
    pass


class DatabaseConnectionError(DatabaseException):
    """
    数据库连接失败
    
    常见原因：
    - 数据库文件不存在
    - 数据库文件被锁定
    - 磁盘空间不足
    
    Example:
        raise DatabaseConnectionError("数据库连接失败", "无法打开数据库文件")
    """
    pass


class DatabaseQueryError(DatabaseException):
    """
    数据库查询失败
    
    常见原因：
    - SQL语法错误
    - 表不存在
    - 数据类型不匹配
    
    Example:
        raise DatabaseQueryError("查询失败", "表 'projects' 不存在")
    """
    pass


# ========== 配置相关异常 ==========

class ConfigException(DocForgeException):
    """
    配置基础异常
    所有配置相关的异常都继承自这个类
    """
    pass


class ConfigParseError(ConfigException):
    """
    配置解析错误
    
    常见原因：
    - JSON语法错误
    - 文件编码问题
    - 文件损坏
    
    Example:
        raise ConfigParseError("配置解析错误", "JSON语法错误在第5行")
    """
    pass


class ConfigValidationError(ConfigException):
    """
    配置验证失败
    
    常见原因：
    - 缺少必需的配置项
    - 配置值类型错误
    - 配置值超出有效范围
    
    Example:
        raise ConfigValidationError("配置验证失败", "缺少 'database.path' 配置")
    """
    pass