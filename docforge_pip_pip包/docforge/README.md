# DocForge 核心框架 - 使用说明

## 什么是这个框架？

这是一个**办公与数据处理自动化框架**。简单来说，它可以帮你：
- 从Excel、Word等文件中提取数据
- 处理这些数据（分割、格式化、过滤等）
- 把数据填入模板，生成新文件
- 批量处理成百上千份文档

## 📦 安装方式

### 方式一：从 PyPI 安装（推荐）

```bash
pip install docforge
```

### 方式二：从源码安装

```bash
# 克隆仓库
git clone https://github.com/nocxen/docforge.git
cd docforge

# 安装
pip install -e .
```

### 方式三：开发模式安装

```bash
# 克隆仓库
git clone https://github.com/nocxen/docforge.git
cd docforge

# 安装开发依赖
pip install -e ".[dev]"
```

### 验证安装

```bash
# 检查版本
docforge --version

# 查看帮助
docforge --help
```

## 🚀 快速开始

### 使用 CLI 命令

#### 初始化项目

```bash
# 在当前目录创建项目
docforge init 我的项目

# 在指定目录创建项目
docforge init 我的项目 -p /path/to/projects
```

#### 执行工作流

```bash
# 基本用法
docforge run workflow.json

# 指定输入文件
docforge run workflow.json -i data1.xlsx data2.xlsx

# 指定模板文件
docforge run workflow.json -i data.xlsx -t template.docx

# 指定输出目录
docforge run workflow.json -i data.xlsx -t template.docx -o ./output
```

#### 插件管理

```bash
# 列出所有插件
docforge plugin list

# 重新加载插件
docforge plugin reload
```

#### 配置管理

```bash
# 显示当前配置
docforge config show

# 设置配置项
docforge config set database.path /path/to/db
```

### 使用 Python API

```python
from docforge import CoreAPI

# 1. 创建 API 实例
api = CoreAPI()

# 2. 初始化框架
api.initialize()

# 3. 创建项目
api.create_project("我的项目", "./my_project")

# 4. 添加输入文件
api.add_input_files(["data1.xlsx", "data2.xlsx"])

# 5. 添加模板文件
api.add_template_files(["template.docx"])

# 6. 设置输出目录
api.set_output_directory("./output")

# 7. 加载工作流
api.load_workflow("workflow.json")

# 8. 执行工作流
result = api.execute_workflow("my_workflow")

# 9. 检查结果
if result.success:
    print(f"处理完成，生成了 {len(result.output_files)} 个文件")
else:
    print(f"处理失败: {result.errors}")

# 10. 关闭框架
api.shutdown()
```

## 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                         API 层                                  │
│              (对外暴露的统一接口，GUI调用入口)                      │
├─────────────────────────────────────────────────────────────────┤
│                       Services 层                               │
│    (核心业务服务：工作流引擎、插件管理、项目管理、文件管理、日志)      │
├─────────────────────────────────────────────────────────────────┤
│                       Plugins 层                                │
│         (插件系统：插件基类、加载器、注册表、类型定义)               │
├─────────────────────────────────────────────────────────────────┤
│                       Storage 层                                │
│           (数据持久化：数据库、配置管理、缓存服务)                  │
├─────────────────────────────────────────────────────────────────┤
│                        Utils 层                                 │
│        (通用工具：文件操作、字符串处理、模板引擎、验证器)            │
└─────────────────────────────────────────────────────────────────┘
```

**各层职责**：
- **API 层**：对外窗口，隐藏内部复杂性，提供简单易用的接口
- **Services 层**：核心业务逻辑，协调各组件完成任务
- **Plugins 层**：插件系统基础设施，支持功能扩展
- **Storage 层**：数据持久化，管理配置、数据库、缓存
- **Utils 层**：通用工具函数，被其他层共同使用

## 目录结构速查

```
docforge/
│
├── README.md              ← 你现在看的这个文件
├── __init__.py            ← 框架入口，别人import我们时先加载这个
├── exceptions.py          ← 错误类型定义（比如"文件找不到"是什么错误）
├── constants.py           ← 常量定义（比如插件类型有哪些）
├── types.py               ← 数据结构定义（比如"文件信息"长什么样）
├── requirements.txt       ← 依赖列表
│
├── api/                   ← 接口层：对外暴露的API
│   ├── README.md          ← 📖 [API层详细说明](api/README.md)
│   ├── core_api.py        ← 核心API：GUI调用的入口
│   ├── plugin_api.py      ← 插件API：插件调用的接口
│   └── event_bus.py       ← 事件总线：组件间通信
│
├── services/              ← 服务层：提供各种功能服务
│   ├── README.md          ← 📖 [服务层详细说明](services/README.md)
│   ├── workflow_engine.py ← 工作流引擎：执行处理流程
│   ├── plugin_manager.py  ← 插件管理：加载和管理插件
│   ├── project_manager.py ← 项目管理：保存和加载项目
│   ├── file_manager.py    ← 文件管理：文件操作工具
│   └── logger.py          ← 日志：记录运行信息
│
├── plugins/               ← 插件层：插件系统的基础设施
│   ├── README.md          ← 📖 [插件层详细说明](plugins/README.md)
│   ├── base.py            ← 插件基类：所有插件都要继承这个
│   ├── loader.py          ← 插件加载器：从文件加载插件
│   ├── registry.py        ← 插件注册表：记住有哪些插件
│   └── types.py           ← 插件专用类型
│
├── storage/               ← 数据层：存储和配置管理
│   ├── README.md          ← 📖 [数据层详细说明](storage/README.md)
│   ├── database.py        ← 数据库：SQLite操作
│   ├── config.py          ← 配置管理：读写设置
│   └── cache.py           ← 缓存：临时存储
│
└── utils/                 ← 工具层：通用小工具
    ├── README.md          ← 📖 [工具层详细说明](utils/README.md)
    ├── __init__.py        ← 包初始化，导出所有公共函数
    ├── file_utils.py      ← 文件工具：路径处理、哈希计算、文件操作
    ├── string_utils.py    ← 字符串工具：模板渲染、文本处理、字段提取
    ├── template_engine.py ← 模板引擎：高级模板处理、批量渲染
    └── validators.py      ← 验证器：文件、JSON、工作流、插件名称等验证
```

> 💡 **提示**：点击各层的 README 链接可以查看该层的详细说明文档。

## 各层依赖关系

```
                    ┌─────────────────────────────────────┐
                    │            API 层                   │
                    │  (CoreAPI, PluginAPI, EventBus)     │
                    └──────────┬──────────────────────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
┌───────────────────┐ ┌───────────────┐ ┌───────────────────┐
│    Services 层    │ │   Storage 层  │ │     Utils 层      │
│  (业务逻辑编排)    │ │  (数据持久化)  │ │   (通用工具)      │
└─────────┬─────────┘ └───────────────┘ └───────────────────┘
          │
          ▼
┌───────────────────┐
│    Plugins 层     │
│   (功能扩展)      │
└───────────────────┘
```

**依赖说明**：
- **API 层** 依赖 Services 层和 Storage 层
- **Services 层** 依赖 Plugins 层、Storage 层和 Utils 层
- **Plugins 层** 依赖 Utils 层和 types.py
- **Storage 层** 相对独立，主要使用标准库
- **Utils 层** 是最底层，被其他所有层使用

## 如何阅读这个框架？

### 如果你是程序员
1. 先看 `types.py` 了解数据结构
2. 再看 `exceptions.py` 了解错误类型
3. 然后按 `api/` → `services/` → `plugins/` → `storage/` 的顺序阅读
4. 最后看 `utils/` 了解通用工具

### 如果你不懂编程
1. 直接看每个目录的 `README.md`
2. 遇到问题时，把代码和错误信息发给AI
3. AI会告诉你问题在哪、怎么改

## 核心概念解释

### 1. 工作流（Workflow）
把处理过程想象成一条流水线：
```
输入文件 → 提取数据 → 处理数据 → 填入模板 → 输出文件
```
工作流就是这条流水线的"配方"，告诉程序每一步做什么。

**示例工作流定义**：
```json
{
  "name": "证书生成",
  "steps": [
    {"plugin_name": "excel_extractor", "order": 0},
    {"plugin_name": "data_transformer", "order": 1},
    {"plugin_name": "docx_replacer", "order": 2}
  ]
}
```

### 2. 插件（Plugin）
插件就是一个个小工具，每个工具做一件事：
- **Extractor（提取器）**：从Excel读数据
- **Transformer（转换器）**：处理和转换数据
- **Replacer（替换器）**：把数据填入Word模板
- **PostProcessor（后处理器）**：处理生成的文件

你可以写自己的插件，也可以用别人写好的。

### 3. 项目（Project）
项目就是一次任务的所有设置：
- 用哪些输入文件
- 用什么模板
- 输出到哪里
- 用哪个工作流

保存项目后，下次可以直接打开继续用。

### 4. 事件总线（EventBus）
事件总线就像公司的公告板：
- 谁都可以贴通知（发布事件）
- 谁都可以看通知（订阅事件）
- 组件之间通过事件通信，不需要直接调用

## 快速开始

### 安装

```bash
# 克隆项目
git clone <repository-url>

# 进入项目目录
cd docforge

# 安装依赖（目前无外部依赖）
pip install -r requirements.txt
```

### 基础使用

```python
from docforge import CoreAPI

# 1. 创建API实例
api = CoreAPI()

# 2. 初始化框架
api.initialize()

# 3. 创建项目
api.create_project("我的项目", "./my_project")

# 4. 添加输入文件
api.add_input_files(["data1.xlsx", "data2.xlsx"])

# 5. 添加模板文件
api.add_template_files(["template.docx"])

# 6. 设置输出目录
api.set_output_directory("./output")

# 7. 加载工作流
api.load_workflow("workflow.json")

# 8. 执行工作流
result = api.execute_workflow("my_workflow")

# 9. 检查结果
if result.success:
    print(f"处理完成，生成了 {len(result.output_files)} 个文件")
else:
    print(f"处理失败: {result.errors}")

# 10. 关闭框架
api.shutdown()
```

### 完整示例

```python
from docforge import CoreAPI
from docforge.constants import LogLevel

# 创建API实例
api = CoreAPI()

# 初始化（带配置）
api.initialize("config.json")

# 获取项目配置
config = api.get_project_config()
print(f"项目名称: {config.get('name')}")

# 添加文件
api.add_input_files([
    "./data/students.xlsx",
    "./data/teachers.xlsx"
])
api.add_template_files([
    "./templates/certificate.docx",
    "./templates/report.docx"
])

# 设置输出目录
api.set_output_directory("./output")

# 加载工作流
if api.load_workflow("./workflows/certificate.json"):
    print("工作流加载成功")
else:
    print("工作流加载失败")
    exit(1)

# 执行工作流（带进度回调）
def on_progress(progress, message):
    print(f"[{progress*100:.1f}%] {message}")

result = api.execute_workflow("certificate", progress_callback=on_progress)

# 处理结果
if result.success:
    print(f"\n✅ 执行成功!")
    print(f"   输出文件: {len(result.output_files)} 个")
    print(f"   执行时间: {result.execution_time:.2f} 秒")
    
    for file in result.output_files:
        print(f"   - {file}")
else:
    print(f"\n❌ 执行失败!")
    for error in result.errors:
        print(f"   错误: {error}")

# 获取日志
logs = api.get_logs(level="ERROR", limit=10)
for log in logs:
    print(f"[{log['level']}] {log['message']}")

# 关闭框架
api.shutdown()
```

## 常见问题

### Q: 我想添加新功能，该改哪个文件？
A: 看你想改什么：
- 添加新的数据处理逻辑 → 写新插件（看 `plugins/README.md`）
- 修改界面 → 这是GUI层的事，不在这
- 改变工作流执行方式 → 改 `services/workflow_engine.py`
- 添加新的文件格式支持 → 写新的插件

### Q: 出错了怎么办？
A: 
1. 看错误信息，会告诉你哪个文件、哪行出错
2. 打开那个文件，找到对应行
3. 把代码和错误信息发给AI，让它帮你分析
4. 查看 `exceptions.py` 了解错误类型

### Q: 这个文件是干什么的？
A: 每个文件开头都有注释说明，读一下就明白了。或者问AI。

### Q: 如何调试？
A:
1. 使用 Logger 查看详细日志
2. 设置日志级别为 DEBUG 获取更多信息
3. 使用 EventBus 订阅事件查看执行过程
4. 查看 `docforge.log` 日志文件

## 文件命名规则

- `*_manager.py` → 管理器，负责某类资源的增删改查
- `*_engine.py` → 引擎，负责执行某个流程
- `*_utils.py` → 工具，提供通用小功能
- `base.py` → 基类，定义接口规范
- `types.py` → 类型，定义数据结构

## 代码风格约定

1. **每个函数都有文档字符串**：说明这个函数干什么、参数是什么、返回什么
2. **类型注解**：函数参数和返回值都有类型提示
3. **异常处理**：出错时抛出明确的异常，不是返回None
4. **单一职责**：一个函数只做一件事

## 扩展开发

### 编写新插件

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
        return "transformer"
    
    def execute(self, **kwargs) -> ExecutionResult:
        # 获取输入数据
        data = kwargs.get("data", {})
        
        # 处理逻辑
        processed_data = self.process(data)
        
        # 返回结果
        return ExecutionResult(
            success=True,
            data=processed_data
        )
    
    def process(self, data):
        # 你的处理逻辑
        return data
    
    def cleanup(self):
        # 清理资源
        pass
```

### 编写新服务

```python
# services/my_service.py
class MyService:
    def __init__(self, logger=None):
        self.logger = logger
    
    def do_something(self):
        if self.logger:
            self.logger.info("执行操作")
        # 实现逻辑...
```

## 相关资源

- 📖 [API层详细文档](api/README.md)
- 📖 [服务层详细文档](services/README.md)
- 📖 [插件层详细文档](plugins/README.md)
- 📖 [存储层详细文档](storage/README.md)
- 📖 [工具层详细文档](utils/README.md)

## 技术规格

| 项目 | 规格 |
|------|------|
| Python版本 | 3.7+ |
| 数据库 | SQLite 3.x |
| 配置格式 | JSON |
| 支持平台 | Windows, Linux, macOS |
| 外部依赖 | 无（仅使用标准库） |

---

*最后更新：2026年3月31日*