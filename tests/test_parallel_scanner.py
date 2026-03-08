from pc_storage_history.scanner import FastScanner, ParallelScanner


def test_parallel_scanner_basic(tmp_path) -> None:
    """ParallelScanner should find the same files as FastScanner."""
    scan_dir = tmp_path / "target"
    scan_dir.mkdir()
    (scan_dir / "folder1").mkdir()
    (scan_dir / "folder1" / "a.txt").write_text("hello")
    (scan_dir / "folder2").mkdir()
    (scan_dir / "folder2" / "b.txt").write_text("world!")
    (scan_dir / "c.txt").write_text("root file")

    fast_nodes = list(FastScanner(str(scan_dir)).scan())
    parallel_nodes = ParallelScanner(str(scan_dir)).scan()

    fast_paths = sorted(n.path for n in fast_nodes)
    parallel_paths = sorted(n.path for n in parallel_nodes)

    assert fast_paths == parallel_paths

    fast_total = sum(n.size for n in fast_nodes if not n.is_dir)
    parallel_total = sum(n.size for n in parallel_nodes if not n.is_dir)
    assert fast_total == parallel_total


def test_parallel_scanner_scan_iter(tmp_path) -> None:
    """scan_iter should yield all nodes via the queue-based iterator."""
    scan_dir = tmp_path / "target"
    scan_dir.mkdir()
    (scan_dir / "sub").mkdir()
    (scan_dir / "sub" / "file.txt").write_text("data")

    scanner = ParallelScanner(str(scan_dir))
    iter_nodes = list(scanner.scan_iter())

    # root + sub + file = 3
    assert len(iter_nodes) == 3

    files = [n for n in iter_nodes if not n.is_dir]
    assert len(files) == 1
    assert files[0].size == 4


def test_parallel_scanner_empty_dir(tmp_path) -> None:
    """ParallelScanner on empty dir should only return root."""
    scan_dir = tmp_path / "empty"
    scan_dir.mkdir()

    nodes = ParallelScanner(str(scan_dir)).scan()
    assert len(nodes) == 1
    assert nodes[0].is_dir is True


def test_parallel_scanner_deep_nesting(tmp_path) -> None:
    """ParallelScanner should handle deeply nested directories."""
    scan_dir = tmp_path / "deep"
    deep = scan_dir / "a" / "b" / "c" / "d" / "e"
    deep.mkdir(parents=True)
    (deep / "file.txt").write_text("deep")

    nodes = ParallelScanner(str(scan_dir)).scan()
    dirs = [n for n in nodes if n.is_dir]
    files = [n for n in nodes if not n.is_dir]

    # root, a, b, c, d, e = 6 dirs
    assert len(dirs) == 6
    assert len(files) == 1
