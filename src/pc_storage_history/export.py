"""Export scan data to CSV and JSON formats."""

import csv
import io
import json
from typing import Any

from pc_storage_history.db import StorageDatabase
from pc_storage_history.gui_model import format_size


class Exporter:
    """Exports scan data from the database to various formats."""

    def __init__(self, db: StorageDatabase) -> None:
        self.db = db

    def _get_nodes(self, scan_id: int) -> list[dict[str, Any]]:
        """Fetch all nodes for a scan as a list of dicts."""
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT path, size, is_dir, mtime FROM nodes WHERE scan_id = ?",
            (scan_id,),
        )
        rows = cursor.fetchall()
        return [
            {
                "path": row[0],
                "size": row[1],
                "size_human": format_size(row[1]),
                "is_dir": bool(row[2]),
                "mtime": row[3],
            }
            for row in rows
        ]

    def to_csv(self, scan_id: int) -> str:
        """Export a scan to CSV string."""
        nodes = self._get_nodes(scan_id)
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["path", "size", "size_human", "is_dir", "mtime"],
        )
        writer.writeheader()
        writer.writerows(nodes)
        return output.getvalue()

    def to_json(self, scan_id: int, indent: int = 2) -> str:
        """Export a scan to JSON string."""
        stats = self.db.get_scan_stats(scan_id)
        nodes = self._get_nodes(scan_id)
        data = {
            "scan": stats,
            "nodes": nodes,
        }
        return json.dumps(data, indent=indent, ensure_ascii=False)

    def to_csv_file(self, scan_id: int, file_path: str) -> None:
        """Export a scan to a CSV file."""
        content = self.to_csv(scan_id)
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            f.write(content)

    def to_json_file(self, scan_id: int, file_path: str) -> None:
        """Export a scan to a JSON file."""
        content = self.to_json(scan_id)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def diff_to_csv(self, old_scan_id: int, new_scan_id: int) -> str:
        """Export a scan diff to CSV string."""
        diff = self.db.compare_scans(old_scan_id, new_scan_id)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["status", "path", "old_size", "new_size", "diff"])

        for item in diff["added"]:
            writer.writerow(
                ["added", item["path"], "", item["size"], f"+{item['size']}"]
            )
        for item in diff["removed"]:
            writer.writerow(
                ["removed", item["path"], item["size"], "", f"-{item['size']}"]
            )
        for item in diff["changed"]:
            writer.writerow(
                [
                    "changed",
                    item["path"],
                    item["old_size"],
                    item["new_size"],
                    f"{item['diff']:+d}",
                ]
            )

        return output.getvalue()

    def diff_to_json(self, old_scan_id: int, new_scan_id: int) -> str:
        """Export a scan diff to JSON string."""
        diff = self.db.compare_scans(old_scan_id, new_scan_id)
        old_stats = self.db.get_scan_stats(old_scan_id)
        new_stats = self.db.get_scan_stats(new_scan_id)
        data = {
            "old_scan": old_stats,
            "new_scan": new_stats,
            "diff": diff,
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
