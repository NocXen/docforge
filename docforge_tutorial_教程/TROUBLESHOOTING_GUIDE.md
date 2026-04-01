# DocForge 问题排查指南

## 一、常见问题及解决方案

### 1. 插件导入失败

**错误信息**：`Can't instantiate abstract class XxxPlugin without an implementation for abstract method 'cleanup'`

**原因**：插件缺少 `cleanup()` 方法实现

**解决方案**：
- 在插件类中添加 `cleanup()` 方法
- 方法签名：`def cleanup(self) -> None:`
- 如果不需要清理资源，可以写 `pass`

**示例**：
```python
def cleanup(self) -> None:
    """
    清理资源
    
    在插件卸载或重新加载前调用，用于释放资源。
    如果没有资源需要清理，可以写 pass。
    """
    pass
```

---

### 2. Excel提取数据混乱

**错误信息**：所有字段的数据都混在一起

**原因**：Excel读取时使用了 `header=None`，导致列名是数字索引而不是实际列标题

**解决方案**：
- 修改 `excel_extractor.py` 中的读取方式
- 将 `pd.read_excel(file_path, sheet_name=sheet_name, header=None)`
- 改为 `pd.read_excel(file_path, sheet_name=sheet_name)`

**关键代码**：
```python
# 错误的方式
df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

# 正确的方式
df = pd.read_excel(file_path, sheet_name=sheet_name)
```

---

### 3. 字段名称不匹配

**错误信息**：`未能生成任何输出文件`

**原因**：Excel提取的字段名称和模板中的字段名称不匹配

**解决方案**：
- 检查模板文件中的字段名称
- 在workflow.json中配置正确的字段映射
- 确保 `PlaceHolderName` 和模板中的字段名称一致

**示例**：
```json
{
    "PlaceHolders": [
        {"PlaceHolderName": "Score.type", "Column": ["colname:性质"]},
        {"PlaceHolderName": "Score.CL.int", "Column": ["colname:分数"]}
    ]
}
```

---

### 4. 工作流配置参数传递错误

**错误信息**：`没有配置参数`

**原因**：workflow_engine.py 中的参数传递方式不正确

**解决方案**：
- 修改 `workflow_engine.py` 中的 `_execute_step` 方法
- 将 `**step.config` 改为 `"config": step.config`
- 确保config作为完整对象传递

**关键代码**：
```python
# 错误的方式
kwargs = {
    "input_files": [str(f) for f in input_files],
    "template_files": [str(f) for f in template_files],
    "output_dir": str(output_dir),
    **step.config  # 这样会展开config对象
}

# 正确的方式
kwargs = {
    "input_files": [str(f) for f in input_files],
    "template_files": [str(f) for f in template_files],
    "output_dir": str(output_dir),
    "config": step.config  # 这样传递完整对象
}
```

---

### 5. 插件加载路径问题

**错误信息**：`插件目录不存在`

**原因**：插件目录路径配置不正确

**解决方案**：
- 检查 `core_api.py` 中的插件目录配置
- 默认从根目录的 `Plugins` 文件夹加载
- 如果目录不存在，回退到 `plugins` 目录

**关键代码**：
```python
# 优先从根目录的Plugins文件夹加载
plugin_dir = self.config.get("plugins.directory", "Plugins")
if not os.path.exists(plugin_dir):
    plugin_dir = "plugins"  # 回退到默认的plugins目录

if os.path.exists(plugin_dir):
    self.plugin_manager.load_all_plugins(plugin_dir)
```

---

### 6. 模块导入错误

**错误信息**：`cannot import name 'BasePlugin' from 'docforge_plugins.base'`

**原因**：插件加载时模块名设置错误

**解决方案**：
- 修改 `plugin_manager.py` 中的模块名
- 将 `f"docforge_plugins.{path.stem}"` 改为 `f"docforge.plugins.{path.stem}"`

**关键代码**：
```python
# 错误的方式
module_name = f"docforge_plugins.{path.stem}"

# 正确的方式
module_name = f"docforge.plugins.{path.stem}"
```

---

## 二、调试技巧

### 1. 查看日志文件
- 日志文件位置：`test_workflow/docforge.log`
- 检查ERROR级别的日志信息
- 查看插件加载和执行的详细过程

### 2. 测试单个插件
```python
# 测试excel_extractor
from docforge.api import CoreAPI
api = CoreAPI()
api.initialize()
api.plugin_manager.load_all_plugins("../Plugins")

# 执行单个插件
result = api.plugin_manager.execute_plugin('excel_extractor', 
    input_files=['input.xlsx'], 
    config={'PlaceHolders': [...]})
```

### 3. 检查Excel数据
```python
import pandas as pd
df = pd.read_excel('input.xlsx')
print(df.head())
print(df.columns.tolist())
```

### 4. 检查模板文件
```python
from docx import Document
doc = Document('template.docx')
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            if cell.text.strip():
                print(cell.text)
```

---

## 三、预防措施

### 1. 插件开发检查清单
- [ ] 继承 `BasePlugin` 类
- [ ] 实现 `name`、`version`、`plugin_type` 属性
- [ ] 实现 `execute()` 方法
- [ ] 实现 `cleanup()` 方法
- [ ] 声明 `dependencies` 属性
- [ ] 使用 `ExecutionResult` 返回结果

### 2. 配置文件检查清单
- [ ] workflow.json 格式正确
- [ ] 字段名称和模板一致
- [ ] 插件名称正确
- [ ] 文件路径正确

### 3. 环境检查清单
- [ ] 插件目录存在
- [ ] 依赖包已安装
- [ ] 文件权限正确
- [ ] 输出目录可写

---

## 四、错误代码对照表

| 错误信息 | 可能原因 | 解决方案 |
|---------|---------|---------|
| `Can't instantiate abstract class` | 缺少cleanup方法 | 添加cleanup方法 |
| `没有配置参数` | config参数传递错误 | 修改workflow_engine.py |
| `未能生成任何输出文件` | 字段名称不匹配 | 检查字段映射 |
| `插件目录不存在` | 路径配置错误 | 检查插件目录路径 |
| `cannot import name` | 模块名错误 | 修改plugin_manager.py |