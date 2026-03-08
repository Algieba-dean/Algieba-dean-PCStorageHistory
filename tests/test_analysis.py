import tempfile
from pathlib import Path

from pc_storage_history.analysis import Analyzer
from pc_storage_history.db import StorageDatabase
from pc_storage_history.scanner import FastScanner


def test_analyzer_tree_building() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        scan_dir = Path(temp_dir) / "scan_target"
        scan_dir.mkdir()

        # folder1 has a file
        folder1 = scan_dir / "folder1"
        folder1.mkdir()
        file1 = folder1 / "file1.txt"
        file1.write_text("Hello")  # 5 bytes

        # folder2 has a nested folder and a file
        folder2 = scan_dir / "folder2"
        folder2.mkdir()
        subfolder = folder2 / "sub"
        subfolder.mkdir()
        file2 = subfolder / "file2.txt"
        file2.write_text("World!")  # 6 bytes

        # Root file
        file3 = scan_dir / "root.txt"
        file3.write_text("Test")  # 4 bytes

        scanner = FastScanner(str(scan_dir))
        db = StorageDatabase(str(db_path))
        scan_id = db.save_scan(str(scan_dir), scanner.scan())

        analyzer = Analyzer(db)
        tree = analyzer.get_directory_tree(scan_id)

        assert tree is not None
        assert tree.path == str(scan_dir)
        # Total size: 5 + 6 + 4 = 15 bytes
        assert tree.size == 15
        assert tree.file_count == 3
        # root -> folder1, folder2
        assert len(tree.children) == 2

        folder1_node = tree.children["folder1"]
        assert folder1_node.size == 5
        assert folder1_node.file_count == 1
        assert len(folder1_node.children) == 0

        folder2_node = tree.children["folder2"]
        assert folder2_node.size == 6
        assert folder2_node.file_count == 1
        assert len(folder2_node.children) == 1

        sub_node = folder2_node.children["sub"]
        assert sub_node.size == 6
        assert sub_node.file_count == 1

        # Test largest files
        largest = analyzer.get_largest_files(scan_id)
        assert len(largest) == 3
        assert largest[0][1] == 6  # file2
        assert largest[1][1] == 5  # file1
        assert largest[2][1] == 4  # file3

        db.close()
