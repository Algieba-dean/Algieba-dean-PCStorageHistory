"""Treemap widget for visualizing directory sizes using squarified treemap algorithm."""

from typing import Any

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QToolTip, QWidget

from pc_storage_history.analysis import DirStat
from pc_storage_history.gui_model import format_size

# Color palette for treemap blocks
_PALETTE = [
    QColor(70, 130, 180),  # Steel Blue
    QColor(60, 179, 113),  # Medium Sea Green
    QColor(218, 165, 32),  # Goldenrod
    QColor(205, 92, 92),  # Indian Red
    QColor(106, 90, 205),  # Slate Blue
    QColor(72, 209, 204),  # Medium Turquoise
    QColor(244, 164, 96),  # Sandy Brown
    QColor(147, 112, 219),  # Medium Purple
    QColor(34, 139, 34),  # Forest Green
    QColor(178, 34, 34),  # Firebrick
]


def _squarify(
    children: list[tuple[str, int]],
    rect: QRectF,
) -> list[tuple[QRectF, str, int]]:
    """
    Compute a squarified treemap layout.

    Args:
        children: List of (name, size) sorted descending by size.
        rect: The bounding rectangle to fill.

    Returns:
        List of (rect, name, size) for each child.
    """
    if not children:
        return []

    total = sum(s for _, s in children)
    if total <= 0 or rect.width() <= 0 or rect.height() <= 0:
        return []

    result: list[tuple[QRectF, str, int]] = []
    _layout_strip(children, rect, total, result)
    return result


def _find_split_index(
    items: list[tuple[str, int]], area: float, total: int, w: float
) -> int:
    """Find the best split point for the strip layout."""
    strip_sum = 0
    best_ratio = float("inf")
    split_idx = 0

    for i, (_name, size) in enumerate(items):
        strip_sum += size
        strip_area = area * strip_sum / total
        avg_cell = strip_area / (i + 1) if strip_area > 0 else 0
        ratio = (
            max(w * w / avg_cell, avg_cell / (w * w)) if avg_cell > 0 else float("inf")
        )

        if ratio <= best_ratio:
            best_ratio = ratio
            split_idx = i + 1
        else:
            break

    return split_idx


def _lay_out_vertical(
    strip_items: list[tuple[str, int]],
    strip_total: int,
    strip_width: float,
    rect: QRectF,
    result: list[tuple[QRectF, str, int]],
) -> None:
    """Lay out strip items vertically."""
    y = rect.y()
    for name, size in strip_items:
        h = rect.height() * size / strip_total if strip_total > 0 else 0
        result.append((QRectF(rect.x(), y, strip_width, h), name, size))
        y += h


def _lay_out_horizontal(
    strip_items: list[tuple[str, int]],
    strip_total: int,
    strip_height: float,
    rect: QRectF,
    result: list[tuple[QRectF, str, int]],
) -> None:
    """Lay out strip items horizontally."""
    x = rect.x()
    for name, size in strip_items:
        w_item = rect.width() * size / strip_total if strip_total > 0 else 0
        result.append((QRectF(x, rect.y(), w_item, strip_height), name, size))
        x += w_item


def _layout_strip(
    items: list[tuple[str, int]],
    rect: QRectF,
    total: int,
    result: list[tuple[QRectF, str, int]],
) -> None:
    """Recursively lay out items in the rectangle using strip-based squarification."""
    if not items or total <= 0:
        return

    if len(items) == 1:
        result.append((rect, items[0][0], items[0][1]))
        return

    w = min(rect.width(), rect.height())
    if w <= 0:
        return

    area = rect.width() * rect.height()
    split_idx = _find_split_index(items, area, total, w)

    strip_items = items[:split_idx]
    rest_items = items[split_idx:]
    strip_total = sum(s for _, s in strip_items)

    if rect.width() >= rect.height():
        strip_width = rect.width() * strip_total / total if total > 0 else 0
        _lay_out_vertical(strip_items, strip_total, strip_width, rect, result)
        if rest_items:
            rest_rect = QRectF(
                rect.x() + strip_width,
                rect.y(),
                rect.width() - strip_width,
                rect.height(),
            )
            _layout_strip(rest_items, rest_rect, total - strip_total, result)
    else:
        strip_height = rect.height() * strip_total / total if total > 0 else 0
        _lay_out_horizontal(strip_items, strip_total, strip_height, rect, result)
        if rest_items:
            rest_rect = QRectF(
                rect.x(),
                rect.y() + strip_height,
                rect.width(),
                rect.height() - strip_height,
            )
            _layout_strip(rest_items, rest_rect, total - strip_total, result)


class TreemapWidget(QWidget):
    """A widget that draws a squarified treemap of directory sizes."""

    dir_clicked = Signal(str)  # Emitted with the path when a block is clicked

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(200, 150)
        self._blocks: list[tuple[QRectF, str, int, str]] = []  # rect, name, size, path
        self._dir_stat: DirStat | None = None
        self.setMouseTracking(True)

    def set_data(self, dir_stat: DirStat) -> None:
        """Set the data to visualize."""
        self._dir_stat = dir_stat
        self._recalc()
        self.update()

    def _recalc(self) -> None:
        """Recalculate treemap layout based on current widget size."""
        self._blocks = []
        if not self._dir_stat or not self._dir_stat.children:
            return

        children = sorted(
            self._dir_stat.children.items(),
            key=lambda x: x[1].size,
            reverse=True,
        )

        items = [(name, stat.size) for name, stat in children if stat.size > 0]
        if not items:
            return

        margin = 2
        rect = QRectF(
            margin, margin, self.width() - 2 * margin, self.height() - 2 * margin
        )
        layout = _squarify(items, rect)

        name_to_path = {name: stat.path for name, stat in children}
        self._blocks = [
            (r, name, size, name_to_path.get(name, "")) for r, name, size in layout
        ]

    def resizeEvent(self, event: Any) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._recalc()

    def paintEvent(self, event: Any) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self._blocks:
            painter.setPen(Qt.GlobalColor.gray)
            painter.drawText(
                self.rect(), Qt.AlignmentFlag.AlignCenter, "No data to display"
            )
            painter.end()
            return

        painter.setFont(QFont("Segoe UI", 9))

        for i, (rect, name, size, _path) in enumerate(self._blocks):
            color = _PALETTE[i % len(_PALETTE)]

            # Fill
            painter.setBrush(color)
            painter.setPen(QPen(color.darker(130), 1))
            painter.drawRect(rect)

            # Text label (only if rect is big enough)
            if rect.width() > 40 and rect.height() > 20:
                painter.setPen(Qt.GlobalColor.white)
                label = f"{name}\n{format_size(size)}"
                text_rect = rect.adjusted(4, 2, -4, -2)
                painter.drawText(
                    text_rect,
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                    label,
                )

        painter.end()

    def mouseMoveEvent(self, event: Any) -> None:  # noqa: N802
        pos = event.position() if hasattr(event, "position") else event.pos()
        for rect, name, size, path in self._blocks:
            if rect.contains(pos):
                QToolTip.showText(
                    event.globalPosition().toPoint()
                    if hasattr(event, "globalPosition")
                    else event.globalPos(),
                    f"{name}\n{format_size(size)}\n{path}",
                )
                return
        QToolTip.hideText()

    def mousePressEvent(self, event: Any) -> None:  # noqa: N802
        pos = event.position() if hasattr(event, "position") else event.pos()
        for rect, _name, _size, path in self._blocks:
            if rect.contains(pos):
                self.dir_clicked.emit(path)
                return
