"""
类型定义模块
定义框架中使用的所有数据结构和类型别名

这个文件定义了框架中"数据长什么样"。
所有模块在传递数据时，都使用这里定义的类型。

使用示例：
    from docforge.types import FileInfo, ExecutionResult
    
    # 创建文件信息
    file_info = FileInfo(
        path=Path("data.xlsx"),
        name="data.xlsx",
        extension=".xlsx",
        size=1024,
        modified_time=datetime.now()
    )
    
    # 创建执行结果
    result = ExecutionResult(
        success=True,
        data={"字段1": ["值1", "值2"]},
        output_files=[Path("output.docx")]
    )
"""

from typing import (
    Dict, 
    List, 
    Optional, 
    Any, 
    Union, 
    Callable
)
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime


# ========== 基础类型别名 ==========

PathLike = Union[str, Path]
"""
路径类型：可以是字符串或Path对象

Example:
    def load_file(path: PathLike) -> None:
        path = Path(path)  # 统一转为Path对象
        ...
"""

JsonDict = Dict[str, Any]
"""
JSON字典类型：键是字符串，值是任意类型

Example:
    config: JsonDict = {
        "name": "my_project",
        "version": "1.0.0",
        "settings": {"debug": True}
    }
"""

DataDict = Dict[str, List[str]]
"""
数据字典类型：用于存储提取的数据

结构：{字段名: [值列表]}

Example:
    data: DataDict = {
        "公司名称": ["ABC公司", "XYZ公司"],
        "职位": ["工程师", "设计师"]
    }
"""


# ========== 文件相关类型 ==========

@dataclass
class FileInfo:
    """
    文件信息
    
    包含文件的基本元数据
    
    Attributes:
        path: 文件完整路径
        name: 文件名（含扩展名）
        extension: 扩展名（如 ".xlsx"）
        size: 文件大小（字节）
        modified_time: 最后修改时间
        status: 处理状态
        hash: 文件哈希值（可选）
    """
    path: Path
    name: str
    extension: str
    size: int
    modified_time: datetime
    status: str = "pending"
    hash: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "path": str(self.path),
            "name": self.name,
            "extension": self.extension,
            "size": self.size,
            "modified_time": self.modified_time.isoformat(),
            "status": self.status,
            "hash": self.hash
        }
    
    @classmethod
    def from_path(cls, file_path: PathLike) -> 'FileInfo':
        """
        从文件路径创建FileInfo
        
        Args:
            file_path: 文件路径
            
        Returns:
            FileInfo: 文件信息对象
            
        Raises:
            FileNotFoundError: 文件不存在
        """
        path = Path(file_path)
        if not path.exists():
            from .exceptions import FileNotFoundError
            raise FileNotFoundError(f"文件不存在: {path}")
        
        stat = path.stat()
        return cls(
            path=path,
            name=path.name,
            extension=path.suffix.lower(),
            size=stat.st_size,
            modified_time=datetime.fromtimestamp(stat.st_mtime)
        )


@dataclass
class FileBatch:
    """
    文件批次
    
    用于管理一组文件
    
    Attributes:
        files: 文件信息列表
        batch_id: 批次ID
        created_at: 创建时间
    """
    files: List[FileInfo] = field(default_factory=list)
    batch_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_file(self, file_info: FileInfo) -> None:
        """添加文件"""
        self.files.append(file_info)
    
    def remove_file(self, file_path: str) -> bool:
        """移除文件"""
        for i, f in enumerate(self.files):
            if str(f.path) == file_path:
                self.files.pop(i)
                return True
        return False
    
    def get_count(self) -> int:
        """获取文件数量"""
        return len(self.files)


# ========== 工作流相关类型 ==========

@dataclass
class WorkflowStep:
    """
    工作流步骤
    
    定义工作流中的一个执行步骤
    
    Attributes:
        step_id: 步骤唯一ID
        plugin_name: 要执行的插件名称
        plugin_type: 插件类型
        config: 步骤配置参数
        order: 执行顺序
        enabled: 是否启用
    """
    step_id: str
    plugin_name: str
    plugin_type: str = ""
    config: JsonDict = field(default_factory=dict)
    order: int = 0
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "step_id": self.step_id,
            "plugin_name": self.plugin_name,
            "plugin_type": self.plugin_type,
            "config": self.config,
            "order": self.order,
            "enabled": self.enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowStep':
        """从字典创建"""
        return cls(
            step_id=data.get("step_id", ""),
            plugin_name=data.get("plugin_name", ""),
            plugin_type=data.get("plugin_type", ""),
            config=data.get("config", {}),
            order=data.get("order", 0),
            enabled=data.get("enabled", True)
        )


@dataclass
class WorkflowDefinition:
    """
    工作流定义
    
    定义一个完整的工作流
    
    Attributes:
        name: 工作流名称
        description: 描述
        version: 版本号
        steps: 步骤列表
        created_at: 创建时间
        updated_at: 更新时间
        author: 作者
    """
    name: str
    description: str = ""
    version: str = "1.0.0"
    steps: List[WorkflowStep] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    author: str = ""
    
    def __post_init__(self):
        """初始化后处理"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def add_step(self, step: WorkflowStep) -> None:
        """添加步骤"""
        self.steps.append(step)
        self._update_order()
    
    def remove_step(self, step_id: str) -> bool:
        """移除步骤"""
        for i, step in enumerate(self.steps):
            if step.step_id == step_id:
                self.steps.pop(i)
                self._update_order()
                return True
        return False
    
    def _update_order(self) -> None:
        """更新步骤顺序"""
        for i, step in enumerate(self.steps):
            step.order = i
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "steps": [s.to_dict() for s in self.steps],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "author": self.author
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowDefinition':
        """从字典创建"""
        steps = [WorkflowStep.from_dict(s) for s in data.get("steps", [])]
        
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])
        
        updated_at = None
        if data.get("updated_at"):
            updated_at = datetime.fromisoformat(data["updated_at"])
        
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            steps=steps,
            created_at=created_at,
            updated_at=updated_at,
            author=data.get("author", "")
        )


# ========== 执行结果类型 ==========

@dataclass
class ExecutionResult:
    """
    执行结果
    
    包含执行操作的结果信息
    
    Attributes:
        success: 是否成功
        data: 输出数据
        output_files: 输出文件列表
        errors: 错误列表
        warnings: 警告列表
        execution_time: 执行时间（秒）
        message: 结果消息
    """
    success: bool
    data: Optional[DataDict] = None
    output_files: List[Path] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    message: str = ""
    
    def add_error(self, error: str) -> None:
        """添加错误"""
        self.errors.append(error)
        self.success = False
    
    def add_warning(self, warning: str) -> None:
        """添加警告"""
        self.warnings.append(warning)
    
    def has_errors(self) -> bool:
        """是否有错误"""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """是否有警告"""
        return len(self.warnings) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "data": self.data,
            "output_files": [str(f) for f in self.output_files],
            "errors": self.errors,
            "warnings": self.warnings,
            "execution_time": self.execution_time,
            "message": self.message
        }


# ========== 插件相关类型 ==========

@dataclass
class PluginInfo:
    """
    插件信息
    
    包含插件的元数据
    
    Attributes:
        name: 插件名称
        version: 版本号
        plugin_type: 插件类型
        author: 作者
        description: 描述
        dependencies: 依赖列表
        entry_point: 入口点
        enabled: 是否启用
        file_path: 插件文件路径
    """
    name: str
    version: str = "0.0.0"
    plugin_type: str = ""
    author: str = ""
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    entry_point: str = ""
    enabled: bool = True
    file_path: Optional[Path] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "version": self.version,
            "plugin_type": self.plugin_type,
            "author": self.author,
            "description": self.description,
            "dependencies": self.dependencies,
            "entry_point": self.entry_point,
            "enabled": self.enabled,
            "file_path": str(self.file_path) if self.file_path else None
        }


# ========== 配置相关类型 ==========

@dataclass
class ConfigSchema:
    """
    配置模式
    
    定义配置项的结构和验证规则
    
    Attributes:
        key: 配置键
        type: 值类型
        default: 默认值
        required: 是否必填
        description: 描述
    """
    key: str
    type: type = str
    default: Any = None
    required: bool = False
    description: str = ""


# ========== 回调函数类型 ==========

ProgressCallback = Callable[[float, str], None]
"""
进度回调函数

Args:
    float: 进度值（0.0 - 1.0）
    str: 进度消息

Example:
    def on_progress(progress: float, message: str):
        print(f"[{progress*100:.1f}%] {message}")
"""

LogCallback = Callable[[str, str], None]
"""
日志回调函数

Args:
    str: 日志级别（DEBUG/INFO/WARNING/ERROR）
    str: 日志消息

Example:
    def on_log(level: str, message: str):
        print(f"[{level}] {message}")
"""

EventCallback = Callable[[str, Any], None]
"""
事件回调函数

Args:
    str: 事件名称
    Any: 事件数据

Example:
    def on_event(event_name: str, data: Any):
        print(f"Event: {event_name}, Data: {data}")
"""