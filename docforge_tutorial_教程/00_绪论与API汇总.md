# DocForge 教程 00：绪论与API汇总

## 1. 软件概述

DocForge 是一个**办公与数据处理自动化框架**，旨在帮助用户：
- 从 Excel、Word 等文件中提取数据
- 处理数据（分割、格式化、过滤等）
- 将数据填入模板，生成新文件
- 批量处理成百上千份文档

**核心特点**：
- 完全模块化设计，功能以插件形式存在
- 支持自定义插件开发
- 工作流驱动，可灵活组合处理步骤
- 提供 Python API，便于集成和扩展

## 2. 核心概念

### 2.1 工作流（Workflow）
工作流是处理流程的“配方”，定义了一系列步骤，每个步骤调用一个插件。例如：
1. 从 Excel 提取数据
2. 分割文本字段
3. 将数据填入 Word 模板

### 2.2 插件（Plugin）
插件是完成具体任务的小工具，分为四种类型：
- **提取器（Extractor）**：从文件提取数据
- **转换器（Transformer）**：转换数据结构
- **替换器（Replacer）**：将数据填入模板，生成输出文件
- **后处理器（PostProcessor）**：对输出文件进行后处理（如合并、压缩）

### 2.3 项目（Project）
项目是一次任务的所有配置，包括输入文件、模板文件、输出目录、工作流等。

### 2.4 数据结构
框架内部使用统一的数据结构：`Dict[str, List[str]]`，即字段名到值列表的映射。例如：
```python
{
    "公司名称": ["ABC有限公司", "BCD有限公司"],
    "职位": ["工程师", "会计"]
}
```

## 3. API 汇总

### 3.1 核心 API（CoreAPI）
供 GUI 或主程序调用，封装所有核心功能。

#### 初始化与生命周期
| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `initialize(config_path=None)` | `config_path`: 配置文件路径（可选） | `bool`: 是否成功 | 初始化框架 |
| `shutdown()` | 无 | 无 | 关闭框架，释放资源 |

#### 项目管理
| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `create_project(name, path)` | `name`: 项目名称<br>`path`: 项目路径 | `bool`: 是否成功 | 创建新项目 |
| `open_project(project_path)` | `project_path`: 项目文件路径 | `bool`: 是否成功 | 打开现有项目 |
| `save_project()` | 无 | `bool`: 是否成功 | 保存当前项目 |
| `close_project()` | 无 | `bool`: 是否成功 | 关闭当前项目 |
| `get_project_config()` | 无 | `Dict[str, Any]`: 项目配置 | 获取项目配置 |

#### 文件管理
| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `add_input_files(files)` | `files`: 文件路径列表 | `bool`: 是否成功 | 添加输入文件 |
| `get_input_files()` | 无 | `List[str]`: 输入文件列表 | 获取输入文件列表 |
| `clear_input_files()` | 无 | `bool`: 是否成功 | 清空输入文件 |
| `add_template_files(files)` | `files`: 文件路径列表 | `bool`: 是否成功 | 添加模板文件 |
| `get_template_files()` | 无 | `List[str]`: 模板文件列表 | 获取模板文件列表 |
| `set_output_directory(directory)` | `directory`: 输出目录路径 | `bool`: 是否成功 | 设置输出目录 |
| `get_output_directory()` | 无 | `str`: 输出目录路径 | 获取输出目录 |

#### 工作流管理
| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `load_workflow(workflow_path)` | `workflow_path`: 工作流文件路径 | `bool`: 是否成功 | 加载工作流 |
| `get_workflow_list()` | 无 | `List[str]`: 工作流名称列表 | 获取工作流列表 |
| `execute_workflow(workflow_name, progress_callback=None)` | `workflow_name`: 工作流名称<br>`progress_callback`: 进度回调函数（可选） | `ExecutionResult`: 执行结果 | 执行工作流 |
| `cancel_execution()` | 无 | `bool`: 是否成功 | 取消正在执行的工作流 |
| `get_execution_status()` | 无 | `WorkflowStatus`: 当前状态 | 获取执行状态 |

#### 插件管理
| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `get_plugin_list()` | 无 | `List[Dict[str, Any]]`: 插件信息列表 | 获取插件列表 |
| `enable_plugin(plugin_name)` | `plugin_name`: 插件名称 | `bool`: 是否成功 | 启用插件 |
| `disable_plugin(plugin_name)` | `plugin_name`: 插件名称 | `bool`: 是否成功 | 禁用插件 |
| `reload_plugins()` | 无 | `Dict[str, bool]`: 插件名->是否成功 | 重新加载所有插件 |

#### 日志管理
| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `get_logs(level=None, limit=100)` | `level`: 日志级别过滤（可选）<br>`limit`: 返回数量限制 | `List[Dict]`: 日志记录列表 | 获取日志 |
| `clear_logs()` | 无 | `bool`: 是否成功 | 清空日志 |

### 3.2 插件 API（PluginAPI）
供插件调用，提供插件运行时所需的环境访问。

#### 日志接口
| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `log_debug(message)` | `message`: 日志消息 | 无 | 记录调试日志 |
| `log_info(message)` | `message`: 日志消息 | 无 | 记录信息日志 |
| `log_warning(message)` | `message`: 日志消息 | 无 | 记录警告日志 |
| `log_error(message)` | `message`: 日志消息 | 无 | 记录错误日志 |

#### 文件接口
| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `read_file(file_path)` | `file_path`: 文件路径 | `Optional[str]`: 文件内容，失败返回 None | 读取文件内容 |
| `write_file(file_path, content)` | `file_path`: 文件路径<br>`content`: 文件内容 | `bool`: 是否成功 | 写入文件内容 |
| `file_exists(file_path)` | `file_path`: 文件路径 | `bool`: 是否存在 | 检查文件是否存在 |
| `get_file_info(file_path)` | `file_path`: 文件路径 | `Optional[Dict[str, Any]]`: 文件信息 | 获取文件信息 |

#### 数据接口
| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `get_input_data()` | 无 | `Optional[DataDict]`: 输入数据 | 获取输入数据 |
| `set_output_data(data)` | `data`: 输出数据 | 无 | 设置输出数据 |

#### 配置接口
| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `get_config(key, default=None)` | `key`: 配置键<br>`default`: 默认值 | `Any`: 配置值 | 获取配置值 |
| `get_plugin_config(key, default=None)` | `key`: 配置键<br>`default`: 默认值 | `Any`: 配置值 | 获取插件专用配置 |

#### 缓存接口
| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `cache_get(key)` | `key`: 缓存键 | `Optional[Any]`: 缓存值 | 获取缓存值 |
| `cache_set(key, value, ttl=3600)` | `key`: 缓存键<br>`value`: 缓存值<br>`ttl`: 过期时间（秒） | `bool`: 是否成功 | 设置缓存值 |

#### 数据库接口
| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `db_query(sql, params=None)` | `sql`: SQL 语句<br>`params`: 参数 | `List[Dict]`: 查询结果 | 执行数据库查询 |
| `db_insert(table, data)` | `table`: 表名<br>`data`: 数据字典 | `Optional[int]`: 插入的行 ID | 插入数据库记录 |

#### 事件接口
| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `emit_event(event_name, data=None)` | `event_name`: 事件名称<br>`data`: 事件数据 | 无 | 发送事件 |
| `subscribe_event(event_name, callback)` | `event_name`: 事件名称<br>`callback`: 回调函数 | `str`: 订阅 ID | 订阅事件 |

#### 工具接口
| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `get_temp_directory()` | 无 | `str`: 临时目录路径 | 获取临时目录 |
| `create_temp_file(suffix="")` | `suffix`: 文件后缀 | `str`: 临时文件路径 | 创建临时文件 |

### 3.3 执行结果类型（ExecutionResult）
工作流或插件执行后返回的对象，包含以下属性：
- `success: bool`：是否执行成功
- `data: Optional[DataDict]`：输出数据
- `output_files: List[Path]`：输出文件路径列表
- `errors: List[str]`：错误信息列表
- `warnings: List[str]`：警告信息列表
- `execution_time: float`：执行时间（秒）

### 3.4 工作流状态（WorkflowStatus）
表示工作流执行状态的枚举：
- `IDLE`：空闲
- `RUNNING`：运行中
- `PAUSED`：暂停
- `COMPLETED`：已完成
- `FAILED`：失败
- `CANCELLED`：已取消

## 4. 快速开始

### 4.1 安装
```bash
# 安装依赖
pip install pandas openpyxl python-docx odfpy

# 克隆或下载项目
git clone <repository_url>
cd docforge
```

### 4.2 最简示例
```python
from docforge.api.core_api import CoreAPI

# 1. 初始化
api = CoreAPI()
api.initialize()

# 2. 创建项目
api.create_project("我的项目", "./my_project")

# 3. 添加输入文件和模板
api.add_input_files(["data.xlsx"])
api.add_template_files(["template.docx"])

# 4. 设置输出目录
api.set_output_directory("./output")

# 5. 加载工作流
api.load_workflow("workflow.json")

# 6. 执行工作流
result = api.execute_workflow("my_workflow")

if result.success:
    print(f"生成文件: {result.output_files}")
else:
    print(f"错误: {result.errors}")

# 7. 关闭
api.shutdown()
```

## 5. 目录结构
```
docforge/
├── docforge/          # 核心框架
│   ├── api/                # API 接口
│   ├── plugins/            # 插件系统
│   ├── services/           # 服务层
│   ├── storage/            # 数据层
│   └── utils/              # 工具函数
├── docforge_instance/      # 实例与测试
├── docforge_plugins/       # 官方插件
├── OTHERS/                 # 开发文档
└── 教程文件...
```

## 6. 下一步
- 阅读 [01_实例编写及使用.md](01_实例编写及使用.md) 了解如何编写和使用实例
- 阅读 [02_工作流编写及使用.md](02_工作流编写及使用.md) 了解如何编写工作流
- 阅读 [03_插件编写及使用.md](03_插件编写及使用.md) 了解如何开发插件

---
*最后更新：2026年3月30日*