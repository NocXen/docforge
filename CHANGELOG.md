# 更新日志

所有重要的项目变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.1.0] - 2026-04-01

### 新增
- 初始版本发布
- 核心框架架构（API层、Services层、Plugins层、Storage层、Utils层）
- 插件系统（支持自定义插件开发）
- 工作流引擎（支持多步骤工作流执行）
- CLI命令行工具
- Python API接口

### 内置插件
- Excel提取器（excel_extractor）：从Excel文件提取数据
- Excel替换器（excel_replacer）：将数据填入Excel模板
- Word替换器（docx_replacer）：将数据填入Word模板
- Word合并器（docx_combiner）：合并多个Word文档
- ...

### 文档
- 完整的README文档
- 详细的教程文档（docforge_tutorial_教程/）
- 插件开发指南
- 故障排除指南

### 特性
- 零依赖（仅使用Python标准库）
- 跨平台支持（Windows、Linux、macOS）
- 配置文件管理
- 日志系统
- 事件总线

## 未来计划

### [0.2.0] - 计划中
- [ ] 添加更多内置插件
- [ ] 支持更多文件格式
- [ ] 性能优化
- [ ] 单元测试覆盖
- [ ] GUI界面（梦想）

---

*更多详细信息请参阅 [GitHub Releases](https://github.com/nocxen/docforge/releases)*