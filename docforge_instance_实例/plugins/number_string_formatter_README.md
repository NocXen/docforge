# NumberStringFormatter 数字字符串格式化器

## 概述

`NumberStringFormatter` 是一个通用的transformer插件，用于在中文数字、英文数字和阿拉伯数字之间进行转换。支持大数字（最高到9999亿）。

## 功能特点

- 支持阿拉伯数字转中文数字
- 支持阿拉伯数字转英文数字
- 支持中文数字转阿拉伯数字
- 支持英文数字转阿拉伯数字
- 支持大数字（最高到9999亿）
- 支持简体和大写中文数字
- 支持错误处理配置

## 配置参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| Target | string | 否 | - | 要格式化的数字字段名。如果未指定，跳过执行 |
| From | string | 否 | "arabic" | 输入数字类型。可选值：arabic、chinese、english |
| To | string | 否 | "chinese" | 输出数字类型。可选值：arabic、chinese、english |
| Error | string | 否 | "!!NumberFormattingError!! [{str}]" | 错误处理模板 |

## 支持的数字类型

### Arabic（阿拉伯数字）
- 标准数字格式：1234567
- 带逗号格式：1,234,567
- 支持范围：0 ~ 999,999,999,999

### Chinese（中文数字）
- 简体数字：零、一、二、三、四、五、六、七、八、九
- 大写数字：壹、贰、叁、肆、伍、陆、柒、捌、玖
- 单位：十、百、千、万、亿
- 支持"两"的表示

### English（英文数字）
- 基础数字：one, two, three, ...
- 十位数：twenty, thirty, forty, ...
- 组合数：twenty-one, thirty-two, ...
- 单位：hundred, thousand, million, billion

## 配置示例

### 阿拉伯数字转中文数字
```json
{
    "Target": "数量",
    "From": "arabic",
    "To": "chinese",
    "Error": "!!NumberFormattingError!! [{str}]"
}
```

### 阿拉伯数字转英文数字
```json
{
    "Target": "数量",
    "From": "arabic",
    "To": "english",
    "Error": "!!NumberFormattingError!! [{str}]"
}
```

### 中文数字转阿拉伯数字
```json
{
    "Target": "数量",
    "From": "chinese",
    "To": "arabic",
    "Error": "!!NumberFormattingError!! [{str}]"
}
```

### 英文数字转阿拉伯数字
```json
{
    "Target": "数量",
    "From": "english",
    "To": "arabic",
    "Error": "!!NumberFormattingError!! [{str}]"
}
```

## 输入输出示例

### 示例1：阿拉伯数字转中文数字

**输入数据：**
```json
{
    "数量": ["1234567", "100000000", "12345678901"]
}
```

**配置：**
```json
{
    "Target": "数量",
    "From": "arabic",
    "To": "chinese"
}
```

**输出数据：**
```json
{
    "数量": ["一百二十三万四千五百六十七", "一亿", "一百二十三亿四千五百六十七万八千九百零一"]
}
```

### 示例2：阿拉伯数字转英文数字

**输入数据：**
```json
{
    "数量": ["1234567", "1000000", "1234567890"]
}
```

**配置：**
```json
{
    "Target": "数量",
    "From": "arabic",
    "To": "english"
}
```

**输出数据：**
```json
{
    "数量": ["one million two hundred thirty-four thousand five hundred sixty-seven", 
            "one million", 
            "one billion two hundred thirty-four million five hundred sixty-seven thousand eight hundred ninety"]
}
```

### 示例3：中文数字转阿拉伯数字

**输入数据：**
```json
{
    "数量": ["一百二十三万四千五百六十七", "一亿", "两百五十"]
}
```

**配置：**
```json
{
    "Target": "数量",
    "From": "chinese",
    "To": "arabic"
}
```

**输出数据：**
```json
{
    "数量": ["1234567", "100000000", "250"]
}
```

### 示例4：英文数字转阿拉伯数字

**输入数据：**
```json
{
    "数量": ["one million", "twenty-five", "one hundred thirty-two"]
}
```

**配置：**
```json
{
    "Target": "数量",
    "From": "english",
    "To": "arabic"
}
```

**输出数据：**
```json
{
    "数量": ["1000000", "25", "132"]
}
```

### 示例5：错误处理

**输入数据：**
```json
{
    "数量": ["1234567", "无效数字", "abc"]
}
```

**配置：**
```json
{
    "Target": "数量",
    "From": "arabic",
    "To": "chinese",
    "Error": "数字格式错误: [{str}]"
}
```

**输出数据：**
```json
{
    "数量": ["一百二十三万四千五百六十七", "数字格式错误: [无效数字]", "数字格式错误: [abc]"]
}
```

### 示例6：带逗号的阿拉伯数字

**输入数据：**
```json
{
    "数量": ["1,234,567", "1,000,000"]
}
```

**配置：**
```json
{
    "Target": "数量",
    "From": "arabic",
    "To": "chinese"
}
```

**输出数据：**
```json
{
    "数量": ["一百二十三万四千五百六十七", "一百万"]
}
```

## 使用场景

### 场景1：生成中文报告

当你的数据是阿拉伯数字，需要生成中文报告时：

1. 使用 `excel_extractor` 提取数字数据
2. 使用 `number_string_formatter` 转换为中文数字
3. 使用 `docx_replacer` 生成中文报告

### 场景2：生成英文报告

当你需要生成英文报告时：

1. 提取阿拉伯数字数据
2. 使用格式化器转换为英文数字
3. 生成英文报告

### 场景3：数据标准化

当你的数据源包含不同格式的数字时：

1. 将中文数字转换为阿拉伯数字
2. 统一数据格式
3. 进行数据分析

## 支持的数字范围

| 类型 | 最小值 | 最大值 |
|------|--------|--------|
| Arabic | 0 | 999,999,999,999 |
| Chinese | 零 | 九千九百九十九亿九千九百九十九万九千九百九十九 |
| English | zero | nine hundred ninety-nine billion nine hundred ninety-nine million nine hundred ninety-nine thousand nine hundred ninety-nine |

## 注意事项

1. **From类型**：如果未指定From类型，默认使用arabic
2. **To类型**：如果未指定To类型，默认使用chinese
3. **错误处理**：可以通过Error参数自定义错误提示
4. **中文数字**：支持简体和大写数字
5. **英文数字**：支持连字符格式（如twenty-one）
6. **"两"的处理**：中文数字中的"两"会自动转换为"二"

## 错误处理

插件会在以下情况返回错误模板：

- 数字字符串为空
- 数字格式无效
- 数字超出支持范围
- 中文数字包含无效字符
- 英文数字包含无效单词

## 版本历史

- v1.0.0: 初始版本
  - 支持阿拉伯数字转中文数字
  - 支持阿拉伯数字转英文数字
  - 支持中文数字转阿拉伯数字
  - 支持英文数字转阿拉伯数字
  - 支持大数字（最高到9999亿）
  - 支持简体和大写中文数字
  - 支持错误处理配置