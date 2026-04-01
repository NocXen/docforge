"""
项目管理服务
负责项目的创建、保存、加载和管理

使用示例：
    from docforge.services.project_manager import ProjectManager
    from docforge.services.logger import Logger
    
    logger = Logger()
    project_manager = ProjectManager(logger)
    
    # 创建项目
    project_manager.create_project("我的项目", "./my_project")
    
    # 添加输入文件
    project_manager.add_input_files(["data1.xlsx", "data2.xlsx"])
    
    # 保存项目
    project_manager.save_project()
"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from ..types import JsonDict, PathLike
from ..exceptions import ConfigParseError


class ProjectManager:
    """
    项目管理器
    
    管理项目配置和状态
    
    Attributes:
        logger: 日志器实例
    """
    
    def __init__(self, logger=None):
        """
        初始化项目管理器
        
        Args:
            logger: 日志器实例（可选）
        """
        self.logger = logger
        self._project_path: Optional[Path] = None
        self._project_config: JsonDict = {}
        self._modified: bool = False
    
    def _log(self, level: str, message: str, **kwargs) -> None:
        """记录日志"""
        if self.logger:
            getattr(self.logger, level)(message, **kwargs)
    
    # ========== 项目基本操作 ==========
    
    def create_project(self, name: str, path: PathLike) -> bool:
        """
        创建新项目
        
        Args:
            name: 项目名称
            path: 项目路径
            
        Returns:
            bool: 是否创建成功
        """
        project_dir = Path(path)
        
        try:
            # 创建项目目录
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建子目录
            (project_dir / "input").mkdir(exist_ok=True)
            (project_dir / "templates").mkdir(exist_ok=True)
            (project_dir / "output").mkdir(exist_ok=True)
            (project_dir / "workflows").mkdir(exist_ok=True)
            
            # 初始化项目配置
            self._project_config = {
                "name": name,
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "input": {
                    "files": [],
                    "directory": str(project_dir / "input")
                },
                "templates": {
                    "files": [],
                    "directory": str(project_dir / "templates")
                },
                "output": {
                    "directory": str(project_dir / "output")
                },
                "workflow": {
                    "name": "",
                    "path": ""
                }
            }
            
            self._project_path = project_dir
            self._modified = True
            
            # 保存项目
            self.save_project()
            
            self._log("info", f"项目已创建: {name} @ {project_dir}")
            return True
            
        except Exception as e:
            self._log("error", f"创建项目失败: {e}")
            return False
    
    def open_project(self, project_path: PathLike) -> bool:
        """
        打开现有项目
        
        Args:
            project_path: 项目路径（可以是目录或项目文件）
            
        Returns:
            bool: 是否打开成功
        """
        path = Path(project_path)
        
        # 如果是目录，查找项目文件
        if path.is_dir():
            project_file = path / "project.json"
            if not project_file.exists():
                self._log("error", f"项目文件不存在: {project_file}")
                return False
            path = project_file
        
        if not path.exists():
            self._log("error", f"项目文件不存在: {path}")
            return False
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self._project_config = json.load(f)
            
            self._project_path = path.parent
            self._modified = False
            
            self._log("info", f"项目已打开: {self._project_config.get('name')} @ {self._project_path}")
            return True
            
        except json.JSONDecodeError as e:
            raise ConfigParseError(f"项目文件格式错误: {path}", str(e))
        except Exception as e:
            self._log("error", f"打开项目失败: {e}")
            return False
    
    def save_project(self) -> bool:
        """
        保存当前项目
        
        Returns:
            bool: 是否保存成功
        """
        if self._project_path is None:
            self._log("error", "没有打开的项目")
            return False
        
        try:
            # 更新修改时间
            self._project_config["updated_at"] = datetime.now().isoformat()
            
            # 保存配置
            project_file = self._project_path / "project.json"
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(self._project_config, f, indent=2, ensure_ascii=False)
            
            self._modified = False
            
            self._log("info", f"项目已保存: {project_file}")
            return True
            
        except Exception as e:
            self._log("error", f"保存项目失败: {e}")
            return False
    
    def close_project(self) -> bool:
        """
        关闭当前项目
        
        Returns:
            bool: 是否关闭成功
        """
        if self._project_path is None:
            return True
        
        # 如果有修改，提示保存
        if self._modified:
            self._log("warning", "项目有未保存的修改")
        
        self._project_path = None
        self._project_config = {}
        self._modified = False
        
        self._log("info", "项目已关闭")
        return True
    
    # ========== 项目配置管理 ==========
    
    def get_project_config(self) -> JsonDict:
        """
        获取项目配置
        
        Returns:
            JsonDict: 项目配置字典
        """
        return self._project_config.copy()
    
    def set_project_config(self, key: str, value: Any) -> bool:
        """
        设置项目配置项
        
        支持点分隔的嵌套键，如 "input.files"
        
        Args:
            key: 配置键
            value: 配置值
            
        Returns:
            bool: 是否设置成功
        """
        keys = key.split('.')
        config = self._project_config
        
        # 遍历到倒数第二层
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
        self._modified = True
        
        return True
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键（支持点分隔）
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        keys = key.split('.')
        value = self._project_config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    # ========== 输入文件管理 ==========
    
    def add_input_files(self, files: List[PathLike]) -> bool:
        """
        添加输入文件
        
        Args:
            files: 文件路径列表
            
        Returns:
            bool: 是否添加成功
        """
        current_files = self.get_config("input.files", [])
        
        for file_path in files:
            path_str = str(file_path)
            if path_str not in current_files:
                current_files.append(path_str)
        
        self.set_project_config("input.files", current_files)
        self._log("info", f"已添加 {len(files)} 个输入文件")
        return True
    
    def remove_input_files(self, files: List[PathLike]) -> bool:
        """
        移除输入文件
        
        Args:
            files: 文件路径列表
            
        Returns:
            bool: 是否移除成功
        """
        current_files = self.get_config("input.files", [])
        
        for file_path in files:
            path_str = str(file_path)
            if path_str in current_files:
                current_files.remove(path_str)
        
        self.set_project_config("input.files", current_files)
        self._log("info", f"已移除 {len(files)} 个输入文件")
        return True
    
    def get_input_files(self) -> List[str]:
        """
        获取输入文件列表
        
        Returns:
            List[str]: 输入文件路径列表
        """
        return self.get_config("input.files", [])
    
    def clear_input_files(self) -> bool:
        """
        清空输入文件
        
        Returns:
            bool: 是否清空成功
        """
        self.set_project_config("input.files", [])
        self._log("info", "已清空输入文件")
        return True
    
    # ========== 模板文件管理 ==========
    
    def add_template_files(self, files: List[PathLike]) -> bool:
        """
        添加模板文件
        
        Args:
            files: 文件路径列表
            
        Returns:
            bool: 是否添加成功
        """
        current_files = self.get_config("templates.files", [])
        
        for file_path in files:
            path_str = str(file_path)
            if path_str not in current_files:
                current_files.append(path_str)
        
        self.set_project_config("templates.files", current_files)
        self._log("info", f"已添加 {len(files)} 个模板文件")
        return True
    
    def get_template_files(self) -> List[str]:
        """
        获取模板文件列表
        
        Returns:
            List[str]: 模板文件路径列表
        """
        return self.get_config("templates.files", [])
    
    # ========== 输出目录管理 ==========
    
    def set_output_directory(self, directory: PathLike) -> bool:
        """
        设置输出目录
        
        Args:
            directory: 输出目录路径
            
        Returns:
            bool: 是否设置成功
        """
        self.set_project_config("output.directory", str(directory))
        self._log("info", f"输出目录已设置: {directory}")
        return True
    
    def get_output_directory(self) -> str:
        """
        获取输出目录
        
        Returns:
            str: 输出目录路径
        """
        return self.get_config("output.directory", "")
    
    # ========== 工作流管理 ==========
    
    def set_workflow(self, workflow_name: str, workflow_path: PathLike = None) -> bool:
        """
        设置工作流
        
        Args:
            workflow_name: 工作流名称
            workflow_path: 工作流文件路径（可选）
            
        Returns:
            bool: 是否设置成功
        """
        self.set_project_config("workflow.name", workflow_name)
        
        if workflow_path:
            self.set_project_config("workflow.path", str(workflow_path))
        
        self._log("info", f"工作流已设置: {workflow_name}")
        return True
    
    def get_workflow(self) -> Dict[str, str]:
        """
        获取工作流配置
        
        Returns:
            Dict[str, str]: 工作流配置
        """
        return {
            "name": self.get_config("workflow.name", ""),
            "path": self.get_config("workflow.path", "")
        }
    
    # ========== 项目状态 ==========
    
    def is_project_open(self) -> bool:
        """
        检查是否有项目打开
        
        Returns:
            bool: 是否有项目打开
        """
        return self._project_path is not None
    
    def is_modified(self) -> bool:
        """
        检查项目是否被修改
        
        Returns:
            bool: 是否被修改
        """
        return self._modified
    
    def get_current_project_path(self) -> Optional[Path]:
        """
        获取当前项目路径
        
        Returns:
            Optional[Path]: 项目路径，无项目时返回None
        """
        return self._project_path
    
    def get_project_name(self) -> str:
        """
        获取项目名称
        
        Returns:
            str: 项目名称
        """
        return self.get_config("name", "未命名项目")
    
    def get_project_modified_time(self) -> Optional[datetime]:
        """
        获取项目最后修改时间
        
        Returns:
            Optional[datetime]: 修改时间
        """
        updated_at = self.get_config("updated_at")
        
        if updated_at:
            try:
                return datetime.fromisoformat(updated_at)
            except ValueError:
                pass
        
        return None