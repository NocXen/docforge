# Excel表格替换插件

## 概述

`excel_replacer` 是一个Excel表格替换插件，可以将数据填入Excel模板，替换所有字段。

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

- `.xlsx` - Excel 2007+
- `.xls` - Excel 97-2003
- `.xlsm` - Excel宏工作簿
- `.xlsb` - Excel二进制工作簿
- `.odf` - OpenDocument公式
- `.ods` - OpenDocument电子表格
- `.odt` - OpenDocument文本

## 配置格式

```json
{
    "Target": ["template1.xlsx", "template2.xlsx"],
    "Ignore": ["temp.xlsx"],
    "FileType": "xlsx",
    "KeepPlaceHolderIfShorter": false,
    "ReplacerOfShorterPlaceHolder": ""
}
```

### 配置参数说明

#### Target（可选）

正选列表，只选择指定的模板文件。

- 空值 `[""]` 或不设置 - 选择所有模板
- `["数据表.xlsx"]` - 只选择数据表.xlsx
- `["数据*.xlsx"]` - 使用通配符匹配
- `["数据表.xlsx", "汇总表.xlsx"]` - 选择多个文件

#### Ignore（可选）

反选列表，不选择指定的模板文件。

- 空值 `[""]` 或不设置 - 不忽略任何文件
- `["临时*.xlsx"]` - 忽略所有以"临时"开头的文件
- `["temp.xlsx", "backup.xlsx"]` - 忽略多个文件

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

#### FileType（可选）

输出文件格式，默认为 `xlsx`。

- `"xlsx"` - Excel 2007+（默认）
- `"xls"` - Excel 97-2003
- `"xlsm"` - Excel宏工作簿
- `"xlsb"` - Excel二进制工作簿
- `"odf"` - OpenDocument公式
- `"ods"` - OpenDocument电子表格
- `"odt"` - OpenDocument文本

## 使用示例

### 示例1：替换所有模板

```json
{
    "step_id": "replace",
    "plugin_name": "excel_replacer",
    "config": {}
}
```

### 示例2：只替换特定模板

```json
{
    "step_id": "replace",
    "plugin_name": "excel_replacer",
    "config": {
        "Target": ["数据表.xlsx"]
    }
}
```

### 示例3：保留短字段占位符

```json
{
    "step_id": "replace",
    "plugin_name": "excel_replacer",
    "config": {
        "KeepPlaceHolderIfShorter": true,
        "ReplacerOfShorterPlaceHolder": "*"
    }
}
```

### 示例4：输出为ODS格式

```json
{
    "step_id": "replace",
    "plugin_name": "excel_replacer",
    "config": {
        "FileType": "ods"
    }
}
```

### 示例5：完整工作流

```json
{
    "name": "Excel数据处理工作流",
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
            "plugin_name": "excel_replacer",
            "config": {
                "Target": ["数据表.xlsx"],
                "FileType": "xlsx"
            }
        }
    ]
}
```

## 字段语法

在Excel模板中使用 `{字段名}` 作为占位符：

```
A1: 公司名称
B1: {公司名称}
C1: 日期
D1: {日期}
```

插件会自动将数据填入对应位置。

## 输出文件名

默认输出文件名为 `{原文件名}_output.{格式}`。

支持在模板文件名中使用字段，如：`{公司名称}_数据表.xlsx`

## 技术细节

### 格式保留策略

插件会根据模板格式自动选择处理方式：

1. **openpyxl模式**（.xlsx, .xlsm, .xlsb）
   - 保留所有格式
   - 保留公式
   - 保留图表
   - 保留条件格式

2. **pandas模式**（其他格式）
   - 保留数据
   - 保留基本格式
   - 可能丢失部分高级格式

### 替换范围

- 所有工作表中的单元格
- 合并单元格
- 文本格式的单元格

### 注意事项

1. 字段区分大小写
2. 字段必须完全匹配才会替换
3. 同一个字段可以在表格中多次使用
4. 如果数据中没有对应字段，占位符会保留原样
5. 数字格式的单元格不会被替换

## 常见问题

### Q: 为什么有些字段没有被替换？

A: 检查以下几点：
- 字段名是否完全匹配（包括大小写）
- 数据中是否包含该字段
- 单元格是否为文本格式

### Q: 如何保留模板格式？

A: 插件会自动保留格式。对于.xlsx格式，使用openpyxl保留所有格式。

### Q: 支持哪些Excel版本？

A: 支持所有主流Excel格式，包括：
- Excel 97-2003 (.xls)
- Excel 2007+ (.xlsx)
- 宏工作簿 (.xlsm)
- 二进制工作簿 (.xlsb)
- OpenDocument格式 (.ods, .odt, .odf)

### Q: 如何处理多个模板？

A: 在Target中指定多个模板文件名，或留空选择所有模板。

### Q: 输出格式会丢失数据吗？

A: 对于xlsx格式，不会丢失数据和格式。对于其他格式，可能会丢失部分高级格式。

## 依赖

- pandas
- openpyxl
- odfpy（用于OpenDocument格式）

安装命令：
```bash
pip install pandas openpyxl odfpy