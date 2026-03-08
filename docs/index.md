# PC Storage History

一个快速的磁盘空间分析工具，支持历史记录、快照对比与可视化树状目录浏览。

## 功能特性

- **极速扫描** - 基于 `os.scandir` 的高性能文件系统遍历
- **历史快照** - 每次扫描自动保存到 SQLite，可随时回溯
- **快照对比** - 比较两次扫描，找出新增、删除、变更的文件
- **目录树分析** - 自底向上聚合大小，按体积降序排列
- **大文件排行** - 快速定位最大的文件
- **GUI 界面** - PySide6 桌面应用，树形浏览 + 右键打开资源管理器

## 快速开始

```bash
# 安装依赖
uv sync

# 启动 GUI
uv run pc-storage-history
```

## 编程接口

```python
from pc_storage_history import FastScanner, StorageDatabase, Analyzer

# 扫描目录
scanner = FastScanner("C:/Users")
db = StorageDatabase("history.db")
scan_id = db.save_scan("C:/Users", scanner.scan())

# 分析
analyzer = Analyzer(db)
tree = analyzer.get_directory_tree(scan_id)
largest = analyzer.get_largest_files(scan_id, limit=20)

# 快照对比
diff = db.compare_scans(old_scan_id=1, new_scan_id=2)
print(diff["added"], diff["removed"], diff["changed"])
```
