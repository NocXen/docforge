"""
Excel数据提取器插件
从Excel文件中提取数据，支持多种格式和灵活的配置

支持格式：xlsx, xls, xlsm, xlsb, odf, ods, odt

配置格式：
{
    "PlaceHolders": [
        {
            "PlaceHolderName": "example",
            "KeepEmptyCells": "True",
            "Sheet": ["sheet1"],
            "Column": ["col:B", "colname:example"],
            "Row": [""],
            "Range": ["B2:C5"]
        }
    ]
}

注意：使用 {{ 而不是 \\{ 来转义字段语法中的 { 字符。

使用示例：
    # 在工作流中配置
    {
        "step_id": "extract",
        "plugin_name": "excel_extractor",
        "config": {
            "PlaceHolders": [
                {
                    "PlaceHolderName": "公司名称",
                    "Sheet": ["Sheet1"],
                    "Column": ["colname:公司名称"]
                }
            ]
        }
    }
"""

import re
from typing import Dict, List, Any, Optional
from pathlib import Path

import pandas as pd

from .base import BasePlugin
from ..types import ExecutionResult
from ..constants import FileExtensions


class ExcelExtractor(BasePlugin):
    """
    Excel数据提取器
    
    从Excel文件中提取数据，支持：
    - 多种格式：xlsx, xls, xlsm, xlsb, odf, ods, odt
    - 灵活的列/行选择
    - 区域选择
    - 空值处理
    """
    
    @property
    def name(self) -> str:
        return "excel_extractor"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def plugin_type(self) -> str:
        return "extractor"
    
    @property
    def description(self) -> str:
        return "从Excel文件中提取数据，支持多种格式和灵活的配置"
    
    @property
    def dependencies(self) -> List[str]:
        return ["pandas", "openpyxl", "odfpy"]
    
    def execute(self, **kwargs) -> ExecutionResult:
        """
        执行Excel数据提取
        
        Args:
            input_files: 输入文件列表
            config: 配置参数
            plugin_api: 插件API
            
        Returns:
            ExecutionResult: 执行结果
        """
        try:
            # 获取参数
            input_files = kwargs.get("input_files", [])
            config = kwargs.get("config", {})
            plugin_api = kwargs.get("plugin_api")
            
            if not input_files:
                return ExecutionResult(
                    success=False,
                    errors=["没有输入文件"]
                )
            
            if not config:
                return ExecutionResult(
                    success=False,
                    errors=["没有配置参数"]
                )
            
            # 获取PlaceHolders配置
            placeholders = config.get("PlaceHolders", [])
            
            if not placeholders:
                return ExecutionResult(
                    success=False,
                    errors=["配置中没有PlaceHolders"]
                )
            
            # 记录日志
            if plugin_api:
                plugin_api.log_info(f"开始提取Excel数据，共 {len(input_files)} 个文件")
            
            # 处理每个输入文件
            all_data = {}
            
            for input_file in input_files:
                file_path = Path(input_file)
                
                if not file_path.exists():
                    if plugin_api:
                        plugin_api.log_warning(f"文件不存在: {input_file}")
                    continue
                
                # 检查文件格式
                if file_path.suffix.lower() not in FileExtensions.EXCEL:
                    if plugin_api:
                        plugin_api.log_warning(f"不支持的文件格式: {file_path.suffix}")
                    continue
                
                # 提取数据
                file_data = self._extract_from_file(file_path, placeholders, plugin_api)
                
                # 合并数据
                for key, values in file_data.items():
                    if key in all_data:
                        # 字段名重复时，追加到后面
                        all_data[key].extend(values)
                    else:
                        all_data[key] = values
            
            if not all_data:
                return ExecutionResult(
                    success=False,
                    errors=["未能提取到任何数据"]
                )
            
            # 记录日志
            if plugin_api:
                plugin_api.log_info(f"提取完成，共 {len(all_data)} 个字段")
            
            return ExecutionResult(
                success=True,
                data=all_data
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                errors=[f"提取失败: {str(e)}"]
            )
    
    def _extract_from_file(
        self,
        file_path: Path,
        placeholders: List[Dict[str, Any]],
        plugin_api=None
    ) -> Dict[str, List[str]]:
        """
        从单个Excel文件提取数据
        
        Args:
            file_path: 文件路径
            placeholders: PlaceHolders配置
            plugin_api: 插件API
            
        Returns:
            Dict[str, List[str]]: 提取的数据
        """
        result = {}
        
        try:
            # 读取Excel文件（获取所有sheet名称）
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            if plugin_api:
                plugin_api.log_debug(f"文件 {file_path.name} 包含 {len(sheet_names)} 个工作表")
            
            # 处理每个PlaceHolder
            for placeholder in placeholders:
                # 获取配置
                name = placeholder.get("PlaceHolderName", "")
                keep_empty = placeholder.get("KeepEmptyCells", "False").lower() == "true"
                sheets = placeholder.get("Sheet", [])
                columns = placeholder.get("Column", [])
                rows = placeholder.get("Row", [])
                ranges = placeholder.get("Range", [])
                
                if not name:
                    if plugin_api:
                        plugin_api.log_warning("PlaceHolder缺少PlaceHolderName")
                    continue
                
                # 确定要处理的工作表
                target_sheets = self._get_target_sheets(sheet_names, sheets)
                
                # 处理每个工作表
                for sheet_name in target_sheets:
                    try:
                        # 读取工作表（将第一行作为列标题）
                        df = pd.read_excel(file_path, sheet_name=sheet_name)
                        
                        # 应用过滤规则
                        filtered_df = self._apply_filters(df, columns, rows, ranges)
                        
                        # 提取数据（传入columns配置用于判断是否需要添加标题）
                        extracted = self._extract_data(filtered_df, keep_empty, columns)
                        
                        # 合并到结果
                        if name in result:
                            result[name].extend(extracted)
                        else:
                            result[name] = extracted
                        
                        if plugin_api:
                            plugin_api.log_debug(f"从工作表 {sheet_name} 提取了 {len(extracted)} 个值")
                            
                    except Exception as e:
                        if plugin_api:
                            plugin_api.log_warning(f"处理工作表 {sheet_name} 失败: {e}")
                        continue
            
        except Exception as e:
            if plugin_api:
                plugin_api.log_error(f"读取文件失败: {e}")
        
        return result
    
    def _get_target_sheets(
        self,
        sheet_names: List[str],
        sheet_config: List[str]
    ) -> List[str]:
        """
        获取目标工作表
        
        Args:
            sheet_names: 所有工作表名称
            sheet_config: 工作表配置
            
        Returns:
            List[str]: 目标工作表列表
        """
        # 如果配置为空或包含空字符串，返回所有工作表
        if not sheet_config or "" in sheet_config:
            return sheet_names
        
        # 过滤出存在的工作表
        target = []
        for sheet in sheet_config:
            if sheet in sheet_names:
                target.append(sheet)
        
        return target if target else sheet_names
    
    def _apply_filters(
        self,
        df: pd.DataFrame,
        columns: List[str],
        rows: List[str],
        ranges: List[str]
    ) -> pd.DataFrame:
        """
        应用过滤规则
        
        过滤顺序：Range > Column > Row
        
        Args:
            df: 原始数据
            columns: 列配置
            rows: 行配置
            ranges: 区域配置
            
        Returns:
            pd.DataFrame: 过滤后的数据
        """
        result = df.copy()
        
        # 应用Range过滤（优先级最高）
        if ranges and "" not in ranges:
            result = self._apply_range_filter(result, ranges[0])
        
        # 应用Column过滤
        if columns and "" not in columns:
            result = self._apply_column_filter(result, columns)
        
        # 应用Row过滤
        if rows and "" not in rows:
            result = self._apply_row_filter(result, rows)
        
        return result
    
    def _apply_range_filter(self, df: pd.DataFrame, range_str: str) -> pd.DataFrame:
        """
        应用区域过滤
        
        Args:
            df: 数据
            range_str: 区域字符串，如 "B2:C5"
            
        Returns:
            pd.DataFrame: 过滤后的数据
        """
        try:
            # 解析区域
            match = re.match(r'^([A-Z]+)(\d+):([A-Z]+)(\d+)$', range_str.upper())
            if not match:
                return df
            
            start_col, start_row, end_col, end_row = match.groups()
            
            # 转换列名为索引
            start_col_idx = self._column_letter_to_index(start_col)
            end_col_idx = self._column_letter_to_index(end_col)
            
            start_row_idx = int(start_row) - 1  # 转为0-based索引
            end_row_idx = int(end_row) - 1
            
            # 应用切片
            return df.iloc[start_row_idx:end_row_idx + 1, start_col_idx:end_col_idx + 1]
            
        except Exception:
            return df
    
    def _apply_column_filter(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        应用列过滤
        
        Args:
            df: 数据
            columns: 列配置，如 ["col:B", "colname:公司名称"]
            
        Returns:
            pd.DataFrame: 过滤后的数据
        """
        selected_columns = []
        
        for col_config in columns:
            if col_config.startswith("col:"):
                # 按列号选择
                col_ref = col_config[4:]
                try:
                    col_idx = self._column_letter_to_index(col_ref)
                    if 0 <= col_idx < len(df.columns):
                        selected_columns.append(df.columns[col_idx])
                except:
                    pass
                    
            elif col_config.startswith("colname:"):
                # 按列标题选择
                col_name = col_config[8:]
                if col_name in df.columns:
                    selected_columns.append(col_name)
        
        if selected_columns:
            return df[selected_columns]
        return df
    
    def _apply_row_filter(self, df: pd.DataFrame, rows: List[str]) -> pd.DataFrame:
        """
        应用行过滤
        
        Args:
            df: 数据
            rows: 行配置，如 ["row:2", "rowname:标题"]
            
        Returns:
            pd.DataFrame: 过滤后的数据
        """
        selected_rows = []
        
        for row_config in rows:
            if row_config.startswith("row:"):
                # 按行号选择
                row_ref = row_config[4:]
                try:
                    row_idx = int(row_ref) - 1  # 转为0-based索引
                    if 0 <= row_idx < len(df):
                        selected_rows.append(row_idx)
                except:
                    pass
                    
            elif row_config.startswith("rowname:"):
                # 按行标题选择（在第一列中查找）
                row_name = row_config[8:]
                for idx, value in enumerate(df.iloc[:, 0]):
                    if str(value) == row_name:
                        selected_rows.append(idx)
                        break
        
        if selected_rows:
            return df.iloc[selected_rows]
        return df
    
    def _extract_data(self, df: pd.DataFrame, keep_empty: bool, columns: List[str] = None) -> List[str]:
        """
        提取数据为字符串列表
        
        Args:
            df: 数据
            keep_empty: 是否保留空值
            columns: 列配置（用于判断是否需要添加标题）
            
        Returns:
            List[str]: 提取的值列表
        """
        values = []
        
        # 检查是否使用col:格式（按列号选择）
        use_col_format = False
        if columns:
            for col_config in columns:
                if col_config.startswith("col:"):
                    use_col_format = True
                    break
        
        # 如果使用col:格式，添加列标题作为每列第一个值
        if use_col_format and len(df) > 0:
            for col_idx in range(len(df.columns)):
                # 获取列标题（第一行）
                header_value = df.iloc[0, col_idx] if len(df) > 0 else None
                
                if not pd.isna(header_value) and str(header_value).strip():
                    values.append(str(header_value).strip())
        
        # 按列提取数据（确保所有列行数相同）
        max_rows = len(df)
        
        if keep_empty:
            # 保留空值：按列遍历，每列都提取到最大行数
            for col_idx in range(len(df.columns)):
                for row_idx in range(max_rows):
                    if row_idx < len(df):
                        value = df.iloc[row_idx, col_idx]
                        
                        if pd.isna(value) or str(value).strip() == "":
                            values.append("")
                        else:
                            values.append(str(value).strip())
                    else:
                        # 超出实际行数，填充空值
                        values.append("")
        else:
            # 不保留空值：只提取非空值
            for col_idx in range(len(df.columns)):
                for row_idx in range(max_rows):
                    if row_idx < len(df):
                        value = df.iloc[row_idx, col_idx]
                        
                        if not pd.isna(value) and str(value).strip():
                            values.append(str(value).strip())
        
        return values
    
    def _column_letter_to_index(self, column_letter: str) -> int:
        """
        将列字母转换为索引
        
        Args:
            column_letter: 列字母，如 "A", "B", "AA"
            
        Returns:
            int: 列索引（0-based）
        """
        result = 0
        for char in column_letter.upper():
            result = result * 26 + (ord(char) - ord('A') + 1)
        return result - 1  # 转为0-based
    
    def cleanup(self) -> None:
        """
        清理资源
        
        在插件卸载或重新加载前调用，用于释放资源。
        Excel提取器没有需要清理的资源。
        """
        pass
