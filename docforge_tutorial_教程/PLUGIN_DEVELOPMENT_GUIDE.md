# DocForge 插件开发指南

## 一、插件基本结构

所有插件必须继承 `BasePlugin` 类并实现以下抽象方法：

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
        return "extractor"  # 或 transformer、replacer、post_processor
    
    def execute(self, **kwargs) -> ExecutionResult:
        # 实现插件逻辑
        return ExecutionResult(success=True, data={})
    
    def cleanup(self) -> None:
        # 清理资源（可选）
        pass
```

## 二、插件类型说明

| 类型 | 用途 | 示例 |
|------|------|------|
| `extractor` | 从文件提取数据 | Excel提取器、CSV提取器 |
| `transformer` | 转换数据结构 | 文本分割器、数据过滤器 |
| `replacer` | 模板替换，生成输出文件 | Word替换器、HTML替换器 |
| `post_processor` | 后处理输出文件 | 文件合并器、压缩器 |

## 三、关键注意事项

### 1. 必须实现 cleanup() 方法
- 即使没有资源需要清理，也必须实现 `cleanup()` 方法
- 方法签名：`def cleanup(self) -> None:`
- 如果不需要清理，可以写 `pass`

### 2. Excel文件读取注意事项
- 使用 `pd.read_excel()` 时，默认将第一行作为列标题
- 如果第一行是数据而不是标题，使用 `header=None`
- 使用 `colname:列名` 格式时，必须确保列名存在

### 3. 字段名称映射
- Excel列名和模板字段名可能不同
- 需要在workflow.json中配置正确的映射关系
- 例如：Excel的"性质"列映射到模板的"Score.type"字段

### 4. 文件路径处理
- 使用 `Path` 对象处理文件路径
- 确保输出目录存在：`output_path.parent.mkdir(parents=True, exist_ok=True)`

## 四、插件配置示例

### Excel提取器配置
```json
{
    "step_id": "extract",
    "plugin_name": "excel_extractor",
    "config": {
        "PlaceHolders": [
            {"PlaceHolderName": "Score.type", "Column": ["colname:性质"]},
            {"PlaceHolderName": "Score.CL.int", "Column": ["colname:分数"]}
        ]
    }
}
```

### Word替换器配置
```json
{
    "step_id": "replace",
    "plugin_name": "docx_replacer",
    "config": {}
}
```

## 五、依赖管理

在插件中声明依赖：
```python
@property
def dependencies(self) -> List[str]:
    return ["pandas", "openpyxl", "odfpy"]
```

## 六、错误处理

使用 `ExecutionResult` 返回结果：
```python
return ExecutionResult(
    success=True,
    data={"字段1": ["值1", "值2"]},
    output_files=["output.docx"]
)

# 或者失败时
return ExecutionResult(
    success=False,
    errors=["错误信息"]
)