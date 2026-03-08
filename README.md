# Python 项目模板

[![English Docs](https://img.shields.io/badge/docs-English-blue)](README.en.md)

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Build](https://img.shields.io/github/actions/workflow/status/Algieba-dean/modern-python-template/ci.yml?label=CI)
![License](https://img.shields.io/badge/license-MIT-green)
![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)
![Type Checker](https://img.shields.io/badge/type%20checker-mypy-blue)

一个旨在严格工程标准和自动化的现代化、工业级 Python 项目模板。

---

## 设置指南（维护者专用）

> **注意：** 在初始化新项目后，请删除本节内容或 `init_project.py` 脚本。

### 1. 启动项目

点击 **[Use this template]** 按钮创建一个新的代码仓库。

### 2. 初始化项目（自动化）

我们提供了一个脚本来自动完成重命名和配置过程。

1.  **运行初始化脚本**：

    ```bash
    # 确保已安装 Python 3
    python init_project.py
    ```

    按照提示输入你的 **项目名称**、**包名称**、**作者姓名** 和 **GitHub 用户名**。

2.  **脚本会自动执行以下操作**：

    - 重命名源代码目录（`src/my_package` -> `src/your_pkg`）。
    - 更新 `pyproject.toml`、`mkdocs.yml`、`Dockerfile` 和 GitHub 模板文件。
    - 替换 `SECURITY.md` 和 `CODE_OF_CONDUCT.md` 中的作者邮箱。
    - 更新引用信息和文档链接。
    - 重置 `uv.lock` 以便重新锁定依赖。

3.  **完成设置**：

    ```bash
    # 安装最新依赖
    uv sync --dev

    # 验证一切是否正常
    uv run pytest

    # 清理脚本
    rm init_project.py

    # 提交初始化的项目
    git add .
    git commit -m "chore: initialize project from template"
    ```

### 3. 设置 CI/CD 密钥

要启用 Codecov 覆盖率报告：

1. 前往 [Codecov](https://about.codecov.io/) 并为你的新仓库启用它。
2. 获取上传令牌（upload token）。
3. 前往 GitHub 仓库的 **Settings** -> **Secrets and variables** -> **Actions**。
4. 添加一个名为 `CODECOV_TOKEN` 的新仓库密钥。

### 4. 启用安全功能

1. 前往 **Settings** -> **Security** -> **Code security and analysis**。
2. 启用 **Private vulnerability reporting**。
   _（这确保了 "Report a vulnerability" 按钮能像 `SECURITY.md` 中描述的那样工作）_

### 5. 同步标签（Labels）

标签同步工作流会在首次推送到 `main` 分支时自动运行。

- 它将 **删除** 默认的 GitHub 标签（如 bug, enhancement）。
- 它将 **创建** 在 `.github/labels.yml` 中定义的标准化标签（如 `kind/bug`, `area/core`, `priority/high`）。
- 如果需要手动触发：前往 **Actions** -> **Sync Labels** -> **Run workflow**。

---

## 功能特性

- **包管理器**: [uv](https://github.com/astral-sh/uv) - 超快速的依赖管理工具。
- **Linter & Formatter**: [ruff](https://github.com/astral-sh/ruff) - 集成式工具，替代 Black、Isort 和 Flake8。
- **类型检查**: [mypy](https://mypy-lang.org/) - 已配置为 **strict mode**（严格模式）。
- **测试**: [pytest](https://docs.pytest.org/) + [pytest-cov](https://pytest-cov.readthedocs.io/)。
- **自动化**:
  - **Pre-commit hooks**: 在提交前确保代码质量。
  - **GitHub Actions**:
    - 自动测试与代码检查。
    - **Stale Bot**: 关闭长期不活跃的 Issues。
    - **Labeler**: 根据更改的文件自动标记 PR。
    - **Label Sync**: 强制统一仓库的标签标准。
    - **Release Drafter**: 根据 PR 标签自动以此撰写发布说明。
- **社区标准**:
  - 开箱即用的 Issue 模板（Bug 报告、功能请求）。
  - 带有检查清单的 PR 模板。
  - 安全策略与行为准则。

## 开发指南

### 先决条件

- Python 3.12+
- [uv](https://github.com/astral-sh/uv)

```bash
# 安装 uv
pip install uv
```

### 安装与设置

```bash
# 克隆仓库
git clone [https://github.com/your-username/your-new-project.git](https://github.com/your-username/your-new-project.git)
cd your-new-project

# 安装依赖（自动创建虚拟环境）
uv sync --dev

# 安装 pre-commit 钩子
uv run pre-commit install
```

### 文档

我们使用 MkDocs 构建文档。

```bash
# 1. 安装文档依赖
uv sync --extra docs

# 2. 启动本地服务器（实时预览）
uv run mkdocs serve
```

在浏览器中打开 http://127.0.0.1:8000

### 常用命令

我们使用 `uv run` 在虚拟环境中执行命令。

| 任务                | 命令                        |
| :------------------ | :-------------------------- |
| **运行测试**        | `uv run pytest`             |
| **代码检查 (Lint)** | `uv run ruff check .`       |
| **自动修复 Lint**   | `uv run ruff check . --fix` |
| **代码格式化**      | `uv run ruff format .`      |
| **类型检查**        | `uv run mypy .`             |

## 项目结构

```text
.
├── .github/                # GitHub Actions, 模板, 标签配置
├── src/
│   └── my_package/         # 源代码（init 脚本会自动重命名此目录）
├── tests/                  # 测试套件
├── pyproject.toml          # 项目配置 (Ruff, Mypy, Pytest)
├── .pre-commit-config.yaml # Pre-commit 钩子配置
├── uv.lock                 # 依赖锁定文件
└── init_project.py         # 初始化脚本（使用后删除）
```

## Docker 支持

本项目包含一个基于 `python:3.12-slim-bookworm` 的多阶段 `Dockerfile`，针对体积和安全性进行了优化。

### 构建镜像

```bash
docker build -t my_package_image .
```

### 运行容器

```bash
docker run --rm my_package_image
```

## 贡献指南

请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解我们的行为准则以及提交拉取请求（Pull Request）的流程。

## 许可证

本项目基于 MIT 许可证开源 - 详情请参阅 [LICENSE](LICENSE) 文件。
