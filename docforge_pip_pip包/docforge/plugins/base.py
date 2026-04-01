"""
插件基类定义
所有插件必须继承BasePlugin类

使用示例：
    from docforge.plugins.base import BasePlugin
    from docforge.types import ExecutionResult
    
    class MyPlugin(BasePlugin):
        @property
        def name(self) -> str:
            return "my_plugin"
        
        @property
        def version(self) -> str:
            return "1.0.0"
        
        @property
        def plugin_type(self) -> str:
            return "extractor"
        
        def execute(self, **kwargs) -> ExecutionResult:
            return ExecutionResult(success=True, data={"key": ["value"]})
        
        def cleanup(self):
            pass
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

from ..types import ExecutionResult, DataDict


class BasePlugin(ABC):
    """
    插件基类
    所有插件必须继承这个类并实现其抽象方法
    
    这个类定义了插件的标准接口，确保所有插件都有一致的行为。
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        获取插件名称
        
        Returns:
            str: 插件唯一标识名称
            
        Example:
            return "excel_extractor"
        """
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """
        获取插件版本
        
        Returns:
            str: 版本号（建议使用语义化版本，如 "1.0.0"）
            
        Example:
            return "1.0.0"
        """
        pass
    
    @property
    @abstractmethod
    def plugin_type(self) -> str:
        """
        获取插件类型
        
        Returns:
            str: 插件类型，必须是以下之一：
                 - "extractor": 数据提取器
                 - "transformer": 数据转换器
                 - "replacer": 模板替换器
                 - "post_processor": 后处理器
                 
        Example:
            return "extractor"
        """
        pass
    
    @property
    def capabilities(self) -> List[str]:
        """
        获取插件能力列表
        
        这个属性声明插件支持哪些功能，供框架和用户参考。
        
        Returns:
            List[str]: 能力列表
            
        Example:
            return ["extract", "transform"]
        """
        return [self.plugin_type]
    
    @property
    def description(self) -> str:
        """
        获取插件描述
        
        Returns:
            str: 插件功能描述
            
        Example:
            return "从Excel文件中提取数据"
        """
        return ""
    
    @property
    def author(self) -> str:
        """
        获取插件作者
        
        Returns:
            str: 作者名称
        """
        return ""
    
    @property
    def dependencies(self) -> List[str]:
        """
        获取插件依赖
        
        Returns:
            List[str]: 依赖的Python包列表
            
        Example:
            return ["pandas", "openpyxl"]
        """
        return []
    
    @abstractmethod
    def execute(self, **kwargs) -> ExecutionResult:
        """
        执行插件功能
        
        这是插件的核心方法，所有的处理逻辑都在这里实现。
        
        Args:
            **kwargs: 插件参数，常用的参数包括：
                - input_files: 输入文件列表
                - template_files: 模板文件列表
                - output_dir: 输出目录
                - data: 输入数据（来自上一步插件）
                
        Returns:
            ExecutionResult: 执行结果
            
        Example:
            def execute(self, **kwargs) -> ExecutionResult:
                input_files = kwargs.get("input_files", [])
                
                if not input_files:
                    return ExecutionResult(
                        success=False,
                        errors=["没有输入文件"]
                    )
                
                # 处理逻辑...
                data = {"字段1": ["值1", "值2"]}
                
                return ExecutionResult(
                    success=True,
                    data=data
                )
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """
        清理资源
        
        在插件卸载或重新加载前调用，用于释放资源。
        如果没有资源需要清理，可以写 pass。
        
        Example:
            def cleanup(self):
                # 关闭打开的文件
                if self._file:
                    self._file.close()
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取插件元数据
        
        Returns:
            Dict[str, Any]: 元数据字典
        """
        return {
            "name": self.name,
            "version": self.version,
            "plugin_type": self.plugin_type,
            "capabilities": self.capabilities,
            "description": self.description,
            "author": self.author,
            "dependencies": self.dependencies
        }
    
    def validate_input(self, **kwargs) -> List[str]:
        """
        验证输入参数
        
        在执行前验证输入参数是否有效。
        
        Args:
            **kwargs: 输入参数
            
        Returns:
            List[str]: 错误列表，空列表表示验证通过
            
        Example:
            def validate_input(self, **kwargs) -> List[str]:
                errors = []
                
                if not kwargs.get("input_files"):
                    errors.append("缺少输入文件")
                
                return errors
        """
        return []
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<{self.__class__.__name__}: {self.name} v{self.version}>"