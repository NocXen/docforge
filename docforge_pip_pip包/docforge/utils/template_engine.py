"""
模板引擎
处理字段替换和模板渲染

使用示例：
    from docforge.utils.template_engine import TemplateEngine
    
    engine = TemplateEngine()
    result = engine.render("审批单-{公司名称}.docx", {"公司名称": "ABC公司"})
"""

import re
from typing import Dict, List, Optional, Tuple


class TemplateEngine:
    """
    模板引擎
    
    支持多种字段语法的模板处理
    """
    
    def __init__(self, field_pattern: str = r'\{([^:}]+)(?::([^}]+))?\}'):
        """
        初始化模板引擎
        
        Args:
            field_pattern: 字段匹配正则表达式
        """
        self.pattern = re.compile(field_pattern)
    
    def extract_fields(self, template: str) -> List[Tuple[str, Optional[str]]]:
        """
        提取模板中的字段
        
        Args:
            template: 模板字符串
            
        Returns:
            List[Tuple[str, Optional[str]]]: (字段名, 索引)列表
            
        Example:
            >>> engine = TemplateEngine()
            >>> engine.extract_fields("{公司名称}-{职位:#}.docx")
            [('公司名称', None), ('职位', '#')]
        """
        matches = self.pattern.findall(template)
        return [(match[0], match[1] if match[1] else None) for match in matches]
    
    def get_unique_fields(self, template: str) -> List[str]:
        """
        获取模板中的唯一字段名
        
        Args:
            template: 模板字符串
            
        Returns:
            List[str]: 去重后的字段名列表
        """
        fields = self.extract_fields(template)
        unique = []
        for field_name, _ in fields:
            if field_name not in unique:
                unique.append(field_name)
        return unique
    
    def render(self, template: str, data: Dict[str, str]) -> str:
        """
        渲染模板
        
        将模板中的 {字段名} 替换为对应的值
        
        Args:
            template: 模板字符串
            data: 替换数据 {字段名: 值}
            
        Returns:
            str: 渲染后的字符串
            
        Example:
            >>> engine = TemplateEngine()
            >>> engine.render("{公司名称}.docx", {"公司名称": "ABC公司"})
            'ABC公司.docx'
        """
        def replacer(match):
            field_name = match.group(1)
            field_index = match.group(2)
            
            value = data.get(field_name)
            
            # 如果值不存在，保留原始字段
            if value is None:
                return match.group(0)
            
            # 如果没有指定索引，直接返回值
            if field_index is None:
                return str(value)
            
            # 如果指定了索引
            if isinstance(value, list):
                try:
                    # 处理特殊索引 "#"
                    if field_index == "#":
                        # "#" 通常用于占位，实际使用时需要指定具体索引
                        return match.group(0)
                    
                    idx = int(field_index) - 1  # 索引从1开始
                    if 0 <= idx < len(value):
                        return str(value[idx])
                except (ValueError, IndexError):
                    pass
            
            return match.group(0)
        
        return self.pattern.sub(replacer, template)
    
    def render_with_index(
        self,
        template: str,
        data: Dict[str, List[str]],
        index: int
    ) -> str:
        """
        使用指定索引渲染模板
        
        Args:
            template: 模板字符串
            data: 数据字典（字段名 -> 值列表）
            index: 索引（从0开始）
            
        Returns:
            str: 渲染后的字符串
            
        Example:
            >>> engine = TemplateEngine()
            >>> data = {"公司名称": ["ABC公司", "XYZ公司"]}
            >>> engine.render_with_index("{公司名称}.docx", data, 0)
            'ABC公司.docx'
        """
        # 构建单值数据
        single_data = {}
        for key, values in data.items():
            if isinstance(values, list) and 0 <= index < len(values):
                single_data[key] = values[index]
        
        return self.render(template, single_data)
    
    def batch_render(
        self,
        template: str,
        data: Dict[str, List[str]]
    ) -> List[str]:
        """
        批量渲染模板
        
        对于数据中的每个索引，生成一个渲染结果
        
        Args:
            template: 模板字符串
            data: 数据字典（字段名 -> 值列表）
            
        Returns:
            List[str]: 渲染结果列表
            
        Example:
            >>> engine = TemplateEngine()
            >>> data = {"公司名称": ["ABC公司", "XYZ公司"]}
            >>> engine.batch_render("{公司名称}.docx", data)
            ['ABC公司.docx', 'XYZ公司.docx']
        """
        if not data:
            return [template]
        
        # 获取数据长度（取最大长度）
        max_length = max(len(v) for v in data.values() if isinstance(v, list))
        
        results = []
        for i in range(max_length):
            result = self.render_with_index(template, data, i)
            results.append(result)
        
        return results
    
    def escape_field_syntax(self, text: str) -> str:
        """
        转义字段语法字符
        
        将 { 和 } 转义为 {{ 和 }}
        
        Args:
            text: 原始文本
            
        Returns:
            str: 转义后的文本
        """
        return text.replace('{', '{{').replace('}', '}}')
    
    def unescape_field_syntax(self, text: str) -> str:
        """
        反转义字段语法字符
        
        将 {{ 和 }} 转义回 { 和 }
        
        Args:
            text: 转义的文本
            
        Returns:
            str: 原始文本
        """
        return text.replace('{{', '{').replace('}}', '}')
    
    def has_fields(self, template: str) -> bool:
        """
        检查模板是否包含字段
        
        Args:
            template: 模板字符串
            
        Returns:
            bool: 是否包含字段
        """
        return bool(self.pattern.search(template))
    
    def validate_template(self, template: str) -> List[str]:
        """
        验证模板格式
        
        Args:
            template: 模板字符串
            
        Returns:
            List[str]: 错误列表，空列表表示验证通过
        """
        errors = []
        
        # 检查未转义的字段语法
        # 简单检查：{ 和 } 应该成对出现
        open_count = template.count('{')
        close_count = template.count('}')
        
        if open_count != close_count:
            errors.append(f"字段括号不匹配: {{ 有 {open_count} 个, }} 有 {close_count} 个")
        
        return errors