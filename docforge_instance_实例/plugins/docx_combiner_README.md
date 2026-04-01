# Word文档合并插件 (docx_combiner)

## 插件信息

- **插件名称**: docx_combiner
- **版本**: 1.0.0
- **类型**: post_processor
- **依赖**: python-docx, docxcompose

## 功能说明

将多个Word文档合并为一个文件。适用于：
- 将批量生成的文档合并为单个文件
- 按文件名前缀分组合并
- 自动添加分页符
- 按文件名数字顺序排序

## 核心特性

### 1. 批量合并
将多个Word文档合并为单个文件，保持原文档的格式和样式。

### 2. 按前缀分组合并
自动识别文件名前缀，将相同前缀的文件合并为一个文件。

例如：
- 院审批单_击掌活动_1.docx
- 院审批单_击掌活动_2.docx
- 院审批单_击掌活动_3.docx
→ 合并为：院审批单_Combined.docx

### 3. 文件名数字排序
自动从文件名中提取数字，按数字顺序排序后合并。

例如：
- 院审批单_1.docx
- 院审批单_2.docx
- 院审批单_10.docx
→ 排序后合并：1, 2, 10（而不是1, 10, 2）

### 4. 自动分页符
在每个文档前自动添加分页符，确保每个文档从新页面开始。

## 配置参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| Target | List[str] | 否 | [] | 正选列表（只选择这些文件，支持通配符*） |
| Ignore | List[str] | 否 | [] | 反选列表（不选择这些文件，支持通配符*） |
| SortBy | str | 否 | "number" | 排序方式：number（按数字）、name（按名称）、time（按时间） |
| SortOrder | str | 否 | "asc" | 排序顺序：asc（升序）、desc（降序） |
| PageBreak | bool | 否 | True | 是否在每个文档前添加分页符 |
| CombineBy | str | 否 | "prefix" | 合并方式：prefix（按前缀分组）、all（合并所有文件） |

## 使用示例

### 示例1：按前缀分组合并

```json
{
    "step_id": "combine",
    "plugin_name": "docx_combiner",
    "config": {
        "Target": ["院审批单*.docx"],
        "SortBy": "number",
        "PageBreak": true,
        "CombineBy": "prefix"
    }
}
```

### 示例2：合并所有文件

```json
{
    "step_id": "combine",
    "plugin_name": "docx_combiner",
    "config": {
        "SortBy": "name",
        "PageBreak": true,
        "CombineBy": "all"
    }
}
```

### 示例3：忽略某些文件

```json
{
    "step_id": "combine",
    "plugin_name": "docx_combiner",
    "config": {
        "Target": ["*.docx"],
        "Ignore": ["temp*.docx", "backup*.docx"],
        "SortBy": "number",
        "PageBreak": true,
        "CombineBy": "prefix"
    }
}
```

## 完整工作流示例

```json
{
    "workflow_id": "generate_and_combine",
    "name": "生成并合并文档",
    "steps": [
        {
            "step_id": "extract",
            "plugin_name": "excel_extractor",
            "config": {
                "Target": ["data.xlsx"]
            }
        },
        {
            "step_id": "replace",
            "plugin_name": "docx_replacer",
            "config": {
                "Target": ["模板.docx"]
            }
        },
        {
            "step_id": "combine",
            "plugin_name": "docx_combiner",
            "config": {
                "Target": ["模板_output_*.docx"],
                "SortBy": "number",
                "PageBreak": true,
                "CombineBy": "prefix"
            }
        }
    ]
}
```

## 工作原理

### 1. 文件过滤
- 根据Target配置过滤需要合并的文件
- 根据Ignore配置排除不需要的文件
- 只处理.docx文件

### 2. 文件排序
- **number模式**：从文件名中提取数字，按数字排序
- **name模式**：按文件名字符串排序
- **time模式**：按文件修改时间排序

### 3. 文件分组
- **prefix模式**：提取文件名前缀（去除数字后缀），按前缀分组
- **all模式**：不进行分组，所有文件合并为一个

### 4. 文档合并
- 使用docxcompose库进行文档合并
- 第一个文件作为模板（保留格式）
- 在每个文档前添加分页符（可选）

## 依赖安装

```bash
pip install python-docx docxcompose
```

## 注意事项

1. **文件格式**：只支持.docx格式，不支持.doc格式
2. **文件大小**：合并大量文件时可能需要较长时间
3. **格式保持**：第一个文件的格式将作为合并后文档的格式
4. **分页符**：默认在每个文档前添加分页符，可通过PageBreak配置关闭
5. **文件排序**：建议使用number模式，确保数字顺序正确（如1, 2, 10而不是1, 10, 2）

## 常见问题

### Q: 合并后的文档格式丢失了？
A: 合并后的文档格式以第一个文件为准。请确保第一个文件的格式符合要求。

### Q: 文件排序不正确？
A: 请检查SortBy配置。建议使用"number"模式，它会自动从文件名中提取数字进行排序。

### Q: 如何只合并部分文件？
A: 使用Target配置指定要合并的文件，或使用Ignore配置排除不需要的文件。

### Q: 合并后没有分页符？
A: 请检查PageBreak配置。默认为true，如果设置为false则不会添加分页符。

---

*最后更新：2026年3月29日*