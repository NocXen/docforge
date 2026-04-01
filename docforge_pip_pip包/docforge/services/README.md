# Services 层 - 核心业务服务

## 概述

Services 层是 DocForge 框架的**核心业务服务层**，充当框架的"大脑"。它负责协调各个组件（插件、存储、API等），编排和执行具体的业务逻辑。

### 架构定位

```
┌─────────────────────────────────────────────────────────┐
│                    API 层 (外部接口)                      │
├─────────────────────────────────────────────────────────┤
│              ▼▼▼  Services 层 (本层) ▼▼▼                │
│   工作流引擎 │ 插件管理 │ 项目管理 │ 文件管理 │ 日志     │
├─────────────────────────────────────────────────────────┤
│                    Plugins 层 (插件)                     │
├─────────────────────────────────────────────────────────┤
│                    Storage 层 (存储)                     │
└─────────────────────────────────────────────────────────┘
```

**职责分工**：
- **Plugins 层**：提供具体的功能实现（工具）
- **Storage 层**：提供数据持久化能力（存储）
- **Services 层**：决定"如何组合使用这些工具完成任务"（编排）

---

## 文件清单

```
services/
├── README.md              ← 本文件，服务层说明文档
├── __init__.py            ← 包初始化，导出公共接口
├── workflow_engine.py     ← 工作流引擎：编排和执行工作流
├── plugin_manager.py      ← 插件管理器：插件的发现、加载、生命周期管理
├── project_manager.py     ← 项目管理器：项目配置和状态管理
├── file_manager.py        ← 文件管理器：高级文件操作接口
└── logger.py              ← 日志管理器：分级日志记录系统
```

---

## 详细模块说明

### 1. workflow_engine.py - 工作流引擎

**模块路径**：`docforge.services.workflow_engine.WorkflowEngine`

**核心职责**：解析、调度和执行工作流定义，协调各个插件按顺序执行。

#### 主要功能

| 功能类别 | 方法 | 说明 |
|---------|------|------|
| **工作流定义管理** | `load_workflow(path)` | 从 JSON 文件加载工作流定义 |
| | `save_workflow(workflow, path)` | 保存工作流定义到文件 |
| | `validate_workflow(workflow)` | 验证工作流有效性，返回错误列表 |
| **执行控制** | `execute(workflow, ...)` | 执行完整工作流 |
| | `pause()` | 暂停当前执行 |
| | `resume()` | 恢复暂停的执行 |
| | `cancel()` | 取消当前执行 |
| **状态查询** | `get_status()` | 获取当前工作状态（IDLE/RUNNING/PAUSED/COMPLETED/FAILED/CANCELLED） |
| | `get_current_step()` | 获取当前执行步骤索引 |
| | `get_execution_history()` | 获取执行历史记录 |
| | `is_running()` / `is_paused()` | 检查运行状态 |

#### 工作流执行流程

```
1. 验证工作流定义（名称、步骤、插件引用）
2. 初始化执行状态（RUNNING）
3. 遍历每个步骤：
   a. 检查步骤是否启用（enabled）
   b. 检查取消/暂停请求
   c. 获取对应插件实例
   d. 准备参数（input_files, template_files, output_dir, config, data）
   e. 调用插件的 execute() 方法
   f. 收集执行结果和输出文件
   g. 将数据传递给下一步
4. 完成或失败处理
```

#### 状态机

```
IDLE ──execute──▶ RUNNING ──▶ COMPLETED (成功)
                        │
                        ├──▶ FAILED (失败)
                        │
                        ├──▶ PAUSED ──resume──▶ RUNNING
                        │         │
                        │         └──▶ CANCELLED
                        │
                        └──▶ CANCELLED (取消)
```

#### 使用示例

```python
from docforge.services import WorkflowEngine, PluginManager, Logger

# 初始化
logger = Logger()
plugin_manager = PluginManager(logger)
engine = WorkflowEngine(plugin_manager, logger)

# 加载并验证工作流
workflow = engine.load_workflow("workflow.json")
errors = engine.validate_workflow(workflow)
if errors:
    for err in errors:
        print(f"验证错误: {err}")

# 执行工作流
result = engine.execute(
    workflow=workflow,
    input_files=["data.xlsx"],
    template_files=["template.docx"],
    output_dir="./output",
    progress_callback=lambda progress, msg: print(f"{progress*100:.0f}% - {msg}")
)

print(f"成功: {result.success}")
print(f"输出文件: {result.output_files}")
print(f"耗时: {result.execution_time:.2f}秒")
```

---

### 2. plugin_manager.py - 插件管理器

**模块路径**：`docforge.services.plugin_manager.PluginManager`

**核心职责**：管理所有插件的完整生命周期，包括发现、加载、注册、卸载、重载和查询。

#### 主要功能

| 功能类别 | 方法 | 说明 |
|---------|------|------|
| **插件发现** | `discover_plugins(dir)` | 扫描目录发现插件文件，提取基本信息 |
| **插件加载** | `load_plugin(path)` | 动态加载单个插件文件 |
| | `load_all_plugins(dir)` | 批量加载目录下所有插件 |
| **插件卸载** | `unload_plugin(name)` | 卸载指定插件并清理资源 |
| | `reload_plugin(name)` | 热重载插件（卸载后重新加载） |
| **插件查询** | `get_plugin(name)` | 获取插件实例 |
| | `get_plugins_by_type(type)` | 按类型获取插件列表 |
| | `get_all_plugins()` | 获取所有已加载插件 |
| | `get_plugin_info(name)` | 获取插件元信息 |
| | `get_plugin_list()` | 获取所有插件信息列表 |
| **插件控制** | `enable_plugin(name)` | 启用插件 |
| | `disable_plugin(name)` | 禁用插件 |
| | `execute_plugin(name, **kwargs)` | 直接执行指定插件 |
| **依赖管理** | `check_dependencies(name)` | 检查插件依赖是否满足 |
| | `install_dependencies(name)` | 自动安装插件依赖（pip） |

#### 插件加载机制

```python
# 动态加载流程
1. 使用 importlib.util.spec_from_file_location() 创建模块规范
2. 使用 importlib.util.module_from_spec() 创建模块对象
3. 将模块注册到 sys.modules
4. 执行模块代码 (spec.loader.exec_module)
5. 遍历模块属性，查找继承自 BasePlugin 的类
6. 实例化插件类并注册到管理器
```

#### 插件类型

- `extractor` - 数据提取插件（从Excel等提取数据）
- `transformer` - 数据转换插件（处理、转换数据）
- `replacer` - 替换插件（将数据填入文档）
- `post_processor` - 后处理插件（生成后的处理）

#### 使用示例

```python
from docforge.services import PluginManager, Logger

logger = Logger()
pm = PluginManager(logger)

# 加载所有插件
results = pm.load_all_plugins("./plugins")
for name, success in results.items():
    status = "✓" if success else "✗"
    print(f"{status} {name}")

# 获取特定插件
plugin = pm.get_plugin("excel_extractor")
print(f"插件: {plugin.name}, 版本: {plugin.version}")

# 按类型获取插件
extractors = pm.get_plugins_by_type("extractor")

# 检查并安装依赖
deps = pm.check_dependencies("my_plugin")
for dep, satisfied in deps.items():
    if not satisfied:
        pm.install_dependencies("my_plugin")

# 直接执行插件
result = pm.execute_plugin("excel_extractor", 
    input_files=["data.xlsx"],
    template_files=[],
    output_dir="./output",
    config={}
)

# 热重载插件
pm.reload_plugin("excel_extractor")
```

---

### 3. project_manager.py - 项目管理器

**模块路径**：`docforge.services.project_manager.ProjectManager`

**核心职责**：管理项目的创建、保存、加载和配置，维护项目的完整状态。

#### 主要功能

| 功能类别 | 方法 | 说明 |
|---------|------|------|
| **项目生命周期** | `create_project(name, path)` | 创建新项目（自动创建目录结构） |
| | `open_project(path)` | 打开现有项目 |
| | `save_project()` | 保存当前项目 |
| | `close_project()` | 关闭当前项目 |
| **配置管理** | `get_project_config()` | 获取完整项目配置 |
| | `set_project_config(key, value)` | 设置配置项（支持点分隔嵌套键） |
| | `get_config(key, default)` | 获取配置值 |
| **输入文件** | `add_input_files(files)` | 添加输入文件 |
| | `remove_input_files(files)` | 移除输入文件 |
| | `get_input_files()` | 获取输入文件列表 |
| | `clear_input_files()` | 清空输入文件 |
| **模板文件** | `add_template_files(files)` | 添加模板文件 |
| | `get_template_files()` | 获取模板文件列表 |
| **输出管理** | `set_output_directory(dir)` | 设置输出目录 |
| | `get_output_directory()` | 获取输出目录 |
| **工作流** | `set_workflow(name, path)` | 设置关联的工作流 |
| | `get_workflow()` | 获取工作流配置 |
| **状态查询** | `is_project_open()` | 检查是否有项目打开 |
| | `is_modified()` | 检查项目是否有未保存修改 |
| | `get_project_name()` | 获取项目名称 |
| | `get_project_modified_time()` | 获取最后修改时间 |

#### 项目目录结构

```
my_project/
├── project.json          ← 项目配置文件（自动生成）
├── input/                ← 输入文件目录
├── templates/            ← 模板文件目录
├── output/               ← 输出文件目录
└── workflows/            ← 工作流定义目录
```

#### 项目配置格式 (project.json)

```json
{
    "name": "我的项目",
    "version": "1.0.0",
    "created_at": "2026-03-27T10:00:00",
    "updated_at": "2026-03-27T10:30:00",
    "input": {
        "files": ["data1.xlsx", "data2.xlsx"],
        "directory": "/path/to/my_project/input"
    },
    "templates": {
        "files": ["template.docx"],
        "directory": "/path/to/my_project/templates"
    },
    "output": {
        "directory": "/path/to/my_project/output"
    },
    "workflow": {
        "name": "my_workflow",
        "path": "/path/to/my_project/workflows/workflow.json"
    }
}
```

#### 使用示例

```python
from docforge.services import ProjectManager, Logger

logger = Logger()
pm = ProjectManager(logger)

# 创建新项目
pm.create_project("文档生成项目", "./my_project")

# 添加文件
pm.add_input_files(["data1.xlsx", "data2.xlsx"])
pm.add_template_files(["template.docx"])
pm.set_output_directory("./my_project/output/custom")

# 设置工作流
pm.set_workflow("标准流程", "./workflows/standard.json")

# 获取配置
files = pm.get_input_files()
workflow = pm.get_workflow()

# 保存并关闭
pm.save_project()
pm.close_project()
```

---

### 4. file_manager.py - 文件管理器

**模块路径**：`docforge.services.file_manager.FileManager`

**核心职责**：提供文件操作的高级接口，封装常用的文件处理任务。

#### 主要功能

| 功能类别 | 方法 | 说明 |
|---------|------|------|
| **文件信息** | `get_file_info(path)` | 获取文件详细信息（名称、扩展名、大小、修改时间） |
| | `get_files_info(paths)` | 批量获取文件信息 |
| | `calculate_hash(path, algorithm)` | 计算文件哈希值（md5/sha1/sha256） |
| **目录操作** | `ensure_directory(dir)` | 确保目录存在，不存在则创建 |
| | `list_files(dir, extensions, recursive)` | 列出目录下的文件（支持扩展名过滤和递归） |
| **文件备份** | `backup_file(path, backup_dir)` | 备份文件（自动添加时间戳） |
| | `restore_backup(backup, target)` | 从备份恢复文件 |
| **批量操作** | `batch_rename(files, pattern)` | 批量重命名（支持占位符） |
| | `batch_move(files, target_dir)` | 批量移动文件 |
| **临时文件** | `create_temp_file(suffix, prefix)` | 创建临时文件 |
| | `create_temp_directory(prefix)` | 创建临时目录 |
| | `cleanup_temp(path)` | 清理临时文件/目录 |
| **路径验证** | `validate_file_path(path, must_exist)` | 验证文件路径 |
| | `validate_directory_path(path, must_exist)` | 验证目录路径 |
| | `check_file_writable(path)` | 检查文件是否可写 |

#### 批量重命名占位符

| 占位符 | 说明 | 示例 |
|--------|------|------|
| `{index}` | 序号（从1开始） | `001`, `002`, `003` |
| `{name}` | 原文件名（不含扩展名） | `data` |
| `{ext}` | 扩展名 | `.xlsx` |
| `{date}` | 当前日期 | `20260327` |

#### 使用示例

```python
from docforge.services import FileManager, Logger

logger = Logger()
fm = FileManager(logger)

# 获取文件信息
info = fm.get_file_info("data.xlsx")
print(f"名称: {info.name}, 大小: {info.size} 字节, 扩展名: {info.extension}")

# 计算文件哈希
md5 = fm.calculate_hash("data.xlsx", "md5")
sha256 = fm.calculate_hash("data.xlsx", "sha256")

# 列出文件
excel_files = fm.list_files("./input", extensions=[".xlsx", ".xls"], recursive=True)

# 备份文件
backup_path = fm.backup_file("important.docx", "./backups")

# 批量重命名
files = fm.list_files("./output", extensions=[".docx"])
renamed = fm.batch_rename(files, "文档_{index}_{date}")
for old, new in renamed.items():
    print(f"{old} -> {new}")

# 临时文件管理
temp_file = fm.create_temp_file(suffix=".tmp")
# ... 使用临时文件 ...
fm.cleanup_temp(temp_file)

# 路径验证
if fm.validate_file_path("data.xlsx", must_exist=True):
    print("文件存在")
if fm.check_file_writable("./output/result.docx"):
    print("文件可写")
```

---

### 5. logger.py - 日志管理器

**模块路径**：`docforge.services.logger.Logger`

**核心职责**：提供分级日志记录系统，支持多输出目标（控制台、文件）和回调通知。

#### 主要功能

| 功能类别 | 方法 | 说明 |
|---------|------|------|
| **日志记录** | `debug(message, **kwargs)` | 调试级别日志 |
| | `info(message, **kwargs)` | 信息级别日志 |
| | `warning(message, **kwargs)` | 警告级别日志 |
| | `error(message, **kwargs)` | 错误级别日志 |
| | `critical(message, **kwargs)` | 严重错误级别日志 |
| **配置** | `set_level(level)` | 设置日志级别 |
| | `add_file_handler(path, max_size, backup_count)` | 添加文件输出（支持日志轮转） |
| **回调** | `add_callback(callback)` | 添加日志回调函数 |
| | `remove_callback(callback)` | 移除回调函数 |
| **其他** | `clear()` | 清空所有处理器 |
| | `get_logs(level, limit)` | 获取日志记录（预留接口） |

#### 日志级别

| 级别 | 常量 | 说明 | 使用场景 |
|------|------|------|---------|
| DEBUG | `LogLevel.DEBUG` | 调试信息 | 开发调试，详细执行过程 |
| INFO | `LogLevel.INFO` | 一般信息 | 正常操作记录 |
| WARNING | `LogLevel.WARNING` | 警告信息 | 潜在问题，不影响运行 |
| ERROR | `LogLevel.ERROR` | 错误信息 | 操作失败，需要处理 |
| CRITICAL | `LogLevel.CRITICAL` | 严重错误 | 系统级错误，可能终止运行 |

#### 日志格式

```
# 控制台格式
2026-03-27 10:30:00 - INFO - 工作流已加载: my_workflow

# 文件格式（包含logger名称）
2026-03-27 10:30:00 - docforge - INFO - 工作流已加载: my_workflow

# 带额外参数
2026-03-27 10:30:00 - ERROR - 插件执行失败 [plugin=excel_extractor, error=FileNotFoundError]
```

#### 日志轮转

使用 `RotatingFileHandler` 实现自动日志轮转：
- 当日志文件达到 `max_size` 时自动切割
- 保留 `backup_count` 个历史备份文件
- 旧文件自动添加 `.1`, `.2`, `.3` 等后缀

#### 使用示例

```python
from docforge.services import Logger
from docforge.constants import LogLevel

# 创建日志器
logger = Logger("my_app")

# 设置日志级别
logger.set_level(LogLevel.DEBUG)

# 添加文件输出（10MB轮转，保留5个备份）
logger.add_file_handler("app.log", max_size=10485760, backup_count=5)

# 记录日志
logger.debug("调试信息", module="workflow", step=1)
logger.info("工作流开始执行")
logger.warning("插件未找到，使用默认实现")
logger.error("文件处理失败", file="data.xlsx", reason="格式错误")
logger.critical("系统异常，需要重启")

# 添加回调（实时通知）
def log_callback(level, message):
    # 可以推送到前端、写入数据库等
    print(f"[回调] {level}: {message}")

callback_id = logger.add_callback(log_callback)

# 移除回调
logger.remove_callback(log_callback)
```

---

## 服务之间的依赖关系

```
                    ┌─────────────────────────────────────┐
                    │         WorkflowEngine              │
                    │    (工作流引擎 - 核心编排)            │
                    └──────────┬──────────────────────────┘
                               │ 依赖
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
┌───────────────────┐ ┌───────────────┐ ┌───────────────────┐
│   PluginManager   │ │ProjectManager │ │   FileManager     │
│   (插件管理)       │ │  (项目管理)    │ │   (文件管理)       │
└─────────┬─────────┘ └───────┬───────┘ └─────────┬─────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │     Logger      │
                    │   (日志服务)     │
                    │   ← 所有服务共用  │
                    └─────────────────┘
```

**依赖说明**：
- `WorkflowEngine` 依赖 `PluginManager` 获取和执行插件
- 所有服务都可选依赖 `Logger` 进行日志记录
- 服务之间可以相互组合使用

---

## 完整使用示例

```python
from docforge.services import (
    WorkflowEngine,
    PluginManager,
    ProjectManager,
    FileManager,
    Logger
)
from docforge.constants import LogLevel

# ========== 1. 初始化服务 ==========
logger = Logger("docforge")
logger.set_level(LogLevel.INFO)
logger.add_file_handler("docforge.log")

plugin_manager = PluginManager(logger)
project_manager = ProjectManager(logger)
file_manager = FileManager(logger)
workflow_engine = WorkflowEngine(plugin_manager, logger)

# ========== 2. 加载插件 ==========
results = plugin_manager.load_all_plugins("./plugins")
print(f"插件加载: {sum(results.values())}/{len(results)} 成功")

# ========== 3. 创建或打开项目 ==========
if not project_manager.is_project_open():
    project_manager.create_project("文档生成", "./project")
    project_manager.add_input_files(["./data/students.xlsx"])
    project_manager.add_template_files(["./templates/certificate.docx"])
    project_manager.set_output_directory("./project/output")
    project_manager.set_workflow("证书生成", "./workflows/certificate.json")
    project_manager.save_project()

# ========== 4. 加载并执行工作流 ==========
workflow = workflow_engine.load_workflow("./workflows/certificate.json")

# 验证工作流
errors = workflow_engine.validate_workflow(workflow)
if errors:
    for err in errors:
        logger.error(f"工作流验证: {err}")

# 执行
result = workflow_engine.execute(
    workflow=workflow,
    input_files=project_manager.get_input_files(),
    template_files=project_manager.get_template_files(),
    output_dir=project_manager.get_output_directory(),
    progress_callback=lambda p, m: logger.info(f"进度: {p*100:.0f}% - {m}")
)

# ========== 5. 处理结果 ==========
if result.success:
    logger.info(f"执行完成! 生成 {len(result.output_files)} 个文件")
    logger.info(f"耗时: {result.execution_time:.2f} 秒")
else:
    logger.error(f"执行失败: {result.errors}")
    if result.warnings:
        logger.warning(f"警告信息: {result.warnings}")

# ========== 6. 清理 ==========
project_manager.save_project()
project_manager.close_project()
```

---

## 扩展指南

### 添加新的服务

1. 在 `services/` 目录下创建新的 Python 文件
2. 定义服务类，建议接收 `logger` 作为可选依赖
3. 在 `__init__.py` 中导入并导出新服务
4. 在需要的地方导入和使用

```python
# services/my_service.py
class MyService:
    def __init__(self, logger=None):
        self.logger = logger
    
    def do_something(self):
        if self.logger:
            self.logger.info("执行操作")
        # 实现逻辑...

# services/__init__.py
from .my_service import MyService
__all__ = [..., "MyService"]
```

---

## 常见问题

### Q: 工作流执行失败了，怎么调试？
A: 
1. 查看日志文件，定位错误信息和堆栈
2. 使用 `workflow_engine.validate_workflow()` 验证工作流定义
3. 检查工作流 JSON 格式是否正确
4. 确认引用的插件名称与已加载插件匹配
5. 检查插件的 `execute()` 方法参数是否正确

### Q: 插件加载失败怎么办？
A:
1. 检查插件文件语法是否正确（`python -m py_compile plugin.py`）
2. 确认插件类继承自 `BasePlugin`
3. 检查插件是否实现了必需的属性和方法（`name`, `version`, `plugin_type`, `execute()`）
4. 使用 `plugin_manager.check_dependencies()` 检查依赖
5. 查看 Logger 的错误日志获取详细原因

### Q: 如何实现插件热重载？
A:
使用 `plugin_manager.reload_plugin("plugin_name")` 可以在不重启程序的情况下重新加载插件。适用于开发调试场景。

### Q: 日志文件太大怎么办？
A:
使用 `add_file_handler()` 时设置合适的 `max_size` 和 `backup_count` 参数，系统会自动进行日志轮转。

### Q: 如何添加新的服务？
A:
1. 在 `services/` 目录下创建新的 Python 文件
2. 定义服务类，接收需要的依赖（如 `logger`）
3. 在 `__init__.py` 中导入并导出新服务
4. 在需要的地方导入和使用

---

*最后更新：2026年3月31日*
