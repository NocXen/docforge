"""
Word文档合并插件
将多个Word文档合并为一个文件

支持格式：.docx

配置格式：
{
    "Target": ["*.docx"],
    "Ignore": ["temp.docx"],
    "SortBy": "number",  // number: 按文件名数字排序, name: 按文件名排序, time: 按修改时间排序
    "SortOrder": "asc",  // asc: 升序, desc: 降序
    "PageBreak": true,   // 是否在每个文档前添加分页符
    "CombineBy": "prefix" // prefix: 按前缀分组合并, all: 合并所有文件
}

使用示例：
    # 在工作流中配置
    {
        "step_id": "combine",
        "plugin_name": "docx_combiner",
        "config": {
            "Target": ["院审批单*.docx"],
            "SortBy": "number",
            "PageBreak": true,
            "CombineBy": "prefix"
        }
    }
"""

import re
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from docx import Document
from docxcompose.composer import Composer

from .base import BasePlugin
from ..types import ExecutionResult
from ..constants import FileExtensions


class DocxCombiner(BasePlugin):
    """
    Word文档合并插件
    
    将多个Word文档合并为一个文件
    支持：
    - 按文件名数字排序
    - 按前缀分组合并
    - 自动添加分页符
    - 文件名匹配过滤
    """
    
    def __init__(self):
        super().__init__()
    
    @property
    def name(self) -> str:
        return "docx_combiner"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def plugin_type(self) -> str:
        return "post_processor"
    
    @property
    def description(self) -> str:
        return "将多个Word文档合并为一个文件"
    
    @property
    def dependencies(self) -> List[str]:
        return ["python-docx", "docxcompose"]
    
    def execute(self, **kwargs) -> ExecutionResult:
        """
        执行Word文档合并
        
        Args:
            input_files: 输入文件列表（待合并的docx文件）
            output_dir: 输出目录
            config: 配置参数
            plugin_api: 插件API
            
        Returns:
            ExecutionResult: 执行结果
        """
        try:
            # 获取参数
            input_files = kwargs.get("input_files", [])
            output_dir = kwargs.get("output_dir", "")
            config = kwargs.get("config", {})
            plugin_api = kwargs.get("plugin_api")
            
            if not output_dir:
                return ExecutionResult(
                    success=False,
                    errors=["未设置输出目录"]
                )
            
            # 获取配置
            target = config.get("Target", [])
            ignore = config.get("Ignore", [])
            sort_by = config.get("SortBy", "number")  # number, name, time
            sort_order = config.get("SortOrder", "asc")  # asc, desc
            page_break = config.get("PageBreak", True)
            combine_by = config.get("CombineBy", "prefix")  # prefix, all
            
            # 从output_dir中查找所有docx文件
            output_dir_path = Path(output_dir)
            if not output_dir_path.exists():
                return ExecutionResult(
                    success=False,
                    errors=[f"输出目录不存在: {output_dir}"]
                )
            
            # 查找所有docx文件
            all_docx_files = list(output_dir_path.glob("*.docx"))
            
            if not all_docx_files:
                return ExecutionResult(
                    success=False,
                    errors=["输出目录中没有docx文件"]
                )
            
            # 转换为字符串列表
            all_docx_files_str = [str(f) for f in all_docx_files]
            
            # 过滤文件（只保留docx文件）
            filtered_files = self._filter_files(all_docx_files_str, target, ignore, plugin_api)
            
            if not filtered_files:
                return ExecutionResult(
                    success=False,
                    errors=["没有需要合并的docx文件"]
                )
            
            # 记录日志
            if plugin_api:
                plugin_api.log_info(f"开始合并Word文档，共 {len(filtered_files)} 个文件")
            
            # 根据合并方式处理
            if combine_by == "prefix":
                # 按前缀分组合并
                output_files = self._combine_by_prefix(
                    filtered_files,
                    output_dir,
                    sort_by,
                    sort_order,
                    page_break,
                    plugin_api
                )
            else:
                # 合并所有文件
                output_files = self._combine_all(
                    filtered_files,
                    output_dir,
                    sort_by,
                    sort_order,
                    page_break,
                    plugin_api
                )
            
            if not output_files:
                return ExecutionResult(
                    success=False,
                    errors=["未能生成任何合并文件"]
                )
            
            # 记录日志
            if plugin_api:
                plugin_api.log_info(f"合并完成，生成 {len(output_files)} 个文件")
            
            return ExecutionResult(
                success=True,
                output_files=output_files
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                errors=[f"合并失败: {str(e)}"]
            )
    
    def _filter_files(
        self,
        input_files: List[str],
        target: List[str],
        ignore: List[str],
        plugin_api=None
    ) -> List[str]:
        """
        过滤文件
        
        Args:
            input_files: 所有输入文件
            target: 正选列表（只选择这些）
            ignore: 反选列表（不选择这些）
            plugin_api: 插件API
            
        Returns:
            List[str]: 过滤后的文件
        """
        result = []
        
        for file_path in input_files:
            file_path = Path(file_path)
            
            # 检查文件是否存在
            if not file_path.exists():
                if plugin_api:
                    plugin_api.log_warning(f"文件不存在，跳过: {file_path}")
                continue
            
            # 检查文件扩展名
            if file_path.suffix.lower() != '.docx':
                continue
            
            filename = file_path.name
            
            # 检查是否应该忽略
            if ignore:
                should_ignore = False
                for ignore_pattern in ignore:
                    if self._match_pattern(filename, ignore_pattern):
                        should_ignore = True
                        break
                if should_ignore:
                    continue
            
            # 检查是否应该选择
            if target:
                should_include = False
                for target_pattern in target:
                    if self._match_pattern(filename, target_pattern):
                        should_include = True
                        break
                if not should_include:
                    continue
            
            result.append(str(file_path))
        
        return result
    
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """
        匹配文件名和模式
        
        支持：
        - 精确匹配
        - 通配符匹配（*）
        
        Args:
            filename: 文件名
            pattern: 匹配模式
            
        Returns:
            bool: 是否匹配
        """
        # 精确匹配
        if filename == pattern:
            return True
        
        # 通配符匹配
        if "*" in pattern:
            regex_pattern = pattern.replace("*", ".*")
            return bool(re.match(regex_pattern, filename))
        
        return False
    
    def _extract_prefix(self, filename: str) -> str:
        """
        从文件名中提取前缀（去除数字后缀和扩展名）
        
        Args:
            filename: 文件名
            
        Returns:
            str: 前缀
        """
        # 去除扩展名
        name = Path(filename).stem
        
        # 去除末尾的数字后缀（如 _1, _2, _output_1 等）
        # 匹配模式：_数字 或 _output_数字
        prefix = re.sub(r'(_output)?_\d+$', '', name)
        
        return prefix
    
    def _extract_numbers(self, filename: str) -> tuple:
        """
        从文件名中提取数字部分用于排序
        
        Args:
            filename: 文件名
            
        Returns:
            tuple: 数字元组
        """
        # 使用正则表达式匹配文件名中的数字
        numbers = re.findall(r'(\d+)', str(filename))
        if numbers:
            # 将字符串数字转换为整数
            return tuple(int(num) for num in numbers)
        else:
            return (0,)
    
    def _sort_files(
        self,
        files: List[str],
        sort_by: str,
        sort_order: str
    ) -> List[str]:
        """
        对文件进行排序
        
        Args:
            files: 文件列表
            sort_by: 排序方式 (number, name, time)
            sort_order: 排序顺序 (asc, desc)
            
        Returns:
            List[str]: 排序后的文件列表
        """
        if sort_by == "number":
            # 按文件名中的数字排序
            sorted_files = sorted(files, key=lambda f: self._extract_numbers(Path(f).name))
        elif sort_by == "time":
            # 按修改时间排序
            sorted_files = sorted(files, key=lambda f: os.path.getmtime(f))
        else:
            # 按文件名排序
            sorted_files = sorted(files, key=lambda f: Path(f).name)
        
        # 如果是降序，反转列表
        if sort_order == "desc":
            sorted_files = sorted_files[::-1]
        
        return sorted_files
    
    def _combine_by_prefix(
        self,
        files: List[str],
        output_dir: str,
        sort_by: str,
        sort_order: str,
        page_break: bool,
        plugin_api=None
    ) -> List[str]:
        """
        按前缀分组合并文件
        
        Args:
            files: 文件列表
            output_dir: 输出目录
            sort_by: 排序方式
            sort_order: 排序顺序
            page_break: 是否添加分页符
            plugin_api: 插件API
            
        Returns:
            List[str]: 输出文件列表
        """
        # 按前缀分组
        prefix_groups = {}
        for file_path in files:
            filename = Path(file_path).name
            prefix = self._extract_prefix(filename)
            
            if prefix not in prefix_groups:
                prefix_groups[prefix] = []
            prefix_groups[prefix].append(file_path)
        
        # 合并每个分组
        output_files = []
        for prefix, group_files in prefix_groups.items():
            # 对组内文件排序
            sorted_files = self._sort_files(group_files, sort_by, sort_order)
            
            # 合并文件
            output_path = Path(output_dir) / f"{prefix}_Combined.docx"
            success = self._merge_documents(sorted_files, output_path, page_break, plugin_api)
            
            if success:
                output_files.append(str(output_path))
        
        return output_files
    
    def _combine_all(
        self,
        files: List[str],
        output_dir: str,
        sort_by: str,
        sort_order: str,
        page_break: bool,
        plugin_api=None
    ) -> List[str]:
        """
        合并所有文件
        
        Args:
            files: 文件列表
            output_dir: 输出目录
            sort_by: 排序方式
            sort_order: 排序顺序
            page_break: 是否添加分页符
            plugin_api: 插件API
            
        Returns:
            List[str]: 输出文件列表
        """
        # 对文件排序
        sorted_files = self._sort_files(files, sort_by, sort_order)
        
        # 合并文件
        output_path = Path(output_dir) / "Combined.docx"
        success = self._merge_documents(sorted_files, output_path, page_break, plugin_api)
        
        if success:
            return [str(output_path)]
        else:
            return []
    
    def _merge_documents(
        self,
        files: List[str],
        output_path: Path,
        page_break: bool,
        plugin_api=None
    ) -> bool:
        """
        合并文档
        
        Args:
            files: 文件列表
            output_path: 输出路径
            page_break: 是否添加分页符
            plugin_api: 插件API
            
        Returns:
            bool: 是否成功
        """
        try:
            if not files:
                if plugin_api:
                    plugin_api.log_warning("没有找到要合并的文件")
                return False
            
            # 创建主文档
            master = Document(files[0])
            if plugin_api:
                plugin_api.log_info(f"已合并: {Path(files[0]).name}")
            
            composer = Composer(master)
            
            # 追加其他文档
            for file_path in files[1:]:
                try:
                    # 打开源文档
                    doc = Document(file_path)
                    
                    # 在追加新文档前，先给当前文档添加分页符
                    if page_break:
                        composer.doc.add_page_break()
                    
                    # 追加文档
                    composer.append(doc)
                    if plugin_api:
                        plugin_api.log_info(f"已合并: {Path(file_path).name}")
                    
                except Exception as e:
                    if plugin_api:
                        plugin_api.log_error(f"处理文件 {file_path} 时出错: {e}")
                    continue
            
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存合并后的文档
            composer.save(output_path)
            
            if plugin_api:
                plugin_api.log_info(f"合并完成，保存为: {output_path.name}")
            
            return True
            
        except Exception as e:
            if plugin_api:
                plugin_api.log_error(f"合并文档失败: {e}")
            return False
    
    def cleanup(self) -> None:
        """
        清理资源
        
        在插件卸载或重新加载前调用，用于释放资源。
        Word合并器没有需要清理的资源。
        """
        pass