from __future__ import annotations

from pathlib import Path
import struct
import zlib

import olefile

from .models import FeatureInventory

OLE_SIGNATURE = bytes.fromhex("D0CF11E0A1B11AE1")
HWP_SIGNATURE = b"HWP Document File"


class HwpValidationError(ValueError):
    pass


def parse_body_records(data: bytes) -> dict[str, int | str]:
    """Count features that have unambiguous HWP 5 record tags."""
    offset = 0
    counts: dict[str, int | str] = {"paragraphs": 0, "tables": 0, "images": 0, "text": ""}
    texts: list[str] = []
    while offset < len(data):
        if len(data) - offset < 4:
            raise ValueError("truncated HWP record header")
        header = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        tag = header & 0x3FF
        size = (header >> 20) & 0xFFF
        if size == 0xFFF:
            if len(data) - offset < 4:
                raise ValueError("truncated extended HWP record size")
            size = struct.unpack_from("<I", data, offset)[0]
            offset += 4
        end = offset + size
        if end > len(data):
            raise ValueError("truncated HWP record payload")
        payload = data[offset:end]
        offset = end
        if tag == 66:  # HWPTAG_PARA_HEADER
            counts["paragraphs"] += 1
        elif tag == 67:  # HWPTAG_PARA_TEXT
            decoded = payload.decode("utf-16le", errors="ignore")
            texts.append("".join(ch for ch in decoded if ch >= " " or ch in "\n\t"))
        elif tag == 77:  # HWPTAG_TABLE
            counts["tables"] += 1
        elif tag == 85:  # HWPTAG_SHAPE_COMPONENT_PICTURE
            counts["images"] += 1
    counts["text"] = "".join(texts)
    return counts


def inspect_hwp(path: Path) -> FeatureInventory:
    path = Path(path)
    try:
        if path.read_bytes()[:8] != OLE_SIGNATURE:
            raise HwpValidationError("실제 HWP OLE 문서가 아닙니다.")
    except OSError as exc:
        raise HwpValidationError("HWP 출력 파일을 읽을 수 없습니다.") from exc

    try:
        with olefile.OleFileIO(path) as ole:
            for required in ("FileHeader", "DocInfo"):
                if not ole.exists(required):
                    raise HwpValidationError(f"HWP 필수 스트림 {required}가 없습니다.")
            header = ole.openstream("FileHeader").read(64)
            if not header.startswith(HWP_SIGNATURE):
                raise HwpValidationError("HWP Document File 헤더 서명이 올바르지 않습니다.")
            sections = sorted(
                "/".join(parts) for parts in ole.listdir(streams=True, storages=False)
                if len(parts) == 2 and parts[0] == "BodyText" and parts[1].lower().startswith("section")
            )
            if not sections:
                raise HwpValidationError("HWP BodyText 섹션이 없습니다.")
            measured = {"paragraphs": 0, "tables": 0, "images": 0, "text": ""}
            measurable = True
            compressed = len(header) >= 40 and bool(struct.unpack_from("<I", header, 36)[0] & 1)
            for section in sections:
                body = ole.openstream(section).read()
                try:
                    if compressed:
                        body = zlib.decompress(body, -15)
                    section_counts = parse_body_records(body)
                except (ValueError, zlib.error):
                    measurable = False
                    break
                for field in ("paragraphs", "tables", "images"):
                    measured[field] += int(section_counts[field])
                measured["text"] += str(section_counts["text"])
            return FeatureInventory(
                sections=len(sections),
                paragraphs=measured["paragraphs"] if measurable else None,
                tables=measured["tables"] if measurable else None,
                images=measured["images"] if measurable else None,
                text=str(measured["text"]) if measurable else "",
            )
    except HwpValidationError:
        raise
    except (OSError, IOError, olefile.OleFileError) as exc:
        raise HwpValidationError("HWP OLE 구조를 읽을 수 없습니다.") from exc
