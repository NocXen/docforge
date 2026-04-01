# Plugins 层 - 插件系统核心

## 概述

Plugins 层是 DocForge 框架的**插件系统基础设施**，提供了完整的插件定义、加载、注册和管理机制。

### 核心设计理念

插件系统采用**面向接口编程**的设计模式，通过抽象基类定义统一接口，确保所有插件都有一致的行为。这种设计使得：

- **可扩展性**：用户可以编写自定义插件，无需修改框架代码
- **热插拔**：插件可以在运行时动态加载和卸载
- **类型安全**：通过抽象基类确保插件实现所有必要接口
- **依赖管理**：插件可以声明依赖，框架负责检查和管理

### 与其他层的关系

```
┌─────────────────────────────────────────────────────────┐
│                    Workflow Engine                       │
│                    (工作流引擎)                           │
├─────────────────────────────────────────────────────────┤
│                    Services Layer                        │
│                    (服务层)                              │
│         决定"用什么工具"处理数据                          │
├─────────────────────────────────────────────────────────┤
│                    Plugins Layer  ← 你在这里              │
│                    (插件层)                              │
│         定义"工具长什么样"和"怎么装工具"                   │
├─────────────────────────────────────────────────────────┤
│                    Storage Layer                         │
│                    (存储层)                              │
│         提供数据持久化能力                                │
└─────────────────────────────────────────────────────────┘
```

## 目录结构

```
plugins/
├── __init__.py            # 包初始化，导出公共 API
├── base.py                # 插件抽象基类（核心接口定义）
├── loader.py              # 插件加载器（从文件系统/包加载插件）
├── registry.py            # 插件注册表（管理已加载的插件）
├── types.py               # 插件相关的数据类型定义
└── README.md              # 本文档
```

---

## 模块详解

### 1. `base.py` - 插件抽象基类

**文件路径**: `docforge/plugins/base.py`

#### 作用

定义所有插件必须实现的接口规范。这是插件系统的**核心契约**，所有自定义插件都必须继承 `BasePlugin` 类并实现其抽象方法。

#### 核心类：`BasePlugin`

`BasePlugin` 是一个抽象基类（ABC），定义了插件的标准接口：

##### 必须实现的抽象属性

| 属性 | 返回类型 | 说明 | 示例 |
|------|----------|------|------|
| `name` | `str` | 插件唯一标识名称 | `"excel_extractor"` |
| `version` | `str` | 插件版本号（建议使用语义化版本） | `"1.0.0"` |
| `plugin_type` | `str` | 插件类型，必须是 `extractor`、`transformer`、`replacer`、`post_processor` 之一 | `"extractor"` |

##### 必须实现的抽象方法

| 方法 | 返回类型 | 说明 |
|------|----------|------|
| `execute(**kwargs)` | `ExecutionResult` | 执行插件核心逻辑，所有处理都在这里 |
| `cleanup()` | `None` | 清理资源，在插件卸载前调用 |

##### 可选覆盖的属性和方法

| 属性/方法 | 返回类型 | 默认值 | 说明 |
|-----------|----------|--------|------|
| `capabilities` | `List[str]` | `[self.plugin_type]` | 插件支持的功能列表 |
| `description` | `str` | `""` | 插件功能描述 |
| `author` | `str` | `""` | 插件作者名称 |
| `dependencies` | `List[str]` | `[]` | 依赖的 Python 包列表 |
| `validate_input(**kwargs)` | `List[str]` | `[]` | 验证输入参数，返回错误列表 |
| `get_metadata()` | `Dict[str, Any]` | 自动生成 | 获取插件元数据字典 |

#### `execute()` 方法详解

这是插件的**核心入口**，工作流引擎会调用此方法并传入参数：

```python
def execute(self, **kwargs) -> ExecutionResult:
    """
    执行插件功能
    
    常用参数（通过 kwargs 传递）：
    - input_files: List[str] - 输入文件路径列表
    - template_files: List[str] - 模板文件路径列表
    - output_dir: str - 输出目录路径
    - data: DataDict - 来自上一步插件的数据
    
    返回：
    - ExecutionResult - 包含 success 状态和 data/errors
    """
```

#### 代码示例

```python
from docforge.plugins.base import BasePlugin
from docforge.types import ExecutionResult

class MyPlugin(BasePlugin):
    """自定义插件示例"""
    
    @property
    def name(self) -> str:
        return "my_plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def plugin_type(self) -> str:
        return "extractor"
    
    @property
    def description(self) -> str:
        return "这是一个自定义插件示例"
    
    @property
    def dependencies(self) -> List[str]:
        return ["pandas"]  # 声明依赖
    
    def validate_input(self, **kwargs) -> List[str]:
        """验证输入参数"""
        errors = []
        if not kwargs.get("input_files"):
            errors.append("缺少输入文件")
        return errors
    
    def execute(self, **kwargs) -> ExecutionResult:
        # 1. 验证输入
        errors = self.validate_input(**kwargs)
        if errors:
            return ExecutionResult(success=False, errors=errors)
        
        # 2. 处理逻辑
        input_files = kwargs.get("input_files", [])
        # ... 具体处理 ...
        
        # 3. 返回结果
        return ExecutionResult(
            success=True,
            data={"result": "处理完成"}
        )
    
    def cleanup(self):
        """清理资源"""
        pass
```

---

### 2. `loader.py` - 插件加载器

**文件路径**: `docforge/plugins/loader.py`

#### 作用

`PluginLoader` 负责从文件系统或已安装的 Python 包中**动态加载插件**。它使用 Python 的 `importlib` 模块实现运行时模块加载。

#### 核心类：`PluginLoader`

##### 加载方法一览

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `load_from_file(file_path)` | 文件路径 | `BasePlugin` | 从单个 `.py` 文件加载插件 |
| `load_from_directory(directory)` | 目录路径 | `List[BasePlugin]` | 从目录批量加载所有插件 |
| `load_from_package(package_name)` | 包名 | `BasePlugin` | 从已安装的 Python 包加载 |
| `load_from_module(module_path)` | 模块路径 | `BasePlugin` | 从模块路径（如 `my_plugins.extractor`）加载 |

##### 辅助方法

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `validate_plugin_class(plugin_class)` | 插件类 | `List[str]` | 验证插件类是否符合规范 |
| `extract_metadata(file_path)` | 文件路径 | `PluginMetadata` | 提取插件元数据（不实例化） |
| `check_imports(file_path)` | 文件路径 | `List[str]` | 检查文件导入的模块 |
| `check_dependencies(plugin_class)` | 插件类 | `Dict[str, bool]` | 检查插件依赖是否满足 |

#### 加载流程详解

```
load_from_file("plugins/my_plugin.py")
         │
         ▼
   检查文件是否存在
         │
         ▼
   创建模块规范 (spec_from_file_location)
         │
         ▼
   创建并注册模块 (module_from_spec)
         │
         ▼
   执行模块代码 (exec_module)
         │
         ▼
   查找继承自 BasePlugin 的类
         │
         ▼
   验证插件类 (validate_plugin_class)
         │
         ▼
   实例化插件 (plugin_class())
         │
         ▼
   返回插件实例
```

#### 代码示例

```python
from docforge.plugins.loader import PluginLoader
from docforge.services.logger import Logger

# 创建加载器（可选传入日志器）
logger = Logger()
loader = PluginLoader(logger)

# 方式1：从单个文件加载
plugin = loader.load_from_file("plugins/excel_extractor.py")

# 方式2：从目录批量加载（自动跳过 __ 开头的文件）
plugins = loader.load_from_directory("plugins/")
for p in plugins:
    print(f"加载了: {p.name} v{p.version}")

# 方式3：从已安装的包加载
plugin = loader.load_from_package("my_docforge_plugins")

# 检查插件依赖
deps = loader.check_dependencies(plugin.__class__)
for dep, satisfied in deps.items():
    status = "✓" if satisfied else "✗"
    print(f"{status} {dep}")
```

#### 注意事项

1. **模块命名**：加载的模块会被命名为 `docforge_plugins.{文件名}`，避免命名冲突
2. **文件过滤**：`load_from_directory` 只加载 `.py` 文件，跳过 `__` 开头的文件
3. **错误处理**：加载失败会抛出 `PluginLoadError` 异常，包含详细错误信息
4. **性能**：加载时会记录耗时，便于性能分析

---

### 3. `registry.py` - 插件注册表

**文件路径**: `docforge/plugins/registry.py`

#### 作用

`PluginRegistry` 是一个**内存中的插件管理器**，负责维护已加载插件的注册表，提供查询、启用/禁用等功能。

#### 核心类：`PluginRegistry`

##### 注册管理

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `register(plugin)` | `BasePlugin` | `bool` | 注册插件实例 |
| `unregister(plugin_name)` | `str` | `bool` | 注销插件（会调用 cleanup） |
| `is_registered(plugin_name)` | `str` | `bool` | 检查是否已注册 |

##### 查询方法

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `get_plugin(plugin_name)` | `str` | `BasePlugin` | 获取指定插件实例 |
| `get_all_plugins()` | - | `Dict[str, BasePlugin]` | 获取所有已注册插件 |
| `get_plugins_by_type(plugin_type)` | `str` | `List[BasePlugin]` | 按类型获取插件 |
| `get_plugin_names()` | - | `List[str]` | 获取所有插件名称 |
| `get_enabled_plugins()` | - | `List[BasePlugin]` | 获取所有启用的插件 |

##### 启用/禁用

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `enable_plugin(plugin_name)` | `str` | `bool` | 启用插件 |
| `disable_plugin(plugin_name)` | `str` | `bool` | 禁用插件 |
| `is_enabled(plugin_name)` | `str` | `bool` | 检查插件是否启用 |

##### 元数据查询

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `get_metadata(plugin_name)` | `str` | `PluginMetadata` | 获取插件元数据 |
| `get_all_metadata()` | - | `Dict[str, PluginMetadata]` | 获取所有元数据 |
| `get_plugins_info()` | - | `List[Dict]` | 获取所有插件的详细信息 |

##### 其他

| 方法 | 说明 |
|------|------|
| `get_plugin_count()` | 获取已注册插件数量 |
| `clear()` | 清空所有注册（会调用每个插件的 cleanup） |

#### 内部数据结构

```python
_plugins: Dict[str, BasePlugin]     # 插件名 -> 插件实例
_metadata: Dict[str, PluginMetadata] # 插件名 -> 元数据
_enabled: Dict[str, bool]            # 插件名 -> 是否启用
```

#### 代码示例

```python
from docforge.plugins.registry import PluginRegistry

registry = PluginRegistry()

# 注册插件
success = registry.register(my_plugin)
if success:
    print(f"插件 {my_plugin.name} 注册成功")

# 查询插件
plugin = registry.get_plugin("excel_extractor")
if plugin:
    result = plugin.execute(input_files=["data.xlsx"])

# 按类型获取插件
extractors = registry.get_plugins_by_type("extractor")

# 禁用/启用插件
registry.disable_plugin("old_plugin")
registry.enable_plugin("old_plugin")

# 获取所有插件信息
for info in registry.get_plugins_info():
    print(f"{info['name']} v{info['version']} - {info['description']}")

# 清空所有注册
registry.clear()
```

---

### 4. `types.py` - 插件数据类型

**文件路径**: `docforge/plugins/types.py`

#### 作用

定义插件系统中使用的**数据结构**，全部使用 `@dataclass` 装饰器，提供类型安全和便捷的字典转换功能。

#### 数据类型详解

##### `PluginMetadata` - 插件元数据

存储插件的静态信息，通常从插件实例中提取。

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | `str` | 必填 | 插件名称 |
| `version` | `str` | `"0.0.0"` | 版本号 |
| `plugin_type` | `str` | `""` | 插件类型 |
| `author` | `str` | `""` | 作者 |
| `description` | `str` | `""` | 描述 |
| `license` | `str` | `""` | 许可证 |
| `homepage` | `str` | `""` | 主页 |
| `dependencies` | `List[str]` | `[]` | 依赖列表 |
| `entry_point` | `str` | `"plugin.py"` | 入口文件 |
| `min_framework_version` | `str` | `"0.1.0"` | 最低框架版本 |

```python
# 创建元数据
metadata = PluginMetadata(
    name="excel_extractor",
    version="1.0.0",
    plugin_type="extractor",
    author="John Doe",
    description="从 Excel 文件提取数据"
)

# 字典转换
data = metadata.to_dict()
metadata2 = PluginMetadata.from_dict(data)
```

##### `PluginContext` - 插件上下文

传递给插件的**运行时环境信息**，插件可以通过上下文访问配置、日志器、数据库等。

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `input_files` | `List[str]` | `[]` | 输入文件列表 |
| `template_files` | `List[str]` | `[]` | 模板文件列表 |
| `output_dir` | `str` | `""` | 输出目录 |
| `logger` | `Any` | `None` | 日志器实例 |
| `database` | `Any` | `None` | 数据库实例 |
| `config` | `Dict[str, Any]` | `{}` | 全局配置 |
| `plugin_config` | `Dict[str, Any]` | `{}` | 插件专用配置 |
| `execution_id` | `str` | `""` | 执行 ID |
| `workflow_name` | `str` | `""` | 工作流名称 |
| `step_index` | `int` | `0` | 步骤索引 |

便捷方法：
- `get_config(key, default)` - 获取全局配置
- `get_plugin_config(key, default)` - 获取插件配置
- `log_debug/info/warning/error(message)` - 记录日志

```python
context = PluginContext(
    input_files=["data.xlsx"],
    output_dir="./output",
    config={"max_rows": 1000},
    plugin_config={"sheet_name": "Sheet1"}
)

# 获取配置
sheet = context.get_plugin_config("sheet_name")
max_rows = context.get_config("max_rows")

# 记录日志
context.log_info(f"正在处理文件: {context.input_files[0]}")
```

##### `PluginDependency` - 插件依赖

描述插件的依赖关系。

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | `str` | 必填 | 依赖名称 |
| `version_spec` | `str` | `""` | 版本要求（如 `">=1.0.0"`） |
| `optional` | `bool` | `False` | 是否可选 |

```python
dep = PluginDependency(
    name="pandas",
    version_spec=">=1.5.0",
    optional=False
)

# 检查依赖是否满足
is_ok = dep.is_satisfied("2.0.0")  # True
```

##### `PluginLoadResult` - 插件加载结果

记录插件加载的详细信息。

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `success` | `bool` | 必填 | 是否成功 |
| `plugin_name` | `str` | `""` | 插件名称 |
| `error_message` | `str` | `""` | 错误信息 |
| `warnings` | `List[str]` | `[]` | 警告列表 |
| `load_time` | `float` | `0.0` | 加载时间（秒） |

---

### 5. `__init__.py` - 包初始化

**文件路径**: `docforge/plugins/__init__.py`

导出插件系统的公共 API，方便外部导入：

```python
from docforge.plugins import (
    BasePlugin,        # 插件基类
    PluginLoader,      # 插件加载器
    PluginRegistry,    # 插件注册表
    PluginMetadata,    # 插件元数据
    PluginContext      # 插件上下文
)
```

---

## 完整工作流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                        插件完整工作流程                               │
└─────────────────────────────────────────────────────────────────────┘

1. 编写插件
   └─> 创建 .py 文件，继承 BasePlugin，实现必要方法

2. 加载插件
   └─> PluginLoader.load_from_file() / load_from_directory()
   └─> 动态导入模块，查找 BasePlugin 子类，验证实例化

3. 注册插件
   └─> PluginRegistry.register()
   └─> 存储插件实例和元数据，标记为启用状态

4. 查询插件
   └─> PluginRegistry.get_plugin() / get_plugins_by_type()
   └─> 按名称或类型查找已注册的插件

5. 执行插件
   └─> plugin.execute(**kwargs)
   └─> 返回 ExecutionResult(success, data, errors)

6. 清理插件
   └─> plugin.cleanup() / registry.unregister()
   └─> 释放资源，关闭文件/连接等
```

---

## 插件类型详解

| 类型 | 常量 | 工作流阶段 | 输入 | 输出 | 典型用途 |
|------|------|------------|------|------|----------|
| 提取器 | `extractor` | 数据获取 | 原始文件 | 结构化数据 | 从 Excel/CSV/JSON 提取数据 |
| 转换器 | `transformer` | 数据处理 | 结构化数据 | 转换后的数据 | 数据清洗、格式转换、过滤 |
| 替换器 | `replacer` | 模板渲染 | 数据 + 模板 | 输出文件 | Word/HTML 模板填充 |
| 后处理器 | `post_processor` | 输出处理 | 输出文件 | 处理后的文件 | 文件合并、压缩、格式转换 |

---

## 插件编写完整指南

### 步骤 1：确定插件类型

首先确定你的插件属于哪种类型：

```python
# 提取器示例：从数据源提取信息
plugin_type = "extractor"

# 转换器示例：处理/转换数据
plugin_type = "transformer"

# 替换器示例：将数据填充到模板
plugin_type = "replacer"

# 后处理器示例：对输出文件进行额外处理
plugin_type = "post_processor"
```

### 步骤 2：创建插件文件

在插件目录创建新的 `.py` 文件：

```python
# plugins/csv_extractor.py
"""CSV 文件数据提取器"""

import csv
from typing import List
from docforge.plugins.base import BasePlugin
from docforge.types import ExecutionResult


class CSVExtractor(BasePlugin):
    """从 CSV 文件中提取数据"""
    
    @property
    def name(self) -> str:
        return "csv_extractor"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def plugin_type(self) -> str:
        return "extractor"
    
    @property
    def description(self) -> str:
        return "从 CSV 文件中提取数据并转换为结构化格式"
    
    @property
    def author(self) -> str:
        return "Your Name"
    
    @property
    def dependencies(self) -> List[str]:
        return []  # CSV 提取不需要额外依赖
    
    def validate_input(self, **kwargs) -> List[str]:
        """验证输入参数"""
        errors = []
        input_files = kwargs.get("input_files", [])
        
        if not input_files:
            errors.append("缺少输入文件")
        
        return errors
    
    def execute(self, **kwargs) -> ExecutionResult:
        """执行数据提取"""
        try:
            input_files = kwargs.get("input_files", [])
            
            if not input_files:
                return ExecutionResult(
                    success=False,
                    errors=["没有输入文件"]
                )
            
            # 读取 CSV 文件
            file_path = input_files[0]
            data = {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    for key, value in row.items():
                        if key not in data:
                            data[key] = []
                        data[key].append(value)
            
            return ExecutionResult(
                success=True,
                data=data,
                metadata={
                    "file": file_path,
                    "rows": len(data.get(list(data.keys())[0], [])) if data else 0
                }
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                errors=[f"提取失败: {str(e)}"]
            )
    
    def cleanup(self):
        """清理资源（本插件不需要）"""
        pass
```

### 步骤 3：测试插件

```python
# 测试插件
from plugins.csv_extractor import CSVExtractor

plugin = CSVExtractor()

# 验证插件属性
print(f"名称: {plugin.name}")
print(f"版本: {plugin.version}")
print(f"类型: {plugin.plugin_type}")
print(f"描述: {plugin.description}")

# 执行插件
result = plugin.execute(input_files=["test.csv"])
print(f"成功: {result.success}")
print(f"数据: {result.data}")
```

---

## 高级插件开发技巧

### 1. 带状态的插件

如果插件需要维护状态，可以使用实例变量：

```python
class StatefulPlugin(BasePlugin):
    def __init__(self):
        self._cache = {}
        self._processed_count = 0
    
    def execute(self, **kwargs) -> ExecutionResult:
        self._processed_count += 1
        # 使用缓存...
        return ExecutionResult(success=True)
    
    def cleanup(self):
        self._cache.clear()
        self._processed_count = 0
```

### 2. 使用配置的插件

```python
class ConfigurablePlugin(BasePlugin):
    def execute(self, **kwargs) -> ExecutionResult:
        # 从 kwargs 获取配置
        config = kwargs.get("config", {})
        option = config.get("my_option", "default_value")
        
        # 根据配置执行不同逻辑
        if option == "mode_a":
            return self._mode_a(kwargs)
        else:
            return self._mode_b(kwargs)
```

### 3. 链式处理插件

```python
class ChainPlugin(BasePlugin):
    """将多个处理步骤链接在一起"""
    
    def execute(self, **kwargs) -> ExecutionResult:
        # 步骤 1：验证
        result = self._validate(kwargs)
        if not result.success:
            return result
        
        # 步骤 2：处理
        result = self._process(result.data)
        if not result.success:
            return result
        
        # 步骤 3：输出
        return self._output(result.data)
    
    def _validate(self, kwargs) -> ExecutionResult:
        # 验证逻辑
        return ExecutionResult(success=True, data=kwargs)
    
    def _process(self, data) -> ExecutionResult:
        # 处理逻辑
        return ExecutionResult(success=True, data=data)
    
    def _output(self, data) -> ExecutionResult:
        # 输出逻辑
        return ExecutionResult(success=True, data=data)
```

---

## 常见问题与解决方案

### Q1: 插件加载失败，报错 "No module named..."

**原因**：插件文件导入了未安装的依赖包。

**解决方案**：
```python
# 方案 1：在插件中声明依赖
@property
def dependencies(self) -> List[str]:
    return ["pandas", "openpyxl"]

# 方案 2：使用可选导入
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

def execute(self, **kwargs) -> ExecutionResult:
    if not HAS_PANDAS:
        return ExecutionResult(
            success=False,
            errors=["需要安装 pandas: pip install pandas"]
        )
```

### Q2: 如何调试插件？

**方法 1**：使用日志记录
```python
def execute(self, **kwargs) -> ExecutionResult:
    # 使用 PluginContext 记录日志
    context = kwargs.get("context")
    if context:
        context.log_debug(f"输入参数: {kwargs}")
```

**方法 2**：在返回结果中包含调试信息
```python
return ExecutionResult(
    success=True,
    data=result_data,
    metadata={"debug_info": "处理了 100 行数据"}
)
```

### Q3: 插件之间如何共享数据？

**方法 1**：通过工作流传递数据
```python
# 插件 A 输出数据
def execute(self, **kwargs) -> ExecutionResult:
    return ExecutionResult(success=True, data={"key": "value"})

# 插件 B 接收数据（工作流会自动传递）
def execute(self, **kwargs) -> ExecutionResult:
    input_data = kwargs.get("data")  # 来自上一步的数据
```

**方法 2**：使用共享存储
```python
# 通过数据库或文件系统共享
from docforge.storage import StorageManager

def execute(self, **kwargs) -> ExecutionResult:
    storage = kwargs.get("storage")
    storage.save("intermediate_result", data)
```

### Q4: 如何处理大文件？

```python
class LargeFileProcessor(BasePlugin):
    def execute(self, **kwargs) -> ExecutionResult:
        file_path = kwargs.get("input_files", [])[0]
        chunk_size = kwargs.get("chunk_size", 1000)
        
        processed = 0
        with open(file_path, 'r') as f:
            for chunk in self._read_in_chunks(f, chunk_size):
                # 处理每个块
                processed += len(chunk)
        
        return ExecutionResult(
            success=True,
            metadata={"total_processed": processed}
        )
    
    def _read_in_chunks(self, file, chunk_size):
        """分块读取文件"""
        while True:
            chunk = [next(file, None) for _ in range(chunk_size)]
            chunk = [c for c in chunk if c is not None]
            if not chunk:
                break
            yield chunk
```

---

## 最佳实践

### 1. 错误处理

```python
def execute(self, **kwargs) -> ExecutionResult:
    try:
        # 你的逻辑
        result = self._process(kwargs)
        return ExecutionResult(success=True, data=result)
    except FileNotFoundError as e:
        return ExecutionResult(
            success=False,
            errors=[f"文件未找到: {e}"]
        )
    except ValueError as e:
        return ExecutionResult(
            success=False,
            errors=[f"数据格式错误: {e}"]
        )
    except Exception as e:
        return ExecutionResult(
            success=False,
            errors=[f"未知错误: {str(e)}"]
        )
```

### 2. 资源管理

```python
class ResourcePlugin(BasePlugin):
    def __init__(self):
        self._file_handle = None
        self._connection = None
    
    def execute(self, **kwargs) -> ExecutionResult:
        # 打开资源
        self._file_handle = open("temp.txt", "w")
        self._connection = create_connection()
        
        try:
            # 处理...
            return ExecutionResult(success=True)
        finally:
            # 确保资源被清理
            self._ensure_cleanup()
    
    def _ensure_cleanup(self):
        if self._file_handle and not self._file_handle.closed:
            self._file_handle.close()
        if self._connection:
            self._connection.close()
    
    def cleanup(self):
        self._ensure_cleanup()
```

### 3. 版本管理

```python
@property
def version(self) -> str:
    return "1.2.3"  # 使用语义化版本：主版本.次版本.修订号

# 版本变更说明：
# 1.0.0 - 初始版本
# 1.1.0 - 添加 CSV 支持
# 1.2.0 - 性能优化
# 1.2.1 - 修复编码问题
```

### 4. 文档字符串

```python
class MyPlugin(BasePlugin):
    """
    我的数据处理插件
    
    功能说明：
    - 从输入文件中提取数据
    - 进行格式转换
    - 输出结构化结果
    
    支持的输入格式：
    - Excel (.xlsx)
    - CSV (.csv)
    
    示例：
        plugin = MyPlugin()
        result = plugin.execute(input_files=["data.xlsx"])
    """
```

---

## API 参考速查

### BasePlugin 接口

```python
# 必须实现
@property
def name(self) -> str: ...

@property
def version(self) -> str: ...

@property
def plugin_type(self) -> str: ...

def execute(self, **kwargs) -> ExecutionResult: ...

def cleanup(self) -> None: ...

# 可选覆盖
@property
def capabilities(self) -> List[str]: ...

@property
def description(self) -> str: ...

@property
def author(self) -> str: ...

@property
def dependencies(self) -> List[str]: ...

def validate_input(self, **kwargs) -> List[str]: ...

def get_metadata(self) -> Dict[str, Any]: ...
```

### PluginLoader 接口

```python
loader = PluginLoader(logger=None)

# 加载方法
loader.load_from_file(file_path)      # -> BasePlugin
loader.load_from_directory(directory) # -> List[BasePlugin]
loader.load_from_package(package_name) # -> BasePlugin
loader.load_from_module(module_path)   # -> BasePlugin

# 辅助方法
loader.validate_plugin_class(cls)     # -> List[str]
loader.extract_metadata(file_path)    # -> PluginMetadata
loader.check_imports(file_path)       # -> List[str]
loader.check_dependencies(cls)        # -> Dict[str, bool]
```

### PluginRegistry 接口

```python
registry = PluginRegistry()

# 注册
registry.register(plugin)             # -> bool
registry.unregister(name)             # -> bool
registry.is_registered(name)          # -> bool

# 查询
registry.get_plugin(name)             # -> BasePlugin
registry.get_all_plugins()            # -> Dict[str, BasePlugin]
registry.get_plugins_by_type(type)    # -> List[BasePlugin]
registry.get_plugin_names()           # -> List[str]
registry.get_enabled_plugins()        # -> List[BasePlugin]

# 启用/禁用
registry.enable_plugin(name)          # -> bool
registry.disable_plugin(name)         # -> bool
registry.is_enabled(name)             # -> bool

# 元数据
registry.get_metadata(name)           # -> PluginMetadata
registry.get_all_metadata()           # -> Dict[str, PluginMetadata]
registry.get_plugins_info()           # -> List[Dict]

# 其他
registry.get_plugin_count()           # -> int
registry.clear()                      # -> None
```

---

## 相关文档

- [DocForge 总体架构](../README.md)
- [工作流编写指南](../../docforge_tutorial/02_工作流编写及使用.md)
- [插件开发教程](../../docforge_tutorial/03_插件编写及使用.md)
- [故障排除指南](../../docforge_tutorial/TROUBLESHOOTING_GUIDE.md)

---

*最后更新：2026年3月31日*
