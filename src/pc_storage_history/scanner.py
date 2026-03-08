import os
import threading
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from queue import Empty, Queue
from threading import Event


@dataclass
class FileNode:
    """Represents a file or directory node in the filesystem."""

    path: str
    size: int
    is_dir: bool
    mtime: float


class FastScanner:
    """
    A fast, non-recursive filesystem scanner using os.scandir.
    Handles permission errors and avoids symlink loops.
    """

    def __init__(self, root_path: str) -> None:
        self.root_path = os.path.abspath(root_path)

    def scan(self) -> Iterator[FileNode]:
        """
        Iteratively scans the directory tree starting from root_path.
        Yields FileNode objects for every file and directory found.
        """
        # Yield the root directory itself first
        try:
            stat = os.stat(self.root_path, follow_symlinks=False)
            yield FileNode(
                path=self.root_path,
                size=stat.st_size,
                is_dir=True,
                mtime=stat.st_mtime,
            )
        except OSError:
            pass

        stack = [self.root_path]

        while stack:
            current_dir = stack.pop()

            try:
                with os.scandir(current_dir) as it:
                    for entry in it:
                        try:
                            # Do not follow symlinks to avoid infinite loops
                            is_dir = entry.is_dir(follow_symlinks=False)
                            stat = entry.stat(follow_symlinks=False)

                            yield FileNode(
                                path=entry.path,
                                size=stat.st_size,
                                is_dir=is_dir,
                                mtime=stat.st_mtime,
                            )

                            if is_dir:
                                stack.append(entry.path)

                        except OSError:
                            # Skip items we can't stat or access (e.g. PermissionError)
                            continue
            except OSError:
                # Skip directories we can't read (e.g. PermissionError)
                continue


def _scan_single_dir(dir_path: str) -> tuple[list[FileNode], list[str]]:
    """Scan a single directory level. Returns (nodes, subdirectories)."""
    nodes: list[FileNode] = []
    subdirs: list[str] = []
    try:
        with os.scandir(dir_path) as it:
            for entry in it:
                try:
                    is_dir = entry.is_dir(follow_symlinks=False)
                    stat = entry.stat(follow_symlinks=False)
                    nodes.append(
                        FileNode(
                            path=entry.path,
                            size=stat.st_size,
                            is_dir=is_dir,
                            mtime=stat.st_mtime,
                        )
                    )
                    if is_dir:
                        subdirs.append(entry.path)
                except OSError:
                    continue
    except OSError:
        pass
    return nodes, subdirs


class ParallelScanner:
    """
    A multi-threaded filesystem scanner that distributes directory
    scanning across a thread pool for faster I/O on large drives.
    """

    def __init__(self, root_path: str, max_workers: int = 8) -> None:
        self.root_path = os.path.abspath(root_path)
        self.max_workers = max_workers

    def scan(self) -> list[FileNode]:
        """
        Scans the directory tree using multiple threads.
        Returns a list of all FileNode objects found.
        """
        all_nodes: list[FileNode] = []

        # Add root node
        try:
            stat = os.stat(self.root_path, follow_symlinks=False)
            all_nodes.append(
                FileNode(
                    path=self.root_path,
                    size=stat.st_size,
                    is_dir=True,
                    mtime=stat.st_mtime,
                )
            )
        except OSError:
            return all_nodes

        pending_dirs: list[str] = [self.root_path]

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while pending_dirs:
                # Submit all pending directories in parallel
                future_to_dir = {
                    executor.submit(_scan_single_dir, d): d for d in pending_dirs
                }
                pending_dirs = []

                for future in as_completed(future_to_dir):
                    nodes, subdirs = future.result()
                    all_nodes.extend(nodes)
                    pending_dirs.extend(subdirs)

        return all_nodes

    def _produce_nodes(
        self, result_queue: "Queue[FileNode | None]", done_event: Event
    ) -> None:
        """Background producer: scans directories in parallel, pushes nodes to queue."""
        try:
            stat = os.stat(self.root_path, follow_symlinks=False)
            result_queue.put(
                FileNode(
                    path=self.root_path,
                    size=stat.st_size,
                    is_dir=True,
                    mtime=stat.st_mtime,
                )
            )
        except OSError:
            done_event.set()
            result_queue.put(None)
            return

        pending_dirs: list[str] = [self.root_path]

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while pending_dirs:
                futures = {
                    executor.submit(_scan_single_dir, d): d for d in pending_dirs
                }
                pending_dirs = []
                for future in as_completed(futures):
                    nodes, subdirs = future.result()
                    for node in nodes:
                        result_queue.put(node)
                    pending_dirs.extend(subdirs)

        done_event.set()
        result_queue.put(None)  # Sentinel

    def scan_iter(self) -> Iterator[FileNode]:
        """
        Scans the directory tree using multiple threads.
        Yields FileNode objects as they are discovered (via internal queue).
        """
        result_queue: Queue[FileNode | None] = Queue(maxsize=10000)
        done_event = Event()

        thread = threading.Thread(
            target=self._produce_nodes,
            args=(result_queue, done_event),
            daemon=True,
        )
        thread.start()

        while True:
            try:
                node = result_queue.get(timeout=0.1)
                if node is None:
                    break
                yield node
            except Empty:
                if done_event.is_set() and result_queue.empty():
                    break
