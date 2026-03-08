# Contributing to this Project

First off, thanks for taking the time to contribute!

The following is a set of guidelines for contributing to this project. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## 🛠 Development Setup

We use modern Python tooling. Please follow these steps to set up your environment:

1.  **Install `uv`**: We use `uv` for ultra-fast dependency management.
    ```bash
    pip install uv
    ```
2.  **Install dependencies**:
    ```bash
    uv sync --dev
    ```
3.  **Install Pre-commit hooks** (Important!):
    This will ensure your code is formatted and linted before you commit.
    ```bash
    uv run pre-commit install
    ```

## Branching Strategy

- **`main`**: The strict production branch. Direct commits are blocked.
- **Feature Branches**: Please create a new branch for your changes.
  - Naming convention: `feat/new-feature`, `fix/bug-fix`, `docs/update-readme`.

## Pull Request Process

We use GitHub Actions to automate code quality checks.

1.  **Update your branch**: Make sure your branch is up to date with `main`.
2.  **Run Tests Locally**:
    ```bash
    uv run pytest
    ```
3.  **Check Types**:
    ```bash
    uv run mypy .
    ```
4.  **Fill out the PR Template**:
    - When you open a PR, a template will appear.
    - **Please verify the Checklist**. It reminds you to run tests and linters.
    - Link related issues (e.g., `Closes #123`) to auto-close them.
5.  **Labels**:
    - **Automatic Labeling**: You don't need to worry about labels! Our bots will automatically label your PR based on the files you changed (e.g., `area/core`, `area/tests`).

## Code Style & Standards

We enforce high code quality standards to keep the project maintainable.

- **Formatter**: `ruff` (handled by pre-commit).
- **Linter**: `ruff` (handled by pre-commit).
- **Type Checker**: `mypy` (Strict mode enabled).
- **Commit Messages**:
  We encourage **Conventional Commits** to keep history clean:
  - `feat: add new card logic`
  - `fix: resolve crash on empty board`
  - `docs: update setup guide`
  - `refactor: simplify dealer class`

## Reporting Bugs

Uses the **Issue Tabs** to report bugs. We have configured templates for:

- **Bug Report**: For reporting reproducible issues.
- **Feature Request**: For suggesting new ideas.

Please choose the appropriate template and fill in the required information.
