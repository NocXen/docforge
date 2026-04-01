# 贡献指南

感谢您对 DocForge 项目的关注！我们欢迎所有形式的贡献。

## 如何贡献

### 报告问题

1. 在 GitHub 上创建 Issue
2. 描述问题的详细情况
3. 提供复现步骤（如果适用）
4. 提供环境信息（操作系统、Python 版本等）

### 提交代码

1. Fork 本项目
2. 创建特性分支：`git checkout -b feature/my-feature`
3. 提交更改：`git commit -am 'Add my feature'`
4. 推送分支：`git push origin feature/my-feature`
5. 提交 Pull Request

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/nocxen/docforge.git
cd docforge

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black docforge_pip_pip包/docforge/

# 代码检查
flake8 docforge_pip_pip包/docforge/
```

## 代码规范

- 遵循 PEP 8 编码规范
- 使用 Black 进行代码格式化
- 使用 Flake8 进行代码检查
- 为新功能编写测试
- 更新相关文档

## 插件开发

如果您想贡献插件，请参考：
- [插件开发指南](docforge_tutorial_教程/03_插件编写及使用.md)
- [插件开发详细指南](docforge_tutorial_教程/PLUGIN_DEVELOPMENT_GUIDE.md)

## 文档贡献

文档位于 `docforge_tutorial_教程/` 目录，欢迎改进和补充。

## 行为准则

- 尊重所有参与者
- 建设性地提出意见
- 帮助新手入门
- 保持友好和专业

## 联系方式

- 项目主页：https://github.com/nocxen/docforge
- 问题反馈：https://github.com/nocxen/docforge/issues
- 邮箱：nocxens@qq.com

感谢您的贡献！