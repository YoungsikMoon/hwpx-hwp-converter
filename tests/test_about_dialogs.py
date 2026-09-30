from hwpx_hwp_app.about_dialogs import AboutDialog, OpenSourceDialog, THIRD_PARTY_COMPONENTS
from hwpx_hwp_app.gui import MainWindow


def test_help_menu_contains_program_and_open_source_actions(qtbot):
    window = MainWindow(); qtbot.addWidget(window)
    labels = [action.text() for action in window.help_menu.actions()]
    assert "프로그램 정보" in labels
    assert "오픈소스 라이선스" in labels


def test_about_dialog_identifies_developer_and_version(qtbot):
    dialog = AboutDialog(); qtbot.addWidget(dialog)
    text = dialog.findChild(type(dialog.details_label), "details").text()
    assert "1.0.0" in text and "문영식" in text and "Copyright © 2026 문영식" in text


def test_open_source_dialog_lists_required_components_and_license_text(qtbot):
    required = {"rhwp", "hwpConverter", "PySide6 / Qt", "Eclipse Temurin OpenJDK"}
    assert required <= {component.name for component in THIRD_PARTY_COMPONENTS}
    dialog = OpenSourceDialog(); qtbot.addWidget(dialog)
    assert dialog.component_list.count() >= len(required)
    dialog.component_list.setCurrentRow(0)
    assert dialog.license_text.toPlainText().strip()
