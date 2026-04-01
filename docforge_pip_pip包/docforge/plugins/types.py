"""
插件相关类型定义
定义插件系统中使用的数据结构

使用示例：
    from docforge.plugins.types import PluginMetadata, PluginContext
    
    # 创建插件元数据
    metadata = PluginMetadata(
        name="my_plugin",
        version="1.0.0",
        plugin_type="extractor"
    )
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PluginMetadata:
    """
    插件元数据
    从插件文件中提取的静态信息
    
    Attributes:
        name: 插件名称
        version: 版本号
        plugin_type: 插件类型
        author: 作者
        description: 描述
        license: 许可证
        homepage: 主页
        dependencies: 依赖列表
        entry_point: 入口文件
        min_framework_version: 最低框架版本
    """
    name: str
    version: str = "0.0.0"
    plugin_type: str = ""
    author: str = ""
    description: str = ""
    license: str = ""
    homepage: str = ""
    dependencies: List[str] = field(default_factory=list)
    entry_point: str = "plugin.py"
    min_framework_version: str = "0.1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "version": self.version,
            "plugin_type": self.plugin_type,
            "author": self.author,
            "description": self.description,
            "license": self.license,
            "homepage": self.homepage,
            "dependencies": self.dependencies,
            "entry_point": self.entry_point,
            "min_framework_version": self.min_framework_version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginMetadata':
        """从字典创建"""
        return cls(
            name=data.get("name", ""),
            version=data.get("version", "0.0.0"),
            plugin_type=data.get("plugin_type", ""),
            author=data.get("author", ""),
            description=data.get("description", ""),
            license=data.get("license", ""),
            homepage=data.get("homepage", ""),
            dependencies=data.get("dependencies", []),
            entry_point=data.get("entry_point", "plugin.py"),
            min_framework_version=data.get("min_framework_version", "0.1.0")
        )


@dataclass
class PluginContext:
    """
    插件上下文
    传递给插件的运行时环境信息
    
    Attributes:
        input_files: 输入文件列表
        template_files: 模板文件列表
        output_dir: 输出目录
        logger: 日志器
        database: 数据库
        config: 全局配置
        plugin_config: 插件专用配置
        execution_id: 执行ID
        workflow_name: 工作流名称
        step_index: 步骤索引
    """
    input_files: List[str] = field(default_factory=list)
    template_files: List[str] = field(default_factory=list)
    output_dir: str = ""
    logger: Any = None
    database: Any = None
    config: Dict[str, Any] = field(default_factory=dict)
    plugin_config: Dict[str, Any] = field(default_factory=dict)
    execution_id: str = ""
    workflow_name: str = ""
    step_index: int = 0
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取全局配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        return self.config.get(key, default)
    
    def get_plugin_config(self, key: str, default: Any = None) -> Any:
        """
        获取插件专用配置
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        return self.plugin_config.get(key, default)
    
    def log_debug(self, message: str) -> None:
        """记录调试日志"""
        if self.logger:
            self.logger.debug(message)
    
    def log_info(self, message: str) -> None:
        """记录信息日志"""
        if self.logger:
            self.logger.info(message)
    
    def log_warning(self, message: str) -> None:
        """记录警告日志"""
        if self.logger:
            self.logger.warning(message)
    
    def log_error(self, message: str) -> None:
        """记录错误日志"""
        if self.logger:
            self.logger.error(message)


@dataclass
class PluginDependency:
    """
    插件依赖信息
    
    Attributes:
        name: 依赖名称
        version_spec: 版本要求（如">=1.0.0"）
        optional: 是否可选
    """
    name: str
    version_spec: str = ""
    optional: bool = False
    
    def is_satisfied(self, installed_version: str) -> bool:
        """
        检查依赖是否满足
        
        Args:
            installed_version: 已安装版本
            
        Returns:
            bool: 是否满足
        """
        if not self.version_spec:
            return True
        
        # 简化实现：只检查版本是否存在
        # 完整实现需要解析版本规范（>=, <=, ==, !=等）
        return bool(installed_version)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "version_spec": self.version_spec,
            "optional": self.optional
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginDependency':
        """从字典创建"""
        return cls(
            name=data.get("name", ""),
            version_spec=data.get("version_spec", ""),
            optional=data.get("optional", False)
        )


@dataclass
class PluginLoadResult:
    """
    插件加载结果
    
    Attributes:
        success: 是否成功
        plugin_name: 插件名称
        error_message: 错误信息
        warnings: 警告列表
        load_time: 加载时间（秒）
    """
    success: bool
    plugin_name: str = ""
    error_message: str = ""
    warnings: List[str] = field(default_factory=list)
    load_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "plugin_name": self.plugin_name,
            "error_message": self.error_message,
            "warnings": self.warnings,
            "load_time": self.load_time
        }