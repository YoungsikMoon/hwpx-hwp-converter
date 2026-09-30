from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from PySide6.QtCore import QUrl, Qt
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QMainWindow, QMessageBox

from .preview_bridge import PreviewPayload, preview_assets


class PreviewWindow(QMainWindow):
    """Offline side-by-side HWPX/HWP preview powered by rhwp WASM."""

    def __init__(self, source: Path, output: Path, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowTitle(f"문서 비교 미리보기 - {Path(source).name}")
        self.resize(1280, 800)
        self._payload = PreviewPayload.from_files(source, output)
        assets = preview_assets()
        self.view = QWebEngineView(self)
        self.setCentralWidget(self.view)
        self.view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True
        )
        self.view.loadFinished.connect(self._page_loaded)
        self.view.setUrl(QUrl.fromLocalFile(str(assets.html.resolve())))

    def _page_loaded(self, ok: bool):
        if not ok:
            QMessageBox.warning(self, "미리보기", "내장 미리보기 화면을 불러오지 못했습니다.")
            return
        payload = json.dumps(asdict(self._payload), ensure_ascii=False)
        self.view.page().runJavaScript(
            f"window.loadPair({payload}).catch(error => {{ window.previewError = String(error); }})"
        )
