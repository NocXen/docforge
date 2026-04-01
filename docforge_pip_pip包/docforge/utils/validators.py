"""
数据验证工具函数
验证数据的有效性

使用示例：
    from docforge.utils.validators import validate_file_path, validate_json
    
    is_valid = validate_file_path("data.xlsx", must_exist=True)
    is_valid = validate_json('{"key": "value"}')
"""

import json
import os
from typing import Any, List, Optional
from pathlib import Path


def validate_file_path(file_path: str, must_exist: bool = True) -> bool:
    """
    验证文件路径
    
    Args:
        file_path: 文件路径
        must_exist: 是否必须存在
        
    Returns:
        bool: 是否有效
        
    Example:
        >>> validate_file_path("data.xlsx", must_exist=True)
        True  # 如果文件存在
    """
    try:
        path = Path(file_path)
        
        if must_exist:
            return path.exists() and path.is_file()
        else:
            # 检查父目录是否存在且可写
            parent = path.parent
            return parent.exists() and os.access(parent, os.W_OK)
            
    except Exception:
        return False


def validate_directory_path(dir_path: str, must_exist: bool = True) -> bool:
    """
    验证目录路径
    
    Args:
        dir_path: 目录路径
        must_exist: 是否必须存在
        
    Returns:
        bool: 是否有效
        
    Example:
        >>> validate_directory_path("./output", must_exist=False)
        True
    """
    try:
        path = Path(dir_path)
        
        if must_exist:
            return path.exists() and path.is_dir()
        else:
            # 检查父目录是否存在且可写
            parent = path.parent
            return parent.exists() and os.access(parent, os.W_OK)
            
    except Exception:
        return False


def validate_file_extension(file_path: str, allowed_extensions: List[str]) -> bool:
    """
    验证文件扩展名
    
    Args:
        file_path: 文件路径
        allowed_extensions: 允许的扩展名列表（如 [".xlsx", ".xls"]）
        
    Returns:
        bool: 是否有效
        
    Example:
        >>> validate_file_extension("data.xlsx", [".xlsx", ".xls"])
        True
    """
    try:
        path = Path(file_path)
        extension = path.suffix.lower()
        return extension in [ext.lower() for ext in allowed_extensions]
    except Exception:
        return False


def validate_json(data: str) -> bool:
    """
    验证JSON字符串
    
    Args:
        data: JSON字符串
        
    Returns:
        bool: 是否有效
        
    Example:
        >>> validate_json('{"key": "value"}')
        True
        >>> validate_json('invalid json')
        False
    """
    try:
        json.loads(data)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def validate_workflow_definition(definition: dict) -> List[str]:
    """
    验证工作流定义
    
    Args:
        definition: 工作流定义字典
        
    Returns:
        List[str]: 错误列表，空列表表示验证通过
        
    Example:
        >>> errors = validate_workflow_definition({
        ...     "name": "my_workflow",
        ...     "steps": []
        ... })
    """
    errors = []
    
    # 检查必需字段
    if "name" not in definition:
        errors.append("缺少必需字段: name")
    elif not definition["name"]:
        errors.append("name 不能为空")
    
    if "steps" not in definition:
        errors.append("缺少必需字段: steps")
    elif not isinstance(definition["steps"], list):
        errors.append("steps 必须是数组")
    
    # 检查步骤
    if "steps" in definition and isinstance(definition["steps"], list):
        for i, step in enumerate(definition["steps"]):
            if not isinstance(step, dict):
                errors.append(f"步骤 {i+1} 必须是对象")
                continue
            
            if "step_id" not in step:
                errors.append(f"步骤 {i+1} 缺少 step_id")
            
            if "plugin_name" not in step:
                errors.append(f"步骤 {i+1} 缺少 plugin_name")
    
    return errors


def validate_plugin_name(name: str) -> bool:
    """
    验证插件名称
    
    Args:
        name: 插件名称
        
    Returns:
        bool: 是否有效
        
    Example:
        >>> validate_plugin_name("excel_extractor")
        True
        >>> validate_plugin_name("my plugin")  # 包含空格
        False
    """
    if not name:
        return False
    
    # 只允许字母、数字、下划线
    import re
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    return bool(re.match(pattern, name))


def validate_version(version: str) -> bool:
    """
    验证版本号（语义化版本）
    
    Args:
        version: 版本号字符串（如 "1.0.0"）
        
    Returns:
        bool: 是否有效
        
    Example:
        >>> validate_version("1.0.0")
        True
        >>> validate_version("invalid")
        False
    """
    if not version:
        return False
    
    import re
    # 简单的语义化版本验证：X.Y.Z
    pattern = r'^\d+\.\d+\.\d+$'
    return bool(re.match(pattern, version))


def validate_config_key(key: str) -> bool:
    """
    验证配置键
    
    配置键应该使用点分隔的格式，如 "database.path"
    
    Args:
        key: 配置键
        
    Returns:
        bool: 是否有效
        
    Example:
        >>> validate_config_key("database.path")
        True
        >>> validate_config_key("invalid key!")  # 包含非法字符
        False
    """
    if not key:
        return False
    
    import re
    # 允许字母、数字、下划线、点
    pattern = r'^[a-zA-Z0-9_.]+$'
    return bool(re.match(pattern, key))


def validate_email(email: str) -> bool:
    """
    验证邮箱地址
    
    Args:
        email: 邮箱地址
        
    Returns:
        bool: 是否有效
        
    Example:
        >>> validate_email("user@example.com")
        True
    """
    if not email:
        return False
    
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    验证URL
    
    Args:
        url: URL字符串
        
    Returns:
        bool: 是否有效
        
    Example:
        >>> validate_url("https://example.com")
        True
    """
    if not url:
        return False
    
    import re
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))