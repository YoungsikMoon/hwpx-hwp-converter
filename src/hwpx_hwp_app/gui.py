from __future__ import annotations

import threading
from pathlib import Path

from PySide6.QtCore import QThread, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QAbstractItemView, QFileDialog, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QPushButton, QProgressBar, QStyle, QTableWidget,
    QTableWidgetItem, QToolButton, QVBoxLayout, QWidget,
)

from .engines import JavaConverterEngine
from .models import ConversionResult, JobStatus
from .orchestrator import convert_one


def default_engines():
    return [JavaConverterEngine()]


class ConversionThread(QThread):
    result_ready = Signal(int, object)

    def __init__(self, paths: list[Path], output_dir: Path):
        super().__init__()
        self.paths, self.output_dir = paths, output_dir
        self.cancel_event = threading.Event()

    def run(self):
        engines = default_engines()
        for index, path in enumerate(self.paths):
            if self.cancel_event.is_set():
                result = ConversionResult(JobStatus.CANCELLED, source=path, message="사용자가 변환을 취소했습니다.")
            else:
                result = convert_one(path, self.output_dir, engines, self.cancel_event)
            self.result_ready.emit(index, result)

    def cancel(self):
        self.cancel_event.set()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HWPX → 구형 HWP 변환기")
        self.resize(880, 540)
        self.setAcceptDrops(True)
        self.paths: list[Path] = []
        self.preview_buttons: list[QToolButton] = []
        self.preview_windows = []
        self.worker: ConversionThread | None = None

        self.help_menu = self.menuBar().addMenu("도움말")
        about_action = self.help_menu.addAction("프로그램 정보")
        licenses_action = self.help_menu.addAction("오픈소스 라이선스")
        about_action.triggered.connect(self._show_about)
        licenses_action.triggered.connect(self._show_open_source)

        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel("HWPX 파일을 한컴 2010에서도 열 수 있는 실제 HWP로 변환합니다.")
        title.setStyleSheet("font-size: 17px; font-weight: 600; padding: 8px 0;")
        layout.addWidget(title)

        row = QHBoxLayout()
        add = QPushButton("HWPX 파일 추가"); add.clicked.connect(self._browse_files)
        remove = QPushButton("선택 항목 제거"); remove.clicked.connect(self._remove_selected)
        row.addWidget(add); row.addWidget(remove); row.addStretch(); layout.addLayout(row)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["미리보기", "파일", "상태", "결과/설명"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        for column, mode in enumerate((QHeaderView.ResizeMode.ResizeToContents, QHeaderView.ResizeMode.Stretch,
                                       QHeaderView.ResizeMode.ResizeToContents, QHeaderView.ResizeMode.Stretch)):
            self.table.horizontalHeader().setSectionResizeMode(column, mode)
        layout.addWidget(self.table)

        out = QHBoxLayout(); out.addWidget(QLabel("저장 폴더"))
        self.output_edit = QLineEdit(); self.output_edit.textChanged.connect(self._update_buttons)
        browse = QPushButton("찾아보기"); browse.clicked.connect(self._browse_output)
        out.addWidget(self.output_edit); out.addWidget(browse); layout.addLayout(out)

        self.progress = QProgressBar(); self.progress.setValue(0); layout.addWidget(self.progress)
        buttons = QHBoxLayout()
        self.convert_button = QPushButton("HWP로 변환")
        self.convert_button.setStyleSheet("padding: 9px 22px; font-weight: 600;")
        self.convert_button.clicked.connect(self._start)
        self.cancel_button = QPushButton("취소"); self.cancel_button.setEnabled(False); self.cancel_button.clicked.connect(self._cancel)
        self.open_button = QPushButton("결과 폴더 열기"); self.open_button.setEnabled(False); self.open_button.clicked.connect(self._open_output)
        buttons.addStretch(); buttons.addWidget(self.convert_button); buttons.addWidget(self.cancel_button); buttons.addWidget(self.open_button)
        layout.addLayout(buttons); self._update_buttons()

    def add_files(self, paths):
        existing = {str(path.resolve()).lower() for path in self.paths}
        for raw in paths:
            path = Path(raw); key = str(path.resolve()).lower()
            if path.suffix.lower() != ".hwpx" or key in existing:
                continue
            existing.add(key); self.paths.append(path)
            row = self.table.rowCount(); self.table.insertRow(row)
            preview = QToolButton(self.table)
            preview.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))
            preview.setToolTip("원본과 변환 결과 미리보기"); preview.setEnabled(False)
            preview.clicked.connect(lambda checked=False, button=preview, source=path: self._open_preview(source, button.property("output_path")))
            self.preview_buttons.append(preview); self.table.setCellWidget(row, 0, preview)
            self.table.setItem(row, 1, QTableWidgetItem(path.name)); self.table.item(row, 1).setToolTip(str(path))
            self.table.setItem(row, 2, QTableWidgetItem(JobStatus.PENDING.label)); self.table.setItem(row, 3, QTableWidgetItem(""))
        self._update_buttons()

    def _browse_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "HWPX 파일 선택", "", "HWPX 문서 (*.hwpx)")
        self.add_files(map(Path, files))

    def _remove_selected(self):
        for row in sorted({i.row() for i in self.table.selectedIndexes()}, reverse=True):
            self.table.removeRow(row); self.paths.pop(row); self.preview_buttons.pop(row)
        self._update_buttons()

    def _browse_output(self):
        folder = QFileDialog.getExistingDirectory(self, "저장 폴더 선택")
        if folder: self.output_edit.setText(folder)

    def _update_buttons(self):
        self.convert_button.setEnabled(bool(self.paths and self.output_edit.text().strip()) and self.worker is None)

    def _start(self):
        output = Path(self.output_edit.text().strip())
        if not output.is_dir():
            QMessageBox.warning(self, "저장 폴더", "존재하는 저장 폴더를 선택해 주세요."); return
        self.progress.setRange(0, len(self.paths)); self.progress.setValue(0)
        for row in range(self.table.rowCount()):
            self.table.item(row, 2).setText(JobStatus.PENDING.label); self.preview_buttons[row].setEnabled(False)
        self.worker = ConversionThread(self.paths.copy(), output)
        self.worker.result_ready.connect(self._on_result); self.worker.finished.connect(self._finished)
        self.cancel_button.setEnabled(True); self.convert_button.setEnabled(False); self.worker.start()

    def _on_result(self, row: int, result: ConversionResult):
        self.table.item(row, 2).setText(result.status.label)
        details = str(result.output) if result.output else result.message
        if result.warnings: details += " | " + " / ".join(w.message for w in result.warnings)
        self.table.item(row, 3).setText(details); self.table.item(row, 3).setToolTip(details)
        button = self.preview_buttons[row]
        if result.output and Path(result.output).is_file() and result.status in (JobStatus.SUCCESS, JobStatus.WARNING):
            button.setProperty("output_path", str(result.output)); button.setEnabled(True)
        self.progress.setValue(row + 1)

    def _finished(self):
        self.worker = None; self.cancel_button.setEnabled(False); self.open_button.setEnabled(True); self._update_buttons()

    def _cancel(self):
        if self.worker: self.worker.cancel(); self.cancel_button.setEnabled(False)

    def _open_output(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.output_edit.text().strip()))

    def _show_about(self):
        from .about_dialogs import AboutDialog
        AboutDialog(self).exec()

    def _show_open_source(self):
        from .about_dialogs import OpenSourceDialog
        OpenSourceDialog(self).exec()

    def _open_preview(self, source: Path, output_path):
        if not output_path: return
        try:
            from .preview_window import PreviewWindow
            window = PreviewWindow(source, Path(output_path), self)
            self.preview_windows.append(window)
            window.destroyed.connect(lambda: self.preview_windows.remove(window) if window in self.preview_windows else None)
            window.show()
        except Exception as exc:
            QMessageBox.warning(self, "미리보기", f"미리보기를 열지 못했습니다.\n\n{exc}")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() and any(Path(u.toLocalFile()).suffix.lower() == ".hwpx" for u in event.mimeData().urls()):
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        self.add_files(Path(u.toLocalFile()) for u in event.mimeData().urls()); event.acceptProposedAction()

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.cancel(); self.worker.wait(3000)
        event.accept()
