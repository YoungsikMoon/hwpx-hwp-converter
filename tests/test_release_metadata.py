from pathlib import Path

import hwpx_hwp_app


ROOT = Path(__file__).resolve().parents[1]


def test_release_version_and_copyright_are_1_0_0():
    assert hwpx_hwp_app.__version__ == "1.0.0"
    assert hwpx_hwp_app.__developer__ == "문영식"
    assert hwpx_hwp_app.__copyright__ == "Copyright © 2026 문영식"
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "1.0.0"' in pyproject


def test_release_contains_own_and_third_party_license_documents():
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "MIT License" in license_text
    assert "Copyright (c) 2026 문영식" in license_text
    assert (ROOT / "CHANGELOG.md").is_file()
    for name in ("MIT-rhwp.txt", "Apache-2.0-hwpConverter.txt", "LGPL-3.0-Qt.txt", "GPL-2.0-Classpath-Exception-OpenJDK.txt"):
        assert (ROOT / "licenses" / name).is_file(), name


def test_1_0_0_packaging_includes_all_legal_assets():
    spec = (ROOT / "HWPX-HWP-변환기-1.0.0.spec").read_text(encoding="utf-8")
    assert "HWPX-HWP-변환기-1.0.0" in spec
    assert "('licenses', 'licenses')" in spec
    assert "('LICENSE', '.')" in spec
    assert "('CHANGELOG.md', '.')" in spec
