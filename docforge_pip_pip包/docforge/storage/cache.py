"""
缓存管理
内存缓存和磁盘缓存的管理

使用示例：
    from docforge.storage.cache import CacheManager
    
    cache = CacheManager(".cache")
    
    # 内存缓存
    cache.set_memory("key1", "value1", ttl=3600)
    value = cache.get_memory("key1")
    
    # 磁盘缓存
    cache.set_disk("key2", {"data": "value"}, ttl=86400)
    data = cache.get_disk("key2")
"""

import json
import pickle
import hashlib
import time
import os
from typing import Any, Optional, Dict
from pathlib import Path
from datetime import datetime, timedelta


class CacheManager:
    """
    缓存管理器
    
    提供多级缓存功能
    """
    
    def __init__(self, cache_dir: str = ".cache"):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 内存缓存 {key: (value, expire_time)}
        self._memory_cache: Dict[str, tuple] = {}
        
        # 磁盘缓存目录
        self._disk_cache_dir = self.cache_dir / "disk"
        self._disk_cache_dir.mkdir(exist_ok=True)
    
    # ========== 内存缓存 ==========
    
    def set_memory(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        设置内存缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），0表示永不过期
            
        Returns:
            bool: 是否设置成功
        """
        try:
            expire_time = None
            if ttl > 0:
                expire_time = time.time() + ttl
            
            self._memory_cache[key] = (value, expire_time)
            return True
            
        except Exception as e:
            print(f"设置内存缓存失败: {e}")
            return False
    
    def get_memory(self, key: str) -> Optional[Any]:
        """
        获取内存缓存
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[Any]: 缓存值，不存在或过期返回None
        """
        if key not in self._memory_cache:
            return None
        
        value, expire_time = self._memory_cache[key]
        
        # 检查是否过期
        if expire_time is not None and time.time() > expire_time:
            del self._memory_cache[key]
            return None
        
        return value
    
    def delete_memory(self, key: str) -> bool:
        """
        删除内存缓存
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否删除成功
        """
        if key in self._memory_cache:
            del self._memory_cache[key]
            return True
        return False
    
    def clear_memory(self) -> None:
        """清空内存缓存"""
        self._memory_cache.clear()
    
    # ========== 磁盘缓存 ==========
    
    def set_disk(self, key: str, value: Any, ttl: int = 86400) -> bool:
        """
        设置磁盘缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），0表示永不过期
            
        Returns:
            bool: 是否设置成功
        """
        try:
            # 生成缓存文件路径
            cache_key = self._generate_key(key)
            cache_file = self._disk_cache_dir / f"{cache_key}.cache"
            
            # 准备缓存数据
            cache_data = {
                "key": key,
                "value": value,
                "created_at": time.time(),
                "ttl": ttl
            }
            
            # 序列化并保存
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            return True
            
        except Exception as e:
            print(f"设置磁盘缓存失败: {e}")
            return False
    
    def get_disk(self, key: str) -> Optional[Any]:
        """
        获取磁盘缓存
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[Any]: 缓存值，不存在或过期返回None
        """
        try:
            # 生成缓存文件路径
            cache_key = self._generate_key(key)
            cache_file = self._disk_cache_dir / f"{cache_key}.cache"
            
            if not cache_file.exists():
                return None
            
            # 读取缓存数据
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # 检查是否过期
            ttl = cache_data.get("ttl", 0)
            if ttl > 0:
                created_at = cache_data.get("created_at", 0)
                if time.time() > created_at + ttl:
                    # 过期，删除缓存文件
                    cache_file.unlink()
                    return None
            
            return cache_data.get("value")
            
        except Exception as e:
            print(f"获取磁盘缓存失败: {e}")
            return None
    
    def delete_disk(self, key: str) -> bool:
        """
        删除磁盘缓存
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否删除成功
        """
        try:
            cache_key = self._generate_key(key)
            cache_file = self._disk_cache_dir / f"{cache_key}.cache"
            
            if cache_file.exists():
                cache_file.unlink()
                return True
            
            return False
            
        except Exception as e:
            print(f"删除磁盘缓存失败: {e}")
            return False
    
    def clear_disk(self) -> None:
        """清空磁盘缓存"""
        try:
            for cache_file in self._disk_cache_dir.glob("*.cache"):
                cache_file.unlink()
        except Exception as e:
            print(f"清空磁盘缓存失败: {e}")
    
    # ========== 文件哈希缓存 ==========
    
    def get_file_hash(self, file_path: str) -> Optional[str]:
        """
        获取文件哈希（带缓存）
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[str]: 文件哈希
        """
        # 检查缓存
        cache_key = f"file_hash:{file_path}"
        cached_hash = self.get_memory(cache_key)
        
        if cached_hash:
            return cached_hash
        
        # 计算哈希
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            hash_md5 = hashlib.md5()
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            
            file_hash = hash_md5.hexdigest()
            
            # 缓存哈希（永不过期，除非文件修改）
            self.set_memory(cache_key, file_hash, ttl=0)
            
            return file_hash
            
        except Exception as e:
            print(f"计算文件哈希失败: {e}")
            return None
    
    def invalidate_file_hash(self, file_path: str) -> None:
        """
        使文件哈希缓存失效
        
        Args:
            file_path: 文件路径
        """
        cache_key = f"file_hash:{file_path}"
        self.delete_memory(cache_key)
    
    # ========== 缓存统计 ==========
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        # 内存缓存统计
        memory_count = len(self._memory_cache)
        memory_expired = 0
        for _, expire_time in self._memory_cache.values():
            if expire_time is not None and time.time() > expire_time:
                memory_expired += 1
        
        # 磁盘缓存统计
        disk_files = list(self._disk_cache_dir.glob("*.cache"))
        disk_count = len(disk_files)
        disk_size = sum(f.stat().st_size for f in disk_files)
        
        return {
            "memory": {
                "count": memory_count,
                "expired": memory_expired
            },
            "disk": {
                "count": disk_count,
                "size_bytes": disk_size,
                "size_mb": round(disk_size / 1024 / 1024, 2)
            }
        }
    
    def cleanup_expired(self) -> int:
        """
        清理过期缓存
        
        Returns:
            int: 清理的数量
        """
        cleaned = 0
        
        # 清理内存缓存
        expired_keys = []
        for key, (_, expire_time) in self._memory_cache.items():
            if expire_time is not None and time.time() > expire_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._memory_cache[key]
            cleaned += 1
        
        # 清理磁盘缓存
        for cache_file in self._disk_cache_dir.glob("*.cache"):
            try:
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                
                ttl = cache_data.get("ttl", 0)
                if ttl > 0:
                    created_at = cache_data.get("created_at", 0)
                    if time.time() > created_at + ttl:
                        cache_file.unlink()
                        cleaned += 1
                        
            except Exception:
                # 文件损坏，删除
                cache_file.unlink()
                cleaned += 1
        
        return cleaned
    
    # ========== 工具方法 ==========
    
    def _generate_key(self, key: str) -> str:
        """
        生成缓存键的哈希值
        
        Args:
            key: 原始键
            
        Returns:
            str: 哈希后的键
        """
        return hashlib.md5(key.encode()).hexdigest()