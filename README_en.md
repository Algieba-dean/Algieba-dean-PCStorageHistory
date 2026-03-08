# Python Project Template

[![中文说明](https://img.shields.io/badge/docs-中文版-F06060)](README.md)

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Build](https://img.shields.io/github/actions/workflow/status/Algieba-dean/modern-python-template/ci.yml?label=CI)
![License](https://img.shields.io/badge/license-MIT-green)
![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)
![Type Checker](https://img.shields.io/badge/type%20checker-mypy-blue)

A modern, industrial-grade Python project template aimed at strict engineering standards and automation.

---

## Setup Guide (For Maintainers)

> **Note:** Delete this section or the `init_project.py` script after you have initialized your new project.

### 1. Bootstrap

Click the **[Use this template]** button to create a new repository.

### 2. Initialize Project (Automated)

We provide a script to automate the renaming and configuration process.

1.  **Run the Initialization Script**:

    ```bash
    # Make sure you have Python 3 installed
    python init_project.py
    ```

    Follow the prompts to enter your **Project Name**, **Package Name**, **Author**, and **GitHub Username**.

2.  **What the script does for you**:

    - Renames the source directory (`src/my_package` -> `src/your_pkg`).
    - Updates `pyproject.toml`, `mkdocs.yml`, `Dockerfile`, and GitHub templates.
    - Replaces author emails in `SECURITY.md` and `CODE_OF_CONDUCT.md`.
    - Updates citations and documentation references.
    - Resets `uv.lock` for a fresh start.

3.  **Finalize**:

    ```bash
    # Install fresh dependencies
    uv sync --dev

    # Verify everything looks good
    uv run pytest

    # Clean up
    rm init_project.py

    # Commit the initialized project
    git add .
    git commit -m "chore: initialize project from template"
    ```

### 3. Setup CI/CD Secrets

To enable Codecov coverage reports:

1. Go to [Codecov](https://about.codecov.io/) and enable it for your new repo.
2. Get the upload token.
3. Go to your GitHub Repo **Settings** -> **Secrets and variables** -> **Actions**.
4. Add a new repository secret named `CODECOV_TOKEN`.

### 4. Enable Security Features

1. Go to **Settings** -> **Security** -> **Code security and analysis**.
2. Enable **Private vulnerability reporting**.
   _(This ensures the "Report a vulnerability" button works as described in `SECURITY.md`)_

### 5. Sync Labels

The label synchronization workflow runs automatically on the first push to `main`.

- It will **delete** default GitHub labels (bug, enhancement).
- It will **create** standardized labels (`kind/bug`, `area/core`, `priority/high`) defined in `.github/labels.yml`.
- If you need to trigger it manually: Go to **Actions** -> **Sync Labels** -> **Run workflow**.

---

## Features

- **Package Manager**: [uv](https://github.com/astral-sh/uv) - Ultra-fast dependency management.
- **Linter & Formatter**: [ruff](https://github.com/astral-sh/ruff) - The all-in-one tool replacing Black, Isort, and Flake8.
- **Type Checking**: [mypy](https://mypy-lang.org/) - Configured in **strict mode**.
- **Testing**: [pytest](https://docs.pytest.org/) + [pytest-cov](https://pytest-cov.readthedocs.io/).
- **Automation**:
  - **Pre-commit hooks**: Ensures code quality before committing.
  - **GitHub Actions**:
    - Automated Testing & Linting.
    - **Stale Bot**: Closes inactive issues.
    - **Labeler**: Auto-labels PRs based on changed files.
    - **Label Sync**: Enforces standardized labels across the repo.
    - **Release Drafter**: Automatically drafts release notes based on PR labels.
- **Community Standards**:
  - Ready-to-use Issue Templates (Bug Report, Feature Request).
  - PR Template with Checklist.
  - Security Policy & Code of Conduct.

## Development

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv)

```bash
# Install uv
pip install uv
```

### Setup

```bash
# Clone the repo
git clone [https://github.com/your-username/your-new-project.git](https://github.com/your-username/your-new-project.git)
cd your-new-project

# Install dependencies (creates a virtualenv automatically)
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install
```

### Documentation

We use MkDocs to build our documentation.

```bash
# 1. Install doc dependencies
uv sync --extra docs

# 2. Start local server (Live preview)
uv run mkdocs serve
```

Open http://127.0.0.1:8000 in your browser

### Common Commands

We use `uv run` to execute commands within the virtual environment.

| Task              | Command                     |
| :---------------- | :-------------------------- |
| **Run Tests**     | `uv run pytest`             |
| **Linting**       | `uv run ruff check .`       |
| **Auto-fix Lint** | `uv run ruff check . --fix` |
| **Formatting**    | `uv run ruff format .`      |
| **Type Check**    | `uv run mypy .`             |

## Project Structure

```text
.
├── .github/                # GitHub Actions, Templates, Labels
├── src/
│   └── my_package/         # Source code (Automatic renamed by init script)
├── tests/                  # Test suite
├── pyproject.toml          # Project configuration (Ruff, Mypy, Pytest)
├── .pre-commit-config.yaml # Pre-commit 钩子配置
├── uv.lock                 # Dependency lock file
└── init_project.py         # Initialization script (Delete after use)
```

## Docker Support

This project includes a multi-stage `Dockerfile` optimized for size and security, based on `python:3.12-slim-bookworm`.

### Build the Image

```bash
docker build -t my_package_image .
```

### Run the Container

```bash
docker run --rm my_package_image
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
