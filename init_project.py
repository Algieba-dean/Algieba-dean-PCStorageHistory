#!/usr/bin/env python3
from pathlib import Path

# --- Configuration ---
# Default placeholders found in the template files
TEMPLATE_CONFIG = {
    "package_name": "my_package",  # Folder name in src/
    "project_name": "python-template",  # Project name in pyproject.toml
    "author_name": "Algieba-dean",  # Author name in pyproject.toml / CITATION.cff
    "author_email": "algieba.king@gmail.com",  # Email in SECURITY.md / pyproject.toml
    "github_username": "Algieba-dean",  # GitHub username for URLs
    "repo_name": "modern-python-template",  # Repo name used in README badges
}

# Directories and files to ignore during processing
IGNORE_DIRS = {
    ".git",
    ".venv",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    "site",
    "dist",
    "build",
    ".idea",
    ".vscode",
}
IGNORE_FILES = {"uv.lock", "init_project.py", ".DS_Store"}


def ask_user_input():
    print("\n🚀 Initializing new project. Please provide the following details:")

    new_project_name = (
        input("1. New Project Name (e.g., my-awesome-tool) [my-awesome-tool]: ").strip()
        or "my-awesome-tool"
    )

    # Suggest a package name by replacing hyphens with underscores
    default_pkg_name = new_project_name.replace("-", "_")
    new_package_name = (
        input(f"2. New Package Name (import name) [{default_pkg_name}]: ").strip()
        or default_pkg_name
    )

    new_author = input("3. Author Name [Your Name]: ").strip() or "Your Name"
    new_email = (
        input("4. Author Email [your.email@example.com]: ").strip()
        or "your.email@example.com"
    )
    new_github_user = (
        input("5. GitHub Username [your-github-user]: ").strip() or "your-github-user"
    )

    return {
        "new_project_name": new_project_name,
        "new_package_name": new_package_name,
        "new_author": new_author,
        "new_email": new_email,
        "new_github_user": new_github_user,
    }


def replace_in_file(file_path: Path, replacements: dict):
    """Reads a file, performs string replacements, and writes back if changed."""
    try:
        # Attempt to read as text (utf-8)
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Skip binary files
            return

        original_content = content

        for old, new in replacements.items():
            content = content.replace(old, new)

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            print(f"✅ Updated: {file_path}")
    except Exception as e:
        print(f"⚠️  Error processing {file_path}: {e}")


def main():
    config = ask_user_input()
    root = Path.cwd()

    # Define the mapping of old strings to new strings
    replacements = {
        # 1. Package Name (Source code imports, Dockerfile CMD, mkdocs references)
        TEMPLATE_CONFIG["package_name"]: config["new_package_name"],
        # 2. Project Name (pyproject.toml name)
        f'name = "{TEMPLATE_CONFIG["project_name"]}"': f'name = "{config["new_project_name"]}"',
        # 3. Author Name (pyproject.toml, LICENSE, CITATION.cff)
        TEMPLATE_CONFIG["author_name"]: config["new_author"],
        # Special case for CITATION.cff if format differs (e.g., split names),
        # but simple replacement usually works for this template.
        # 4. Email (SECURITY.md, CODE_OF_CONDUCT.md, pyproject.toml)
        TEMPLATE_CONFIG["author_email"]: config["new_email"],
        # 5. GitHub URLs & Badges
        # Replace: github.com/Algieba-dean/my_package
        f"github.com/{TEMPLATE_CONFIG['github_username']}/{TEMPLATE_CONFIG['package_name']}": f"github.com/{config['new_github_user']}/{config['new_project_name']}",
        # Replace README badges pointing to the template repo
        f"github.com/{TEMPLATE_CONFIG['github_username']}/{TEMPLATE_CONFIG['repo_name']}": f"github.com/{config['new_github_user']}/{config['new_project_name']}",
        # Replace Documentation URLs (GitHub Pages)
        f"https://{TEMPLATE_CONFIG['github_username']}.github.io/{TEMPLATE_CONFIG['package_name']}": f"https://{config['new_github_user']}.github.io/{config['new_project_name']}",
        # Replace PyPI/Generic references in pyproject.toml if present
        f"{TEMPLATE_CONFIG['github_username']}/{TEMPLATE_CONFIG['project_name']}": f"{config['new_github_user']}/{config['new_project_name']}",
    }

    print("\n📦 Replacing content in files...")

    # Walk through all files in the directory
    for path in root.rglob("*"):
        # Skip hidden directories and ignored folders
        if any(part in IGNORE_DIRS for part in path.parts):
            continue

        if path.is_file() and path.name not in IGNORE_FILES:
            replace_in_file(path, replacements)

    print("\n📂 Renaming source directory...")
    # Rename src/my_package to src/new_package_name
    src_dir = root / "src" / TEMPLATE_CONFIG["package_name"]
    target_dir = root / "src" / config["new_package_name"]

    if src_dir.exists():
        if not target_dir.exists():
            src_dir.rename(target_dir)
            print(f"✅ Renamed directory: {src_dir} -> {target_dir}")
        else:
            print(f"⚠️  Target directory already exists, skipping rename: {target_dir}")
    else:
        print(f"⚠️  Source directory not found: {src_dir} (Already renamed?)")

    print("\n🧹 Cleaning up environment...")
    # Remove uv.lock to force fresh dependency resolution for the new name
    lock_file = root / "uv.lock"
    if lock_file.exists():
        lock_file.unlink()
        print("✅ Removed old uv.lock")

    print("\n🎉 Initialization Complete!")
    print("-" * 50)
    print("Next Steps:")
    print("1. Run `uv sync` to install dependencies and regenerate lock file.")
    print("2. Run `uv run pytest` to ensure tests pass.")
    print("3. Delete this script: `rm init_project.py`")
    print(
        "4. Initialize git: `git init && git add . && git commit -m 'Initial commit'`"
    )
    print("-" * 50)


if __name__ == "__main__":
    main()
