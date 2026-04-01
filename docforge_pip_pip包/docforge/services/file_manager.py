"""
文件管理服务
提供文件操作的高级接口

使用示例：
    from docforge.services.file_manager import FileManager
    from docforge.services.logger import Logger
    
    logger = Logger()
    file_manager = FileManager(logger)
    
    # 获取文件信息
    info = file_manager.get_file_info("data.xlsx")
    print(f"文件大小: {info.size} 字节")
"""

import os
import shutil
import hashlib
from typing import Dict, List, Optional, Callable
from pathlib import Path
from datetime import datetime

from ..types import FileInfo, PathLike
from ..exceptions import FileNotFoundError, FilePermissionError


class FileManager:
    """
    文件管理器
    
    提供文件操作的高级接口
    
    Attributes:
        logger: 日志器实例
    """
    
    def __init__(self, logger=None):
        """
        初始化文件管理器
        
        Args:
            logger: 日志器实例（可选）
        """
        self.logger = logger
        self._watchers: Dict[str, Callable] = {}
    
    def _log(self, level: str, message: str, **kwargs) -> None:
        """记录日志"""
        if self.logger:
            getattr(self.logger, level)(message, **kwargs)
    
    # ========== 文件信息获取 ==========
    
    def get_file_info(self, file_path: PathLike) -> FileInfo:
        """
        获取文件详细信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            FileInfo: 文件信息对象
            
        Raises:
            FileNotFoundError: 文件不存在
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        
        if not path.is_file():
            raise FileNotFoundError(f"不是文件: {path}")
        
        stat = path.stat()
        
        return FileInfo(
            path=path,
            name=path.name,
            extension=path.suffix.lower(),
            size=stat.st_size,
            modified_time=datetime.fromtimestamp(stat.st_mtime)
        )
    
    def get_files_info(self, file_paths: List[PathLike]) -> List[FileInfo]:
        """
        批量获取文件信息
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            List[FileInfo]: 文件信息列表
        """
        result = []
        for path in file_paths:
            try:
                info = self.get_file_info(path)
                result.append(info)
            except FileNotFoundError as e:
                self._log("warning", str(e))
        return result
    
    def calculate_hash(self, file_path: PathLike, algorithm: str = "md5") -> str:
        """
        计算文件哈希值
        
        Args:
            file_path: 文件路径
            algorithm: 哈希算法（md5/sha1/sha256）
            
        Returns:
            str: 哈希值
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        
        hash_func = getattr(hashlib, algorithm)()
        
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    # ========== 目录操作 ==========
    
    def ensure_directory(self, dir_path: PathLike) -> Path:
        """
        确保目录存在，不存在则创建
        
        Args:
            dir_path: 目录路径
            
        Returns:
            Path: 目录路径对象
        """
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        self._log("debug", f"目录已确保存在: {path}")
        return path
    
    def list_files(
        self,
        directory: PathLike,
        extensions: List[str] = None,
        recursive: bool = False
    ) -> List[Path]:
        """
        列出目录下的文件
        
        Args:
            directory: 目录路径
            extensions: 扩展名过滤（如 [".xlsx", ".xls"]）
            recursive: 是否递归子目录
            
        Returns:
            List[Path]: 文件路径列表
        """
        path = Path(directory)
        
        if not path.exists():
            raise FileNotFoundError(f"目录不存在: {path}")
        
        if not path.is_dir():
            raise FileNotFoundError(f"不是目录: {path}")
        
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        files = []
        for item in path.glob(pattern):
            if item.is_file():
                if extensions is None or item.suffix.lower() in extensions:
                    files.append(item)
        
        return sorted(files)
    
    # ========== 文件备份 ==========
    
    def backup_file(self, file_path: PathLike, backup_dir: str = ".backup") -> Optional[Path]:
        """
        备份文件
        
        Args:
            file_path: 要备份的文件路径
            backup_dir: 备份目录
            
        Returns:
            Optional[Path]: 备份文件路径，失败返回None
        """
        source = Path(file_path)
        
        if not source.exists():
            self._log("error", f"文件不存在，无法备份: {source}")
            return None
        
        try:
            # 创建备份目录
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # 生成备份文件名（带时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source.stem}_{timestamp}{source.suffix}"
            destination = backup_path / backup_name
            
            # 复制文件
            shutil.copy2(source, destination)
            
            self._log("info", f"文件已备份: {source} -> {destination}")
            return destination
            
        except Exception as e:
            self._log("error", f"备份失败: {e}")
            return None
    
    def restore_backup(self, backup_path: PathLike, target_path: PathLike) -> bool:
        """
        从备份恢复文件
        
        Args:
            backup_path: 备份文件路径
            target_path: 目标路径
            
        Returns:
            bool: 是否恢复成功
        """
        source = Path(backup_path)
        destination = Path(target_path)
        
        if not source.exists():
            self._log("error", f"备份文件不存在: {source}")
            return False
        
        try:
            # 确保目标目录存在
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            shutil.copy2(source, destination)
            
            self._log("info", f"文件已恢复: {source} -> {destination}")
            return True
            
        except Exception as e:
            self._log("error", f"恢复失败: {e}")
            return False
    
    # ========== 批量操作 ==========
    
    def batch_rename(
        self,
        files: List[PathLike],
        pattern: str
    ) -> Dict[str, str]:
        """
        批量重命名文件
        
        Args:
            files: 文件路径列表
            pattern: 命名模式，支持占位符：
                     {index} - 序号
                     {name} - 原文件名（不含扩展名）
                     {ext} - 扩展名
                     {date} - 日期
            
        Returns:
            Dict[str, str]: 原路径 -> 新路径
        """
        result = {}
        date_str = datetime.now().strftime("%Y%m%d")
        
        for index, file_path in enumerate(files):
            source = Path(file_path)
            
            if not source.exists():
                self._log("warning", f"文件不存在，跳过: {source}")
                continue
            
            # 替换占位符
            new_name = pattern.replace("{index}", str(index + 1).zfill(3))
            new_name = new_name.replace("{name}", source.stem)
            new_name = new_name.replace("{ext}", source.suffix)
            new_name = new_name.replace("{date}", date_str)
            
            # 确保有扩展名
            if not new_name.endswith(source.suffix):
                new_name += source.suffix
            
            destination = source.parent / new_name
            
            try:
                source.rename(destination)
                result[str(source)] = str(destination)
                self._log("debug", f"重命名: {source.name} -> {destination.name}")
            except Exception as e:
                self._log("error", f"重命名失败: {e}")
        
        return result
    
    def batch_move(
        self,
        files: List[PathLike],
        target_dir: PathLike
    ) -> Dict[str, bool]:
        """
        批量移动文件
        
        Args:
            files: 文件路径列表
            target_dir: 目标目录
            
        Returns:
            Dict[str, bool]: 文件路径 -> 是否成功
        """
        result = {}
        target = Path(target_dir)
        
        # 确保目标目录存在
        target.mkdir(parents=True, exist_ok=True)
        
        for file_path in files:
            source = Path(file_path)
            
            if not source.exists():
                self._log("warning", f"文件不存在，跳过: {source}")
                result[str(source)] = False
                continue
            
            try:
                destination = target / source.name
                shutil.move(str(source), str(destination))
                result[str(source)] = True
                self._log("debug", f"移动: {source} -> {destination}")
            except Exception as e:
                self._log("error", f"移动失败: {e}")
                result[str(source)] = False
        
        return result
    
    # ========== 临时文件管理 ==========
    
    def create_temp_file(self, suffix: str = "", prefix: str = "docforge_") -> Path:
        """
        创建临时文件
        
        Args:
            suffix: 文件后缀
            prefix: 文件前缀
            
        Returns:
            Path: 临时文件路径
        """
        import tempfile
        
        fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        os.close(fd)
        
        self._log("debug", f"创建临时文件: {path}")
        return Path(path)
    
    def create_temp_directory(self, prefix: str = "docforge_") -> Path:
        """
        创建临时目录
        
        Args:
            prefix: 目录前缀
            
        Returns:
            Path: 临时目录路径
        """
        import tempfile
        
        path = tempfile.mkdtemp(prefix=prefix)
        
        self._log("debug", f"创建临时目录: {path}")
        return Path(path)
    
    def cleanup_temp(self, temp_path: PathLike) -> int:
        """
        清理临时文件或目录
        
        Args:
            temp_path: 临时路径
            
        Returns:
            int: 清理的文件数量
        """
        path = Path(temp_path)
        count = 0
        
        try:
            if path.is_file():
                path.unlink()
                count = 1
            elif path.is_dir():
                count = len(list(path.rglob("*")))
                shutil.rmtree(path)
            
            self._log("debug", f"清理临时路径: {path} ({count} 个文件)")
            
        except Exception as e:
            self._log("error", f"清理失败: {e}")
        
        return count
    
    # ========== 文件验证 ==========
    
    def validate_file_path(self, file_path: PathLike, must_exist: bool = True) -> bool:
        """
        验证文件路径
        
        Args:
            file_path: 文件路径
            must_exist: 是否必须存在
            
        Returns:
            bool: 是否有效
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
    
    def validate_directory_path(self, dir_path: PathLike, must_exist: bool = True) -> bool:
        """
        验证目录路径
        
        Args:
            dir_path: 目录路径
            must_exist: 是否必须存在
            
        Returns:
            bool: 是否有效
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
    
    def check_file_writable(self, file_path: PathLike) -> bool:
        """
        检查文件是否可写
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否可写
        """
        path = Path(file_path)
        
        if path.exists():
            return os.access(path, os.W_OK)
        else:
            # 检查父目录是否可写
            return os.access(path.parent, os.W_OK)