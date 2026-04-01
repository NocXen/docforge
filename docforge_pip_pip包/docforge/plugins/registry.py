"""
插件注册表
管理已加载插件的注册和查询

使用示例：
    from docforge.plugins.registry import PluginRegistry
    
    registry = PluginRegistry()
    
    # 注册插件
    registry.register(plugin)
    
    # 获取插件
    plugin = registry.get_plugin("my_plugin")
    
    # 获取所有插件
    all_plugins = registry.get_all_plugins()
"""

from typing import Dict, List, Optional

from .base import BasePlugin
from .types import PluginMetadata


class PluginRegistry:
    """
    插件注册表
    
    提供插件的注册、查询和管理功能
    """
    
    def __init__(self):
        """初始化注册表"""
        self._plugins: Dict[str, BasePlugin] = {}
        self._metadata: Dict[str, PluginMetadata] = {}
        self._enabled: Dict[str, bool] = {}
    
    # ========== 注册管理 ==========
    
    def register(self, plugin: BasePlugin) -> bool:
        """
        注册插件
        
        Args:
            plugin: 插件实例
            
        Returns:
            bool: 是否注册成功
        """
        if plugin is None:
            return False
        
        name = plugin.name
        
        # 检查是否已注册
        if name in self._plugins:
            return False
        
        # 注册插件
        self._plugins[name] = plugin
        self._enabled[name] = True
        
        # 保存元数据
        metadata = PluginMetadata(
            name=plugin.name,
            version=plugin.version,
            plugin_type=plugin.plugin_type,
            author=plugin.author,
            description=plugin.description,
            dependencies=plugin.dependencies
        )
        self._metadata[name] = metadata
        
        return True
    
    def unregister(self, plugin_name: str) -> bool:
        """
        注销插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            bool: 是否注销成功
        """
        if plugin_name not in self._plugins:
            return False
        
        # 清理资源
        plugin = self._plugins[plugin_name]
        plugin.cleanup()
        
        # 移除注册
        del self._plugins[plugin_name]
        del self._metadata[plugin_name]
        del self._enabled[plugin_name]
        
        return True
    
    def is_registered(self, plugin_name: str) -> bool:
        """
        检查插件是否已注册
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            bool: 是否已注册
        """
        return plugin_name in self._plugins
    
    # ========== 查询方法 ==========
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        获取插件实例
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            Optional[BasePlugin]: 插件实例，不存在返回None
        """
        return self._plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, BasePlugin]:
        """
        获取所有已注册插件
        
        Returns:
            Dict[str, BasePlugin]: 插件名 -> 插件实例
        """
        return self._plugins.copy()
    
    def get_plugins_by_type(self, plugin_type: str) -> List[BasePlugin]:
        """
        按类型获取插件
        
        Args:
            plugin_type: 插件类型
            
        Returns:
            List[BasePlugin]: 插件列表
        """
        return [
            plugin for plugin in self._plugins.values()
            if plugin.plugin_type == plugin_type
        ]
    
    def get_plugin_names(self) -> List[str]:
        """
        获取所有插件名称
        
        Returns:
            List[str]: 插件名称列表
        """
        return list(self._plugins.keys())
    
    def get_enabled_plugins(self) -> List[BasePlugin]:
        """
        获取所有启用的插件
        
        Returns:
            List[BasePlugin]: 启用的插件列表
        """
        return [
            plugin for name, plugin in self._plugins.items()
            if self._enabled.get(name, True)
        ]
    
    # ========== 启用/禁用 ==========
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """
        启用插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            bool: 是否成功
        """
        if plugin_name not in self._plugins:
            return False
        
        self._enabled[plugin_name] = True
        return True
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """
        禁用插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            bool: 是否成功
        """
        if plugin_name not in self._plugins:
            return False
        
        self._enabled[plugin_name] = False
        return True
    
    def is_enabled(self, plugin_name: str) -> bool:
        """
        检查插件是否启用
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            bool: 是否启用
        """
        return self._enabled.get(plugin_name, True)
    
    # ========== 元数据查询 ==========
    
    def get_metadata(self, plugin_name: str) -> Optional[PluginMetadata]:
        """
        获取插件元数据
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            Optional[PluginMetadata]: 插件元数据
        """
        return self._metadata.get(plugin_name)
    
    def get_all_metadata(self) -> Dict[str, PluginMetadata]:
        """
        获取所有插件元数据
        
        Returns:
            Dict[str, PluginMetadata]: 插件名 -> 元数据
        """
        return self._metadata.copy()
    
    # ========== 统计信息 ==========
    
    def get_plugin_count(self) -> int:
        """
        获取已注册插件数量
        
        Returns:
            int: 插件数量
        """
        return len(self._plugins)
    
    def get_plugins_info(self) -> List[Dict]:
        """
        获取所有插件的详细信息
        
        Returns:
            List[Dict]: 插件信息列表
        """
        result = []
        
        for name, plugin in self._plugins.items():
            info = {
                "name": name,
                "version": plugin.version,
                "plugin_type": plugin.plugin_type,
                "enabled": self.is_enabled(name),
                "description": plugin.description
            }
            result.append(info)
        
        return result
    
    def clear(self) -> None:
        """清空所有注册的插件"""
        # 清理所有插件资源
        for plugin in self._plugins.values():
            plugin.cleanup()
        
        self._plugins.clear()
        self._metadata.clear()
        self._enabled.clear()