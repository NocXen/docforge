# Excel数据提取器插件

## 概述

`excel_extractor` 是一个通用的Excel数据提取插件，可以从Excel文件中灵活地提取数据。

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
    "PlaceHolders": [
        {
            "PlaceHolderName": "字段名称",
            "KeepEmptyCells": "False",
            "Sheet": ["Sheet1"],
            "Column": ["col:B", "colname:公司名称"],
            "Row": [""],
            "Range": ["B2:C5"]
            班级	姓名	事由	性质	分数	日期
        }
    ]
}
```

**重要**：使用 `{{` 而不是 `\{` 来转义字段语法中的 `{` 字符。

### 配置参数说明

#### PlaceHolderName（必需）

字段名称，用于在模板中引用提取的数据。

**特殊规则**：如果多个PlaceHolder使用相同名称，第二个的数据会追加到第一个后面。

#### KeepEmptyCells（可选）

是否保留空单元格，默认为 `"False"`。

- `"True"` - 保留空值，空单元格会输出空字符串
- `"False"` - 过滤空值，只输出有内容的单元格

**注意**：当启用 `KeepEmptyCells` 时，会以行数最多的列为准，其他列用空值填充。

#### Sheet（可选）

指定要读取的工作表。

- 空值 `[""]` 或不设置 - 读取所有工作表
- `["Sheet1"]` - 只读取 Sheet1
- `["Sheet1", "Sheet2"]` - 读取 Sheet1 和 Sheet2

#### Column（可选）

指定要提取的列。

**格式**：
- `["col:B"]` - 按列号选择，选择B列（会自动添加该列标题作为第一个值）
- `["colname:公司名称"]` - 按列标题选择，选择标题为"公司名称"的列
- `["col:B", "colname:公司名称"]` - 同时选择B列和标题为"公司名称"的列
- `[""]` - 保留所有列

**重要特性**：
- 使用 `col:` 格式时，会自动将该列的标题（第一行）作为提取数据的第一个值
- 这样可以确保后续处理能够根据标题进行匹配
- 支持 row:1 提取（第一行数据）

#### Row（可选）

指定要提取的行。

**格式**：
- `["row:2"]` - 按行号选择，选择第2行
- `["rowname:标题"]` - 按行标题选择，选择第一列内容为"标题"的行
- `[""]` - 保留所有行

#### Range（可选）

指定要提取的区域，优先级最高。

**格式**：
- `["B2:C5"]` - 提取B2到C5区域
- `[""]` - 不使用区域过滤

**注意**：Range会先执行，然后才应用Column和Row过滤。

## 使用示例

### 示例1：提取特定列

```json
{
    "step_id": "extract",
    "plugin_name": "excel_extractor",
    "config": {
        "PlaceHolders": [
            {
                "PlaceHolderName": "公司名称",
                "Sheet": ["Sheet1"],
                "Column": ["colname:公司名称"]
            },
            {
                "PlaceHolderName": "职位",
                "Sheet": ["Sheet1"],
                "Column": ["colname:职位"]
            }
        ]
    }
}
```

### 示例2：提取特定区域

```json
{
    "step_id": "extract",
    "plugin_name": "excel_extractor",
    "config": {
        "PlaceHolders": [
            {
                "PlaceHolderName": "数据区域",
                "Range": ["B2:D10"]
            }
        ]
    }
}
```

### 示例3：保留空值

```json
{
    "step_id": "extract",
    "plugin_name": "excel_extractor",
    "config": {
        "PlaceHolders": [
            {
                "PlaceHolderName": "完整数据",
                "KeepEmptyCells": "True",
                "Sheet": ["Sheet1"]
            }
        ]
    }
}
```

### 示例4：多字段同名（追加）

```json
{
    "step_id": "extract",
    "plugin_name": "excel_extractor",
    "config": {
        "PlaceHolders": [
            {
                "PlaceHolderName": "姓名",
                "Sheet": ["Sheet1"],
                "Column": ["colname:姓名"]
            },
            {
                "PlaceHolderName": "姓名",
                "Sheet": ["Sheet2"],
                "Column": ["colname:姓名"]
            }
        ]
    }
}
```

结果：Sheet1和Sheet2中的姓名会合并到同一个字段中。

### 示例5：完整工作流

```json
{
    "name": "数据提取工作流",
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
                    },
                    {
                        "PlaceHolderName": "{招聘职位}",
                        "Sheet": ["Sheet1"],
                        "Column": ["colname:职位"]
                    }
                ]
            }
        }
    ]
}
```

## 常见问题

### Q: 为什么提取的数据顺序不对？

A: 插件按行优先、列次之的顺序遍历单元格。如果需要特定顺序，建议使用Range指定区域。

### Q: 如何提取多个工作表的数据？

A: 在Sheet配置中指定多个工作表名称，或留空 `[""]` 读取所有工作表。

### Q: 为什么有些单元格的值没有被提取？

A: 检查是否启用了 `KeepEmptyCells`。默认情况下，空值会被过滤掉。

### Q: 如何处理第一行作为数据而不是标题？

A: pandas默认将第一行作为列标题。如果第一行是数据，需要在代码中特殊处理（当前版本暂不支持）。

### Q: 列号和列名有什么区别？

A: 
- `col:B` - 按Excel列号选择，不管列标题是什么
- `colname:公司名称` - 按列标题选择，找到标题为"公司名称"的列

## 技术细节

### 过滤顺序

1. Range（优先级最高）
2. Column
3. Row

### 空值处理

- 当 `KeepEmptyCells=False` 时，提取后会过滤掉所有空字符串
- 当 `KeepEmptyCells=True` 时，会保留空字符串，并且所有列的行数会对齐：
  - 以最高行数的列为准
  - 其他列用空值填充
  - 确保表格数据一一对应，不串位置

### 列字母转换

支持标准Excel列名：A-Z, AA-ZZ, AAA-ZZZ等

## 依赖

- pandas
- openpyxl（用于 .xlsx）
- odfpy（用于 .odf, .ods, .odt）

安装命令：
```bash
pip install pandas openpyxl odfpy