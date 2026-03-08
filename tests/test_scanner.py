import tempfile
from pathlib import Path

from pc_storage_history.scanner import FastScanner


def test_fast_scanner_basic() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a mock directory structure
        base_dir = Path(temp_dir)
        (base_dir / "folder1").mkdir()
        (base_dir / "folder2").mkdir()

        file1 = base_dir / "file1.txt"
        file1.write_text("Hello World!")  # 12 bytes

        file2 = base_dir / "folder1" / "file2.txt"
        file2.write_text("Test")  # 4 bytes

        scanner = FastScanner(temp_dir)
        nodes = list(scanner.scan())

        # Root + 2 folders + 2 files = 5 nodes
        assert len(nodes) == 5

        files = [n for n in nodes if not n.is_dir]
        dirs = [n for n in nodes if n.is_dir]

        assert len(files) == 2
        assert len(dirs) == 3  # root, folder1, folder2

        file_sizes = {Path(n.path).name: n.size for n in files}
        assert file_sizes["file1.txt"] == 12
        assert file_sizes["file2.txt"] == 4
