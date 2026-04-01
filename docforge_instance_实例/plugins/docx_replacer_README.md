# Word文档替换插件

## 概述

`docx_replacer` 是一个Word文档替换插件，可以将数据填入Word模板，替换所有字段。

## 核心特性

### 批量生成文档
- **多值支持**：每个字段可以有多个值（值1、值2、值3等）
- **顺序保持**：值的顺序保持不变，确保每个文档都有自己的归宿
- **批量生成**：根据字段值的数量，自动生成多个文档
- **避免串值**：检查所有字段的值数量是否一致，防止串值问题

### 示例
如果Excel中有21行数据，每个字段有21个值，那么：
- 每个模板会生成21个文档
- 如果有2个模板，总共会生成42个文档
- 每个文档使用对应行的数据进行替换

## 支持格式

- `.docx` - Word 2007+

## 配置格式

```json
{
    "Target": ["template1.docx", "template2.docx"],
    "Ignore": ["temp.docx"],
    "KeepPlaceHolderIfShorter": false,
    "ReplacerOfShorterPlaceHolder": ""
}
```

### 配置参数说明

#### Target（可选）

正选列表，只选择指定的模板文件。

- 空值 `[""]` 或不设置 - 选择所有模板
- `["审批单.docx"]` - 只选择审批单.docx
- `["审批单*.docx"]` - 使用通配符匹配
- `["审批单.docx", "回执单.docx"]` - 选择多个文件

#### Ignore（可选）

反选列表，不选择指定的模板文件。

- 空值 `[""]` 或不设置 - 不忽略任何文件
- `["临时*.docx"]` - 忽略所有以"临时"开头的文件
- `["temp.docx", "backup.docx"]` - 忽略多个文件

**注意**：Ignore优先级高于Target。如果文件同时匹配Target和Ignore，会被忽略。

#### KeepPlaceHolderIfShorter（可选）

控制当替换值比占位符短时是否保留占位符。

- `false`（默认）- 正常替换，即使替换值较短
- `true` - 当替换值比占位符短时，保留原占位符或使用自定义替换字符

#### ReplacerOfShorterPlaceHolder（可选）

当 `KeepPlaceHolderIfShorter` 为 `true` 时，用于替换短值的自定义字符。

- 空值 `""` - 保留原占位符
- `"*"` - 用 `*` 替换占位符
- `"-"` - 用 `-` 替换占位符

## 使用示例

### 示例1：替换所有模板

```json
{
    "step_id": "replace",
    "plugin_name": "docx_replacer",
    "config": {}
}
```

### 示例2：只替换特定模板

```json
{
    "step_id": "replace",
    "plugin_name": "docx_replacer",
    "config": {
        "Target": ["审批单.docx"]
    }
}
```

### 示例3：忽略临时文件

```json
{
    "step_id": "replace",
    "plugin_name": "docx_replacer",
    "config": {
        "Ignore": ["临时*.docx", "~*.docx"]
    }
}
```

### 示例4：保留短字段占位符

```json
{
    "step_id": "replace",
    "plugin_name": "docx_replacer",
    "config": {
        "KeepPlaceHolderIfShorter": true,
        "ReplacerOfShorterPlaceHolder": "*"
    }
}
```

### 示例5：完整工作流

```json
{
    "name": "文档生成工作流",
    "steps": [
        {
            "step_id": "extract",
            "plugin_name": "excel_extractor",
            "config": {
                "PlaceHolders": [
                    {
                        "PlaceHolderName": "{公司名称}",
                        "Sheet": ["Sheet1"],
                        "Column": ["colname:公司名称"]
                    }
                ]
            }
        },
        {
            "step_id": "replace",
            "plugin_name": "docx_replacer",
            "config": {
                "Target": ["审批单.docx"]
            }
        }
    ]
}
```

## 字段语法

在Word模板中使用 `{字段名}` 作为占位符：

```
公司名称：{公司名称}
日期：{日期}
负责人：{负责人}
```

插件会自动将数据填入对应位置。

## 输出文件名

默认输出文件名为 `{原文件名}_output.docx`。

支持在模板文件名中使用字段，如：`{公司名称}_审批单.docx`

## 技术细节

### 格式继承

插件会继承模板的所有格式，包括：
- 字体样式（大小、颜色、加粗等）
- 段落格式（对齐、缩进、行距等）
- 表格样式（边框、底纹等）
- 页眉页脚
- 图片和图形

### 替换范围

- 段落中的文本
- 表格中的文本
- 文本框中的文本
- 页眉页脚中的文本

### 注意事项

1. 字段区分大小写
2. 字段必须完全匹配才会替换
3. 同一个字段可以在文档中多次使用
4. 如果数据中没有对应字段，占位符会保留原样

## 常见问题

### Q: 为什么有些字段没有被替换？

A: 检查以下几点：
- 字段名是否完全匹配（包括大小写）
- 数据中是否包含该字段
- 字段是否在支持的范围内（段落、表格等）

### Q: 如何保留模板格式？

A: 插件会自动保留所有格式，无需特殊配置。

### Q: 支持哪些Word版本？

A: 只支持 `.docx` 格式（Word 2007+）。如果需要处理 `.doc` 格式，需要先转换为 `.docx`。

### Q: 如何处理多个模板？

A: 在Target中指定多个模板文件名，或留空选择所有模板。

## 依赖

- python-docx

安装命令：
```bash
pip install python-docx