# Storage层 - 数据持久化层

## 概述

Storage层是 DocForge 框架的数据持久化层，负责**数据存储、配置管理和缓存服务**。它为上层业务逻辑提供统一的数据访问接口，屏蔽底层存储细节。

### 架构定位

```
┌─────────────────────────────────────────────────────────┐
│                    DocForge 框架                         │
├─────────────────────────────────────────────────────────┤
│  plugins层    │  插件系统，产生和消费数据                  │
├─────────────────────────────────────────────────────────┤
│  services层   │  业务逻辑层，使用数据完成业务              │
├─────────────────────────────────────────────────────────┤
│  storage层    │  数据持久化层（本层）                      │
│               │  - 数据库存储                             │
│               │  - 配置管理                               │
│               │  - 缓存服务                               │
└─────────────────────────────────────────────────────────┘
```

## 目录结构

```
storage/
├── README.md              ← 本文档
├── __init__.py            ← 包初始化，导出核心类
├── database.py            ← SQLite数据库管理器
├── config.py              ← JSON配置管理器
└── cache.py               ← 多级缓存管理器
```

## 核心组件

### 1. DatabaseManager - 数据库管理器

**文件**: `database.py`

**职责**: 封装SQLite数据库操作，提供高级数据访问接口

**核心功能**:
| 功能类别 | 方法 | 说明 |
|---------|------|------|
| 连接管理 | `connect()` | 连接数据库 |
| | `disconnect()` | 断开连接 |
| | `is_connected()` | 检查连接状态 |
| 表操作 | `create_tables()` | 创建所有必要的表 |
| | `drop_tables()` | 删除所有表 |
| | `table_exists()` | 检查表是否存在 |
| CRUD操作 | `insert()` | 插入数据 |
| | `select()` | 查询数据 |
| | `update()` | 更新数据 |
| | `delete()` | 删除数据 |
| 事务管理 | `begin_transaction()` | 开始事务 |
| | `commit()` | 提交事务 |
| | `rollback()` | 回滚事务 |
| 备份恢复 | `backup()` | 备份数据库 |
| | `restore()` | 恢复数据库 |
| | `vacuum()` | 压缩数据库 |

**数据库表结构**:

#### projects 表（项目信息）
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 主键ID |
| name | TEXT | NOT NULL | 项目名称 |
| path | TEXT | NOT NULL | 项目路径 |
| config | TEXT | DEFAULT '{}' | 项目配置（JSON格式） |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

#### workflows 表（工作流定义）
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 主键ID |
| name | TEXT | NOT NULL UNIQUE | 工作流名称（唯一） |
| description | TEXT | DEFAULT '' | 工作流描述 |
| version | TEXT | DEFAULT '1.0.0' | 版本号 |
| steps | TEXT | DEFAULT '[]' | 步骤定义（JSON格式） |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

#### executions 表（执行记录）
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 主键ID |
| workflow_name | TEXT | NOT NULL | 工作流名称 |
| status | TEXT | DEFAULT 'pending' | 执行状态 |
| input_files | TEXT | DEFAULT '[]' | 输入文件列表（JSON格式） |
| output_files | TEXT | DEFAULT '[]' | 输出文件列表（JSON格式） |
| error_message | TEXT | DEFAULT '' | 错误信息 |
| execution_time | REAL | DEFAULT 0.0 | 执行耗时（秒） |
| started_at | TIMESTAMP | - | 开始时间 |
| completed_at | TIMESTAMP | - | 完成时间 |

#### plugin_configs 表（插件配置）
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 主键ID |
| plugin_name | TEXT | NOT NULL | 插件名称 |
| config | TEXT | DEFAULT '{}' | 插件配置（JSON格式） |
| enabled | INTEGER | DEFAULT 1 | 是否启用（1启用，0禁用） |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

---

### 2. ConfigManager - 配置管理器

**文件**: `config.py`

**职责**: 管理应用程序的JSON配置文件

**核心功能**:
| 功能类别 | 方法 | 说明 |
|---------|------|------|
| 配置读取 | `load()` | 加载配置文件 |
| | `get()` | 获取配置值（支持点分隔嵌套键） |
| | `get_section()` | 获取配置段 |
| | `get_all()` | 获取所有配置 |
| 配置写入 | `set()` | 设置配置值 |
| | `set_section()` | 设置配置段 |
| | `save()` | 保存配置到文件 |
| 配置管理 | `has()` | 检查配置键是否存在 |
| | `delete()` | 删除配置键 |
| | `reset()` | 重置为默认配置 |
| | `merge()` | 深度合并配置 |
| 验证 | `validate()` | 验证配置有效性 |
| | `set_defaults()` | 设置默认值 |
| 导入导出 | `export_config()` | 导出配置 |
| | `import_config()` | 导入配置 |

**配置文件格式示例**:
```json
{
  "database": {
    "path": "docforge.db",
    "backup_enabled": true
  },
  "logging": {
    "level": "INFO",
    "file": "docforge.log"
  },
  "cache": {
    "enabled": true,
    "ttl": 3600
  }
}
```

---

### 3. CacheManager - 缓存管理器

**文件**: `cache.py`

**职责**: 提供多级缓存服务，提升数据访问性能

**核心功能**:
| 功能类别 | 方法 | 说明 |
|---------|------|------|
| 内存缓存 | `set_memory()` | 设置内存缓存 |
| | `get_memory()` | 获取内存缓存 |
| | `delete_memory()` | 删除内存缓存 |
| | `clear_memory()` | 清空内存缓存 |
| 磁盘缓存 | `set_disk()` | 设置磁盘缓存 |
| | `get_disk()` | 获取磁盘缓存 |
| | `delete_disk()` | 删除磁盘缓存 |
| | `clear_disk()` | 清空磁盘缓存 |
| 文件哈希 | `get_file_hash()` | 获取文件哈希（带缓存） |
| | `invalidate_file_hash()` | 使文件哈希缓存失效 |
| 统计清理 | `get_stats()` | 获取缓存统计信息 |
| | `cleanup_expired()` | 清理过期缓存 |

**缓存层级对比**:
| 特性 | 内存缓存 | 磁盘缓存 |
|------|---------|---------|
| 速度 | ⚡ 极快 | 🐢 较慢 |
| 持久性 | ❌ 重启丢失 | ✅ 持久保存 |
| 容量 | 有限（受内存限制） | 大（受磁盘限制） |
| 默认TTL | 3600秒（1小时） | 86400秒（24小时） |
| 适用场景 | 频繁访问的热数据 | 较大或不常访问的数据 |

---

## 使用指南

### 数据库操作

#### 基础用法

```python
from docforge.storage.database import DatabaseManager

# 1. 创建数据库管理器
db = DatabaseManager("docforge.db")

# 2. 连接数据库
if not db.connect():
    print("数据库连接失败")
    exit(1)

# 3. 创建表
db.create_tables()

# 4. 插入数据
project_id = db.insert("projects", {
    "name": "我的项目",
    "path": "/path/to/project",
    "config": {"setting1": "value1"}
})

# 5. 查询数据
projects = db.select(
    "projects",
    columns=["id", "name", "path"],
    where="name = ?",
    params=("我的项目",),
    order_by="created_at DESC",
    limit=10
)

# 6. 更新数据
affected_rows = db.update(
    "projects",
    {"name": "新项目名称", "updated_at": "2026-03-31"},
    "id = ?",
    (project_id,)
)

# 7. 删除数据
deleted_rows = db.delete("projects", "id = ?", (project_id,))

# 8. 断开连接
db.disconnect()
```

#### 事务操作

```python
# 使用事务确保数据一致性
db.begin_transaction()
try:
    db.insert("projects", {"name": "项目1", "path": "/path1"})
    db.insert("workflows", {"name": "工作流1", "steps": []})
    db.commit()
    print("事务提交成功")
except Exception as e:
    db.rollback()
    print(f"事务回滚: {e}")
```

#### 备份与恢复

```python
# 备份数据库
if db.backup("backups/docforge_backup_20260331.db"):
    print("备份成功")
else:
    print("备份失败")

# 恢复数据库
if db.restore("backups/docforge_backup_20260331.db"):
    print("恢复成功")
else:
    print("恢复失败")

# 压缩数据库（释放未使用空间）
db.vacuum()
```

---

### 配置管理

#### 基础用法

```python
from docforge.storage.config import ConfigManager

# 1. 创建配置管理器
config = ConfigManager("config.json")

# 2. 加载配置
config.load()

# 3. 获取配置（支持点分隔的嵌套键）
db_path = config.get("database.path", "docforge.db")
log_level = config.get("logging.level", "INFO")
cache_ttl = config.get("cache.ttl", 3600)

# 4. 设置配置
config.set("database.path", "/new/path/docforge.db")
config.set("logging.level", "DEBUG")
config.set("cache.enabled", True)

# 5. 保存配置
config.save()
```

#### 高级用法

```python
# 检查配置是否存在
if config.has("database.backup_enabled"):
    backup_enabled = config.get("database.backup_enabled")

# 获取整个配置段
db_config = config.get_section("database")
# 返回: {"path": "docforge.db", "backup_enabled": true}

# 删除配置项
config.delete("logging.file")
config.save()

# 深度合并配置
new_config = {
    "database": {
        "pool_size": 10
    },
    "new_section": {
        "key": "value"
    }
}
config.merge(new_config)
config.save()

# 导出配置
config.export_config("exported_config.json")

# 导入配置
config.import_config("imported_config.json")
config.save()
```

#### 配置验证

```python
# 设置默认值
config.set_defaults({
    "database": {"path": "docforge.db"},
    "logging": {"level": "INFO"}
})

# 验证配置
errors = config.validate()
if errors:
    print("配置错误:", errors)
else:
    print("配置有效")
```

---

### 缓存管理

#### 基础用法

```python
from docforge.storage.cache import CacheManager

# 1. 创建缓存管理器
cache = CacheManager(".cache")

# 2. 内存缓存操作
cache.set_memory("user:123", {"name": "张三", "age": 25}, ttl=3600)
user = cache.get_memory("user:123")
cache.delete_memory("user:123")

# 3. 磁盘缓存操作
cache.set_disk("large_data", {"items": list(range(1000))}, ttl=86400)
data = cache.get_disk("large_data")
cache.delete_disk("large_data")

# 4. 清理过期缓存
cleaned_count = cache.cleanup_expired()
print(f"清理了 {cleaned_count} 个过期缓存")
```

#### 文件哈希缓存

```python
# 获取文件哈希（自动缓存）
file_hash = cache.get_file_hash("/path/to/file.docx")
print(f"文件哈希: {file_hash}")

# 文件修改后使缓存失效
cache.invalidate_file_hash("/path/to/file.docx")
```

#### 缓存统计

```python
# 获取缓存统计信息
stats = cache.get_stats()
print(f"内存缓存: {stats['memory']['count']} 项")
print(f"磁盘缓存: {stats['disk']['count']} 项, {stats['disk']['size_mb']} MB")

# 清空缓存
cache.clear_memory()  # 清空内存缓存
cache.clear_disk()    # 清空磁盘缓存
```

---

## 数据存储位置

默认情况下，DocForge 的数据存储在以下位置：

### Windows
```
C:\Users\<用户名>\.docforge\
├── docforge.db              # 主数据库
├── config.json              # 全局配置
├── docforge.log             # 日志文件
├── cache/                   # 缓存目录
│   └── disk/                # 磁盘缓存文件
└── backups/                 # 备份目录
```

### Linux/macOS
```
~/.docforge/
├── docforge.db              # 主数据库
├── config.json              # 全局配置
├── docforge.log             # 日志文件
├── cache/                   # 缓存目录
│   └── disk/                # 磁盘缓存文件
└── backups/                 # 备份目录
```

### 自定义路径

```python
# 使用自定义数据库路径
db = DatabaseManager("/custom/path/docforge.db")

# 使用自定义配置路径
config = ConfigManager("/custom/path/config.json")

# 使用自定义缓存目录
cache = CacheManager("/custom/path/cache")
```

---

## 最佳实践

### 1. 数据库操作最佳实践

```python
# ✅ 推荐：使用上下文管理器模式
class DatabaseContext:
    def __init__(self, db_path):
        self.db = DatabaseManager(db_path)
    
    def __enter__(self):
        self.db.connect()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.disconnect()

# 使用示例
with DatabaseContext("docforge.db") as db:
    db.create_tables()
    db.insert("projects", {"name": "项目1", "path": "/path1"})
```

### 2. 配置管理最佳实践

```python
# ✅ 推荐：使用单例模式管理全局配置
class AppConfig:
    _instance = None
    _config = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._config = ConfigManager("config.json")
            cls._config.load()
        return cls._config

# 使用示例
config = AppConfig.get_instance()
db_path = config.get("database.path")
```

### 3. 缓存使用最佳实践

```python
# ✅ 推荐：使用缓存装饰器
def cached(ttl=3600, cache_type="memory"):
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache = CacheManager(".cache")
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            
            # 尝试从缓存获取
            if cache_type == "memory":
                result = cache.get_memory(cache_key)
            else:
                result = cache.get_disk(cache_key)
            
            if result is not None:
                return result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            if cache_type == "memory":
                cache.set_memory(cache_key, result, ttl)
            else:
                cache.set_disk(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# 使用示例
@cached(ttl=3600, cache_type="memory")
def get_user_info(user_id):
    # 耗时操作
    return {"id": user_id, "name": "张三"}
```

---

## 错误处理

### 常见错误及解决方案

#### 1. 数据库连接失败

```python
# 错误处理示例
db = DatabaseManager("docforge.db")
if not db.connect():
    print("数据库连接失败，可能原因：")
    print("1. 数据库文件被占用")
    print("2. 磁盘空间不足")
    print("3. 权限不足")
    # 尝试使用备用路径
    db = DatabaseManager("/tmp/docforge.db")
    db.connect()
```

#### 2. 配置文件损坏

```python
config = ConfigManager("config.json")
if not config.load():
    print("配置加载失败，使用默认配置")
    config.set_defaults({
        "database": {"path": "docforge.db"},
        "logging": {"level": "INFO"}
    })
    config.save()
```

#### 3. 缓存空间不足

```python
cache = CacheManager(".cache")
stats = cache.get_stats()

# 检查磁盘缓存大小
if stats['disk']['size_mb'] > 100:  # 超过100MB
    print("缓存空间过大，执行清理")
    cache.cleanup_expired()
    cache.clear_disk()
```

---

## 性能优化

### 1. 数据库优化

```python
# 批量插入使用事务
db.begin_transaction()
for i in range(1000):
    db.insert("projects", {"name": f"项目{i}", "path": f"/path{i}"})
db.commit()

# 使用索引（在create_tables中添加）
cursor.execute('CREATE INDEX IF NOT EXISTS idx_project_name ON projects(name)')
```

### 2. 缓存优化

```python
# 根据数据特性选择缓存类型
# 频繁访问的小数据 -> 内存缓存
cache.set_memory("hot_data", small_data, ttl=3600)

# 较大的不常访问数据 -> 磁盘缓存
cache.set_disk("cold_data", large_data, ttl=86400)
```

### 3. 配置优化

```python
# 启动时加载一次配置，避免重复IO
config = ConfigManager("config.json")
config.load()

# 运行期间只修改内存中的配置
config.set("runtime.value", 123)

# 程序退出时保存
config.save()
```

---

## 常见问题 FAQ

### Q1: 数据库文件损坏了怎么办？

**A**: 
1. 检查是否有备份文件（在 `backups/` 目录）
2. 使用 `db.restore(backup_path)` 恢复备份
3. 如果没有备份，删除损坏的数据库文件，框架会自动重建
4. 定期调用 `db.backup()` 创建备份

### Q2: 配置文件在哪里？

**A**: 默认在用户目录下的 `.docforge/config.json`
- Windows: `C:\Users\<用户名>\.docforge\config.json`
- Linux/macOS: `~/.docforge/config.json`

### Q3: 缓存占用太多空间怎么办？

**A**: 
```python
# 方法1: 清理过期缓存
cache.cleanup_expired()

# 方法2: 清空所有磁盘缓存
cache.clear_disk()

# 方法3: 手动删除缓存目录
# rm -rf ~/.docforge/cache/
```

### Q4: 如何备份数据？

**A**: 
```python
# 备份数据库
db.backup("backups/backup_20260331.db")

# 导出配置
config.export_config("backups/config_20260331.json")
```

### Q5: 多个进程同时访问数据库怎么办？

**A**: SQLite支持多读单写，建议：
1. 使用WAL模式：`PRAGMA journal_mode=WAL`
2. 设置超时：`sqlite3.connect(timeout=30)`
3. 使用事务避免冲突

### Q6: 如何迁移数据到新版本？

**A**: 
```python
# 1. 备份旧数据
db.backup("backup_old.db")

# 2. 创建新表结构
db.create_tables()

# 3. 迁移数据（根据需要编写迁移脚本）
old_data = db.select("old_table")
for row in old_data:
    db.insert("new_table", transform_data(row))
```

---

## 技术规格

| 项目 | 规格 |
|------|------|
| 数据库类型 | SQLite 3.x |
| 配置格式 | JSON |
| 缓存序列化 | Pickle (磁盘), 直接存储 (内存) |
| 支持平台 | Windows, Linux, macOS |
| Python版本 | 3.7+ |
| 依赖包 | 无外部依赖（仅使用标准库） |

---

## 更新日志

### v1.0.0 (2026-03-27)
- 初始版本
- 实现 DatabaseManager
- 实现 ConfigManager
- 实现 CacheManager

---

*最后更新：2026年3月31日*