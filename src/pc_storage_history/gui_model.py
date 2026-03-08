import os
from typing import Any, Optional

from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt

from pc_storage_history.analysis import DirStat


def format_size(size: int) -> str:
    """Format bytes into a human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


class TreeNode:
    """A wrapper around DirStat to make it compatible with Qt's ItemModel."""

    def __init__(self, stat: DirStat, parent: Optional["TreeNode"] = None) -> None:
        self.stat = stat
        self.parent_item = parent
        self.child_items: list[TreeNode] = []
        # Lazy loading children
        self._is_populated = False

    def append_child(self, item: "TreeNode") -> None:
        self.child_items.append(item)

    def child(self, row: int) -> Optional["TreeNode"]:
        self.populate()
        if 0 <= row < len(self.child_items):
            return self.child_items[row]
        return None

    def child_count(self) -> int:
        self.populate()
        return len(self.child_items)

    def column_count(self) -> int:
        return 3  # Name, Size, Type/Count

    def data(self, column: int) -> Any:
        if column == 0:
            return os.path.basename(self.stat.path) or self.stat.path
        elif column == 1:
            return format_size(self.stat.size)
        elif column == 2:
            return f"{self.stat.file_count} files, {self.stat.dir_count} dirs"
        return None

    def parent(self) -> Optional["TreeNode"]:
        return self.parent_item

    def row(self) -> int:
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0

    def populate(self) -> None:
        """Populate children on demand from the DirStat dictionary."""
        if self._is_populated:
            return

        # Sort children by size descending
        sorted_children = sorted(
            self.stat.children.values(), key=lambda x: x.size, reverse=True
        )

        for child_stat in sorted_children:
            self.append_child(TreeNode(child_stat, self))

        self._is_populated = True


class StorageTreeModel(QAbstractItemModel):
    """A custom model to display the directory tree efficiently."""

    def __init__(self, root_stat: DirStat, parent: Any = None) -> None:
        super().__init__(parent)
        self.root_item = TreeNode(root_stat)

    def columnCount(self, parent: QModelIndex | None = None) -> int:  # noqa: N802
        if parent is None:
            parent = QModelIndex()
        if parent.isValid():
            return parent.internalPointer().column_count()
        return self.root_item.column_count()

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if role != Qt.ItemDataRole.DisplayRole:
            return None

        item = index.internalPointer()
        return item.data(index.column())

    def headerData(  # noqa: N802
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            headers = {0: "Name", 1: "Size", 2: "Contents"}
            return headers.get(section)
        return None

    def index(
        self, row: int, column: int, parent: QModelIndex | None = None
    ) -> QModelIndex:
        if parent is None:
            parent = QModelIndex()

        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self.root_item or parent_item is None:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent: QModelIndex | None = None) -> int:  # noqa: N802
        if parent is None:
            parent = QModelIndex()

        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        return parent_item.child_count()
