# DocForge - 办公与数据处理自动化框架

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)](https://github.com/nocxen/docforge)

## 📖 简介

DocForge 是一个**办公与数据处理自动化框架**，专为批量处理文档而设计。它可以帮助你：

- 📊 从 Excel、Word 等文件中提取数据
- 🔄 处理和转换数据（分割、格式化、过滤等）
- 📝 把数据填入模板，生成新文件
- 🚀 批量处理成百上千份文档

## ✨ 特性

- **插件化架构**：易于扩展，支持自定义插件
- **工作流引擎**：可视化编排处理流程
- **CLI 支持**：命令行工具，方便自动化
- **零依赖**：仅使用 Python 标准库
- **跨平台**：支持 Windows、Linux、macOS

## 也许这是这个项目唯一由人类编写的注释 by NocXen：

不得不说，这个软件很简单，也只是个框架，GitHub截至 2026.4.1 有 160 个 docforge 的 REPO ，我都没想到。但本软件可能是最接近 Forge（锻造坊） 的一个：你需要准备自己的锻造模板，你需要自己的锻造流程和工具；你可以随意操作，想怎么锻，就怎么锻，无论你想要城门楼子还是胯骨轴子。只要“工艺”正确，你能锻造出一切你想要的风格；无论是你只打算批量替换文档的某个词，还是接入AI给你做精美的文档。

我的 Python 很烂。所以这个软件里满满全是'readme'和'tutorial'等md文件————希望对你有帮助。如果你要修改代码，一定要让你的助手AI !!!**先读这些md文档**!!! ，没了它们，我自己也看不懂我做了什么。

最后感谢小米的两周 MiMo-V2-Pro 免费API，不然以我的水平，我是不会也不能做这个包的。此外，希望我能有朝一日完成这个软件的GUI梦。

## 🚀 快速开始

### 安装

#### 方式一：从 PyPI 安装（推荐）

```bash
pip install python-docforge
```

#### 方式二：从源码安装

```bash
# 克隆仓库
git clone https://github.com/nocxen/docforge.git
cd docforge

# 安装
pip install -e .
```

#### 方式三：开发模式安装

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

## 📚 使用指南

### 方式一：使用 CLI 命令

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

### 方式二：使用 Python API

#### 基础示例

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

#### 完整示例

```python
from docforge import CoreAPI
from docforge.constants import LogLevel

# 创建 API 实例
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

## 📁 项目结构

```
docforge_pip/
├── README.md              ← 本文件
├── setup.py               ← 安装配置
├── pyproject.toml         ← 项目配置
├── requirements.txt       ← 依赖列表
│
└── docforge/              ← 框架源码
    ├── README.md          ← 框架详细说明
    ├── __init__.py        ← 包入口
    ├── cli.py             ← 命令行接口
    ├── constants.py       ← 常量定义
    ├── exceptions.py      ← 异常定义
    ├── types.py           ← 类型定义
    │
    ├── api/               ← API 层
    │   ├── core_api.py    ← 核心 API
    │   ├── plugin_api.py  ← 插件 API
    │   └── event_bus.py   ← 事件总线
    │
    ├── services/          ← 服务层
    │   ├── workflow_engine.py   ← 工作流引擎
    │   ├── plugin_manager.py    ← 插件管理
    │   ├── project_manager.py   ← 项目管理
    │   ├── file_manager.py      ← 文件管理
    │   └── logger.py            ← 日志服务
    │
    ├── plugins/           ← 插件层
    │   ├── base.py        ← 插件基类
    │   ├── loader.py      ← 插件加载器
    │   └── registry.py    ← 插件注册表
    │
    ├── storage/           ← 存储层
    │   ├── database.py    ← 数据库
    │   ├── config.py      ← 配置管理
    │   └── cache.py       ← 缓存服务
    │
    └── utils/             ← 工具层
        ├── file_utils.py      ← 文件工具
        ├── string_utils.py    ← 字符串工具
        ├── template_engine.py ← 模板引擎
        └── validators.py      ← 验证器
```

## 🔧 核心概念

### 工作流（Workflow）

工作流是处理过程的"配方"，定义了数据处理的步骤：

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

### 插件（Plugin）

插件是功能模块，每个插件完成特定任务：

- **Extractor（提取器）**：从 Excel/CSV 提取数据
- **Transformer（转换器）**：处理和转换数据
- **Replacer（替换器）**：把数据填入模板
- **PostProcessor（后处理器）**：处理生成的文件

### 项目（Project）

项目是一次任务的所有设置：
- 输入文件
- 模板文件
- 输出目录
- 工作流配置

## 🛠️ 开发指南

### 编写自定义插件

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

### 插件存放位置

插件可以放在以下位置：

1. **项目目录**：`项目目录/plugins/`
2. **用户目录**：`~/.docforge/plugins/`
3. **系统目录**：`/usr/local/docforge/plugins/`（Linux/macOS）

## ❓ 常见问题

### Q: 安装后命令找不到？

A: 确保 Python 的 Scripts 目录在 PATH 中：

```bash
# Windows
set PATH=%PATH%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python3X\Scripts

# Linux/macOS
export PATH=$PATH:~/.local/bin
```

### Q: 如何查看详细日志？

A: 设置日志级别为 DEBUG：

```python
from docforge import CoreAPI
from docforge.constants import LogLevel

api = CoreAPI()
api.initialize()
api.logger.set_level(LogLevel.DEBUG)
```

### Q: 支持哪些文件格式？

A: 目前支持：
- Excel: `.xlsx`, `.xls`
- Word: `.docx`
- CSV: `.csv`
- JSON: `.json`
- 文本: `.txt`

### Q: 如何贡献代码？

A: 
1. Fork 项目
2. 创建特性分支：`git checkout -b feature/my-feature`
3. 提交更改：`git commit -am 'Add my feature'`
4. 推送分支：`git push origin feature/my-feature`
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👥 作者

- **Xiaomi-MiMo-V2-pro** - *初始开发*
- **NocXen** - *初始开发*

## 🙏 致谢

感谢所有为这个项目做出贡献的人！

## 📞 联系方式

- 项目主页：https://github.com/nocxen/docforge
- 问题反馈：https://github.com/nocxen/docforge/issues
- 邮箱：nocxens@qq.com

---

*最后更新：2026年4月1日*