"""
工作流引擎服务
负责解析、调度和执行工作流

使用示例：
    from docforge.services.workflow_engine import WorkflowEngine
    from docforge.services.plugin_manager import PluginManager
    from docforge.services.logger import Logger
    
    logger = Logger()
    plugin_manager = PluginManager(logger)
    workflow_engine = WorkflowEngine(plugin_manager, logger)
    
    # 加载工作流
    workflow = workflow_engine.load_workflow("my_workflow.json")
    
    # 执行工作流
    result = workflow_engine.execute(
        workflow=workflow,
        input_files=["data.xlsx"],
        template_files=["template.docx"],
        output_dir="./output"
    )
"""

import json
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from ..types import (
    WorkflowDefinition,
    WorkflowStep,
    ExecutionResult,
    ProgressCallback,
    JsonDict,
    PathLike
)
from ..constants import WorkflowStatus
from ..exceptions import (
    WorkflowDefinitionError,
    WorkflowExecuteError,
    WorkflowCancelledError
)


class WorkflowEngine:
    """
    工作流引擎
    
    管理工作流的整个生命周期
    
    Attributes:
        plugin_manager: 插件管理器实例
        logger: 日志器实例
    """
    
    def __init__(self, plugin_manager, logger=None):
        """
        初始化工作流引擎
        
        Args:
            plugin_manager: 插件管理器实例
            logger: 日志器实例（可选）
        """
        self.plugin_manager = plugin_manager
        self.logger = logger
        
        self._status: WorkflowStatus = WorkflowStatus.IDLE
        self._current_step: int = -1
        self._execution_history: List[Dict[str, Any]] = []
        self._cancel_requested: bool = False
        self._pause_requested: bool = False
    
    def _log(self, level: str, message: str, **kwargs) -> None:
        """记录日志"""
        if self.logger:
            getattr(self.logger, level)(message, **kwargs)
    
    # ========== 工作流定义管理 ==========
    
    def load_workflow(self, workflow_path: PathLike) -> WorkflowDefinition:
        """
        从文件加载工作流定义
        
        Args:
            workflow_path: 工作流文件路径（JSON/YAML）
            
        Returns:
            WorkflowDefinition: 工作流定义对象
            
        Raises:
            WorkflowDefinitionError: 工作流定义格式错误
        """
        path = Path(workflow_path)
        
        if not path.exists():
            raise WorkflowDefinitionError(f"工作流文件不存在: {path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            workflow = WorkflowDefinition.from_dict(data)
            
            self._log("info", f"工作流已加载: {workflow.name}")
            return workflow
            
        except json.JSONDecodeError as e:
            raise WorkflowDefinitionError(f"工作流文件格式错误: {path}", str(e))
        except Exception as e:
            raise WorkflowDefinitionError(f"加载工作流失败: {path}", str(e))
    
    def save_workflow(self, workflow: WorkflowDefinition, path: PathLike) -> bool:
        """
        保存工作流定义到文件
        
        Args:
            workflow: 工作流定义对象
            path: 保存路径
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 更新修改时间
            workflow.updated_at = datetime.now()
            
            # 保存
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(workflow.to_dict(), f, indent=2, ensure_ascii=False)
            
            self._log("info", f"工作流已保存: {file_path}")
            return True
            
        except Exception as e:
            self._log("error", f"保存工作流失败: {e}")
            return False
    
    def validate_workflow(self, workflow: WorkflowDefinition) -> List[str]:
        """
        验证工作流定义的有效性
        
        Args:
            workflow: 工作流定义对象
            
        Returns:
            List[str]: 错误列表，空列表表示验证通过
        """
        errors = []
        
        # 检查名称
        if not workflow.name:
            errors.append("工作流名称为空")
        
        # 检查步骤
        if not workflow.steps:
            errors.append("工作流没有步骤")
        
        # 检查每个步骤
        for i, step in enumerate(workflow.steps):
            if not step.step_id:
                errors.append(f"步骤 {i+1} 没有ID")
            
            if not step.plugin_name:
                errors.append(f"步骤 {i+1} 没有指定插件")
            else:
                # 检查插件是否存在
                plugin = self.plugin_manager.get_plugin(step.plugin_name)
                if plugin is None:
                    errors.append(f"步骤 {i+1} 引用的插件不存在: {step.plugin_name}")
        
        return errors
    
    # ========== 工作流执行控制 ==========
    
    def execute(
        self,
        workflow: WorkflowDefinition,
        input_files: List[PathLike],
        template_files: List[PathLike],
        output_dir: PathLike,
        progress_callback: Optional[ProgressCallback] = None
    ) -> ExecutionResult:
        """
        执行工作流
        
        Args:
            workflow: 工作流定义
            input_files: 输入文件列表
            template_files: 模板文件列表
            output_dir: 输出目录
            progress_callback: 进度回调函数
            
        Returns:
            ExecutionResult: 执行结果
        """
        start_time = time.time()
        
        # 验证工作流
        errors = self.validate_workflow(workflow)
        if errors:
            return ExecutionResult(
                success=False,
                errors=errors,
                message="工作流验证失败"
            )
        
        # 初始化状态
        self._status = WorkflowStatus.RUNNING
        self._current_step = 0
        self._cancel_requested = False
        self._pause_requested = False
        
        # 执行结果
        result = ExecutionResult(success=True)
        current_data = None
        
        try:
            self._log("info", f"开始执行工作流: {workflow.name}")
            
            # 通知开始
            if progress_callback:
                progress_callback(0.0, f"开始执行工作流: {workflow.name}")
            
            # 执行每个步骤
            for i, step in enumerate(workflow.steps):
                # 检查是否启用
                if not step.enabled:
                    self._log("info", f"跳过已禁用的步骤: {step.step_id}")
                    continue
                
                self._current_step = i
                
                # 检查取消
                if self._cancel_requested:
                    self._status = WorkflowStatus.CANCELLED
                    raise WorkflowCancelledError("工作流已取消")
                
                # 检查暂停
                while self._pause_requested:
                    self._status = WorkflowStatus.PAUSED
                    time.sleep(0.1)
                    if self._cancel_requested:
                        raise WorkflowCancelledError("工作流已取消")
                
                self._status = WorkflowStatus.RUNNING
                
                # 计算进度
                progress = (i + 1) / len(workflow.steps)
                message = f"执行步骤 {i+1}/{len(workflow.steps)}: {step.step_id}"
                
                # 通知进度
                if progress_callback:
                    progress_callback(progress, message)
                
                self._log("info", message)
                
                # 执行步骤
                step_result = self._execute_step(
                    step=step,
                    input_files=input_files,
                    template_files=template_files,
                    output_dir=output_dir,
                    previous_data=current_data
                )
                
                # 记录历史
                self._execution_history.append({
                    "step_id": step.step_id,
                    "success": step_result.success,
                    "execution_time": step_result.execution_time,
                    "timestamp": datetime.now().isoformat()
                })
                
                # 合并结果
                if step_result.has_errors():
                    result.errors.extend(step_result.errors)
                    result.success = False
                    self._log("error", f"步骤执行失败: {step_result.errors}")
                    break
                
                if step_result.has_warnings():
                    result.warnings.extend(step_result.warnings)
                
                # 合并输出文件
                result.output_files.extend(step_result.output_files)
                
                # 传递数据到下一步
                if step_result.data:
                    current_data = step_result.data
            
            # 完成
            if result.success:
                self._status = WorkflowStatus.COMPLETED
                result.message = "工作流执行完成"
                
                if progress_callback:
                    progress_callback(1.0, "工作流执行完成")
                
                self._log("info", f"工作流执行完成，生成 {len(result.output_files)} 个文件")
            else:
                self._status = WorkflowStatus.FAILED
                result.message = "工作流执行失败"
                self._log("error", "工作流执行失败")
            
        except WorkflowCancelledError:
            self._status = WorkflowStatus.CANCELLED
            result.success = False
            result.message = "工作流已取消"
            self._log("warning", "工作流已取消")
            
        except Exception as e:
            self._status = WorkflowStatus.FAILED
            result.success = False
            result.errors.append(str(e))
            result.message = f"工作流执行异常: {e}"
            self._log("error", f"工作流执行异常: {e}")
        
        finally:
            # 计算总执行时间
            result.execution_time = time.time() - start_time
            self._current_step = -1
        
        return result
    
    def _execute_step(
        self,
        step: WorkflowStep,
        input_files: List[PathLike],
        template_files: List[PathLike],
        output_dir: PathLike,
        previous_data: Optional[Dict[str, List[str]]] = None
    ) -> ExecutionResult:
        """
        执行单个工作流步骤
        
        Args:
            step: 工作流步骤
            input_files: 输入文件列表
            template_files: 模板文件列表
            output_dir: 输出目录
            previous_data: 上一步的数据
            
        Returns:
            ExecutionResult: 执行结果
        """
        start_time = time.time()
        
        try:
            # 获取插件
            plugin = self.plugin_manager.get_plugin(step.plugin_name)
            
            if plugin is None:
                return ExecutionResult(
                    success=False,
                    errors=[f"插件不存在: {step.plugin_name}"]
                )
            
            # 准备参数
            kwargs = {
                "input_files": [str(f) for f in input_files],
                "template_files": [str(f) for f in template_files],
                "output_dir": str(output_dir),
                "config": step.config  # 将config作为完整对象传递，而不是展开
            }
            
            # 如果有上一步的数据，传递给插件
            if previous_data:
                kwargs["data"] = previous_data
            
            # 执行插件
            result = plugin.execute(**kwargs)
            
            # 计算执行时间
            result.execution_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                errors=[f"步骤执行异常: {str(e)}"],
                execution_time=time.time() - start_time
            )
    
    def pause(self) -> bool:
        """
        暂停当前执行的工作流
        
        Returns:
            bool: 是否成功暂停
        """
        if self._status != WorkflowStatus.RUNNING:
            self._log("warning", "工作流未在运行")
            return False
        
        self._pause_requested = True
        self._log("info", "工作流暂停请求已发送")
        return True
    
    def resume(self) -> bool:
        """
        恢复暂停的工作流
        
        Returns:
            bool: 是否成功恢复
        """
        if self._status != WorkflowStatus.PAUSED:
            self._log("warning", "工作流未在暂停")
            return False
        
        self._pause_requested = False
        self._log("info", "工作流已恢复")
        return True
    
    def cancel(self) -> bool:
        """
        取消当前执行的工作流
        
        Returns:
            bool: 是否成功取消
        """
        if self._status not in [WorkflowStatus.RUNNING, WorkflowStatus.PAUSED]:
            self._log("warning", "工作流未在运行")
            return False
        
        self._cancel_requested = True
        self._pause_requested = False
        self._log("info", "工作流取消请求已发送")
        return True
    
    # ========== 状态查询 ==========
    
    def get_status(self) -> WorkflowStatus:
        """
        获取当前工作流状态
        
        Returns:
            WorkflowStatus: 当前状态
        """
        return self._status
    
    def get_current_step(self) -> Optional[int]:
        """
        获取当前执行步骤索引
        
        Returns:
            Optional[int]: 当前步骤索引，未执行时返回None
        """
        if self._current_step >= 0:
            return self._current_step
        return None
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """
        获取执行历史记录
        
        Returns:
            List[Dict]: 历史记录列表
        """
        return self._execution_history.copy()
    
    def is_running(self) -> bool:
        """
        检查工作流是否正在运行
        
        Returns:
            bool: 是否正在运行
        """
        return self._status == WorkflowStatus.RUNNING
    
    def is_paused(self) -> bool:
        """
        检查工作流是否暂停
        
        Returns:
            bool: 是否暂停
        """
        return self._status == WorkflowStatus.PAUSED
    
    def clear_history(self) -> None:
        """清空执行历史"""
        self._execution_history.clear()
        self._log("info", "执行历史已清空")