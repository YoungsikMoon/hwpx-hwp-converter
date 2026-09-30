from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest

import hwpx_hwp_app.hwp_validator as module
from hwpx_hwp_app.hwp_validator import HwpValidationError, inspect_hwp, parse_body_records


class FakeOle:
    def __init__(self, path):
        self.streams = {
            "FileHeader": b"HWP Document File" + b"\x00" * 16 + bytes((0, 0, 1, 5)) + b"\x00" * 4,
            "DocInfo": b"x",
            "BodyText/Section0": b"x",
        }

    def __enter__(self): return self
    def __exit__(self, *args): pass
    def exists(self, name): return name in self.streams
    def openstream(self, name): return BytesIO(self.streams[name])
    def listdir(self, streams=True, storages=False): return [name.split("/") for name in self.streams]


def test_rejects_non_ole_file(tmp_path):
    path = tmp_path / "fake.hwp"
    path.write_bytes(b"not hwp")
    with pytest.raises(HwpValidationError, match="OLE"):
        inspect_hwp(path)


def test_accepts_real_hwp_header_and_required_streams(tmp_path, monkeypatch):
    path = tmp_path / "valid.hwp"
    path.write_bytes(bytes.fromhex("D0CF11E0A1B11AE1"))
    monkeypatch.setattr(module.olefile, "OleFileIO", FakeOle)
    inv = inspect_hwp(path)
    assert inv.sections == 1


def test_rejects_wrong_document_signature(tmp_path, monkeypatch):
    path = tmp_path / "wrong.hwp"
    path.write_bytes(bytes.fromhex("D0CF11E0A1B11AE1"))

    class Wrong(FakeOle):
        def __init__(self, path):
            super().__init__(path)
            self.streams["FileHeader"] = b"wrong" + b"\x00" * 40

    monkeypatch.setattr(module.olefile, "OleFileIO", Wrong)
    with pytest.raises(HwpValidationError, match="HWP Document File"):
        inspect_hwp(path)


def record(tag: int, payload: bytes = b"") -> bytes:
    return ((tag & 0x3FF) | (len(payload) << 20)).to_bytes(4, "little") + payload


def test_body_record_parser_counts_measured_features_and_text():
    body = b"".join([
        record(66), record(67, "첫 문단".encode("utf-16le")),
        record(66), record(77), record(85),
    ])
    measured = parse_body_records(body)
    assert measured == {"paragraphs": 2, "tables": 1, "images": 1, "text": "첫 문단"}


def test_real_converted_hwp_reports_actual_paragraph_table_and_image_counts():
    fixture = Path(__file__).parent / "data" / "FormattingShowcase.expected.hwp"
    inventory = inspect_hwp(fixture)
    assert (inventory.sections, inventory.paragraphs, inventory.tables, inventory.images) == (1, 13, 1, 0)
