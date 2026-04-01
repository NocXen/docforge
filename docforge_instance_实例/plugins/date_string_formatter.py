"""
日期字符串格式化插件
将日期字符串转换为统一格式，支持中英文日期格式

配置格式：
{
    "Target": "example",
    "From": "YMD",
    "To": "{Y}年{M}月{D}日",
    "Error": "!!DateFormattingError!! [{str}]",
    "CustomM": {"9": "Sept"},
    "CustomD": {}
}

使用示例：
    # 在工作流中配置
    {
        "step_id": "format_date",
        "plugin_name": "date_string_formatter",
        "config": {
            "Target": "日期",
            "From": "YMD",
            "To": "{Y}年{M}月{D}日",
            "Error": "!!DateFormattingError!! [{str}]"
        }
    }

支持的To占位符：
    {str} - 原值信息
    {Y} - 四位年份（如2026）
    {YY} - 两位年份（如26）
    {M} - 数字月份（1~12）
    {MM} - 两位补零月份（01~12）
    {ensM} - 英文简写月份（Jan~Dec）
    {enwM} - 英文完整月份（January~December）
    {D} - 数字日期（1~31）
    {DD} - 两位补零日期（01~31）
    {ensD} - 英文简写日期（1st~31st）
    {enwD} - 英文完整日期（First~Thirty-one）
"""

import re
from typing import Dict, List, Any, Optional, Tuple

from .base import BasePlugin
from ..types import ExecutionResult, DataDict


class DateStringFormatter(BasePlugin):
    """
    日期字符串格式化器
    
    将日期字符串转换为统一格式，支持：
    - 多种输入格式（YMD、DMY、MDY）
    - 多种输出格式（中文、英文）
    - 自定义月份/日期名称
    - 错误处理配置
    """
    
    # 英文月份名称
    ENGLISH_MONTHS_SHORT = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
        5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
    }
    
    ENGLISH_MONTHS_FULL = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }
    
    # 英文日期后缀
    ENGLISH_DAY_SUFFIX = {
        1: "st", 2: "nd", 3: "rd", 21: "st", 22: "nd", 23: "rd", 31: "st"
    }
    
    # 英文完整日期名称
    ENGLISH_DAY_FULL = {
        1: "First", 2: "Second", 3: "Third", 4: "Fourth",
        5: "Fifth", 6: "Sixth", 7: "Seventh", 8: "Eighth",
        9: "Ninth", 10: "Tenth", 11: "Eleventh", 12: "Twelfth",
        13: "Thirteenth", 14: "Fourteenth", 15: "Fifteenth",
        16: "Sixteenth", 17: "Seventeenth", 18: "Eighteenth",
        19: "Nineteenth", 20: "Twentieth", 21: "Twenty-first",
        22: "Twenty-second", 23: "Twenty-third", 24: "Twenty-fourth",
        25: "Twenty-fifth", 26: "Twenty-sixth", 27: "Twenty-seventh",
        28: "Twenty-eighth", 29: "Twenty-ninth", 30: "Thirtieth",
        31: "Thirty-first"
    }
    
    @property
    def name(self) -> str:
        return "date_string_formatter"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def plugin_type(self) -> str:
        return "transformer"
    
    @property
    def description(self) -> str:
        return "将日期字符串转换为统一格式，支持中英文日期格式"
    
    def execute(self, **kwargs) -> ExecutionResult:
        """
        执行日期格式化
        
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
            from_format = config.get("From", "YMD").upper()
            to_format = config.get("To", "{Y}年{M}月{D}日")
            error_template = config.get("Error", "!!DateFormattingError!! [{str}]")
            custom_months = config.get("CustomM", {})
            custom_days = config.get("CustomD", {})
            
            # 验证From格式
            if from_format not in ["YMD", "DMY", "MDY"]:
                from_format = "YMD"
            
            # 记录日志
            if plugin_api:
                plugin_api.log_info(f"开始格式化日期字段: {target}")
            
            # 处理每个值
            target_values = data[target]
            formatted_values = []
            
            for value in target_values:
                formatted = self._format_date(
                    str(value),
                    from_format,
                    to_format,
                    error_template,
                    custom_months,
                    custom_days
                )
                formatted_values.append(formatted)
            
            # 创建新的数据字典
            new_data: DataDict = {}
            for key, values in data.items():
                if key == target:
                    new_data[key] = formatted_values
                else:
                    new_data[key] = values.copy()
            
            # 记录日志
            if plugin_api:
                plugin_api.log_info(f"日期格式化完成，共处理 {len(formatted_values)} 个值")
            
            return ExecutionResult(
                success=True,
                data=new_data,
                message=f"成功格式化字段 {target}"
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                errors=[f"日期格式化失败: {str(e)}"]
            )
    
    def _format_date(
        self,
        date_str: str,
        from_format: str,
        to_format: str,
        error_template: str,
        custom_months: Dict[str, str],
        custom_days: Dict[str, str]
    ) -> str:
        """
        格式化单个日期字符串
        
        Args:
            date_str: 日期字符串
            from_format: 输入格式（YMD、DMY、MDY）
            to_format: 输出格式
            error_template: 错误模板
            custom_months: 自定义月份名称
            custom_days: 自定义日期名称
            
        Returns:
            str: 格式化后的日期字符串
        """
        try:
            # 提取所有数字
            numbers = re.findall(r'\d+', date_str)
            
            # 检查数字数量
            if len(numbers) != 3:
                # 处理错误情况
                return error_template.replace("{str}", date_str)
            
            # 根据From格式解析年、月、日
            if from_format == "YMD":
                year, month, day = numbers[0], numbers[1], numbers[2]
            elif from_format == "DMY":
                day, month, year = numbers[0], numbers[1], numbers[2]
            elif from_format == "MDY":
                month, day, year = numbers[0], numbers[1], numbers[2]
            else:
                year, month, day = numbers[0], numbers[1], numbers[2]
            
            # 转换为整数
            year_int = int(year)
            month_int = int(month)
            day_int = int(day)
            
            # 验证日期有效性
            if not self._is_valid_date(year_int, month_int, day_int):
                return error_template.replace("{str}", date_str)
            
            # 格式化年份
            year_str = str(year_int).zfill(4)
            year_short = year_str[-2:]
            
            # 格式化月份
            month_str = str(month_int)
            month_padded = month_str.zfill(2)
            
            # 检查自定义月份
            if month_str in custom_months:
                month_short = custom_months[month_str]
                month_full = custom_months[month_str]
            else:
                month_short = self.ENGLISH_MONTHS_SHORT.get(month_int, month_str)
                month_full = self.ENGLISH_MONTHS_FULL.get(month_int, month_str)
            
            # 格式化日期
            day_str = str(day_int)
            day_padded = day_str.zfill(2)
            
            # 检查自定义日期
            if day_str in custom_days:
                day_suffix = custom_days[day_str]
                day_full = custom_days[day_str]
            else:
                day_suffix = self._get_day_suffix(day_int)
                day_full = self.ENGLISH_DAY_FULL.get(day_int, day_str)
            
            # 构建格式化结果
            result = to_format
            
            # 替换占位符
            result = result.replace("{Y}", year_str)
            result = result.replace("{YY}", year_short)
            result = result.replace("{M}", month_str)
            result = result.replace("{MM}", month_padded)
            result = result.replace("{ensM}", month_short)
            result = result.replace("{enwM}", month_full)
            result = result.replace("{D}", day_str)
            result = result.replace("{DD}", day_padded)
            result = result.replace("{ensD}", day_suffix)
            result = result.replace("{enwD}", day_full)
            result = result.replace("{str}", date_str)
            
            # 清理无效的括号内容
            result = self._clean_brackets(result)
            
            return result
            
        except Exception:
            return error_template.replace("{str}", date_str)
    
    def _is_valid_date(self, year: int, month: int, day: int) -> bool:
        """
        验证日期有效性
        
        Args:
            year: 年份
            month: 月份
            day: 日期
            
        Returns:
            bool: 是否有效
        """
        if month < 1 or month > 12:
            return False
        
        if day < 1 or day > 31:
            return False
        
        # 检查每月天数
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        # 闰年二月
        if month == 2 and self._is_leap_year(year):
            days_in_month[1] = 29
        
        if day > days_in_month[month - 1]:
            return False
        
        return True
    
    def _is_leap_year(self, year: int) -> bool:
        """
        判断是否为闰年
        
        Args:
            year: 年份
            
        Returns:
            bool: 是否为闰年
        """
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    
    def _get_day_suffix(self, day: int) -> str:
        """
        获取英文日期后缀
        
        Args:
            day: 日期
            
        Returns:
            str: 带后缀的日期（如1st, 2nd, 3rd）
        """
        if day in self.ENGLISH_DAY_SUFFIX:
            return f"{day}{self.ENGLISH_DAY_SUFFIX[day]}"
        elif 11 <= day <= 13:
            return f"{day}th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
            return f"{day}{suffix}"
    
    def _clean_brackets(self, text: str) -> str:
        """
        清理无效的括号内容
        
        Args:
            text: 输入文本
            
        Returns:
            str: 清理后的文本
        """
        # 处理 {{ 和 }} 转义
        text = text.replace("{{", "\x00LEFT_BRACE\x00")
        text = text.replace("}}", "\x00RIGHT_BRACE\x00")
        
        # 删除空括号或无效内容
        text = re.sub(r'\{[^}]*\}', '', text)
        
        # 恢复转义的括号
        text = text.replace("\x00LEFT_BRACE\x00", "{")
        text = text.replace("\x00RIGHT_BRACE\x00", "}")
        
        return text
    
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
        
        from_format = config.get("From", "YMD").upper()
        if from_format not in ["YMD", "DMY", "MDY"]:
            errors.append(f"不支持的From格式: {from_format}")
        
        return errors