"""
配置管理
JSON配置文件的读写和管理

使用示例：
    from docforge.storage.config import ConfigManager
    
    config = ConfigManager("config.json")
    config.load()
    
    # 获取配置
    value = config.get("database.path", "default.db")
    
    # 设置配置
    config.set("database.path", "/new/path.db")
    config.save()
"""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path


class ConfigManager:
    """
    配置管理器
    
    管理应用程序配置
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._defaults: Dict[str, Any] = {}
    
    # ========== 配置读取 ==========
    
    def load(self) -> bool:
        """
        加载配置文件
        
        Returns:
            bool: 是否加载成功
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                self._config = self._defaults.copy()
            
            return True
            
        except Exception as e:
            print(f"加载配置失败: {e}")
            self._config = self._defaults.copy()
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值（支持点分隔的嵌套键）
        
        Args:
            key: 配置键（如"database.path"）
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        获取配置段
        
        Args:
            section: 段名
            
        Returns:
            Dict[str, Any]: 配置字典
        """
        return self._config.get(section, {}).copy()
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        Returns:
            Dict[str, Any]: 完整配置字典
        """
        return self._config.copy()
    
    # ========== 配置写入 ==========
    
    def set(self, key: str, value: Any) -> bool:
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
            
        Returns:
            bool: 是否设置成功
        """
        keys = key.split('.')
        config = self._config
        
        # 遍历到倒数第二层
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            elif not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
        return True
    
    def set_section(self, section: str, data: Dict[str, Any]) -> bool:
        """
        设置配置段
        
        Args:
            section: 段名
            data: 配置数据
            
        Returns:
            bool: 是否设置成功
        """
        self._config[section] = data
        return True
    
    def save(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            bool: 是否保存成功
        """
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    # ========== 配置管理 ==========
    
    def has(self, key: str) -> bool:
        """
        检查配置键是否存在
        
        Args:
            key: 配置键
            
        Returns:
            bool: 是否存在
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return False
        
        return True
    
    def delete(self, key: str) -> bool:
        """
        删除配置键
        
        Args:
            key: 配置键
            
        Returns:
            bool: 是否删除成功
        """
        keys = key.split('.')
        config = self._config
        
        # 遍历到倒数第二层
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                return False
            config = config[k]
        
        # 删除键
        if keys[-1] in config:
            del config[keys[-1]]
            return True
        
        return False
    
    def reset(self) -> bool:
        """
        重置为默认配置
        
        Returns:
            bool: 是否重置成功
        """
        self._config = self._defaults.copy()
        return True
    
    def merge(self, other_config: Dict[str, Any]) -> bool:
        """
        合并配置（深度合并）
        
        Args:
            other_config: 要合并的配置
            
        Returns:
            bool: 是否合并成功
        """
        def deep_merge(target: dict, source: dict):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    deep_merge(target[key], value)
                else:
                    target[key] = value
        
        deep_merge(self._config, other_config)
        return True
    
    # ========== 验证 ==========
    
    def validate(self) -> List[str]:
        """
        验证配置有效性
        
        Returns:
            List[str]: 错误列表
        """
        errors = []
        
        # 这里可以添加具体的验证逻辑
        # 例如检查必需的配置项是否存在
        
        return errors
    
    def set_defaults(self, defaults: Dict[str, Any]) -> None:
        """
        设置默认值
        
        Args:
            defaults: 默认配置
        """
        self._defaults = defaults.copy()
    
    # ========== 导入导出 ==========
    
    def export_config(self, export_path: str) -> bool:
        """
        导出配置
        
        Args:
            export_path: 导出路径
            
        Returns:
            bool: 是否导出成功
        """
        try:
            path = Path(export_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"导出配置失败: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """
        导入配置
        
        Args:
            import_path: 导入路径
            
        Returns:
            bool: 是否导入成功
        """
        try:
            path = Path(import_path)
            
            if not path.exists():
                return False
            
            with open(path, 'r', encoding='utf-8') as f:
                imported = json.load(f)
            
            self._config = imported
            return True
            
        except Exception as e:
            print(f"导入配置失败: {e}")
            return False