
import sys

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTableWidget,
    QTableWidgetItem, QMessageBox, QProgressBar, QTextEdit
)
from PyQt5.QtCore import Qt, QThread

from ui import DownloadThread, FetchThread, ConfigDialog

class PKGFetcher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PKG Fetcher")
        self.setMinimumSize(900, 520)
        self.packages = []
        self.downloaded_packages = []
        self.thread = None
        self.worker = None
        self.dl_thread = None
        self.dl_worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        top = QHBoxLayout()
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("E.g. NPUA80490")
        self.serial_input.returnPressed.connect(self.fetch_packages)
        self.fetch_btn = QPushButton("Search")
        self.fetch_btn.clicked.connect(self.fetch_packages)
        self.settings_btn = QPushButton("⚙ Settings")
        self.settings_btn.clicked.connect(self.open_settings)

        top.addWidget(QLabel("Serial:"))
        top.addWidget(self.serial_input)
        top.addWidget(self.fetch_btn)
        top.addWidget(self.settings_btn)

        # ID List input section
        id_list_layout = QHBoxLayout()
        self.id_list_input = QTextEdit()
        self.id_list_input.setPlaceholderText("Enter IDs (one per line)\nE.g. NPUA80490\n      NPUA80491\n      NPUA80492")
        self.id_list_input.setMaximumHeight(80)
        self.fetch_list_btn = QPushButton("Fetch All IDs")
        self.fetch_list_btn.clicked.connect(self.fetch_packages_from_list)
        id_list_layout.addWidget(QLabel("ID List:"))
        id_list_layout.addWidget(self.id_list_input, 1)
        id_list_layout.addWidget(self.fetch_list_btn)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Select", "Title", "Tag", "Version", "Size (MB)"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)

        bottom = QHBoxLayout()
        self.download_btn = QPushButton("Download selected")
        self.download_btn.clicked.connect(self.download_selected)
        self.remove_btn = QPushButton("Remove selected")
        self.remove_btn.clicked.connect(self.remove_selected)
        self.progress = QProgressBar()

        bottom.addWidget(self.download_btn)
        bottom.addWidget(self.remove_btn)
        bottom.addWidget(self.progress)

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        layout.addLayout(top)
        layout.addLayout(id_list_layout)
        layout.addWidget(self.table)
        layout.addLayout(bottom)
        layout.addWidget(QLabel("Log:"))
        layout.addWidget(self.log)
        self.setLayout(layout)

    # ===================== FETCH =====================

    def _cleanup_thread(self, thread, worker):
        """Properly clean up a thread and its worker."""
        if worker is not None:
            try:
                worker.finished.disconnect()
                worker.error.disconnect()
                worker.log.disconnect()
            except:
                pass
        
        if thread is not None:
            try:
                # Check if thread is still valid before checking if running
                if thread.isRunning():
                    thread.quit()
                    thread.wait()
            except RuntimeError:
                # Thread object has been deleted, ignore
                pass
            try:
                thread.started.disconnect()
                thread.finished.disconnect()
            except:
                pass

    def open_settings(self):
        """Open the settings dialog."""
        dialog = ConfigDialog.ConfigDialog(self)
        dialog.exec_()

    DownloadThread.DownloadWorker

    def fetch_packages(self):
        serial = self.serial_input.text().strip().upper()
        if not serial:
            return

        # Clean up any previous fetch thread and worker
        self._cleanup_thread(self.thread, self.worker)

        self.fetch_btn.setEnabled(False)
        self.log.clear()

        self.thread = QThread()
        self.worker = FetchThread.FetchWorker(serial)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_fetch_finished)
        self.worker.log.connect(self.log.append)
        self.worker.error.connect(self.on_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def fetch_packages_from_list(self):
        """Fetch packages for multiple IDs from the list."""
        id_list_text = self.id_list_input.toPlainText().strip()
        if not id_list_text:
            QMessageBox.warning(self, "Warning", "Please enter at least one ID.")
            return

        # Parse IDs from the text area (one per line, trimmed and uppercased)
        ids = [line.strip().upper() for line in id_list_text.split('\n') if line.strip()]
        
        if not ids:
            QMessageBox.warning(self, "Warning", "Please enter valid IDs.")
            return

        # Clean up any previous fetch thread and worker
        self._cleanup_thread(self.thread, self.worker)

        self.fetch_list_btn.setEnabled(False)
        self.fetch_btn.setEnabled(False)
        self.log.clear()
        self.packages = []  # Clear previous packages
        self.populate_table()

        self.thread = QThread()
        self.worker = FetchThread.FetchWorker(ids)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_fetch_finished)
        self.worker.log.connect(self.log.append)
        self.worker.error.connect(self.on_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_fetch_finished(self, packages):
        self.fetch_btn.setEnabled(True)
        self.fetch_list_btn.setEnabled(True)
        self.packages.extend(packages)
        self.populate_table()
        self.log.append(f"{len(packages)} package(s) found.")

    # ===================== DOWNLOAD =====================

    def download_selected(self):
        selected = [
            self.packages[i]
            for i in range(self.table.rowCount())
            if self.table.item(i, 0).checkState() == Qt.Checked
        ]

        if not selected:
            return

        # Clean up any previous download thread and worker
        self._cleanup_thread(self.dl_thread, self.dl_worker)

        # Store the packages being downloaded to remove them later
        self.downloaded_packages = selected

        self.progress.setValue(0)
        self.download_btn.setEnabled(False)

        self.dl_thread = QThread()
        self.dl_worker = DownloadThread.DownloadWorker(selected)
        self.dl_worker.moveToThread(self.dl_thread)

        self.dl_thread.started.connect(self.dl_worker.run)
        self.dl_worker.progress.connect(self.progress.setValue)
        self.dl_worker.log.connect(self.log.append)
        self.dl_worker.finished.connect(self.on_download_finished)
        self.dl_worker.error.connect(self.on_error)

        self.dl_worker.finished.connect(self.dl_thread.quit)
        self.dl_worker.finished.connect(self.dl_worker.deleteLater)
        self.dl_thread.finished.connect(self.dl_thread.deleteLater)

        self.dl_thread.start()

    def on_download_finished(self):
        self.download_btn.setEnabled(True)
        
        # Remove downloaded packages from the list
        for pkg in self.downloaded_packages:
            if pkg in self.packages:
                self.packages.remove(pkg)
        
        self.populate_table()
        QMessageBox.information(self, "Completed", "Downloads completed.")

    def remove_selected(self):
        """Remove selected games from the list."""
        # Collect indices of checked rows (in reverse to avoid index shifting)
        checked_rows = []
        for i in range(self.table.rowCount()):
            if self.table.item(i, 0).checkState() == Qt.Checked:
                checked_rows.append(i)
        
        if not checked_rows:
            QMessageBox.warning(self, "Warning", "Please select games to remove.")
            return
        
        # Remove in reverse order to avoid index shifting
        for row in sorted(checked_rows, reverse=True):
            self.packages.pop(row)
        
        self.populate_table()
        self.log.append(f"Removed {len(checked_rows)} game(s).")

    # ===================== HELPERS =====================

    def populate_table(self):
        self.table.setRowCount(len(self.packages))
        for row, pkg in enumerate(self.packages):
            check = QTableWidgetItem()
            check.setCheckState(Qt.Unchecked)
            self.table.setItem(row, 0, check)
            self.table.setItem(row, 1, QTableWidgetItem(pkg["title"]))
            self.table.setItem(row, 2, QTableWidgetItem(pkg["tag"]))
            self.table.setItem(row, 3, QTableWidgetItem(pkg["version"]))
            self.table.setItem(
                row, 4,
                QTableWidgetItem(f"{pkg['size']/1024/1024:.2f}")
            )

    def on_error(self, msg):
        self.fetch_btn.setEnabled(True)
        self.fetch_list_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", msg)

# ===================== MAIN =====================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PKGFetcher()
    win.show()
    sys.exit(app.exec_())
