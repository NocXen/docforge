# PlaceholderSplitter 占位符分割器

## 概述

`PlaceholderSplitter` 是一个通用的transformer插件，用于将一个字段分割为多个新字段。主要用于一表制多表的场景，通过配置可以灵活地控制分割行为。

## 功能特点

- 支持自定义分隔符
- 支持数字补零（Digits参数）
- 可选择是否保留原字段
- 自动计算数字宽度

## 配置参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| Target | string | 否 | - | 要分割的目标字段名。如果未指定，跳过执行 |
| Digits | string | 否 | 自动 | 数字宽度，用于补零。如"2"表示01, 02, 03... |
| SeparateCharacter | string | 否 | "." | 分隔符，用于连接原字段名和索引 |
| KeepOriginal | string | 否 | "True" | 是否保留原字段。设为"False"时删除原字段 |

## 配置示例

### 基础配置
```json
{
    "Target": "example",
    "Digits": "2",
    "SeparateCharacter": ".",
    "KeepOriginal": "True"
}
```

### 完整工作流示例
```json
{
    "step_id": "split",
    "plugin_name": "placeholder_splitter",
    "config": {
        "Target": "example",
        "Digits": "2",
        "SeparateCharacter": ".",
        "KeepOriginal": "True"
    }
}
```

## 输入输出示例

### 示例1：基础分割

**输入数据：**
```json
{
    "example": ["草莓", "牛奶", "蛋糕"]
}
```

**配置：**
```json
{
    "Target": "example",
    "Digits": "2",
    "SeparateCharacter": ".",
    "KeepOriginal": "True"
}
```

**输出数据：**
```json
{
    "example": ["草莓", "牛奶", "蛋糕"],
    "example.01": ["草莓", "草莓", "草莓"],
    "example.02": ["牛奶", "牛奶", "牛奶"],
    "example.03": ["蛋糕", "蛋糕", "蛋糕"]
}
```

### 示例2：不保留原字段

**输入数据：**
```json
{
    "example": ["草莓", "牛奶", "蛋糕"]
}
```

**配置：**
```json
{
    "Target": "example",
    "Digits": "2",
    "SeparateCharacter": ".",
    "KeepOriginal": "False"
}
```

**输出数据：**
```json
{
    "example.01": ["草莓", "草莓", "草莓"],
    "example.02": ["牛奶", "牛奶", "牛奶"],
    "example.03": ["蛋糕", "蛋糕", "蛋糕"]
}
```

### 示例3：自动计算宽度

**输入数据：**
```json
{
    "example": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]
}
```

**配置：**
```json
{
    "Target": "example",
    "SeparateCharacter": "_"
}
```

**输出数据：**
```json
{
    "example": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"],
    "example_01": ["A", "A", "A", "A", "A", "A", "A", "A", "A", "A", "A"],
    "example_02": ["B", "B", "B", "B", "B", "B", "B", "B", "B", "B", "B"],
    ...
    "example_11": ["K", "K", "K", "K", "K", "K", "K", "K", "K", "K", "K"]
}
```

## 使用场景

### 场景1：一表制多表

当你有一个包含多个产品的表格，需要为每个产品生成单独的文档时：

1. 使用 `excel_extractor` 提取产品列表
2. 使用 `placeholder_splitter` 将产品字段分割为独立字段
3. 使用 `docx_replacer` 为每个产品生成文档

### 场景2：批量生成证书

当你需要为每个学员生成证书时：

1. 提取学员名单
2. 使用分割器将学员姓名分割为独立字段
3. 使用替换器生成证书

## 注意事项

1. **Target字段必须存在**：如果指定的Target字段不存在，将返回错误
2. **Digits参数**：如果未指定Digits，将自动根据分割数量计算宽度
3. **分隔符**：默认使用"."作为分隔符，可以根据需要自定义
4. **原字段保留**：默认保留原字段，如果不需要可以设置KeepOriginal为False

## 错误处理

插件会在以下情况返回错误：

- 没有输入数据
- 目标字段不存在
- 目标字段为空
- Digits参数不是数字

## 版本历史

- v1.0.0: 初始版本
  - 支持基本的字段分割功能
  - 支持自定义分隔符和数字补零
  - 支持保留/删除原字段选项