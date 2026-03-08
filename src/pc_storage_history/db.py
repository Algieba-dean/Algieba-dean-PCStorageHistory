import sqlite3
from collections.abc import Iterable
from typing import Any

from pc_storage_history.scanner import FileNode


class StorageDatabase:
    """Handles saving and retrieving scan histories using SQLite."""

    def __init__(self, db_path: str) -> None:
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self) -> None:
        """Create necessary tables and indices if they don't exist."""
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    root_path TEXT NOT NULL,
                    total_size INTEGER DEFAULT 0,
                    total_files INTEGER DEFAULT 0,
                    total_dirs INTEGER DEFAULT 0
                )
            """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER,
                    path TEXT NOT NULL,
                    size INTEGER,
                    is_dir BOOLEAN,
                    mtime REAL,
                    FOREIGN KEY(scan_id) REFERENCES scans(id)
                )
            """
            )
            # Create indices for faster lookups when comparing histories
            self.conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_scan_id ON nodes(scan_id)"
            )
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_path ON nodes(path)")

    def save_scan(self, root_path: str, nodes: Iterable[FileNode]) -> int:
        """
        Saves a scan snapshot to the database.
        Returns the ID of the newly created scan.
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO scans (root_path) VALUES (?)", (root_path,))
            scan_id = cursor.lastrowid

            if scan_id is None:
                raise RuntimeError("Failed to create scan record.")

            total_size = 0
            total_files = 0
            total_dirs = 0

            # Use a generator to feed executemany to save memory during bulk insert
            def node_generator() -> Iterable[tuple[int, str, int, bool, float]]:
                nonlocal total_size, total_files, total_dirs
                for node in nodes:
                    if node.is_dir:
                        total_dirs += 1
                    else:
                        total_files += 1
                        total_size += node.size
                    yield (scan_id, node.path, node.size, node.is_dir, node.mtime)

            cursor.executemany(
                """
                INSERT INTO nodes (scan_id, path, size, is_dir, mtime)
                VALUES (?, ?, ?, ?, ?)
                """,
                node_generator(),
            )

            # Update the scan statistics
            cursor.execute(
                """
                UPDATE scans 
                SET total_size = ?, total_files = ?, total_dirs = ?
                WHERE id = ?
                """,
                (total_size, total_files, total_dirs, scan_id),
            )

            return scan_id

    def get_scan_stats(self, scan_id: int) -> dict[str, Any] | None:
        """Retrieve the top-level statistics for a specific scan."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT root_path, timestamp, total_size, total_files, total_dirs
            FROM scans WHERE id = ?
            """,
            (scan_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None

        return {
            "root_path": row[0],
            "timestamp": row[1],
            "total_size": row[2],
            "total_files": row[3],
            "total_dirs": row[4],
        }

    def get_all_scans(self) -> list[dict[str, Any]]:
        """Retrieve a list of all scans ordered by timestamp descending."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, root_path, timestamp, total_size, total_files, total_dirs
            FROM scans ORDER BY timestamp DESC
            """
        )
        rows = cursor.fetchall()

        result = []
        for row in rows:
            result.append(
                {
                    "id": row[0],
                    "root_path": row[1],
                    "timestamp": row[2],
                    "total_size": row[3],
                    "total_files": row[4],
                    "total_dirs": row[5],
                }
            )
        return result

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()
