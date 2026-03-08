# PC Storage History

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green)
![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)

一个快速的磁盘空间分析工具，支持历史记录与可视化树状目录浏览。

## 功能特性

- **极速扫描**: 基于 `os.scandir` 的高性能文件系统遍历，自动跳过无权限目录和符号链接循环。
- **历史记录**: 每次扫描结果自动保存到本地 SQLite 数据库，可随时回溯查看历史快照。
- **目录树分析**: 自底向上聚合文件夹大小，按体积降序排列，快速定位空间占用大户。
- **大文件排行**: 一键查看指定扫描中最大的文件列表。
- **多线程并发扫描**: `ParallelScanner` 使用 ThreadPoolExecutor 分发目录级 I/O，大盘扫描显著提速。
- **GUI 界面**: 基于 PySide6 (Qt) 的现代桌面应用，支持：
  - 树形目录浏览（懒加载，大数据量不卡顿）
  - **Treemap 可视化**: 色块面积直观反映目录大小占比
  - **快照对比面板**: 选择两次扫描，一键查看增/删/改文件列表
  - 后台线程扫描（UI 不冻结）
  - 右键菜单：在资源管理器中打开 / 复制路径
  - 历史记录对话框：浏览并加载过去的扫描快照
- **导出功能**: 将扫描结果或对比差异导出为 CSV / JSON 文件

## 快速开始

### 先决条件

- Python 3.12+
- [uv](https://github.com/astral-sh/uv)

### 安装与运行

```bash
# 克隆仓库
git clone https://github.com/Algieba-dean/Algieba-dean-PCStorageHistory.git
cd Algieba-dean-PCStorageHistory

# 安装依赖
uv sync

# 启动 GUI
uv run pc-storage-history
```

## 开发指南

```bash
# 安装开发依赖
uv sync --dev

# 安装 pre-commit 钩子
uv run pre-commit install
```

### 常用命令

| 任务                | 命令                        |
| :------------------ | :-------------------------- |
| **启动应用**        | `uv run pc-storage-history` |
| **运行测试**        | `uv run pytest`             |
| **代码检查 (Lint)** | `uv run ruff check .`       |
| **自动修复 Lint**   | `uv run ruff check . --fix` |
| **代码格式化**      | `uv run ruff format .`      |
| **类型检查**        | `uv run mypy .`             |

## 项目结构

```text
.
├── src/
│   └── pc_storage_history/
│       ├── scanner.py       # 高速文件系统扫描器 (os.scandir)
│       ├── db.py            # SQLite 数据库层（快照存储与历史管理）
│       ├── analysis.py      # 数据聚合与分析（目录树、大文件排行）
│       ├── gui_model.py     # Qt 树模型（懒加载 QAbstractItemModel）
│       ├── gui.py           # 主窗口 GUI（PySide6）
│       └── main.py          # CLI 入口（性能测试用）
├── tests/                   # 测试套件（12 个测试用例）
├── pyproject.toml           # 项目配置
└── uv.lock                  # 依赖锁定文件
```

## 架构概览

```
Scanner (os.scandir)  →  Database (SQLite)  →  Analyzer (聚合)  →  GUI (PySide6 TreeView)
         ↓                      ↓                    ↓                      ↓
   遍历文件系统           批量存储快照          构建目录树           懒加载渲染 + 右键菜单
```

## 许可证

本项目基于 MIT 许可证开源 - 详情请参阅 [LICENSE](LICENSE) 文件。
