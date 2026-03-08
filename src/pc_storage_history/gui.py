import os
import subprocess
import sys
from typing import Any

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from pc_storage_history.analysis import Analyzer, DirStat
from pc_storage_history.db import StorageDatabase
from pc_storage_history.gui_model import StorageTreeModel, format_size
from pc_storage_history.scanner import FastScanner


class HistoryDialog(QDialog):
    """Dialog to show and select past scans from the database."""

    def __init__(self, db: StorageDatabase, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Scan History")
        self.resize(600, 400)
        self.db = db
        self.selected_scan_id: int | None = None

        self.setup_ui()
        self.load_history()

    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()

        self.btn_load = QPushButton("Load Selected")
        self.btn_load.clicked.connect(self.on_load_clicked)
        btn_layout.addWidget(self.btn_load)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

    def load_history(self) -> None:
        scans = self.db.get_all_scans()
        for scan in scans:
            size_str = format_size(scan["total_size"])
            text = f"{scan['timestamp']} - {scan['root_path']} [{size_str}, {scan['total_files']} files]"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, scan["id"])
            self.list_widget.addItem(item)

    def on_item_double_clicked(self, item: QListWidgetItem) -> None:
        self.selected_scan_id = item.data(Qt.ItemDataRole.UserRole)
        self.accept()

    def on_load_clicked(self) -> None:
        current_item = self.list_widget.currentItem()
        if current_item:
            self.selected_scan_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.accept()


class LoadWorker(QThread):
    """Worker thread for loading a tree from the database without freezing the UI."""

    finished_load = Signal(object, dict)
    error_load = Signal(str)

    def __init__(self, db: StorageDatabase, analyzer: Analyzer, scan_id: int) -> None:
        super().__init__()
        self.db = db
        self.analyzer = analyzer
        self.scan_id = scan_id

    def run(self) -> None:
        try:
            tree_data = self.analyzer.get_directory_tree(self.scan_id)
            stats = self.db.get_scan_stats(self.scan_id)
            self.finished_load.emit(tree_data, stats)
        except Exception as e:
            self.error_load.emit(str(e))


class ScanWorker(QThread):
    """Worker thread for running the filesystem scan and building the tree without freezing the UI."""

    finished_scan = Signal(object, dict)  # Emits (DirStat, stats_dict)
    error_scan = Signal(str)

    def __init__(
        self, db: StorageDatabase, analyzer: Analyzer, folder_path: str
    ) -> None:
        super().__init__()
        self.db = db
        self.analyzer = analyzer
        self.folder_path = folder_path

    def run(self) -> None:
        try:
            scanner = FastScanner(self.folder_path)
            scan_id = self.db.save_scan(self.folder_path, scanner.scan())

            tree_data = self.analyzer.get_directory_tree(scan_id)
            stats = self.db.get_scan_stats(scan_id)

            self.finished_scan.emit(tree_data, stats)
        except Exception as e:
            self.error_scan.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self, db_path: str = "storage_history.db") -> None:
        super().__init__()
        self.setWindowTitle("PC Storage History Analyzer")
        self.resize(1024, 768)

        self.db = StorageDatabase(db_path)
        self.analyzer = Analyzer(self.db)

        self.current_scan_id: int | None = None
        self.tree_model: StorageTreeModel | None = None
        self.scan_worker: ScanWorker | None = None
        self.load_worker: LoadWorker | None = None

        self.setup_ui()

    def setup_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top controls
        controls_layout = QHBoxLayout()

        self.btn_scan = QPushButton("New Scan")
        self.btn_scan.clicked.connect(self.on_new_scan)
        controls_layout.addWidget(self.btn_scan)

        self.btn_history = QPushButton("History")
        self.btn_history.clicked.connect(self.on_history)
        controls_layout.addWidget(self.btn_history)

        self.lbl_status = QLabel("Ready")
        controls_layout.addWidget(self.lbl_status, stretch=1)

        main_layout.addLayout(controls_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        # Tree View
        self.tree_view = QTreeView()
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setUniformRowHeights(True)
        self.tree_view.setSortingEnabled(False)  # We pre-sort the model by size

        # Context Menu
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.on_context_menu)

        header = self.tree_view.header()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        main_layout.addWidget(self.tree_view)

    def on_history(self) -> None:
        dialog = HistoryDialog(self.db, self)
        if (
            dialog.exec() == QDialog.DialogCode.Accepted
            and dialog.selected_scan_id is not None
        ):
            self.load_scan_from_db(dialog.selected_scan_id)

    def load_scan_from_db(self, scan_id: int) -> None:
        self.set_ui_loading_state(True, f"Loading scan ID {scan_id} from database...")

        self.load_worker = LoadWorker(self.db, self.analyzer, scan_id)
        self.load_worker.finished_load.connect(self.on_scan_finished)
        self.load_worker.error_load.connect(self.on_scan_error)
        self.load_worker.start()

    def set_ui_loading_state(self, is_loading: bool, msg: str = "") -> None:
        self.btn_scan.setEnabled(not is_loading)
        self.btn_history.setEnabled(not is_loading)

        if is_loading:
            self.progress_bar.show()
            self.lbl_status.setText(msg)
        else:
            self.progress_bar.hide()

    def on_new_scan(self) -> None:
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Directory to Scan", ""
        )

        if not folder_path:
            return

        self.set_ui_loading_state(True, f"Scanning {folder_path}...")

        # Run scan in background thread
        self.scan_worker = ScanWorker(self.db, self.analyzer, folder_path)
        self.scan_worker.finished_scan.connect(self.on_scan_finished)
        self.scan_worker.error_scan.connect(self.on_scan_error)
        self.scan_worker.start()

    def on_scan_finished(
        self, tree_data: DirStat | None, stats: dict[str, Any] | None
    ) -> None:
        self.set_ui_loading_state(False)

        if tree_data and stats:
            self.update_tree_view(tree_data)
            self.lbl_status.setText(
                f"Scan/Load complete. Size: {stats['total_size'] / (1024**2):.2f} MB, "
                f"Files: {stats['total_files']}, Dirs: {stats['total_dirs']}"
            )
        else:
            self.lbl_status.setText("Failed to build tree.")

    def on_scan_error(self, error_msg: str) -> None:
        self.set_ui_loading_state(False)
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_msg}")
        self.lbl_status.setText("Operation failed.")

    def update_tree_view(self, root_stat: DirStat) -> None:
        self.tree_model = StorageTreeModel(root_stat)
        self.tree_view.setModel(self.tree_model)
        # Expand just the root level initially
        self.tree_view.expandToDepth(0)

    def on_context_menu(self, position: Any) -> None:
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return

        item = index.internalPointer()
        if not item:
            return

        path = item.stat.path

        menu = QMenu()
        open_action = QAction("Open in Explorer", self)
        open_action.triggered.connect(lambda: self.open_in_explorer(path))
        menu.addAction(open_action)

        copy_action = QAction("Copy Path", self)
        copy_action.triggered.connect(lambda: QApplication.clipboard().setText(path))  # type: ignore[union-attr]
        menu.addAction(copy_action)

        menu.exec_(self.tree_view.viewport().mapToGlobal(position))

    def open_in_explorer(self, path: str) -> None:
        """Opens the selected path in Windows Explorer."""
        if os.name == "nt":
            if os.path.isdir(path):
                os.startfile(path)
            else:
                # Select the file in explorer
                subprocess.run(["explorer", "/select,", os.path.normpath(path)])

    def closeEvent(self, event: Any) -> None:  # noqa: N802
        if self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.wait()
        if self.load_worker and self.load_worker.isRunning():
            self.load_worker.wait()
        self.db.close()
        super().closeEvent(event)


def main() -> None:
    app = QApplication(sys.argv)

    # Set style
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
