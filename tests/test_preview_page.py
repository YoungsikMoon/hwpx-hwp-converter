import base64
from pathlib import Path

import pytest

from hwpx_hwp_app.preview_bridge import PreviewFileError, PreviewPayload, preview_assets


def test_preview_payload_reads_two_files_as_base64(tmp_path):
    source = tmp_path / "원본.hwpx"; source.write_bytes(b"source")
    output = tmp_path / "결과.hwp"; output.write_bytes(b"output")
    payload = PreviewPayload.from_files(source, output)
    assert base64.b64decode(payload.left_base64) == b"source"
    assert base64.b64decode(payload.right_base64) == b"output"
    assert payload.left_name == "원본.hwpx"
    assert payload.right_name == "결과.hwp"


def test_preview_payload_rejects_missing_file(tmp_path):
    with pytest.raises(PreviewFileError, match="찾을 수 없습니다"):
        PreviewPayload.from_files(tmp_path / "missing.hwpx", tmp_path / "missing.hwp")


def test_preview_payload_enforces_exact_size_limit(tmp_path, monkeypatch):
    source = tmp_path / "large.hwpx"; source.write_bytes(b"x")
    output = tmp_path / "out.hwp"; output.write_bytes(b"x")
    original = Path.stat

    def fake_stat(self, *args, **kwargs):
        result = original(self, *args, **kwargs)
        if self == source:
            values = list(result)
            values[6] = 200 * 1024 * 1024 + 1
            return type(result)(values)
        return result

    monkeypatch.setattr(Path, "stat", fake_stat)
    with pytest.raises(PreviewFileError, match="200MB"):
        PreviewPayload.from_files(source, output)


def test_preview_page_is_local_and_has_independent_controls():
    root = preview_assets().root
    html = (root / "index.html").read_text(encoding="utf-8")
    js = (root / "preview.js").read_text(encoding="utf-8")
    assert "http://" not in html + js and "https://" not in html + js
    assert "leftState" in js and "rightState" in js
    assert "left-prev" in html and "right-prev" in html
    assert "left-zoom-in" in html and "right-zoom-in" in html
    assert "window.loadPair" in js


def test_preview_panes_have_independent_two_axis_scrolling():
    root = preview_assets().root
    css = (root / "preview.css").read_text(encoding="utf-8")
    js = (root / "preview.js").read_text(encoding="utf-8")
    assert "overflow-x: auto" in css
    assert "overflow-y: auto" in css
    assert "style.width" in js and "style.height" in js
