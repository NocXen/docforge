"""
占位符分割器插件
将一个字段分割为多个新字段，支持灵活的配置

配置格式：
{
    "Target": "example",
    "Digits": "2",
    "SeparateCharacter": ".",
    "KeepOriginal": "True"
}

使用示例：
    # 在工作流中配置
    {
        "step_id": "split",
        "plugin_name": "placeholder_splitter",
        "config": {
            "Target": "example",
            "Digits": "2",
            "SeparateCharacter": ".",
            "KeepOriginal": "True"
        }
    }

效果示例：
    输入: {"example": ["草莓", "牛奶", "蛋糕"]}
    输出: {"example.01": ["草莓", "草莓", "草莓"], 
           "example.02": ["牛奶", "牛奶", "牛奶"], 
           "example.03": ["蛋糕", "蛋糕", "蛋糕"]}
"""

from typing import Dict, List, Any, Optional

from .base import BasePlugin
from ..types import ExecutionResult, DataDict


class PlaceholderSplitter(BasePlugin):
    """
    占位符分割器
    
    将一个字段分割为多个新字段，主要用于一表制多表的场景。
    
    功能特点：
    - 支持自定义分隔符
    - 支持数字补零（Digits参数）
    - 可选择是否保留原字段
    """
    
    @property
    def name(self) -> str:
        return "placeholder_splitter"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def plugin_type(self) -> str:
        return "transformer"
    
    @property
    def description(self) -> str:
        return "将一个字段分割为多个新字段，支持灵活的配置"
    
    def execute(self, **kwargs) -> ExecutionResult:
        """
        执行占位符分割
        
        Args:
            data: 输入数据（来自上一步插件）
            config: 配置参数
            plugin_api: 插件API
            
        Returns:
            ExecutionResult: 执行结果
        """
        try:
            # 获取参数
            data = kwargs.get("data", {})
            config = kwargs.get("config", {})
            plugin_api = kwargs.get("plugin_api")
            
            if not data:
                return ExecutionResult(
                    success=False,
                    errors=["没有输入数据"]
                )
            
            # 获取配置参数
            target = config.get("Target", "")
            
            # 如果没有指定Target，跳过执行
            if not target:
                if plugin_api:
                    plugin_api.log_info("未指定Target参数，跳过执行")
                return ExecutionResult(
                    success=True,
                    data=data,
                    message="未指定Target参数，跳过执行"
                )
            
            # 检查目标字段是否存在
            if target not in data:
                return ExecutionResult(
                    success=False,
                    errors=[f"目标字段不存在: {target}"]
                )
            
            # 获取其他配置参数
            digits = config.get("Digits", "")
            separate_char = config.get("SeparateCharacter", ".")
            keep_original = config.get("KeepOriginal", "True").lower() == "true"
            
            # 记录日志
            if plugin_api:
                plugin_api.log_info(f"开始分割字段: {target}")
            
            # 获取目标字段的值列表
            target_values = data[target]
            
            # 计算分割数量
            split_count = len(target_values)
            
            if split_count == 0:
                return ExecutionResult(
                    success=False,
                    errors=[f"目标字段为空: {target}"]
                )
            
            # 计算数字宽度
            if digits and digits.isdigit():
                width = int(digits)
            else:
                # 自动计算宽度
                width = len(str(split_count))
            
            # 创建新的数据字典
            new_data: DataDict = {}
            
            # 如果保留原字段，复制原字段
            if keep_original:
                new_data[target] = target_values.copy()
            
            # 为每个值创建新字段
            for idx, value in enumerate(target_values, start=1):
                # 生成带补零的索引
                padded_idx = str(idx).zfill(width)
                
                # 生成新字段名
                new_field_name = f"{target}{separate_char}{padded_idx}"
                
                # 创建新字段的值列表（每个位置都是该值）
                new_data[new_field_name] = [value] * split_count
            
            # 记录日志
            if plugin_api:
                plugin_api.log_info(f"分割完成，生成 {split_count} 个新字段")
            
            return ExecutionResult(
                success=True,
                data=new_data,
                message=f"成功分割字段 {target} 为 {split_count} 个新字段"
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                errors=[f"分割失败: {str(e)}"]
            )
    
    def cleanup(self) -> None:
        """清理资源"""
        pass
    
    def validate_input(self, **kwargs) -> List[str]:
        """
        验证输入参数
        
        Args:
            **kwargs: 输入参数
            
        Returns:
            List[str]: 错误列表
        """
        errors = []
        
        data = kwargs.get("data", {})
        config = kwargs.get("config", {})
        
        if not data:
            errors.append("缺少输入数据")
        
        target = config.get("Target", "")
        if target and target not in data:
            errors.append(f"目标字段不存在: {target}")
        
        digits = config.get("Digits", "")
        if digits and not digits.isdigit():
            errors.append(f"Digits参数必须是数字: {digits}")
        
        return errors