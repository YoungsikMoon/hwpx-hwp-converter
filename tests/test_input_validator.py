from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from hwpx_hwp_app.input_validator import InputValidationError, inspect_hwpx


HEADER = """<?xml version='1.0' encoding='UTF-8'?><hh:head xmlns:hh='http://www.hancom.co.kr/hwpml/2011/head'/>"""
SECTION = """<?xml version='1.0' encoding='UTF-8'?><hs:sec xmlns:hs='http://www.hancom.co.kr/hwpml/2011/section'><hp:p xmlns:hp='http://www.hancom.co.kr/hwpml/2011/paragraph'><hp:run><hp:t>안녕하세요</hp:t></hp:run><hp:tbl/><hp:pic/></hp:p></hs:sec>"""


def make_hwpx(path: Path, *, header: str = HEADER, section: str = SECTION, extra=()):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", "application/hwp+zip")
        if header:
            zf.writestr("Contents/header.xml", header)
        if section:
            zf.writestr("Contents/section0.xml", section)
        for name, data in extra:
            zf.writestr(name, data)


def test_valid_hwpx_returns_inventory(tmp_path):
    path = tmp_path / "정상.hwpx"
    make_hwpx(path)
    inv = inspect_hwpx(path)
    assert (inv.sections, inv.paragraphs, inv.tables, inv.images) == (1, 1, 1, 1)
    assert inv.text == "안녕하세요"


def test_rejects_non_zip_even_with_hwpx_extension(tmp_path):
    path = tmp_path / "가짜.hwpx"
    path.write_bytes(b"not a zip")
    with pytest.raises(InputValidationError, match="HWPX ZIP"):
        inspect_hwpx(path)


def test_rejects_missing_required_header(tmp_path):
    path = tmp_path / "missing.hwpx"
    make_hwpx(path, header="")
    with pytest.raises(InputValidationError, match="header.xml"):
        inspect_hwpx(path)


def test_rejects_path_traversal_member(tmp_path):
    path = tmp_path / "traversal.hwpx"
    make_hwpx(path, extra=(("../evil.xml", "x"),))
    with pytest.raises(InputValidationError, match="안전하지 않은 경로"):
        inspect_hwpx(path)


def test_rejects_xml_doctype(tmp_path):
    path = tmp_path / "xxe.hwpx"
    make_hwpx(path, section="<!DOCTYPE x [<!ENTITY e SYSTEM 'file:///c:/x'>]><x>&e;</x>")
    with pytest.raises(InputValidationError, match="안전하지 않은 XML"):
        inspect_hwpx(path)


def test_rejects_extreme_compression_ratio(tmp_path):
    path = tmp_path / "bomb.hwpx"
    make_hwpx(path, extra=(("BinData/bomb.bin", b"0" * 2_000_000),))
    with pytest.raises(InputValidationError, match="압축률"):
        inspect_hwpx(path)
