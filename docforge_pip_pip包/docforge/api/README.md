# API层 - 接口层说明

## 这一层是干什么的？

API层提供**对外暴露的统一接口**。它是框架的"门面"，GUI和其他外部代码通过这一层调用框架功能。

简单来说：
- **其他层**是内部实现
- **api层**是对外窗口，隐藏内部复杂性

## 架构定位

```
┌─────────────────────────────────────────────────────────────────┐
│                         外部调用者                               │
│                    (GUI / 脚本 / 其他程序)                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API 层 (本层)                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  CoreAPI    │  │  PluginAPI  │  │       EventBus          │  │
│  │ (核心API)   │  │ (插件API)   │  │     (事件总线)           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    内部实现层                                    │
│         (Services / Plugins / Storage / Utils)                  │
└─────────────────────────────────────────────────────────────────┘
```

## 文件清单

```
api/
├── README.md              ← 你现在看的这个文件
├── __init__.py            ← 包初始化，导出公共接口
├── core_api.py            ← 核心API（GUI调用入口）
├── plugin_api.py          ← 插件API（插件调用接口）
└── event_bus.py           ← 事件总线（组件间通信）
```

## 各文件职责

### 1. core_api.py - 核心API

**作用**：提供GUI层调用的主要接口

**核心功能**：
- 初始化框架
- 项目管理（创建、打开、保存）
- 文件管理（添加、获取、排序）
- 工作流执行
- 插件管理

**类比**：就像电视遥控器，按按钮就能完成操作，不需要知道内部电路

**依赖的其他层**：
- `services` 层：Logger, FileManager, PluginManager, ProjectManager, WorkflowEngine
- `storage` 层：DatabaseManager, ConfigManager, CacheManager

### 2. plugin_api.py - 插件API

**作用**：提供插件调用的接口

**核心功能**：
- 日志记录
- 文件读写
- 数据访问
- 配置获取
- 事件发送

**类比**：就像插件的"工具箱"，插件可以用它完成各种操作

**依赖的其他层**：
- `types.py`：数据结构定义

### 3. event_bus.py - 事件总线

**作用**：提供组件间的事件通信机制

**核心功能**：
- 发布事件
- 订阅事件
- 取消订阅
- 异步事件处理

**类比**：就像公司的公告板，谁都可以贴通知，谁都可以看通知

**依赖**：无外部依赖，独立实现

## API使用流程

### GUI调用流程

```
GUI界面
   ↓
CoreAPI (api/core_api.py)
   ↓
┌─────────────────────────────────────┐
│  Services层                         │
│  (WorkflowEngine, PluginManager...) │
└─────────────────────────────────────┘
   ↓
┌─────────────────────────────────────┐
│  Plugins层 / Storage层 / Utils层    │
└─────────────────────────────────────┘
```

### 插件调用流程

```
插件代码
   ↓
PluginAPI (api/plugin_api.py)
   ↓
┌─────────────────────────────────────┐
│  Services层                         │
│  (Logger, FileManager...)          │
└─────────────────────────────────────┘
```

## CoreAPI 详细说明

### 初始化与生命周期

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `__init__()` | 创建API实例 | - |
| `initialize(config_path)` | 初始化框架 | `bool`: 是否成功 |
| `shutdown()` | 关闭框架 | `None` |

### 项目管理

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `create_project(name, path)` | 创建项目 | `name`: 项目名称<br>`path`: 项目路径 | `bool` |
| `open_project(project_path)` | 打开项目 | `project_path`: 项目路径 | `bool` |
| `save_project()` | 保存项目 | - | `bool` |
| `close_project()` | 关闭项目 | - | `bool` |
| `get_project_config()` | 获取项目配置 | - | `Dict` |

### 文件管理

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `add_input_files(files)` | 添加输入文件 | `files`: 文件路径列表 | `bool` |
| `get_input_files()` | 获取输入文件列表 | - | `List[str]` |
| `clear_input_files()` | 清空输入文件 | - | `bool` |
| `add_template_files(files)` | 添加模板文件 | `files`: 文件路径列表 | `bool` |
| `get_template_files()` | 获取模板文件列表 | - | `List[str]` |
| `set_output_directory(directory)` | 设置输出目录 | `directory`: 目录路径 | `bool` |
| `get_output_directory()` | 获取输出目录 | - | `str` |

### 工作流管理

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `load_workflow(workflow_path)` | 加载工作流 | `workflow_path`: 工作流文件路径 | `bool` |
| `get_workflow_list()` | 获取工作流列表 | - | `List[str]` |
| `execute_workflow(workflow_name, progress_callback)` | 执行工作流 | `workflow_name`: 工作流名称<br>`progress_callback`: 进度回调 | `ExecutionResult` |
| `cancel_execution()` | 取消执行 | - | `bool` |
| `get_execution_status()` | 获取执行状态 | - | `WorkflowStatus` |

### 插件管理

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `get_plugin_list()` | 获取插件列表 | - | `List[Dict]` |
| `enable_plugin(plugin_name)` | 启用插件 | `plugin_name`: 插件名称 | `bool` |
| `disable_plugin(plugin_name)` | 禁用插件 | `plugin_name`: 插件名称 | `bool` |
| `reload_plugins()` | 重新加载所有插件 | - | `Dict[str, bool]` |

### 日志管理

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `get_logs(level, limit)` | 获取日志 | `level`: 日志级别<br>`limit`: 返回数量 | `List[Dict]` |
| `clear_logs()` | 清空日志 | - | `bool` |

## PluginAPI 详细说明

### 日志接口

| 方法 | 说明 | 参数 |
|------|------|------|
| `log_debug(message)` | 记录调试日志 | `message`: 日志消息 |
| `log_info(message)` | 记录信息日志 | `message`: 日志消息 |
| `log_warning(message)` | 记录警告日志 | `message`: 日志消息 |
| `log_error(message)` | 记录错误日志 | `message`: 日志消息 |

### 文件接口

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `read_file(file_path)` | 读取文件内容 | `file_path`: 文件路径 | `Optional[str]` |
| `write_file(file_path, content)` | 写入文件内容 | `file_path`: 文件路径<br>`content`: 文件内容 | `bool` |
| `file_exists(file_path)` | 检查文件是否存在 | `file_path`: 文件路径 | `bool` |
| `get_file_info(file_path)` | 获取文件信息 | `file_path`: 文件路径 | `Optional[Dict]` |

### 数据接口

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `get_input_data()` | 获取输入数据 | `Optional[DataDict]` |
| `set_output_data(data)` | 设置输出数据 | `None` |

### 配置接口

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `get_config(key, default)` | 获取配置值 | `key`: 配置键<br>`default`: 默认值 | `Any` |
| `get_plugin_config(key, default)` | 获取插件专用配置 | `key`: 配置键<br>`default`: 默认值 | `Any` |

### 缓存接口

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `cache_get(key)` | 获取缓存值 | `key`: 缓存键 | `Optional[Any]` |
| `cache_set(key, value, ttl)` | 设置缓存值 | `key`: 缓存键<br>`value`: 缓存值<br>`ttl`: 过期时间(秒) | `bool` |

### 数据库接口

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `db_query(sql, params)` | 执行数据库查询 | `sql`: SQL语句<br>`params`: 参数 | `List[Dict]` |
| `db_insert(table, data)` | 插入数据库记录 | `table`: 表名<br>`data`: 数据 | `Optional[int]` |

### 事件接口

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `emit_event(event_name, data)` | 发送事件 | `event_name`: 事件名称<br>`data`: 事件数据 | `None` |
| `subscribe_event(event_name, callback)` | 订阅事件 | `event_name`: 事件名称<br>`callback`: 回调函数 | `str` |

### 工具接口

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `get_temp_directory()` | 获取临时目录 | - | `str` |
| `create_temp_file(suffix)` | 创建临时文件 | `suffix`: 文件后缀 | `str` |

## EventBus 详细说明

### Event 事件对象

| 属性 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 事件名称 |
| `data` | `Any` | 事件数据 |
| `source` | `str` | 事件来源 |
| `timestamp` | `datetime` | 事件时间戳 |

### EventBus 方法

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `subscribe(event_name, callback)` | 订阅事件 | `event_name`: 事件名称<br>`callback`: 回调函数 | `str`: 订阅ID |
| `unsubscribe(subscription_id)` | 取消订阅 | `subscription_id`: 订阅ID | `bool` |
| `unsubscribe_all(event_name)` | 取消所有订阅 | `event_name`: 事件名称(可选) | `int`: 取消数量 |
| `publish(event)` | 发布事件(同步) | `event`: 事件对象 | `None` |
| `publish_async(event)` | 异步发布事件 | `event`: 事件对象 | `None` |
| `get_subscribers(event_name)` | 获取事件的订阅者 | `event_name`: 事件名称 | `List[str]` |
| `get_subscription_count()` | 获取订阅总数 | - | `int` |
| `get_event_names()` | 获取所有已订阅的事件名称 | - | `List[str]` |
| `has_subscribers(event_name)` | 检查事件是否有订阅者 | `event_name`: 事件名称 | `bool` |

## 使用示例

### CoreAPI 使用

```python
from docforge.api.core_api import CoreAPI

# 创建API实例
api = CoreAPI()

# 初始化
api.initialize()

# 创建项目
api.create_project("我的项目", "./my_project")

# 添加输入文件
api.add_input_files(["data1.xlsx", "data2.xlsx"])

# 添加模板文件
api.add_template_files(["template.docx"])

# 设置输出目录
api.set_output_directory("./output")

# 执行工作流
result = api.execute_workflow("my_workflow")

if result.success:
    print(f"处理完成，生成了 {len(result.output_files)} 个文件")
else:
    print(f"处理失败: {result.errors}")
```

### PluginAPI 使用（在插件中）

```python
from docforge.plugins.base import BasePlugin
from docforge.types import ExecutionResult

class MyPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "my_plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def plugin_type(self) -> str:
        return "extractor"
    
    def execute(self, **kwargs) -> ExecutionResult:
        # 获取PluginAPI
        plugin_api = kwargs.get("plugin_api")
        
        if plugin_api:
            # 记录日志
            plugin_api.log_info("开始执行插件")
            
            # 读取文件
            content = plugin_api.read_file("input.txt")
            
            # 获取配置
            config = plugin_api.get_config("my_setting", "default")
            
            # 发送事件
            plugin_api.emit_event("processing_started", {"file": "input.txt"})
        
        # 处理逻辑...
        data = {"字段1": ["值1", "值2"]}
        
        return ExecutionResult(success=True, data=data)
    
    def cleanup(self):
        pass
```

### EventBus 使用

```python
from docforge.api.event_bus import EventBus, Event

# 创建事件总线
event_bus = EventBus()

# 定义事件处理函数
def on_file_processed(event: Event):
    print(f"文件处理完成: {event.data}")

# 订阅事件
subscription_id = event_bus.subscribe("file_processed", on_file_processed)

# 发布事件
event_bus.publish(Event(
    name="file_processed",
    data={"file": "output.docx"},
    source="workflow_engine"
))

# 取消订阅
event_bus.unsubscribe(subscription_id)
```

## API设计原则

1. **简单易用**：GUI开发者不需要了解内部实现
2. **统一接口**：所有功能通过同一套API访问
3. **错误处理**：API内部处理异常，返回明确的结果
4. **向后兼容**：API版本升级时保持兼容性
5. **文档完善**：每个方法都有详细的文档说明

## 常见问题

### Q: 如何添加新的API方法？
A: 在相应的API类中添加方法，并更新文档

### Q: API方法返回什么？
A: 通常返回 `ExecutionResult` 或具体值，失败时返回 `None` 或 `False`

### Q: 如何处理异步操作？
A: 使用 `EventBus` 发布事件，GUI监听事件更新界面

### Q: 插件如何获取文件列表？
A: 通过 `PluginAPI` 的 `get_input_data()` 方法

### Q: 如何调试API调用？
A: 查看日志文件，或使用 `Logger` 的回调功能

### Q: CoreAPI 和 PluginAPI 有什么区别？
A: 
- **CoreAPI**：供GUI层使用，管理整个框架的生命周期
- **PluginAPI**：供插件使用，提供插件执行时需要的工具

### Q: EventBus 支持通配符吗？
A: 是的，可以使用 `*` 订阅所有事件

## 相关资源

- 📖 [服务层详细文档](../services/README.md)
- 📖 [插件层详细文档](../plugins/README.md)
- 📖 [存储层详细文档](../storage/README.md)
- 📖 [工具层详细文档](../utils/README.md)

---

*最后更新：2026年3月31日*