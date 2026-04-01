"""
字符串处理工具函数
提供字符串处理的通用函数

使用示例：
    from docforge.utils.string_utils import extract_fields, render_template
    
    fields = extract_fields("审批单-{公司名称}.docx")  # ["公司名称"]
    result = render_template("审批单-{公司名称}.docx", {"公司名称": "ABC公司"})
"""

import re
from typing import Dict, List, Optional


def extract_fields(template: str, pattern: str = r'\{([^:}]+)(?::([^}]+))?\}') -> List[str]:
    """
    从模板字符串中提取字段名
    
    Args:
        template: 模板字符串
        pattern: 正则表达式模式
        
    Returns:
        List[str]: 字段名列表（去重）
        
    Example:
        >>> extract_fields("审批单-{公司名称}.docx")
        ['公司名称']
        >>> extract_fields("{公司名称}-{职位:#}.docx")
        ['公司名称', '职位']
    """
    matches = re.findall(pattern, template)
    fields = []
    
    for match in matches:
        field_name = match[0]  # 第一个捕获组是字段名
        if field_name not in fields:
            fields.append(field_name)
    
    return fields


def render_template(template: str, data: Dict[str, str]) -> str:
    """
    渲染模板字符串
    
    将模板中的 {字段名} 替换为对应的值
    
    Args:
        template: 模板字符串
        data: 替换数据 {字段名: 值}
        
    Returns:
        str: 渲染后的字符串
        
    Example:
        >>> render_template("审批单-{公司名称}.docx", {"公司名称": "ABC公司"})
        '审批单-ABC公司.docx'
    """
    def replacer(match):
        field_name = match.group(1)
        field_index = match.group(2)
        
        # 如果没有指定索引，直接返回值
        if field_index is None:
            return str(data.get(field_name, match.group(0)))
        
        # 如果指定了索引
        value = data.get(field_name)
        if isinstance(value, list):
            try:
                idx = int(field_index) - 1  # 索引从1开始
                if 0 <= idx < len(value):
                    return str(value[idx])
            except (ValueError, IndexError):
                pass
        
        return match.group(0)
    
    pattern = r'\{([^:}]+)(?::([^}]+))?\}'
    return re.sub(pattern, replacer, template)


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 清理后的文件名
        
    Example:
        >>> sanitize_filename("file:name?.txt")
        'filename.txt'
    """
    # 移除Windows/Linux不允许的字符
    illegal_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(illegal_chars, '', filename)
    
    # 移除首尾空格和点
    sanitized = sanitized.strip(' .')
    
    # 如果文件名为空，使用默认名称
    if not sanitized:
        sanitized = "unnamed"
    
    return sanitized


def split_text(text: str, delimiter: str = ",") -> List[str]:
    """
    分割文本
    
    Args:
        text: 文本
        delimiter: 分隔符
        
    Returns:
        List[str]: 分割后的列表（去除空字符串）
        
    Example:
        >>> split_text("A,B,C", ",")
        ['A', 'B', 'C']
        >>> split_text("A,,B", ",")
        ['A', 'B']
    """
    items = [item.strip() for item in text.split(delimiter)]
    return [item for item in items if item]


def format_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 字节数
        
    Returns:
        str: 格式化的大小字符串
        
    Example:
        >>> format_size(1024)
        '1.0 KB'
        >>> format_size(1048576)
        '1.0 MB'
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    截断字符串
    
    Args:
        text: 原始字符串
        max_length: 最大长度
        suffix: 截断后缀
        
    Returns:
        str: 截断后的字符串
        
    Example:
        >>> truncate_string("这是一段很长的文本", 10)
        '这是一段很...'
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def escape_field_syntax(text: str) -> str:
    """
    转义字段语法字符
    
    将 { 和 } 转义为 {{ 和 }}
    
    Args:
        text: 原始文本
        
    Returns:
        str: 转义后的文本
        
    Example:
        >>> escape_field_syntax("这是一个{字段}")
        '这是一个{{字段}}'
    """
    return text.replace('{', '{{').replace('}', '}}')


def unescape_field_syntax(text: str) -> str:
    """
    反转义字段语法字符
    
    将 {{ 和 }} 转义回 { 和 }
    
    Args:
        text: 转义的文本
        
    Returns:
        str: 原始文本
        
    Example:
        >>> unescape_field_syntax("这是一个{{字段}}")
        '这是一个{字段}'
    """
    return text.replace('{{', '{').replace('}}', '}')
