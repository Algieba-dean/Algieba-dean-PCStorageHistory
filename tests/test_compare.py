import pytest

from pc_storage_history.db import StorageDatabase
from pc_storage_history.scanner import FastScanner


@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test.db"
    db = StorageDatabase(str(db_path))
    yield db
    db.close()


def test_compare_scans_added_file(temp_db, tmp_path) -> None:
    """New files in the second scan should appear in 'added'."""
    scan_dir = tmp_path / "target"
    scan_dir.mkdir()
    (scan_dir / "a.txt").write_text("aaa")

    scanner1 = FastScanner(str(scan_dir))
    id1 = temp_db.save_scan(str(scan_dir), scanner1.scan())

    # Add a new file
    (scan_dir / "b.txt").write_text("bbbbb")

    scanner2 = FastScanner(str(scan_dir))
    id2 = temp_db.save_scan(str(scan_dir), scanner2.scan())

    diff = temp_db.compare_scans(id1, id2)

    assert len(diff["added"]) == 1
    assert diff["added"][0]["path"] == str(scan_dir / "b.txt")
    assert diff["added"][0]["size"] == 5
    assert len(diff["removed"]) == 0


def test_compare_scans_removed_file(temp_db, tmp_path) -> None:
    """Files missing from the second scan should appear in 'removed'."""
    scan_dir = tmp_path / "target"
    scan_dir.mkdir()
    file_a = scan_dir / "a.txt"
    file_a.write_text("aaa")
    (scan_dir / "b.txt").write_text("bbb")

    scanner1 = FastScanner(str(scan_dir))
    id1 = temp_db.save_scan(str(scan_dir), scanner1.scan())

    # Remove a file
    file_a.unlink()

    scanner2 = FastScanner(str(scan_dir))
    id2 = temp_db.save_scan(str(scan_dir), scanner2.scan())

    diff = temp_db.compare_scans(id1, id2)

    assert len(diff["removed"]) == 1
    assert diff["removed"][0]["path"] == str(file_a)
    assert len(diff["added"]) == 0


def test_compare_scans_changed_file(temp_db, tmp_path) -> None:
    """Files with different sizes should appear in 'changed'."""
    scan_dir = tmp_path / "target"
    scan_dir.mkdir()
    file_a = scan_dir / "a.txt"
    file_a.write_text("short")

    scanner1 = FastScanner(str(scan_dir))
    id1 = temp_db.save_scan(str(scan_dir), scanner1.scan())

    # Modify file size
    file_a.write_text("much longer content here")

    scanner2 = FastScanner(str(scan_dir))
    id2 = temp_db.save_scan(str(scan_dir), scanner2.scan())

    diff = temp_db.compare_scans(id1, id2)

    assert len(diff["changed"]) == 1
    assert diff["changed"][0]["path"] == str(file_a)
    assert diff["changed"][0]["old_size"] == 5
    assert diff["changed"][0]["new_size"] == 24
    assert diff["changed"][0]["diff"] == 19


def test_compare_scans_no_changes(temp_db, tmp_path) -> None:
    """Identical scans should produce empty diff."""
    scan_dir = tmp_path / "target"
    scan_dir.mkdir()
    (scan_dir / "a.txt").write_text("aaa")

    scanner1 = FastScanner(str(scan_dir))
    id1 = temp_db.save_scan(str(scan_dir), scanner1.scan())

    scanner2 = FastScanner(str(scan_dir))
    id2 = temp_db.save_scan(str(scan_dir), scanner2.scan())

    diff = temp_db.compare_scans(id1, id2)

    assert len(diff["added"]) == 0
    assert len(diff["removed"]) == 0
    assert len(diff["changed"]) == 0
