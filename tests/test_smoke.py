from pc_storage_history.scanner import FastScanner, FileNode


def test_smoke() -> None:
    """Smoke test: ensure core classes can be imported and instantiated."""
    scanner = FastScanner(".")
    assert scanner.root_path is not None
    node = FileNode(path="test", size=0, is_dir=False, mtime=0.0)
    assert node.path == "test"
