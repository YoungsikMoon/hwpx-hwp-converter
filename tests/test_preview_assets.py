from pathlib import Path

import pytest

from hwpx_hwp_app.preview_bridge import PreviewAssetError, preview_assets


def test_preview_assets_are_pinned_and_complete():
    assets = preview_assets()
    assert assets.version.read_text(encoding="utf-8").strip() == "@rhwp/core 0.8.2"
    assert assets.javascript.is_file()
    assert assets.wasm.is_file()
    assert "MIT License" in assets.license.read_text(encoding="utf-8")


def test_preview_assets_reports_missing_root(tmp_path):
    with pytest.raises(PreviewAssetError, match="미리보기 엔진"):
        preview_assets(tmp_path)
