"""
对外接口模块
提供GUI和插件调用的统一接口
"""

from .core_api import CoreAPI
from .plugin_api import PluginAPI
from .event_bus import EventBus, Event

__all__ = [
    "CoreAPI",
    "PluginAPI",
    "EventBus",
    "Event"
]