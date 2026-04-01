# Utils层 - 工具层说明

## 这一层是干什么的？

Utils层提供**通用工具函数**。这些是被其他层频繁使用的小功能，不涉及业务逻辑。

简单来说：
- **其他层**负责"做什么"
- **utils层**提供"怎么做"的工具

## 文件清单

```
utils/
├── README.md              ← 你现在看的这个文件
├── __init__.py            ← 包初始化，导出所有公共函数
├── file_utils.py          ← 文件操作工具
├── string_utils.py        ← 字符串处理工具
├── template_engine.py     ← 模板引擎
└── validators.py          ← 数据验证工具
```

## 各文件详细说明

### 1. file_utils.py - 文件操作工具

**作用**：提供文件和路径操作的通用函数

**导出函数**：

| 函数名 | 参数 | 返回值 | 说明 |
|--------|------|--------|------|
| `get_file_extension` | `file_path: str` | `str` | 获取文件扩展名（含点号），如 ".xlsx" |
| `get_file_name` | `file_path: str`, `with_extension: bool = True` | `str` | 获取文件名，可选择是否包含扩展名 |
| `ensure_directory` | `dir_path: str` | `bool` | 确保目录存在，不存在则创建，返回是否成功 |
| `list_files` | `directory: str`, `extensions: List[str] = None`, `recursive: bool = False` | `List[str]` | 列出目录下的文件，支持扩展名过滤和递归 |
| `calculate_file_hash` | `file_path: str`, `algorithm: str = "md5"` | `str` | 计算文件哈希值，支持 md5/sha1/sha256 |
| `safe_delete` | `file_path: str` | `bool` | 安全删除文件，返回是否删除成功 |
| `get_file_size` | `file_path: str` | `int` | 获取文件大小（字节） |
| `copy_file` | `source: str`, `destination: str` | `bool` | 复制文件，自动创建目标目录 |

**使用示例**：

```python
from docforge.utils import (
    get_file_extension,
    get_file_name,
    ensure_directory,
    list_files,
    calculate_file_hash,
    safe_delete,
    get_file_size,
    copy_file
)

# 获取扩展名
ext = get_file_extension("data.xlsx")  # ".xlsx"
ext = get_file_extension("path/to/file.txt")  # ".txt"

# 获取文件名
name = get_file_name("path/to/data.xlsx")  # "data.xlsx"
name = get_file_name("path/to/data.xlsx", with_extension=False)  # "data"

# 确保目录存在
success = ensure_directory("./output/data")  # True

# 列出Excel文件
files = list_files("./data", extensions=[".xlsx", ".xls"])
# ['./data/file1.xlsx', './data/file2.xlsx']

# 递归列出所有文件
all_files = list_files("./data", recursive=True)

# 计算文件哈希
hash_value = calculate_file_hash("data.xlsx")  # "5d41402abc4b2a76b9719d911017c592"
hash_value = calculate_file_hash("data.xlsx", algorithm="sha256")

# 获取文件大小
size = get_file_size("data.xlsx")  # 10240

# 复制文件
success = copy_file("data.xlsx", "backup/data.xlsx")  # True

# 安全删除文件
success = safe_delete("./temp/file.txt")  # True
```

**异常处理**：
- `calculate_file_hash`: 文件不存在时抛出 `FileNotFoundError`
- `get_file_size`: 文件不存在时抛出 `FileNotFoundError`

---

### 2. string_utils.py - 字符串处理工具

**作用**：提供字符串处理的通用函数

**导出函数**：

| 函数名 | 参数 | 返回值 | 说明 |
|--------|------|--------|------|
| `extract_fields` | `template: str`, `pattern: str = r'\{([^:}]+)(?::([^}]+))?\}'` | `List[str]` | 从模板字符串中提取字段名（去重） |
| `render_template` | `template: str`, `data: Dict[str, str]` | `str` | 渲染模板字符串，将 `{字段名}` 替换为对应的值 |
| `sanitize_filename` | `filename: str` | `str` | 清理文件名，移除非法字符 |
| `split_text` | `text: str`, `delimiter: str = ","` | `List[str]` | 分割文本，去除空字符串 |
| `format_size` | `size_bytes: int` | `str` | 格式化文件大小，如 "1.0 MB" |
| `truncate_string` | `text: str`, `max_length: int = 50`, `suffix: str = "..."` | `str` | 截断字符串，超过最大长度时添加后缀 |
| `escape_field_syntax` | `text: str` | `str` | 转义字段语法字符，`{` → `{{`，`}` → `}}` |
| `unescape_field_syntax` | `text: str` | `str` | 反转义字段语法字符，`{{` → `{`，`}}` → `}` |

**使用示例**：

```python
from docforge.utils import (
    extract_fields,
    render_template,
    sanitize_filename,
    split_text,
    format_size,
    truncate_string,
    escape_field_syntax,
    unescape_field_syntax
)

# 提取字段
fields = extract_fields("审批单-{公司名称}.docx")  # ["公司名称"]
fields = extract_fields("{公司名称}-{职位:#}.docx")  # ["公司名称", "职位"]

# 渲染模板
result = render_template(
    "审批单-{公司名称}.docx",
    {"公司名称": "ABC公司"}
)  # "审批单-ABC公司.docx"

# 清理文件名
clean_name = sanitize_filename("file:name?.txt")  # "filename.txt"
clean_name = sanitize_filename("  .hidden  ")  # "hidden"

# 分割文本
items = split_text("A,B,C", ",")  # ["A", "B", "C"]
items = split_text("A,,B", ",")  # ["A", "B"]

# 格式化大小
size_str = format_size(1024)  # "1.0 KB"
size_str = format_size(1048576)  # "1.0 MB"

# 截断字符串
truncated = truncate_string("这是一段很长的文本", 10)  # "这是一段很..."
truncated = truncate_string("短文本", 10)  # "短文本"

# 转义字段语法
escaped = escape_field_syntax("这是一个{字段}")  # "这是一个{{字段}}"
unescaped = unescape_field_syntax("这是一个{{字段}}")  # "这是一个{字段}"
```

**字段语法说明**：

框架使用 `{字段名}` 或 `{字段名:索引}` 的语法：

```python
# 简单字段
模板: "审批单-{公司名称}.docx"
数据: {"公司名称": "ABC公司"}
结果: "审批单-ABC公司.docx"

# 带索引的字段
模板: "审批单-{公司名称:#}.docx"
数据: {"公司名称": ["ABC公司", "XYZ公司"]}
结果1: "审批单-ABC公司.docx"
结果2: "审批单-XYZ公司.docx"

# 指定索引
模板: "审批单-{公司名称:1}.docx"
数据: {"公司名称": ["ABC公司", "XYZ公司"]}
结果: "审批单-ABC公司.docx"

# 转义字符
模板: "审批单-{{公司名称}}.docx"
结果: "审批单-{公司名称}.docx"  # 不进行替换
```

---

### 3. template_engine.py - 模板引擎

**作用**：处理字段替换和模板渲染

**TemplateEngine 类方法**：

| 方法名 | 参数 | 返回值 | 说明 |
|--------|------|--------|------|
| `__init__` | `field_pattern: str = r'\{([^:}]+)(?::([^}]+))?\}'` | - | 初始化模板引擎，可自定义字段匹配模式 |
| `extract_fields` | `template: str` | `List[Tuple[str, Optional[str]]]` | 提取模板中的字段，返回 (字段名, 索引) 列表 |
| `get_unique_fields` | `template: str` | `List[str]` | 获取模板中的唯一字段名 |
| `render` | `template: str`, `data: Dict[str, str]` | `str` | 渲染模板，将 `{字段名}` 替换为对应的值 |
| `render_with_index` | `template: str`, `data: Dict[str, List[str]]`, `index: int` | `str` | 使用指定索引渲染模板 |
| `batch_render` | `template: str`, `data: Dict[str, List[str]]` | `List[str]` | 批量渲染模板，生成多个结果 |
| `escape_field_syntax` | `text: str` | `str` | 转义字段语法字符 |
| `unescape_field_syntax` | `text: str` | `str` | 反转义字段语法字符 |
| `has_fields` | `template: str` | `bool` | 检查模板是否包含字段 |
| `validate_template` | `template: str` | `List[str]` | 验证模板格式，返回错误列表 |

**使用示例**：

```python
from docforge.utils import TemplateEngine

# 创建模板引擎
engine = TemplateEngine()

# 提取字段
fields = engine.extract_fields("审批单-{公司名称}.docx")
# [('公司名称', None)]

fields = engine.extract_fields("{公司名称}-{职位:#}.docx")
# [('公司名称', None), ('职位', '#')]

# 获取唯一字段名
unique_fields = engine.get_unique_fields("{公司名称}-{公司名称}.docx")
# ['公司名称']

# 渲染模板
result = engine.render(
    "审批单-{公司名称}.docx",
    {"公司名称": "ABC公司"}
)  # "审批单-ABC公司.docx"

# 批量渲染
results = engine.batch_render(
    "审批单-{公司名称:#}.docx",
    {"公司名称": ["ABC公司", "XYZ公司"]}
)  # ["审批单-ABC公司.docx", "审批单-XYZ公司.docx"]

# 使用索引渲染
data = {"公司名称": ["ABC公司", "XYZ公司"]}
result = engine.render_with_index("{公司名称}.docx", data, 0)  # "ABC公司.docx"
result = engine.render_with_index("{公司名称}.docx", data, 1)  # "XYZ公司.docx"

# 检查是否包含字段
has_fields = engine.has_fields("审批单-{公司名称}.docx")  # True
has_fields = engine.has_fields("审批单.docx")  # False

# 验证模板
errors = engine.validate_template("审批单-{公司名称.docx")  # ["字段括号不匹配..."]
errors = engine.validate_template("审批单-{公司名称}.docx")  # []

# 转义/反转义
escaped = engine.escape_field_syntax("这是一个{字段}")  # "这是一个{{字段}}"
unescaped = engine.unescape_field_syntax("这是一个{{字段}}")  # "这是一个{字段}"
```

**与 string_utils 的区别**：
- `string_utils.render_template` 是简单的函数式接口
- `TemplateEngine` 是面向对象的接口，支持更多高级功能（批量渲染、索引渲染、验证等）

---

### 4. validators.py - 数据验证工具

**作用**：验证数据的有效性

**导出函数**：

| 函数名 | 参数 | 返回值 | 说明 |
|--------|------|--------|------|
| `validate_file_path` | `file_path: str`, `must_exist: bool = True` | `bool` | 验证文件路径 |
| `validate_directory_path` | `dir_path: str`, `must_exist: bool = True` | `bool` | 验证目录路径 |
| `validate_file_extension` | `file_path: str`, `allowed_extensions: List[str]` | `bool` | 验证文件扩展名 |
| `validate_json` | `data: str` | `bool` | 验证JSON字符串 |
| `validate_workflow_definition` | `definition: dict` | `List[str]` | 验证工作流定义，返回错误列表 |
| `validate_plugin_name` | `name: str` | `bool` | 验证插件名称（只允许字母、数字、下划线） |
| `validate_version` | `version: str` | `bool` | 验证版本号（语义化版本 X.Y.Z） |
| `validate_config_key` | `key: str` | `bool` | 验证配置键（点分隔格式） |
| `validate_email` | `email: str` | `bool` | 验证邮箱地址 |
| `validate_url` | `url: str` | `bool` | 验证URL |

**使用示例**：

```python
from docforge.utils import (
    validate_file_path,
    validate_directory_path,
    validate_file_extension,
    validate_json,
    validate_workflow_definition,
    validate_plugin_name,
    validate_version,
    validate_config_key,
    validate_email,
    validate_url
)

# 验证文件路径
is_valid = validate_file_path("data.xlsx", must_exist=True)  # True（如果文件存在）
is_valid = validate_file_path("new_file.xlsx", must_exist=False)  # True（如果父目录存在且可写）

# 验证目录路径
is_valid = validate_directory_path("./output", must_exist=False)  # True

# 验证扩展名
is_valid = validate_file_extension("data.xlsx", [".xlsx", ".xls"])  # True
is_valid = validate_file_extension("data.txt", [".xlsx", ".xls"])  # False

# 验证JSON
is_valid = validate_json('{"key": "value"}')  # True
is_valid = validate_json('invalid json')  # False

# 验证工作流定义
errors = validate_workflow_definition({
    "name": "my_workflow",
    "steps": [
        {"step_id": "step1", "plugin_name": "excel_extractor"}
    ]
})  # []

errors = validate_workflow_definition({
    "steps": []
})  # ["缺少必需字段: name"]

# 验证插件名称
is_valid = validate_plugin_name("excel_extractor")  # True
is_valid = validate_plugin_name("my plugin")  # False（包含空格）
is_valid = validate_plugin_name("123plugin")  # False（以数字开头）

# 验证版本号
is_valid = validate_version("1.0.0")  # True
is_valid = validate_version("invalid")  # False

# 验证配置键
is_valid = validate_config_key("database.path")  # True
is_valid = validate_config_key("invalid key!")  # False（包含非法字符）

# 验证邮箱
is_valid = validate_email("user@example.com")  # True
is_valid = validate_email("invalid-email")  # False

# 验证URL
is_valid = validate_url("https://example.com")  # True
is_valid = validate_url("invalid-url")  # False
```

**验证规则说明**：

1. **文件路径验证**：
   - `must_exist=True`: 文件必须存在且是文件
   - `must_exist=False`: 父目录必须存在且可写

2. **目录路径验证**：
   - `must_exist=True`: 目录必须存在且是目录
   - `must_exist=False`: 父目录必须存在且可写

3. **插件名称验证**：
   - 只允许字母、数字、下划线
   - 必须以字母或下划线开头
   - 示例：`excel_extractor`, `_my_plugin`, `Plugin123`

4. **版本号验证**：
   - 语义化版本格式：`X.Y.Z`
   - 示例：`1.0.0`, `2.1.3`

5. **配置键验证**：
   - 点分隔格式
   - 只允许字母、数字、下划线、点
   - 示例：`database.path`, `api.endpoint.url`

---

## 常见问题

### Q: 如何添加新的工具函数？
A: 
1. 在相应的 utils 文件中添加函数
2. 在文件开头的文档字符串中说明用途
3. 在 `__init__.py` 中导入并添加到 `__all__` 列表
4. 在本 README 中添加说明

### Q: 工具函数应该返回什么？
A: 
- 通常返回具体值或布尔值（表示是否成功）
- 不要返回 None（除非明确说明）
- 验证函数返回 `bool` 或 `List[str]`（错误列表）

### Q: 如何处理错误？
A: 
- 工具函数应该抛出明确的异常，不要静默失败
- 常见异常：`FileNotFoundError`, `ValueError`, `TypeError`
- 验证函数返回 `False` 或错误列表，不抛出异常

### Q: 支持哪些文件格式？
A: 见 `constants.py` 中的 `FileExtensions` 类

### Q: string_utils 和 template_engine 有什么区别？
A: 
- `string_utils` 提供简单的函数式接口，适合一次性使用
- `template_engine` 提供面向对象的接口，适合需要复用或高级功能的场景

### Q: 如何自定义字段匹配模式？
A: 
```python
from docforge.utils import TemplateEngine

# 自定义模式：支持 ${字段名} 语法
engine = TemplateEngine(r'\$\{([^}]+)\}')
result = engine.render("${公司名称}.docx", {"公司名称": "ABC公司"})
```

---

## 最佳实践

1. **导入方式**：
   ```python
   # 推荐：从包级别导入
   from docforge.utils import get_file_extension, render_template
   
   # 也可以：从具体模块导入
   from docforge.utils.file_utils import get_file_extension
   ```

2. **错误处理**：
   ```python
   from docforge.utils import validate_file_path, calculate_file_hash
   
   # 先验证再操作
   if validate_file_path("data.xlsx", must_exist=True):
       hash_value = calculate_file_hash("data.xlsx")
   else:
       print("文件不存在")
   ```

3. **批量处理**：
   ```python
   from docforge.utils import TemplateEngine, list_files
   
   # 批量处理文件
   engine = TemplateEngine()
   files = list_files("./data", extensions=[".xlsx"])
   for file in files:
       result = engine.render(file, data)
   ```

---

*最后更新：2026年3月31日*