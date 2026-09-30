from pathlib import Path

from PySide6.QtCore import Qt

from hwpx_hwp_app.engines import JavaConverterEngine
from hwpx_hwp_app.gui import MainWindow, default_engines
from hwpx_hwp_app.models import ConversionResult, JobStatus


def test_add_files_filters_hwpx_and_suppresses_duplicates(qtbot, tmp_path):
    one = tmp_path / "하나.hwpx"; one.write_bytes(b"x")
    other = tmp_path / "아님.txt"; other.write_bytes(b"x")
    window = MainWindow(); qtbot.addWidget(window)
    window.add_files([one, one, other])
    assert window.table.rowCount() == 1
    assert window.table.item(0, 1).text() == "하나.hwpx"
    assert not window.table.cellWidget(0, 0).isEnabled()


def test_preview_button_is_enabled_after_successful_conversion(qtbot, tmp_path):
    source = tmp_path / "a.hwpx"; source.write_bytes(b"source")
    output = tmp_path / "a.hwp"; output.write_bytes(b"output")
    window = MainWindow(); qtbot.addWidget(window); window.add_files([source])
    window._on_result(0, ConversionResult(JobStatus.SUCCESS, source, output=output))
    assert window.table.cellWidget(0, 0).isEnabled()
    assert window.table.cellWidget(0, 0).property("output_path") == str(output)


def test_convert_button_requires_files_and_output_folder(qtbot, tmp_path):
    window = MainWindow(); qtbot.addWidget(window)
    assert not window.convert_button.isEnabled()
    source = tmp_path / "a.hwpx"; source.write_bytes(b"x")
    window.add_files([source])
    assert not window.convert_button.isEnabled()
    window.output_edit.setText(str(tmp_path))
    assert window.convert_button.isEnabled()


def test_window_has_korean_title_and_drop_support(qtbot):
    window = MainWindow(); qtbot.addWidget(window)
    assert "HWPX" in window.windowTitle()
    assert window.acceptDrops()


def test_default_gui_uses_only_bundled_engine():
    engines = default_engines()
    assert len(engines) == 1
    assert isinstance(engines[0], JavaConverterEngine)
