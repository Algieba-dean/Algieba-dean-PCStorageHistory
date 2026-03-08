from pc_storage_history.gui_model import format_size


def test_format_size_bytes() -> None:
    assert format_size(0) == "0.00 B"
    assert format_size(512) == "512.00 B"


def test_format_size_kb() -> None:
    assert format_size(1024) == "1.00 KB"
    assert format_size(1536) == "1.50 KB"


def test_format_size_mb() -> None:
    assert format_size(1024 * 1024) == "1.00 MB"


def test_format_size_gb() -> None:
    assert format_size(1024 * 1024 * 1024) == "1.00 GB"


def test_format_size_tb() -> None:
    assert format_size(1024**4) == "1.00 TB"
