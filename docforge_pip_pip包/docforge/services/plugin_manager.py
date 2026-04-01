"""
插件管理服务
负责插件的发现、加载、注册和管理

使用示例：
    from docforge.services.plugin_manager import PluginManager
    from docforge.services.logger import Logger
    
    logger = Logger()
    plugin_manager = PluginManager(logger)
    
    # 加载所有插件
    plugin_manager.load_all_plugins("./plugins")
    
    # 获取插件
    plugin = plugin_manager.get_plugin("excel_extractor")
"""

import os
import sys
import importlib
import importlib.util
from typing import Dict, List, Optional, Type
from pathlib import Path

from ..types import PluginInfo, PathLike
from ..plugins.base import BasePlugin
from ..exceptions import PluginLoadError, PluginDependencyError


class PluginManager:
    """
    插件管理器
    
    管理所有插件的生命周期
    
    Attributes:
        logger: 日志器实例
    """
    
    def __init__(self, logger=None):
        """
        初始化插件管理器
        
        Args:
            logger: 日志器实例（可选）
        """
        self.logger = logger
        self._plugins: Dict[str, BasePlugin] = {}
        self._plugin_info: Dict[str, PluginInfo] = {}
        self._plugin_paths: Dict[str, Path] = {}
    
    def _log(self, level: str, message: str, **kwargs) -> None:
        """记录日志"""
        if self.logger:
            getattr(self.logger, level)(message, **kwargs)
    
    # ========== 插件发现与加载 ==========
    
    def discover_plugins(self, plugin_dir: PathLike) -> List[PluginInfo]:
        """
        发现指定目录下的所有插件
        
        Args:
            plugin_dir: 插件目录路径
            
        Returns:
            List[PluginInfo]: 发现的插件信息列表
        """
        from ..types import PathLike
        
        path = Path(plugin_dir)
        
        if not path.exists():
            self._log("warning", f"插件目录不存在: {path}")
            return []
        
        discovered = []
        
        for item in path.iterdir():
            if item.is_file() and item.suffix == ".py" and not item.name.startswith("_"):
                try:
                    info = self._extract_plugin_info(item)
                    if info:
                        discovered.append(info)
                        self._log("debug", f"发现插件: {info.name}")
                except Exception as e:
                    self._log("warning", f"无法读取插件信息: {item.name} - {e}")
        
        return discovered
    
    def _extract_plugin_info(self, file_path: Path) -> Optional[PluginInfo]:
        """
        从文件提取插件信息（不加载插件）
        
        Args:
            file_path: 插件文件路径
            
        Returns:
            Optional[PluginInfo]: 插件信息
        """
        # 简化实现：读取文件头部注释
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(2000)  # 只读前2000字符
            
            # 提取插件名称（从文件名）
            name = file_path.stem
            
            # 尝试从注释提取描述
            description = ""
            for line in content.split('\n')[:20]:  # 只看前20行
                line = line.strip()
                if line.startswith('"""') or line.startswith("'''"):
                    description = line.strip('"""').strip("'''").strip()
                    break
            
            return PluginInfo(
                name=name,
                description=description,
                file_path=file_path
            )
            
        except Exception:
            return None
    
    def load_plugin(self, plugin_path: PathLike) -> bool:
        """
        加载单个插件
        
        Args:
            plugin_path: 插件文件路径
            
        Returns:
            bool: 是否加载成功
            
        Raises:
            PluginLoadError: 加载失败
        """
        path = Path(plugin_path)
        
        if not path.exists():
            raise PluginLoadError(f"插件文件不存在: {path}")
        
        try:
            # 动态加载模块
            module_name = f"docforge.plugins.{path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, path)
            
            if spec is None or spec.loader is None:
                raise PluginLoadError(f"无法加载插件: {path}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # 查找插件类（继承自BasePlugin的类）
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BasePlugin) and 
                    attr is not BasePlugin):
                    plugin_class = attr
                    break
            
            if plugin_class is None:
                raise PluginLoadError(f"插件文件中没有找到插件类: {path}")
            
            # 实例化插件
            plugin_instance = plugin_class()
            
            # 获取插件信息
            info = PluginInfo(
                name=plugin_instance.name,
                version=plugin_instance.version,
                plugin_type=plugin_instance.plugin_type,
                description=plugin_instance.get_metadata().get("description", ""),
                file_path=path
            )
            
            # 注册插件
            self._plugins[info.name] = plugin_instance
            self._plugin_info[info.name] = info
            self._plugin_paths[info.name] = path
            
            self._log("info", f"插件加载成功: {info.name} v{info.version}")
            return True
            
        except Exception as e:
            raise PluginLoadError(f"加载插件失败: {path}", str(e))
    
    def load_all_plugins(self, plugin_dir: PathLike) -> Dict[str, bool]:
        """
        加载目录下所有插件
        
        Args:
            plugin_dir: 插件目录路径
            
        Returns:
            Dict[str, bool]: 插件名 -> 是否加载成功
        """
        path = Path(plugin_dir)
        
        if not path.exists():
            self._log("warning", f"插件目录不存在: {path}")
            return {}
        
        results = {}
        
        for item in path.iterdir():
            if item.is_file() and item.suffix == ".py" and not item.name.startswith("_"):
                try:
                    success = self.load_plugin(item)
                    results[item.stem] = success
                except PluginLoadError as e:
                    self._log("error", str(e))
                    results[item.stem] = False
        
        self._log("info", f"插件加载完成: {sum(results.values())}/{len(results)} 成功")
        return results
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        卸载插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            bool: 是否卸载成功
        """
        if plugin_name not in self._plugins:
            self._log("warning", f"插件不存在: {plugin_name}")
            return False
        
        try:
            # 清理资源
            plugin = self._plugins[plugin_name]
            plugin.cleanup()
            
            # 移除注册
            del self._plugins[plugin_name]
            del self._plugin_info[plugin_name]
            del self._plugin_paths[plugin_name]
            
            self._log("info", f"插件已卸载: {plugin_name}")
            return True
            
        except Exception as e:
            self._log("error", f"卸载插件失败: {e}")
            return False
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """
        重新加载插件（热重载）
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            bool: 是否重载成功
        """
        if plugin_name not in self._plugin_paths:
            self._log("error", f"插件路径未知: {plugin_name}")
            return False
        
        # 先卸载
        self.unload_plugin(plugin_name)
        
        # 再加载
        try:
            return self.load_plugin(self._plugin_paths[plugin_name])
        except PluginLoadError as e:
            self._log("error", f"重载插件失败: {e}")
            return False
    
    # ========== 插件查询 ==========
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        获取插件实例
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            Optional[BasePlugin]: 插件实例，不存在返回None
        """
        return self._plugins.get(plugin_name)
    
    def get_plugins_by_type(self, plugin_type: str) -> List[BasePlugin]:
        """
        按类型获取插件列表
        
        Args:
            plugin_type: 插件类型（extractor/transformer/replacer/post_processor）
            
        Returns:
            List[BasePlugin]: 插件列表
        """
        return [
            plugin for plugin in self._plugins.values()
            if plugin.plugin_type == plugin_type
        ]
    
    def get_all_plugins(self) -> Dict[str, BasePlugin]:
        """
        获取所有已加载的插件
        
        Returns:
            Dict[str, BasePlugin]: 插件名 -> 插件实例
        """
        return self._plugins.copy()
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """
        获取插件详细信息
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            Optional[PluginInfo]: 插件信息，不存在返回None
        """
        return self._plugin_info.get(plugin_name)
    
    def get_plugin_list(self) -> List[PluginInfo]:
        """
        获取所有插件信息列表
        
        Returns:
            List[PluginInfo]: 插件信息列表
        """
        return list(self._plugin_info.values())
    
    # ========== 插件控制 ==========
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """
        启用插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            bool: 是否成功启用
        """
        if plugin_name not in self._plugin_info:
            self._log("error", f"插件不存在: {plugin_name}")
            return False
        
        self._plugin_info[plugin_name].enabled = True
        self._log("info", f"插件已启用: {plugin_name}")
        return True
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """
        禁用插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            bool: 是否成功禁用
        """
        if plugin_name not in self._plugin_info:
            self._log("error", f"插件不存在: {plugin_name}")
            return False
        
        self._plugin_info[plugin_name].enabled = False
        self._log("info", f"插件已禁用: {plugin_name}")
        return True
    
    def execute_plugin(
        self,
        plugin_name: str,
        **kwargs
    ) -> 'ExecutionResult':
        """
        执行指定插件
        
        Args:
            plugin_name: 插件名称
            **kwargs: 传递给插件的参数
            
        Returns:
            ExecutionResult: 执行结果
        """
        from ..types import ExecutionResult
        
        plugin = self.get_plugin(plugin_name)
        
        if plugin is None:
            return ExecutionResult(
                success=False,
                errors=[f"插件不存在: {plugin_name}"]
            )
        
        info = self._plugin_info.get(plugin_name)
        if info and not info.enabled:
            return ExecutionResult(
                success=False,
                errors=[f"插件已禁用: {plugin_name}"]
            )
        
        try:
            result = plugin.execute(**kwargs)
            return result
        except Exception as e:
            return ExecutionResult(
                success=False,
                errors=[f"插件执行失败: {str(e)}"]
            )
    
    # ========== 依赖管理 ==========
    
    def check_dependencies(self, plugin_name: str) -> Dict[str, bool]:
        """
        检查插件依赖
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            Dict[str, bool]: 依赖名 -> 是否满足
        """
        info = self._plugin_info.get(plugin_name)
        
        if info is None:
            return {}
        
        results = {}
        
        for dep in info.dependencies:
            try:
                __import__(dep)
                results[dep] = True
            except ImportError:
                results[dep] = False
        
        return results
    
    def install_dependencies(self, plugin_name: str) -> bool:
        """
        安装插件依赖（调用pip）
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            bool: 是否安装成功
        """
        info = self._plugin_info.get(plugin_name)
        
        if info is None:
            self._log("error", f"插件不存在: {plugin_name}")
            return False
        
        if not info.dependencies:
            return True
        
        import subprocess
        
        for dep in info.dependencies:
            try:
                self._log("info", f"安装依赖: {dep}")
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            except subprocess.CalledProcessError as e:
                self._log("error", f"安装依赖失败: {dep} - {e}")
                return False
        
        self._log("info", f"依赖安装完成: {plugin_name}")
        return True