import json

import pytest

from pc_storage_history.db import StorageDatabase
from pc_storage_history.export import Exporter
from pc_storage_history.scanner import FastScanner


@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test.db"
    db = StorageDatabase(str(db_path))
    yield db
    db.close()


@pytest.fixture
def scan_with_files(temp_db, tmp_path):
    scan_dir = tmp_path / "target"
    scan_dir.mkdir()
    (scan_dir / "hello.txt").write_text("hello")
    (scan_dir / "sub").mkdir()
    (scan_dir / "sub" / "world.txt").write_text("world!")

    scanner = FastScanner(str(scan_dir))
    scan_id = temp_db.save_scan(str(scan_dir), scanner.scan())
    return scan_id


def test_export_csv(temp_db, scan_with_files) -> None:
    exporter = Exporter(temp_db)
    csv_str = exporter.to_csv(scan_with_files)

    assert "path" in csv_str
    assert "size" in csv_str
    assert "hello.txt" in csv_str
    assert "world.txt" in csv_str
    lines = csv_str.strip().split("\n")
    # header + nodes (root + sub + hello.txt + world.txt = 4)
    assert len(lines) == 5


def test_export_json(temp_db, scan_with_files) -> None:
    exporter = Exporter(temp_db)
    json_str = exporter.to_json(scan_with_files)

    data = json.loads(json_str)
    assert "scan" in data
    assert "nodes" in data
    assert len(data["nodes"]) == 4
    assert data["scan"]["total_files"] == 2


def test_export_csv_file(temp_db, scan_with_files, tmp_path) -> None:
    exporter = Exporter(temp_db)
    out_path = tmp_path / "output.csv"
    exporter.to_csv_file(scan_with_files, str(out_path))

    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")
    assert "hello.txt" in content


def test_export_json_file(temp_db, scan_with_files, tmp_path) -> None:
    exporter = Exporter(temp_db)
    out_path = tmp_path / "output.json"
    exporter.to_json_file(scan_with_files, str(out_path))

    assert out_path.exists()
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["scan"]["total_files"] == 2


def test_diff_to_csv(temp_db, tmp_path) -> None:
    scan_dir = tmp_path / "diff_target"
    scan_dir.mkdir()
    (scan_dir / "a.txt").write_text("aaa")

    scanner1 = FastScanner(str(scan_dir))
    id1 = temp_db.save_scan(str(scan_dir), scanner1.scan())

    (scan_dir / "b.txt").write_text("bbbbb")

    scanner2 = FastScanner(str(scan_dir))
    id2 = temp_db.save_scan(str(scan_dir), scanner2.scan())

    exporter = Exporter(temp_db)
    csv_str = exporter.diff_to_csv(id1, id2)

    assert "added" in csv_str
    assert "b.txt" in csv_str


def test_diff_to_json(temp_db, tmp_path) -> None:
    scan_dir = tmp_path / "diff_target"
    scan_dir.mkdir()
    (scan_dir / "a.txt").write_text("aaa")

    scanner1 = FastScanner(str(scan_dir))
    id1 = temp_db.save_scan(str(scan_dir), scanner1.scan())

    (scan_dir / "a.txt").write_text("longer content")

    scanner2 = FastScanner(str(scan_dir))
    id2 = temp_db.save_scan(str(scan_dir), scanner2.scan())

    exporter = Exporter(temp_db)
    json_str = exporter.diff_to_json(id1, id2)

    data = json.loads(json_str)
    assert "diff" in data
    assert len(data["diff"]["changed"]) == 1
