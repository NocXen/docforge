"""
文件操作工具函数
提供文件和路径操作的通用函数

使用示例：
    from docforge.utils.file_utils import get_file_extension, ensure_directory
    
    ext = get_file_extension("data.xlsx")  # ".xlsx"
    ensure_directory("./output")
"""

import os
import hashlib
from typing import List, Optional
from pathlib import Path


def get_file_extension(file_path: str) -> str:
    """
    获取文件扩展名
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 扩展名（含点号），如 ".xlsx"
        
    Example:
        >>> get_file_extension("data.xlsx")
        '.xlsx'
        >>> get_file_extension("path/to/file.txt")
        '.txt'
    """
    return Path(file_path).suffix.lower()


def get_file_name(file_path: str, with_extension: bool = True) -> str:
    """
    获取文件名
    
    Args:
        file_path: 文件路径
        with_extension: 是否包含扩展名
        
    Returns:
        str: 文件名
        
    Example:
        >>> get_file_name("path/to/data.xlsx")
        'data.xlsx'
        >>> get_file_name("path/to/data.xlsx", with_extension=False)
        'data'
    """
    path = Path(file_path)
    if with_extension:
        return path.name
    else:
        return path.stem


def ensure_directory(dir_path: str) -> bool:
    """
    确保目录存在，不存在则创建
    
    Args:
        dir_path: 目录路径
        
    Returns:
        bool: 是否成功
        
    Example:
        >>> ensure_directory("./output/data")
        True
    """
    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def list_files(
    directory: str,
    extensions: List[str] = None,
    recursive: bool = False
) -> List[str]:
    """
    列出目录下的文件
    
    Args:
        directory: 目录路径
        extensions: 扩展名过滤（如 [".xlsx", ".xls"]）
        recursive: 是否递归子目录
        
    Returns:
        List[str]: 文件路径列表
        
    Example:
        >>> list_files("./data", extensions=[".xlsx"])
        ['./data/file1.xlsx', './data/file2.xlsx']
    """
    path = Path(directory)
    
    if not path.exists():
        return []
    
    if recursive:
        pattern = "**/*"
    else:
        pattern = "*"
    
    files = []
    for item in path.glob(pattern):
        if item.is_file():
            if extensions is None or item.suffix.lower() in extensions:
                files.append(str(item))
    
    return sorted(files)


def calculate_file_hash(file_path: str, algorithm: str = "md5") -> str:
    """
    计算文件哈希值
    
    Args:
        file_path: 文件路径
        algorithm: 哈希算法（md5/sha1/sha256）
        
    Returns:
        str: 哈希值
        
    Raises:
        FileNotFoundError: 文件不存在
        
    Example:
        >>> calculate_file_hash("data.xlsx")
        '5d41402abc4b2a76b9719d911017c592'
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    
    hash_func = getattr(hashlib, algorithm)()
    
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def safe_delete(file_path: str) -> bool:
    """
    安全删除文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 是否删除成功
        
    Example:
        >>> safe_delete("./temp/file.txt")
        True
    """
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False
    except Exception:
        return False


def get_file_size(file_path: str) -> int:
    """
    获取文件大小（字节）
    
    Args:
        file_path: 文件路径
        
    Returns:
        int: 文件大小
        
    Raises:
        FileNotFoundError: 文件不存在
        
    Example:
        >>> get_file_size("data.xlsx")
        10240
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    
    return path.stat().st_size


def copy_file(source: str, destination: str) -> bool:
    """
    复制文件
    
    Args:
        source: 源文件路径
        destination: 目标路径
        
    Returns:
        bool: 是否复制成功
        
    Example:
        >>> copy_file("data.xlsx", "backup/data.xlsx")
        True
    """
    import shutil
    
    try:
        src = Path(source)
        dst = Path(destination)
        
        if not src.exists():
            return False
        
        # 确保目标目录存在
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(src, dst)
        return True
        
    except Exception:
        return False