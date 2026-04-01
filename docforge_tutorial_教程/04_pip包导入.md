# DocForge 教程 04：pip 包导入

本教程介绍如何在 DocForge 中管理和使用 pip 包。DocForge 支持动态安装和导入 Python 包，以扩展插件功能。

## 1. pip 包管理概述

DocForge 提供了以下 pip 包管理功能：
- 安装、卸载、更新 Python 包
- 在插件中导入和使用外部包
- 管理包依赖关系
- 虚拟环境隔离（可选）

## 2. 安装 pip 包

### 2.1 使用 CoreAPI 安装
```python
from docforge.api.core_api import CoreAPI

api = CoreAPI()
api.initialize()

# 安装单个包
api.install_package("pandas")

# 安装指定版本
api.install_package("openpyxl==3.0.10")

# 安装多个包
api.install_packages(["pandas", "openpyxl", "python-docx"])

# 从 requirements.txt 安装
api.install_from_requirements("requirements.txt")

api.shutdown()
```

### 2.2 使用命令行安装
在 DocForge 的内置终端中，可以使用 pip 命令：
```bash
# 安装包
pip install pandas

# 安装指定版本
pip install openpyxl==3.0.10

# 从 requirements.txt 安装
pip install -r requirements.txt

# 升级包
pip install --upgrade pandas

# 卸载包
pip uninstall pandas
```

### 2.3 使用配置文件自动安装
在项目配置中指定依赖，框架初始化时自动安装：
```json
{
  "dependencies": {
    "packages": ["pandas>=1.5.0", "openpyxl", "python-docx"],
    "requirements_file": "requirements.txt"
  }
}
```

## 3. 在插件中使用 pip 包

### 3.1 直接导入
在插件文件中直接导入已安装的包：
```python
"""
excel_extractor.py
使用 pandas 和 openpyxl 的 Excel 提取器
"""

from docforge.plugins.base import BaseExtractor
from docforge.types import ExecutionResult, DataDict
import pandas as pd  # 直接导入 pandas

class ExcelExtractor(BaseExtractor):
    @property
    def name(self) -> str:
        return "excel_extractor"
    
    def extract(self, file_path: str) -> DataDict:
        # 使用 pandas 读取 Excel
        df = pd.read_excel(file_path)
        
        # 转换为 DataDict
        data = {}
        for column in df.columns:
            data[column] = df[column].astype(str).tolist()
        
        return data
```

### 3.2 条件导入
处理包可能未安装的情况：
```python
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

class ExcelExtractor(BaseExtractor):
    def extract(self, file_path: str) -> DataDict:
        if not HAS_PANDAS:
            raise ImportError("需要安装 pandas 包: pip install pandas")
        
        # 使用 pandas...
```

### 3.3 动态导入
根据配置动态导入包：
```python
import importlib

class FlexibleExtractor(BaseExtractor):
    def extract(self, file_path: str) -> DataDict:
        # 根据文件扩展名选择库
        if file_path.endswith('.xlsx'):
            module = importlib.import_module('openpyxl')
            # 使用 openpyxl 处理
        elif file_path.endswith('.csv'):
            module = importlib.import_module('csv')
            # 使用 csv 模块处理
```

## 4. 依赖管理

### 4.1 requirements.txt
在项目根目录创建 `requirements.txt`：
```
pandas>=1.5.0
openpyxl>=3.0.0
python-docx>=0.8.11
odfpy>=1.4.1
```

### 4.2 插件依赖声明
在插件文件中声明依赖：
```python
"""
插件依赖声明（注释形式）
# requires: pandas>=1.5.0
# requires: openpyxl>=3.0.0
# requires: python-docx>=0.8.11
"""

from docforge.plugins.base import BaseExtractor
import pandas as pd
import openpyxl

class ExcelExtractor(BaseExtractor):
    # 插件实现...
```

### 4.3 自动依赖检查
框架可以检查并安装插件依赖：
```python
from docforge.api.core_api import CoreAPI

api = CoreAPI()
api.initialize()

# 检查插件依赖
plugin_name = "excel_extractor"
dependencies = api.check_plugin_dependencies(plugin_name)

# 安装缺失的依赖
missing = [pkg for pkg, installed in dependencies.items() if not installed]
if missing:
    api.install_packages(missing)

api.shutdown()
```

## 5. 虚拟环境管理

### 5.1 创建虚拟环境
```python
api.create_virtual_environment("venv")
```

### 5.2 激活虚拟环境
```python
api.activate_virtual_environment("venv")
```

### 5.3 在虚拟环境中安装包
```python
api.install_in_virtual_environment("venv", "pandas")
```

## 6. 包版本管理

### 6.1 查看已安装包
```python
# 获取所有已安装包
packages = api.get_installed_packages()
for pkg in packages:
    print(f"{pkg['name']}=={pkg['version']}")

# 检查特定包
if api.is_package_installed("pandas"):
    version = api.get_package_version("pandas")
    print(f"pandas 版本: {version}")
```

### 6.2 版本兼容性检查
```python
# 检查版本是否满足要求
if api.check_package_version("pandas", ">=1.5.0"):
    print("pandas 版本符合要求")
else:
    print("需要升级 pandas")
```

### 6.3 导出依赖列表
```python
# 导出当前环境的依赖
api.export_requirements("requirements.txt")

# 导出特定插件的依赖
api.export_plugin_requirements("excel_extractor", "plugin_requirements.txt")
```

## 7. 常用 pip 包及其用途

### 7.1 数据处理
| 包名 | 用途 | 安装命令 |
|------|------|----------|
| pandas | 数据分析和处理 | `pip install pandas` |
| numpy | 数值计算 | `pip install numpy` |
| openpyxl | 读写 Excel 文件 | `pip install openpyxl` |
| xlrd | 读取旧版 Excel | `pip install xlrd` |

### 7.2 文档处理
| 包名 | 用途 | 安装命令 |
|------|------|----------|
| python-docx | 处理 Word 文档 | `pip install python-docx` |
| odfpy | 处理 OpenDocument 格式 | `pip install odfpy` |
| PyPDF2 | 处理 PDF 文件 | `pip install PyPDF2` |
| markdown | 处理 Markdown | `pip install markdown` |

### 7.3 文件格式
| 包名 | 用途 | 安装命令 |
|------|------|----------|
| chardet | 检测文件编码 | `pip install chardet` |
| python-magic | 检测文件类型 | `pip install python-magic` |

### 7.4 网络和 API
| 包名 | 用途 | 安装命令 |
|------|------|----------|
| requests | HTTP 请求 | `pip install requests` |
| beautifulsoup4 | 解析 HTML | `pip install beautifulsoup4` |

## 8. 示例：使用 pandas 处理 Excel

### 8.1 完整插件示例
```python
"""
advanced_excel_extractor.py
使用 pandas 的高级 Excel 提取器
"""

from docforge.plugins.base import BaseExtractor
from docforge.types import ExecutionResult, DataDict
import pandas as pd
from typing import Dict, List, Any

class AdvancedExcelExtractor(BaseExtractor):
    @property
    def name(self) -> str:
        return "advanced_excel_extractor"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def plugin_type(self) -> str:
        return "extractor"
    
    def extract(self, file_path: str, **kwargs) -> DataDict:
        """
        使用 pandas 提取 Excel 数据
        
        支持配置：
        - sheet_name: 工作表名称或索引
        - usecols: 要读取的列
        - skiprows: 跳过的行
        """
        config = kwargs.get('config', {})
        
        # 读取参数
        sheet_name = config.get('sheet_name', 0)
        usecols = config.get('usecols', None)
        skiprows = config.get('skiprows', None)
        
        # 使用 pandas 读取
        df = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            usecols=usecols,
            skiprows=skiprows
        )
        
        # 转换为 DataDict
        data = {}
        for column in df.columns:
            # 处理 NaN 值
            values = df[column].fillna('').astype(str).tolist()
            data[column] = values
        
        return data
    
    def execute(self, file_path: str = None, **kwargs) -> ExecutionResult:
        if file_path is None:
            return ExecutionResult(
                success=False,
                errors=["file_path parameter is required"]
            )
        
        try:
            data = self.extract(file_path, **kwargs)
            return ExecutionResult(success=True, data=data)
        except Exception as e:
            return ExecutionResult(success=False, errors=[str(e)])
```

### 8.2 使用配置
```json
{
  "step_id": "extract",
  "plugin_name": "advanced_excel_extractor",
  "config": {
    "sheet_name": "数据表",
    "usecols": "A:D",
    "skiprows": 2
  }
}
```

## 9. 错误处理

### 9.1 包未安装错误
```python
try:
    import pandas as pd
except ImportError as e:
    raise ImportError(
        f"缺少必要的包: {e.name}\n"
        f"请运行: pip install {e.name}"
    ) from e
```

### 9.2 版本不兼容错误
```python
import pandas as pd

if pd.__version__ < '1.5.0':
    raise ImportError(
        f"pandas 版本过低: {pd.__version__}\n"
        f"需要 pandas>=1.5.0\n"
        f"请运行: pip install --upgrade pandas"
    )
```

### 9.3 导入回退
```python
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    # 使用内置模块或其他方案
    import imghdr
```

## 10. 最佳实践

### 10.1 依赖最小化
- 只导入实际使用的包
- 避免导入大型不需要的库
- 使用条件导入处理可选功能

### 10.2 版本锁定
在 `requirements.txt` 中锁定版本：
```
pandas==1.5.3
openpyxl==3.0.10
python-docx==0.8.11
```

### 10.3 虚拟环境隔离
为不同项目使用独立的虚拟环境，避免包冲突。

### 10.4 依赖文档化
在插件文档中说明所需的包和版本。

### 10.5 安装检查
在插件初始化时检查依赖：
```python
def initialize(self, context):
    # 检查依赖
    required = ['pandas', 'openpyxl']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        raise ImportError(f"缺少依赖: {', '.join(missing)}")
    
    return True
```

## 11. 常见问题

### 11.1 安装速度慢
使用国内镜像源：
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pandas
```

或在配置中设置：
```json
{
  "pip": {
    "index_url": "https://pypi.tuna.tsinghua.edu.cn/simple",
    "trusted_host": "pypi.tuna.tsinghua.edu.cn"
  }
}
```

### 11.2 权限问题
使用 `--user` 选项安装到用户目录：
```bash
pip install --user pandas
```

### 11.3 编译错误
某些包需要编译，可以安装预编译版本：
```bash
# 对于 Windows
pip install pandas‑1.5.3‑cp310‑cp310‑win_amd64.whl
```

### 11.4 包冲突
使用虚拟环境隔离：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install pandas
```

## 12. 下一步

- 阅读 [05_总体组合运行方法.md](05_总体组合运行方法.md) 了解如何组合实例、工作流和插件
- 阅读 [06_总结.md](06_总结.md) 获取完整的工作流程总结
- 查看 `docforge_plugins` 目录下的实际插件示例

---
*最后更新：2026年3月30日*