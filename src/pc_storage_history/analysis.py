import os
from dataclasses import dataclass, field

from pc_storage_history.db import StorageDatabase


@dataclass
class DirStat:
    path: str
    size: int = 0
    file_count: int = 0
    dir_count: int = 0
    children: dict[str, "DirStat"] = field(default_factory=dict)


class Analyzer:
    """Analyzes scan data from the database."""

    def __init__(self, db: StorageDatabase) -> None:
        self.db = db

    def get_directory_tree(self, scan_id: int) -> DirStat | None:
        """
        Retrieves all nodes for a given scan and builds a tree structure
        with aggregated sizes.
        """
        root_path = self._get_root_path(scan_id)
        if not root_path:
            return None

        nodes = self._get_scan_nodes(scan_id)
        if not nodes:
            return None

        return self._build_tree(root_path, nodes)

    def _get_root_path(self, scan_id: int) -> str | None:
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT root_path FROM scans WHERE id = ?", (scan_id,))
        row = cursor.fetchone()
        return row[0] if row else None

    def _get_scan_nodes(self, scan_id: int) -> list[tuple[str, int, bool]]:
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT path, size, is_dir FROM nodes WHERE scan_id = ?", (scan_id,)
        )
        return cursor.fetchall()

    def _build_tree(
        self, root_path: str, nodes: list[tuple[str, int, bool]]
    ) -> DirStat:
        dir_stats: dict[str, DirStat] = {root_path: DirStat(path=root_path)}

        # First pass: initialize all directories
        for path, _, is_dir in nodes:
            if is_dir and path not in dir_stats:
                dir_stats[path] = DirStat(path=path)

        # Second pass: accumulate sizes
        for path, size, is_dir in nodes:
            if not is_dir:
                self._accumulate_file_size(path, size, root_path, dir_stats)

        return dir_stats[root_path]

    def _accumulate_file_size(
        self, file_path: str, size: int, root_path: str, dir_stats: dict[str, DirStat]
    ) -> None:
        parent_dir = os.path.dirname(file_path)
        current_dir = parent_dir

        while current_dir:
            self._ensure_dir_exists(current_dir, dir_stats)

            stat = dir_stats[current_dir]
            stat.size += size
            stat.file_count += 1

            parent_of_current = os.path.dirname(current_dir)
            if parent_of_current and parent_of_current != current_dir:
                self._link_to_parent(current_dir, parent_of_current, dir_stats)

            if current_dir == root_path or parent_of_current == current_dir:
                break
            current_dir = parent_of_current

    def _ensure_dir_exists(self, dir_path: str, dir_stats: dict[str, DirStat]) -> None:
        if dir_path not in dir_stats:
            dir_stats[dir_path] = DirStat(path=dir_path)

    def _link_to_parent(
        self, child_dir: str, parent_dir: str, dir_stats: dict[str, DirStat]
    ) -> None:
        self._ensure_dir_exists(parent_dir, dir_stats)

        basename = os.path.basename(child_dir)
        if basename not in dir_stats[parent_dir].children:
            dir_stats[parent_dir].children[basename] = dir_stats[child_dir]
            dir_stats[parent_dir].dir_count += 1

    def get_largest_files(
        self, scan_id: int, limit: int = 100
    ) -> list[tuple[str, int]]:
        """Return the largest files in a specific scan."""
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT path, size FROM nodes 
            WHERE scan_id = ? AND is_dir = 0 
            ORDER BY size DESC LIMIT ?
            """,
            (scan_id, limit),
        )
        return cursor.fetchall()
