import tempfile
from pathlib import Path

from pc_storage_history.db import StorageDatabase
from pc_storage_history.scanner import FastScanner


def test_database_save_scan() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        scan_dir = Path(temp_dir) / "scan_target"
        scan_dir.mkdir()

        (scan_dir / "folder1").mkdir()
        file1 = scan_dir / "file1.txt"
        file1.write_text("Hello DB!")  # 9 bytes

        scanner = FastScanner(str(scan_dir))
        db = StorageDatabase(str(db_path))

        scan_id = db.save_scan(str(scan_dir), scanner.scan())

        assert scan_id == 1

        stats = db.get_scan_stats(scan_id)
        assert stats is not None
        assert stats["root_path"] == str(scan_dir)
        assert stats["total_size"] == 9
        assert stats["total_files"] == 1
        assert stats["total_dirs"] == 2  # root and folder1

        db.close()
