import os
from collections.abc import Iterator
from dataclasses import dataclass


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
