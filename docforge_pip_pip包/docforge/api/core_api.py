"""
核心API
供GUI层调用的主要接口

使用示例：
    from docforge.api.core_api import CoreAPI
    
    api = CoreAPI()
    api.initialize()
    
    # 创建项目
    api.create_project("我的项目", "./my_project")
    
    # 执行工作流
    result = api.execute_workflow("my_workflow")
"""

import os
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..types import ExecutionResult, WorkflowDefinition, PathLike
from ..services.logger import Logger
from ..services.file_manager import FileManager
from ..services.plugin_manager import PluginManager
from ..services.project_manager import ProjectManager
from ..services.workflow_engine import WorkflowEngine
from ..storage.database import DatabaseManager
from ..storage.config import ConfigManager
from ..storage.cache import CacheManager
from ..constants import LogLevel, WorkflowStatus


class CoreAPI:
    """
    核心API类
    
    封装所有核心功能，供GUI调用
    """
    
    def __init__(self):
        """初始化核心API"""
        self._initialized = False
        
        # 服务实例
        self.logger: Optional[Logger] = None
        self.file_manager: Optional[FileManager] = None
        self.plugin_manager: Optional[PluginManager] = None
        self.project_manager: Optional[ProjectManager] = None
        self.workflow_engine: Optional[WorkflowEngine] = None
        
        # 存储实例
        self.database: Optional[DatabaseManager] = None
        self.config: Optional[ConfigManager] = None
        self.cache: Optional[CacheManager] = None
    
    def initialize(self, config_path: str = None) -> bool:
        """
        初始化框架
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            bool: 是否初始化成功
        """
        if self._initialized:
            return True
        
        try:
            # 初始化配置
            self.config = ConfigManager(config_path or "config.json")
            self.config.load()
            
            # 初始化日志
            log_level = self.config.get("logging.level", LogLevel.INFO)
            log_file = self.config.get("logging.file", "docforge.log")
            
            self.logger = Logger()
            self.logger.set_level(log_level)
            
            if log_file:
                self.logger.add_file_handler(log_file)
            
            self.logger.info("框架初始化开始")
            
            # 初始化数据库
            db_path = self.config.get("database.path", "docforge.db")
            self.database = DatabaseManager(db_path)
            self.database.connect()
            self.database.create_tables()
            
            # 初始化缓存
            cache_dir = self.config.get("files.temp_directory", ".cache")
            self.cache = CacheManager(cache_dir)
            
            # 初始化服务
            self.file_manager = FileManager(self.logger)
            self.plugin_manager = PluginManager(self.logger)
            self.project_manager = ProjectManager(self.logger)
            self.workflow_engine = WorkflowEngine(self.plugin_manager, self.logger)
            
            # 加载插件
            plugin_dir = self.config.get("plugins.directory", "plugins")
            if not os.path.exists(plugin_dir):
                plugin_dir = "plugins"  # 回退到默认的plugins目录
            
            if os.path.exists(plugin_dir):
                self.plugin_manager.load_all_plugins(plugin_dir)
                self.logger.info(f"已加载插件目录: {os.path.abspath(plugin_dir)}")
            else:
                self.logger.warning(f"插件目录不存在: {plugin_dir}")
            
            self._initialized = True
            self.logger.info("框架初始化完成")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"框架初始化失败: {e}")
            else:
                print(f"框架初始化失败: {e}")
            return False
    
    def shutdown(self) -> None:
        """关闭框架"""
        if not self._initialized:
            return
        
        self.logger.info("框架关闭开始")
        
        # 关闭数据库
        if self.database:
            self.database.disconnect()
        
        # 清理缓存
        if self.cache:
            self.cache.cleanup_expired()
        
        self._initialized = False
        self.logger.info("框架关闭完成")
    
    # ========== 项目管理 API ==========
    
    def create_project(self, name: str, path: PathLike) -> bool:
        """
        创建项目
        
        Args:
            name: 项目名称
            path: 项目路径
            
        Returns:
            bool: 是否创建成功
        """
        self._check_initialized()
        return self.project_manager.create_project(name, path)
    
    def open_project(self, project_path: PathLike) -> bool:
        """
        打开项目
        
        Args:
            project_path: 项目路径
            
        Returns:
            bool: 是否打开成功
        """
        self._check_initialized()
        return self.project_manager.open_project(project_path)
    
    def save_project(self) -> bool:
        """
        保存项目
        
        Returns:
            bool: 是否保存成功
        """
        self._check_initialized()
        return self.project_manager.save_project()
    
    def close_project(self) -> bool:
        """
        关闭项目
        
        Returns:
            bool: 是否关闭成功
        """
        self._check_initialized()
        return self.project_manager.close_project()
    
    def get_project_config(self) -> Dict[str, Any]:
        """
        获取项目配置
        
        Returns:
            Dict[str, Any]: 项目配置
        """
        self._check_initialized()
        return self.project_manager.get_project_config()
    
    # ========== 文件管理 API ==========
    
    def add_input_files(self, files: List[PathLike]) -> bool:
        """
        添加输入文件
        
        Args:
            files: 文件路径列表
            
        Returns:
            bool: 是否添加成功
        """
        self._check_initialized()
        return self.project_manager.add_input_files(files)
    
    def get_input_files(self) -> List[str]:
        """
        获取输入文件列表
        
        Returns:
            List[str]: 输入文件列表
        """
        self._check_initialized()
        return self.project_manager.get_input_files()
    
    def clear_input_files(self) -> bool:
        """
        清空输入文件
        
        Returns:
            bool: 是否清空成功
        """
        self._check_initialized()
        return self.project_manager.clear_input_files()
    
    def add_template_files(self, files: List[PathLike]) -> bool:
        """
        添加模板文件
        
        Args:
            files: 文件路径列表
            
        Returns:
            bool: 是否添加成功
        """
        self._check_initialized()
        return self.project_manager.add_template_files(files)
    
    def get_template_files(self) -> List[str]:
        """
        获取模板文件列表
        
        Returns:
            List[str]: 模板文件列表
        """
        self._check_initialized()
        return self.project_manager.get_template_files()
    
    def set_output_directory(self, directory: PathLike) -> bool:
        """
        设置输出目录
        
        Args:
            directory: 输出目录路径
            
        Returns:
            bool: 是否设置成功
        """
        self._check_initialized()
        return self.project_manager.set_output_directory(directory)
    
    def get_output_directory(self) -> str:
        """
        获取输出目录
        
        Returns:
            str: 输出目录路径
        """
        self._check_initialized()
        return self.project_manager.get_output_directory()
    
    # ========== 工作流 API ==========
    
    def load_workflow(self, workflow_path: PathLike) -> bool:
        """
        加载工作流
        
        Args:
            workflow_path: 工作流文件路径
            
        Returns:
            bool: 是否加载成功
        """
        self._check_initialized()
        try:
            workflow = self.workflow_engine.load_workflow(workflow_path)
            self.project_manager.set_workflow(workflow.name, workflow_path)
            return True
        except Exception as e:
            self.logger.error(f"加载工作流失败: {e}")
            return False
    
    def get_workflow_list(self) -> List[str]:
        """
        获取工作流列表
        
        Returns:
            List[str]: 工作流名称列表
        """
        self._check_initialized()
        # 简化实现：返回当前项目的工作流
        workflow = self.project_manager.get_workflow()
        if workflow["name"]:
            return [workflow["name"]]
        return []
    
    def execute_workflow(
        self,
        workflow_name: str,
        progress_callback: callable = None
    ) -> ExecutionResult:
        """
        执行工作流
        
        Args:
            workflow_name: 工作流名称
            progress_callback: 进度回调函数
            
        Returns:
            ExecutionResult: 执行结果
        """
        self._check_initialized()
        
        # 获取工作流
        workflow_config = self.project_manager.get_workflow()
        workflow_path = workflow_config.get("path")
        
        if not workflow_path:
            return ExecutionResult(
                success=False,
                errors=["未设置工作流"]
            )
        
        try:
            # 加载工作流
            workflow = self.workflow_engine.load_workflow(workflow_path)
            
            # 获取文件列表
            input_files = self.project_manager.get_input_files()
            template_files = self.project_manager.get_template_files()
            output_dir = self.project_manager.get_output_directory()
            
            if not input_files:
                return ExecutionResult(
                    success=False,
                    errors=["没有输入文件"]
                )
            
            if not template_files:
                return ExecutionResult(
                    success=False,
                    errors=["没有模板文件"]
                )
            
            if not output_dir:
                return ExecutionResult(
                    success=False,
                    errors=["未设置输出目录"]
                )
            
            # 执行工作流
            result = self.workflow_engine.execute(
                workflow=workflow,
                input_files=input_files,
                template_files=template_files,
                output_dir=output_dir,
                progress_callback=progress_callback
            )
            
            return result
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                errors=[f"执行失败: {str(e)}"]
            )
    
    def cancel_execution(self) -> bool:
        """
        取消执行
        
        Returns:
            bool: 是否取消成功
        """
        self._check_initialized()
        return self.workflow_engine.cancel()
    
    def get_execution_status(self) -> WorkflowStatus:
        """
        获取执行状态
        
        Returns:
            WorkflowStatus: 当前状态
        """
        self._check_initialized()
        return self.workflow_engine.get_status()
    
    # ========== 插件 API ==========
    
    def get_plugin_list(self) -> List[Dict[str, Any]]:
        """
        获取插件列表
        
        Returns:
            List[Dict[str, Any]]: 插件信息列表
        """
        self._check_initialized()
        return self.plugin_manager.get_plugin_list()
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """
        启用插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            bool: 是否启用成功
        """
        self._check_initialized()
        return self.plugin_manager.enable_plugin(plugin_name)
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """
        禁用插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            bool: 是否禁用成功
        """
        self._check_initialized()
        return self.plugin_manager.disable_plugin(plugin_name)
    
    def reload_plugins(self) -> Dict[str, bool]:
        """
        重新加载所有插件
        
        Returns:
            Dict[str, bool]: 插件名 -> 是否加载成功
        """
        self._check_initialized()
        plugin_dir = self.config.get("plugins.directory", "plugins")
        return self.plugin_manager.load_all_plugins(plugin_dir)
    
    # ========== 日志 API ==========
    
    def get_logs(self, level: str = None, limit: int = 100) -> List[Dict]:
        """
        获取日志
        
        Args:
            level: 日志级别过滤
            limit: 返回数量限制
            
        Returns:
            List[Dict]: 日志记录列表
        """
        self._check_initialized()
        return self.logger.get_logs(level=level, limit=limit)
    
    def clear_logs(self) -> bool:
        """
        清空日志
        
        Returns:
            bool: 是否清空成功
        """
        self._check_initialized()
        self.logger.clear()
        return True
    
    # ========== 内部方法 ==========
    
    def _check_initialized(self) -> None:
        """检查是否已初始化"""
        if not self._initialized:
            raise RuntimeError("框架未初始化，请先调用 initialize()")