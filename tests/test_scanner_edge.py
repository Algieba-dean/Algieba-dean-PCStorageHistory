import os
import tempfile
from pathlib import Path

from pc_storage_history.scanner import FastScanner


def test_scanner_empty_directory() -> None:
    """Scanning an empty directory should yield only the root node."""
    with tempfile.TemporaryDirectory() as temp_dir:
        scanner = FastScanner(temp_dir)
        nodes = list(scanner.scan())

        assert len(nodes) == 1
        assert nodes[0].is_dir is True
        assert nodes[0].path == os.path.abspath(temp_dir)


def test_scanner_nested_directories() -> None:
    """Deeply nested directories should all be found."""
    with tempfile.TemporaryDirectory() as temp_dir:
        base = Path(temp_dir)
        deep = base / "a" / "b" / "c" / "d"
        deep.mkdir(parents=True)
        (deep / "deep.txt").write_text("deep file")

        scanner = FastScanner(temp_dir)
        nodes = list(scanner.scan())

        dirs = [n for n in nodes if n.is_dir]
        files = [n for n in nodes if not n.is_dir]

        # root, a, b, c, d = 5 dirs
        assert len(dirs) == 5
        assert len(files) == 1
        assert files[0].size == 9  # len("deep file")


def test_scanner_skips_symlink_loops(tmp_path) -> None:
    """Scanner should not follow symlinks to avoid infinite loops."""
    real_dir = tmp_path / "real"
    real_dir.mkdir()
    (real_dir / "file.txt").write_text("data")

    # Create a symlink that points back to parent
    link_path = real_dir / "loop_link"
    try:
        link_path.symlink_to(tmp_path, target_is_directory=True)
    except OSError:
        # On Windows, symlink creation may require elevated privileges
        return

    scanner = FastScanner(str(tmp_path))
    nodes = list(scanner.scan())

    # The symlink should appear as a directory node but NOT be followed
    # So we should NOT see infinite expansion
    paths = [n.path for n in nodes]
    assert str(real_dir / "file.txt") in paths
    # Symlink itself may appear, but its children should not be traversed
    assert len(nodes) < 20  # Sanity check: no infinite loop


def test_scanner_handles_special_characters(tmp_path) -> None:
    """Scanner should handle filenames with spaces and unicode."""
    special_dir = tmp_path / "my folder (1)"
    special_dir.mkdir()
    (special_dir / "file with spaces.txt").write_text("test")
    (special_dir / "unicode_文件.txt").write_text("unicode")

    scanner = FastScanner(str(tmp_path))
    nodes = list(scanner.scan())

    files = [n for n in nodes if not n.is_dir]
    assert len(files) == 2

    names = {Path(f.path).name for f in files}
    assert "file with spaces.txt" in names
    assert "unicode_文件.txt" in names
