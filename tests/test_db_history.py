import pytest

from pc_storage_history.db import StorageDatabase
from pc_storage_history.scanner import FastScanner


@pytest.fixture
def temp_db(tmp_path):
    """Provide a StorageDatabase that auto-closes before tmp_path cleanup."""
    db_path = tmp_path / "test.db"
    db = StorageDatabase(str(db_path))
    yield db
    db.close()


def test_get_all_scans_empty(temp_db) -> None:
    scans = temp_db.get_all_scans()
    assert scans == []


def test_get_all_scans_multiple(temp_db, tmp_path) -> None:
    scan_dir1 = tmp_path / "dir1"
    scan_dir1.mkdir()
    (scan_dir1 / "a.txt").write_text("aaa")

    scan_dir2 = tmp_path / "dir2"
    scan_dir2.mkdir()
    (scan_dir2 / "b.txt").write_text("bbbbbb")

    scanner1 = FastScanner(str(scan_dir1))
    temp_db.save_scan(str(scan_dir1), scanner1.scan())

    scanner2 = FastScanner(str(scan_dir2))
    temp_db.save_scan(str(scan_dir2), scanner2.scan())

    scans = temp_db.get_all_scans()
    assert len(scans) == 2

    # Verify both scans are present (check by total_size regardless of order)
    sizes = {s["total_size"] for s in scans}
    assert sizes == {3, 6}

    paths = {s["root_path"] for s in scans}
    assert str(scan_dir1) in paths
    assert str(scan_dir2) in paths


def test_get_scan_stats_not_found(temp_db) -> None:
    stats = temp_db.get_scan_stats(999)
    assert stats is None
