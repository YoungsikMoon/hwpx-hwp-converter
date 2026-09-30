from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QListWidget, QPlainTextEdit,
    QVBoxLayout,
)

from . import __copyright__, __developer__, __version__
from .preview_bridge import application_root


@dataclass(frozen=True)
class ThirdPartyComponent:
    name: str
    version: str
    license_name: str
    homepage: str
    license_file: str


THIRD_PARTY_COMPONENTS = (
    ThirdPartyComponent("rhwp", "0.8.2", "MIT", "https://github.com/edwardkim/rhwp", "licenses/MIT-rhwp.txt"),
    ThirdPartyComponent("hwpConverter", "9af63ea", "Apache-2.0", "https://github.com/vsdn/hwpConverter", "licenses/Apache-2.0-hwpConverter.txt"),
    ThirdPartyComponent("PySide6 / Qt", "6.11.1", "LGPL-3.0-only OR GPL", "https://www.qt.io/qt-for-python", "licenses/LGPL-3.0-Qt.txt"),
    ThirdPartyComponent("Eclipse Temurin OpenJDK", "21.0.12+8", "GPL-2.0 with Classpath Exception", "https://adoptium.net/", "licenses/GPL-2.0-Classpath-Exception-OpenJDK.txt"),
    ThirdPartyComponent("Python", "3.11+", "PSF-2.0", "https://www.python.org/", "licenses/PSF-Python.txt"),
    ThirdPartyComponent("olefile", "0.47", "BSD-2-Clause", "https://github.com/decalage2/olefile", "licenses/BSD-2-Clause-olefile.txt"),
    ThirdPartyComponent("defusedxml", "0.7.1", "PSFL", "https://github.com/tiran/defusedxml", "licenses/PSFL-defusedxml.txt"),
    ThirdPartyComponent("pywin32", "312", "PSFL", "https://github.com/mhammond/pywin32", "licenses/PSFL-pywin32.txt"),
    ThirdPartyComponent("PyInstaller", "6.22.0", "GPL-2.0 with bootloader exception", "https://pyinstaller.org/", "licenses/GPL-2.0-PyInstaller-Bootloader-Exception.txt"),
    ThirdPartyComponent("Java 변환 라이브러리", "고정 버전", "Apache-2.0 및 각 라이선스", "https://github.com/neolord0/hwplib", "vendor/hwp-converter/LICENSE"),
)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("프로그램 정보")
        self.setMinimumWidth(430)
        layout = QVBoxLayout(self)
        title = QLabel("HWPX-HWP 변환기"); title.setStyleSheet("font-size: 20px; font-weight: 700;")
        layout.addWidget(title)
        self.details_label = QLabel(f"버전 {__version__}\n개발자: {__developer__}\n{__copyright__}\n\n프로그램 자체 코드는 MIT 라이선스로 배포됩니다.")
        self.details_label.setObjectName("details"); self.details_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.details_label)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close); buttons.rejected.connect(self.reject); layout.addWidget(buttons)


class OpenSourceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("오픈소스 라이선스")
        self.resize(900, 600)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("아래 구성요소의 저작권은 각 원저작자에게 있습니다."))
        body = QHBoxLayout(); layout.addLayout(body, 1)
        self.component_list = QListWidget(); self.license_text = QPlainTextEdit(); self.license_text.setReadOnly(True)
        body.addWidget(self.component_list, 1); body.addWidget(self.license_text, 2)
        for component in THIRD_PARTY_COMPONENTS:
            self.component_list.addItem(f"{component.name} {component.version}\n{component.license_name}")
        self.component_list.currentRowChanged.connect(self._show_component)
        self.component_list.setCurrentRow(0)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close); buttons.rejected.connect(self.reject); layout.addWidget(buttons)

    def _show_component(self, row: int):
        if row < 0: return
        component = THIRD_PARTY_COMPONENTS[row]
        path = application_root() / component.license_file
        try:
            license_text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            license_text = f"라이선스 파일을 읽지 못했습니다: {exc}"
        self.license_text.setPlainText(
            f"{component.name} {component.version}\n{component.license_name}\n{component.homepage}\n\n{license_text}"
        )
