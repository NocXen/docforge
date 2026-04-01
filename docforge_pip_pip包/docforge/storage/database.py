"""
数据库管理
SQLite数据库的封装和操作

使用示例：
    from docforge.storage.database import DatabaseManager
    
    db = DatabaseManager("docforge.db")
    db.connect()
    db.create_tables()
    
    # 插入数据
    row_id = db.insert("projects", {"name": "项目1"})
    
    # 查询数据
    results = db.select("projects")
    
    db.disconnect()
"""

import sqlite3
import json
import shutil
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime


class DatabaseManager:
    """
    数据库管理器
    
    提供SQLite数据库的高级接口
    """
    
    def __init__(self, db_path: str = "docforge.db"):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self._connection: Optional[sqlite3.Connection] = None
    
    # ========== 连接管理 ==========
    
    def connect(self) -> bool:
        """
        连接数据库
        
        Returns:
            bool: 是否连接成功
        """
        try:
            # 确保目录存在
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 连接数据库
            self._connection = sqlite3.connect(
                str(self.db_path),
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            self._connection.row_factory = sqlite3.Row
            
            return True
            
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False
    
    def disconnect(self) -> None:
        """断开数据库连接"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def is_connected(self) -> bool:
        """
        检查是否已连接
        
        Returns:
            bool: 是否已连接
        """
        return self._connection is not None
    
    # ========== 表操作 ==========
    
    def create_tables(self) -> bool:
        """
        创建所有必要的表
        
        Returns:
            bool: 是否创建成功
        """
        if not self._connection:
            return False
        
        try:
            cursor = self._connection.cursor()
            
            # 项目表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    config TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 工作流表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT DEFAULT '',
                    version TEXT DEFAULT '1.0.0',
                    steps TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 执行记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_name TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    input_files TEXT DEFAULT '[]',
                    output_files TEXT DEFAULT '[]',
                    error_message TEXT DEFAULT '',
                    execution_time REAL DEFAULT 0.0,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP
                )
            ''')
            
            # 插件配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plugin_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_name TEXT NOT NULL,
                    config TEXT DEFAULT '{}',
                    enabled INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self._connection.commit()
            return True
            
        except Exception as e:
            print(f"创建表失败: {e}")
            return False
    
    def drop_tables(self) -> bool:
        """
        删除所有表
        
        Returns:
            bool: 是否删除成功
        """
        if not self._connection:
            return False
        
        try:
            cursor = self._connection.cursor()
            
            tables = ['projects', 'workflows', 'executions', 'plugin_configs']
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
            
            self._connection.commit()
            return True
            
        except Exception as e:
            print(f"删除表失败: {e}")
            return False
    
    def table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在
        
        Args:
            table_name: 表名
            
        Returns:
            bool: 是否存在
        """
        if not self._connection:
            return False
        
        try:
            cursor = self._connection.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            return cursor.fetchone() is not None
        except:
            return False
    
    # ========== CRUD 操作 ==========
    
    def insert(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """
        插入数据
        
        Args:
            table: 表名
            data: 数据字典
            
        Returns:
            Optional[int]: 插入的行ID
        """
        if not self._connection:
            return None
        
        try:
            # 处理JSON字段
            processed_data = {}
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    processed_data[key] = json.dumps(value, ensure_ascii=False)
                else:
                    processed_data[key] = value
            
            # 构建SQL
            columns = ', '.join(processed_data.keys())
            placeholders = ', '.join(['?' for _ in processed_data])
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            cursor = self._connection.cursor()
            cursor.execute(sql, list(processed_data.values()))
            self._connection.commit()
            
            return cursor.lastrowid
            
        except Exception as e:
            print(f"插入数据失败: {e}")
            return None
    
    def select(
        self,
        table: str,
        columns: List[str] = None,
        where: str = None,
        params: tuple = None,
        order_by: str = None,
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """
        查询数据
        
        Args:
            table: 表名
            columns: 要查询的列
            where: WHERE条件
            params: 参数元组
            order_by: 排序字段
            limit: 限制数量
            
        Returns:
            List[Dict]: 结果列表
        """
        if not self._connection:
            return []
        
        try:
            # 构建SQL
            cols = ', '.join(columns) if columns else '*'
            sql = f"SELECT {cols} FROM {table}"
            
            if where:
                sql += f" WHERE {where}"
            
            if order_by:
                sql += f" ORDER BY {order_by}"
            
            if limit:
                sql += f" LIMIT {limit}"
            
            cursor = self._connection.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            rows = cursor.fetchall()
            
            # 转换为字典列表
            result = []
            for row in rows:
                row_dict = dict(row)
                # 处理JSON字段
                for key, value in row_dict.items():
                    if isinstance(value, str):
                        try:
                            row_dict[key] = json.loads(value)
                        except:
                            pass
                result.append(row_dict)
            
            return result
            
        except Exception as e:
            print(f"查询数据失败: {e}")
            return []
    
    def update(
        self,
        table: str,
        data: Dict[str, Any],
        where: str,
        params: tuple = None
    ) -> int:
        """
        更新数据
        
        Args:
            table: 表名
            data: 要更新的数据
            where: WHERE条件
            params: 参数元组
            
        Returns:
            int: 影响的行数
        """
        if not self._connection:
            return 0
        
        try:
            # 处理JSON字段
            processed_data = {}
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    processed_data[key] = json.dumps(value, ensure_ascii=False)
                else:
                    processed_data[key] = value
            
            # 构建SQL
            set_clause = ', '.join([f"{k} = ?" for k in processed_data.keys()])
            sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
            
            cursor = self._connection.cursor()
            values = list(processed_data.values())
            if params:
                values.extend(params)
            
            cursor.execute(sql, values)
            self._connection.commit()
            
            return cursor.rowcount
            
        except Exception as e:
            print(f"更新数据失败: {e}")
            return 0
    
    def delete(
        self,
        table: str,
        where: str,
        params: tuple = None
    ) -> int:
        """
        删除数据
        
        Args:
            table: 表名
            where: WHERE条件
            params: 参数元组
            
        Returns:
            int: 删除的行数
        """
        if not self._connection:
            return 0
        
        try:
            sql = f"DELETE FROM {table} WHERE {where}"
            
            cursor = self._connection.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            self._connection.commit()
            return cursor.rowcount
            
        except Exception as e:
            print(f"删除数据失败: {e}")
            return 0
    
    # ========== 事务操作 ==========
    
    def begin_transaction(self) -> None:
        """开始事务"""
        if self._connection:
            self._connection.execute("BEGIN TRANSACTION")
    
    def commit(self) -> None:
        """提交事务"""
        if self._connection:
            self._connection.commit()
    
    def rollback(self) -> None:
        """回滚事务"""
        if self._connection:
            self._connection.rollback()
    
    # ========== 备份与恢复 ==========
    
    def backup(self, backup_path: str) -> bool:
        """
        备份数据库
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            bool: 是否备份成功
        """
        try:
            # 确保源数据库存在
            if not self.db_path.exists():
                return False
            
            # 确保备份目录存在
            backup = Path(backup_path)
            backup.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            shutil.copy2(self.db_path, backup)
            
            return True
            
        except Exception as e:
            print(f"备份失败: {e}")
            return False
    
    def restore(self, backup_path: str) -> bool:
        """
        恢复数据库
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            bool: 是否恢复成功
        """
        try:
            backup = Path(backup_path)
            
            if not backup.exists():
                return False
            
            # 断开当前连接
            self.disconnect()
            
            # 复制备份文件
            shutil.copy2(backup, self.db_path)
            
            # 重新连接
            return self.connect()
            
        except Exception as e:
            print(f"恢复失败: {e}")
            return False
    
    def vacuum(self) -> None:
        """压缩数据库"""
        if self._connection:
            self._connection.execute("VACUUM")
            self._connection.commit()