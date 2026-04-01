"""
插件加载器
负责从文件系统动态加载插件

使用示例：
    from docforge.plugins.loader import PluginLoader
    from docforge.services.logger import Logger
    
    logger = Logger()
    loader = PluginLoader(logger)
    
    # 从文件加载插件
    plugin = loader.load_from_file("plugins/my_plugin.py")
    
    # 从目录加载所有插件
    plugins = loader.load_from_directory("plugins/")
"""

import os
import sys
import importlib
import importlib.util
from typing import Dict, List, Optional, Type
from pathlib import Path
import time

from .base import BasePlugin
from .types import PluginMetadata, PluginLoadResult
from ..types import PathLike
from ..exceptions import PluginLoadError


class PluginLoader:
    """
    插件加载器
    
    提供多种插件加载方式
    """
    
    def __init__(self, logger=None):
        """
        初始化加载器
        
        Args:
            logger: 日志器实例（可选）
        """
        self.logger = logger
    
    def _log(self, level: str, message: str, **kwargs) -> None:
        """记录日志"""
        if self.logger:
            getattr(self.logger, level)(message, **kwargs)
    
    # ========== 文件加载 ==========
    
    def load_from_file(self, file_path: PathLike) -> Optional[BasePlugin]:
        """
        从单个Python文件加载插件
        
        Args:
            file_path: Python文件路径
            
        Returns:
            Optional[BasePlugin]: 插件实例，失败返回None
            
        Raises:
            PluginLoadError: 加载失败
        """
        path = Path(file_path)
        
        if not path.exists():
            raise PluginLoadError(f"插件文件不存在: {path}")
        
        if not path.is_file():
            raise PluginLoadError(f"不是文件: {path}")
        
        start_time = time.time()
        
        try:
            # 动态加载模块
            module_name = f"docforge_plugins.{path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, path)
            
            if spec is None or spec.loader is None:
                raise PluginLoadError(f"无法创建模块规范: {path}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # 查找插件类（继承自BasePlugin的类）
            plugin_class = self._find_plugin_class(module)
            
            if plugin_class is None:
                raise PluginLoadError(f"插件文件中没有找到插件类: {path}")
            
            # 验证插件类
            errors = self.validate_plugin_class(plugin_class)
            if errors:
                raise PluginLoadError(f"插件类验证失败: {errors}")
            
            # 实例化插件
            plugin_instance = plugin_class()
            
            load_time = time.time() - start_time
            self._log("info", f"插件加载成功: {plugin_instance.name} v{plugin_instance.version} ({load_time:.3f}s)")
            
            return plugin_instance
            
        except PluginLoadError:
            raise
        except Exception as e:
            raise PluginLoadError(f"加载插件失败: {path}", str(e))
    
    def _find_plugin_class(self, module) -> Optional[Type[BasePlugin]]:
        """
        在模块中查找插件类
        
        Args:
            module: Python模块
            
        Returns:
            Optional[Type[BasePlugin]]: 插件类
        """
        plugin_class = None
        
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            # 检查是否是类，且继承自BasePlugin
            if (isinstance(attr, type) and 
                issubclass(attr, BasePlugin) and 
                attr is not BasePlugin):
                plugin_class = attr
                break
        
        return plugin_class
    
    def load_from_directory(self, directory: PathLike) -> List[BasePlugin]:
        """
        从目录加载所有插件
        
        Args:
            directory: 目录路径
            
        Returns:
            List[BasePlugin]: 插件实例列表
        """
        path = Path(directory)
        
        if not path.exists():
            self._log("warning", f"插件目录不存在: {path}")
            return []
        
        if not path.is_dir():
            self._log("warning", f"不是目录: {path}")
            return []
        
        plugins = []
        
        for item in path.iterdir():
            # 只处理.py文件，跳过__init__.py等
            if item.is_file() and item.suffix == ".py" and not item.name.startswith("_"):
                try:
                    plugin = self.load_from_file(item)
                    if plugin:
                        plugins.append(plugin)
                except PluginLoadError as e:
                    self._log("error", str(e))
        
        self._log("info", f"从目录加载了 {len(plugins)} 个插件: {path}")
        return plugins
    
    # ========== 包加载 ==========
    
    def load_from_package(self, package_name: str) -> Optional[BasePlugin]:
        """
        从已安装的Python包加载插件
        
        Args:
            package_name: 包名
            
        Returns:
            Optional[BasePlugin]: 插件实例，失败返回None
        """
        try:
            # 导入包
            package = importlib.import_module(package_name)
            
            # 查找插件类
            plugin_class = self._find_plugin_class(package)
            
            if plugin_class is None:
                self._log("warning", f"包中没有找到插件类: {package_name}")
                return None
            
            # 实例化插件
            plugin_instance = plugin_class()
            
            self._log("info", f"从包加载插件: {plugin_instance.name}")
            return plugin_instance
            
        except ImportError as e:
            self._log("error", f"无法导入包: {package_name} - {e}")
            return None
        except Exception as e:
            self._log("error", f"加载插件失败: {package_name} - {e}")
            return None
    
    def load_from_module(self, module_path: str) -> Optional[BasePlugin]:
        """
        从模块路径加载插件
        
        Args:
            module_path: 模块路径（如"my_plugins.extractor"）
            
        Returns:
            Optional[BasePlugin]: 插件实例，失败返回None
        """
        try:
            module = importlib.import_module(module_path)
            plugin_class = self._find_plugin_class(module)
            
            if plugin_class is None:
                self._log("warning", f"模块中没有找到插件类: {module_path}")
                return None
            
            plugin_instance = plugin_class()
            self._log("info", f"从模块加载插件: {plugin_instance.name}")
            return plugin_instance
            
        except ImportError as e:
            self._log("error", f"无法导入模块: {module_path} - {e}")
            return None
    
    # ========== 验证 ==========
    
    def validate_plugin_class(self, plugin_class: Type) -> List[str]:
        """
        验证插件类是否符合规范
        
        Args:
            plugin_class: 插件类
            
        Returns:
            List[str]: 错误列表，空列表表示验证通过
        """
        errors = []
        
        # 检查是否继承自BasePlugin
        if not issubclass(plugin_class, BasePlugin):
            errors.append(f"插件类必须继承自BasePlugin: {plugin_class.__name__}")
        
        # 检查必要的属性
        required_properties = ['name', 'version', 'plugin_type']
        for prop in required_properties:
            if not hasattr(plugin_class, prop):
                errors.append(f"缺少必要的属性: {prop}")
        
        # 检查必要的方法
        required_methods = ['execute', 'cleanup']
        for method in required_methods:
            if not hasattr(plugin_class, method):
                errors.append(f"缺少必要的方法: {method}")
            elif not callable(getattr(plugin_class, method)):
                errors.append(f"不是可调用的方法: {method}")
        
        return errors
    
    def extract_metadata(self, file_path: PathLike) -> Optional[PluginMetadata]:
        """
        从文件提取插件元数据（不加载插件）
        
        简化实现：尝试加载插件并获取元数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[PluginMetadata]: 插件元数据
        """
        try:
            plugin = self.load_from_file(file_path)
            if plugin:
                return PluginMetadata(
                    name=plugin.name,
                    version=plugin.version,
                    plugin_type=plugin.plugin_type,
                    author=plugin.author,
                    description=plugin.description,
                    dependencies=plugin.dependencies
                )
        except:
            pass
        
        return None
    
    # ========== 依赖检查 ==========
    
    def check_imports(self, file_path: PathLike) -> List[str]:
        """
        检查文件导入的模块
        
        简化实现：读取文件内容，查找import语句
        
        Args:
            file_path: 文件路径
            
        Returns:
            List[str]: 导入的模块列表
        """
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的正则匹配import语句
            import re
            pattern = r'^(?:from\s+(\S+)\s+import|import\s+(\S+))'
            
            for line in content.split('\n'):
                line = line.strip()
                match = re.match(pattern, line)
                if match:
                    module = match.group(1) or match.group(2)
                    imports.append(module)
            
        except Exception as e:
            self._log("error", f"检查导入失败: {e}")
        
        return imports
    
    def check_dependencies(self, plugin_class: Type) -> Dict[str, bool]:
        """
        检查插件依赖是否满足
        
        Args:
            plugin_class: 插件类
            
        Returns:
            Dict[str, bool]: 依赖名 -> 是否满足
        """
        results = {}
        
        # 获取依赖列表
        if hasattr(plugin_class, 'dependencies'):
            dependencies = plugin_class.dependencies
        else:
            dependencies = []
        
        for dep in dependencies:
            try:
                __import__(dep)
                results[dep] = True
            except ImportError:
                results[dep] = False
        
        return results