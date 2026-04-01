"""
数字字符串格式化插件
在中文数字、英文数字和阿拉伯数字之间进行转换

配置格式：
{
    "Target": "example",
    "From": "arabic",
    "To": "chinese",
    "Error": "!!NumberFormattingError!! [{str}]"
}

使用示例：
    # 在工作流中配置
    {
        "step_id": "format_number",
        "plugin_name": "number_string_formatter",
        "config": {
            "Target": "数量",
            "From": "arabic",
            "To": "chinese",
            "Error": "!!NumberFormattingError!! [{str}]"
        }
    }

支持的数字类型：
    - arabic: 阿拉伯数字（如1234567）
    - chinese: 中文数字（如一百二十三万四千五百六十七）
    - english: 英文数字（如one million two hundred thirty-four thousand five hundred sixty-seven）

支持范围：0 ~ 999,999,999,999（9999亿）
"""

import re
from typing import Dict, List, Any, Optional

from .base import BasePlugin
from ..types import ExecutionResult, DataDict


class NumberStringFormatter(BasePlugin):
    """
    数字字符串格式化器
    
    在中文数字、英文数字和阿拉伯数字之间进行转换。
    
    功能特点：
    - 支持阿拉伯数字转中文数字
    - 支持阿拉伯数字转英文数字
    - 支持中文数字转阿拉伯数字
    - 支持英文数字转阿拉伯数字
    - 支持大数字（最高到9999亿）
    """
    
    # 中文数字字符
    CHINESE_DIGITS = {
        '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
        '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
        '壹': 1, '贰': 2, '叁': 3, '肆': 4, '伍': 5,
        '陆': 6, '柒': 7, '捌': 8, '玖': 9
    }
    
    # 中文数字单位
    CHINESE_UNITS = {
        '十': 10, '百': 100, '千': 1000,
        '万': 10000, '亿': 100000000,
        '拾': 10, '佰': 100, '仟': 1000
    }
    
    # 阿拉伯数字转中文字符
    ARABIC_TO_CHINESE = {
        '0': '零', '1': '一', '2': '二', '3': '三', '4': '四',
        '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'
    }
    
    # 英文数字单词
    ENGLISH_ONES = [
        '', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
        'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen',
        'seventeen', 'eighteen', 'nineteen'
    ]
    
    ENGLISH_TENS = [
        '', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety'
    ]
    
    ENGLISH_UNITS = [
        '', 'thousand', 'million', 'billion'
    ]
    
    # 英文数字单词到数字的映射
    ENGLISH_WORDS = {}
    
    def __init__(self):
        """初始化"""
        super().__init__()
        self._build_english_words()
    
    def _build_english_words(self):
        """构建英文单词映射"""
        # 基础数字
        for i, word in enumerate(self.ENGLISH_ONES):
            if word:
                self.ENGLISH_WORDS[word] = i
        
        # 十位数
        for i, word in enumerate(self.ENGLISH_TENS):
            if word:
                self.ENGLISH_WORDS[word] = i * 10
        
        # 特殊组合 (21-99)
        for tens in range(2, 10):
            for ones in range(1, 10):
                word = f"{self.ENGLISH_TENS[tens]}-{self.ENGLISH_ONES[ones]}"
                self.ENGLISH_WORDS[word] = tens * 10 + ones
        
        # 单位
        self.ENGLISH_WORDS['hundred'] = 100
        self.ENGLISH_WORDS['thousand'] = 1000
        self.ENGLISH_WORDS['million'] = 1000000
        self.ENGLISH_WORDS['billion'] = 1000000000
        self.ENGLISH_WORDS['and'] = 0  # 忽略and
    
    @property
    def name(self) -> str:
        return "number_string_formatter"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def plugin_type(self) -> str:
        return "transformer"
    
    @property
    def description(self) -> str:
        return "在中文数字、英文数字和阿拉伯数字之间进行转换"
    
    def execute(self, **kwargs) -> ExecutionResult:
        """
        执行数字格式化
        
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
            from_type = config.get("From", "arabic").lower()
            to_type = config.get("To", "chinese").lower()
            error_template = config.get("Error", "!!NumberFormattingError!! [{str}]")
            
            # 验证类型
            valid_types = ["arabic", "chinese", "english"]
            if from_type not in valid_types:
                from_type = "arabic"
            if to_type not in valid_types:
                to_type = "chinese"
            
            # 记录日志
            if plugin_api:
                plugin_api.log_info(f"开始格式化数字字段: {target} ({from_type} -> {to_type})")
            
            # 处理每个值
            target_values = data[target]
            formatted_values = []
            
            for value in target_values:
                formatted = self._format_number(
                    str(value),
                    from_type,
                    to_type,
                    error_template
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
                plugin_api.log_info(f"数字格式化完成，共处理 {len(formatted_values)} 个值")
            
            return ExecutionResult(
                success=True,
                data=new_data,
                message=f"成功格式化字段 {target}"
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                errors=[f"数字格式化失败: {str(e)}"]
            )
    
    def _format_number(
        self,
        number_str: str,
        from_type: str,
        to_type: str,
        error_template: str
    ) -> str:
        """
        格式化单个数字字符串
        
        Args:
            number_str: 数字字符串
            from_type: 输入类型（arabic、chinese、english）
            to_type: 输出类型（arabic、chinese、english）
            error_template: 错误模板
            
        Returns:
            str: 格式化后的数字字符串
        """
        try:
            # 清理输入
            number_str = number_str.strip()
            
            if not number_str:
                return error_template.replace("{str}", number_str)
            
            # 如果输入输出类型相同，直接返回
            if from_type == to_type:
                return number_str
            
            # 先转换为阿拉伯数字
            arabic_number = self._to_arabic(number_str, from_type)
            
            if arabic_number is None:
                return error_template.replace("{str}", number_str)
            
            # 从阿拉伯数字转换为目标类型
            if to_type == "arabic":
                return str(arabic_number)
            elif to_type == "chinese":
                return self._arabic_to_chinese(arabic_number)
            elif to_type == "english":
                return self._arabic_to_english(arabic_number)
            else:
                return error_template.replace("{str}", number_str)
                
        except Exception:
            return error_template.replace("{str}", number_str)
    
    def _to_arabic(self, number_str: str, from_type: str) -> Optional[int]:
        """
        将数字字符串转换为阿拉伯数字
        
        Args:
            number_str: 数字字符串
            from_type: 输入类型
            
        Returns:
            Optional[int]: 阿拉伯数字，失败返回None
        """
        if from_type == "arabic":
            return self._parse_arabic(number_str)
        elif from_type == "chinese":
            return self._chinese_to_arabic(number_str)
        elif from_type == "english":
            return self._english_to_arabic(number_str)
        else:
            return None
    
    def _parse_arabic(self, number_str: str) -> Optional[int]:
        """
        解析阿拉伯数字字符串
        
        Args:
            number_str: 数字字符串
            
        Returns:
            Optional[int]: 数字，失败返回None
        """
        try:
            # 移除逗号和空格
            cleaned = number_str.replace(',', '').replace(' ', '')
            return int(cleaned)
        except ValueError:
            return None
    
    def _chinese_to_arabic(self, chinese_str: str) -> Optional[int]:
        """
        中文数字转阿拉伯数字
        
        Args:
            chinese_str: 中文数字字符串
            
        Returns:
            Optional[int]: 阿拉伯数字，失败返回None
        """
        try:
            # 移除空格
            chinese_str = chinese_str.replace(' ', '')
            
            if not chinese_str:
                return None
            
            # 处理"两"的情况
            chinese_str = chinese_str.replace('两', '二')
            
            # 分割亿和万
            result = 0
            temp = 0
            
            # 处理亿
            if '亿' in chinese_str:
                parts = chinese_str.split('亿')
                yi_part = parts[0]
                chinese_str = parts[1] if len(parts) > 1 else ''
                
                yi_value = self._parse_chinese_part(yi_part)
                if yi_value is not None:
                    result += yi_value * 100000000
            
            # 处理万
            if '万' in chinese_str:
                parts = chinese_str.split('万')
                wan_part = parts[0]
                chinese_str = parts[1] if len(parts) > 1 else ''
                
                wan_value = self._parse_chinese_part(wan_part)
                if wan_value is not None:
                    result += wan_value * 10000
            
            # 处理剩余部分
            if chinese_str:
                remaining_value = self._parse_chinese_part(chinese_str)
                if remaining_value is not None:
                    result += remaining_value
            
            return result if result > 0 or chinese_str == '零' else None
            
        except Exception:
            return None
    
    def _parse_chinese_part(self, part: str) -> Optional[int]:
        """
        解析中文数字部分（不含亿、万）
        
        Args:
            part: 中文数字部分
            
        Returns:
            Optional[int]: 数字，失败返回None
        """
        if not part or part == '零':
            return 0
        
        result = 0
        current = 0
        
        i = 0
        while i < len(part):
            char = part[i]
            
            if char in self.CHINESE_DIGITS:
                current = self.CHINESE_DIGITS[char]
            elif char in self.CHINESE_UNITS:
                unit = self.CHINESE_UNITS[char]
                if current == 0:
                    current = 1
                result += current * unit
                current = 0
            else:
                return None
            
            i += 1
        
        result += current
        return result
    
    def _english_to_arabic(self, english_str: str) -> Optional[int]:
        """
        英文数字转阿拉伯数字
        
        Args:
            english_str: 英文数字字符串
            
        Returns:
            Optional[int]: 阿拉伯数字，失败返回None
        """
        try:
            # 转换为小写并移除连字符（统一用空格）
            english_str = english_str.lower().replace('-', ' ')
            
            # 分割单词
            words = english_str.split()
            
            if not words:
                return None
            
            result = 0
            current = 0
            
            for word in words:
                if word in self.ENGLISH_WORDS:
                    value = self.ENGLISH_WORDS[word]
                    
                    if value == 100:
                        current *= 100
                    elif value >= 1000:
                        current *= value
                        result += current
                        current = 0
                    else:
                        current += value
                else:
                    return None
            
            result += current
            return result
            
        except Exception:
            return None
    
    def _arabic_to_chinese(self, number: int) -> str:
        """
        阿拉伯数字转中文数字
        
        Args:
            number: 阿拉伯数字
            
        Returns:
            str: 中文数字
        """
        if number == 0:
            return '零'
        
        if number < 0:
            return '负' + self._arabic_to_chinese(-number)
        
        # 分割亿、万、个
        yi = number // 100000000
        wan = (number % 100000000) // 10000
        ge = number % 10000
        
        result = ''
        
        if yi > 0:
            result += self._number_to_chinese_part(yi) + '亿'
        
        if wan > 0:
            if yi > 0 and wan < 1000:
                result += '零'
            result += self._number_to_chinese_part(wan) + '万'
        
        if ge > 0:
            if (yi > 0 or wan > 0) and ge < 1000:
                result += '零'
            result += self._number_to_chinese_part(ge)
        elif yi == 0 and wan == 0:
            result = '零'
        
        return result
    
    def _number_to_chinese_part(self, number: int) -> str:
        """
        将数字（0-9999）转换为中文
        
        Args:
            number: 数字
            
        Returns:
            str: 中文数字
        """
        if number == 0:
            return '零'
        
        digits = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
        units = ['', '十', '百', '千']
        
        result = ''
        num_str = str(number)
        length = len(num_str)
        
        for i, char in enumerate(num_str):
            digit = int(char)
            unit_index = length - i - 1
            
            if digit != 0:
                result += digits[digit] + units[unit_index]
            elif result and result[-1] != '零':
                result += '零'
        
        # 移除末尾的零
        result = result.rstrip('零')
        
        # 处理"一十"开头的情况
        if result.startswith('一十'):
            result = result[1:]
        
        return result
    
    def _arabic_to_english(self, number: int) -> str:
        """
        阿拉伯数字转英文数字
        
        Args:
            number: 阿拉伯数字
            
        Returns:
            str: 英文数字
        """
        if number == 0:
            return 'zero'
        
        if number < 0:
            return 'negative ' + self._arabic_to_english(-number)
        
        result = []
        
        # 处理billion, million, thousand
        for i, unit_value in enumerate([1000000000, 1000000, 1000]):
            if number >= unit_value:
                count = number // unit_value
                number = number % unit_value
                result.append(self._number_to_english_part(count))
                result.append(self.ENGLISH_UNITS[3 - i])
        
        # 处理剩余部分
        if number > 0:
            result.append(self._number_to_english_part(number))
        
        return ' '.join(result)
    
    def _number_to_english_part(self, number: int) -> str:
        """
        将数字（0-999）转换为英文
        
        Args:
            number: 数字
            
        Returns:
            str: 英文数字
        """
        if number == 0:
            return ''
        
        result = []
        
        # 百位
        if number >= 100:
            hundreds = number // 100
            result.append(self.ENGLISH_ONES[hundreds])
            result.append('hundred')
            number = number % 100
        
        # 十位和个位
        if number >= 20:
            tens = number // 10
            ones = number % 10
            if ones > 0:
                result.append(f"{self.ENGLISH_TENS[tens]}-{self.ENGLISH_ONES[ones]}")
            else:
                result.append(self.ENGLISH_TENS[tens])
        elif number > 0:
            result.append(self.ENGLISH_ONES[number])
        
        return ' '.join(result)
    
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
        
        valid_types = ["arabic", "chinese", "english"]
        from_type = config.get("From", "arabic").lower()
        to_type = config.get("To", "chinese").lower()
        
        if from_type not in valid_types:
            errors.append(f"不支持的From类型: {from_type}")
        
        if to_type not in valid_types:
            errors.append(f"不支持的To类型: {to_type}")
        
        return errors