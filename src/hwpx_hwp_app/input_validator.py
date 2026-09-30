from __future__ import annotations

import posixpath
import re
import zipfile
from pathlib import Path, PurePosixPath

from defusedxml import ElementTree as SafeET
from defusedxml.common import DefusedXmlException

from .models import FeatureInventory

MAX_FILES = 20_000
MAX_TOTAL_SIZE = 1_000_000_000
MAX_XML_SIZE = 100_000_000
MAX_COMPRESSION_RATIO = 500


class InputValidationError(ValueError):
    pass


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _safe_name(name: str) -> bool:
    normalized = name.replace("\\", "/")
    path = PurePosixPath(normalized)
    return not path.is_absolute() and ".." not in path.parts and not re.match(r"^[A-Za-z]:", normalized)


def inspect_hwpx(path: Path) -> FeatureInventory:
    path = Path(path)
    if not path.is_file() or not zipfile.is_zipfile(path):
        raise InputValidationError("실제 HWPX ZIP 문서가 아닙니다.")

    try:
        with zipfile.ZipFile(path) as zf:
            infos = zf.infolist()
            if len(infos) > MAX_FILES:
                raise InputValidationError("HWPX 내부 파일 수가 안전 제한을 초과합니다.")
            names = {info.filename.replace("\\", "/") for info in infos}
            for info in infos:
                if not _safe_name(info.filename):
                    raise InputValidationError("HWPX에 안전하지 않은 경로가 있습니다.")
                if info.file_size and info.compress_size and info.file_size / info.compress_size > MAX_COMPRESSION_RATIO:
                    raise InputValidationError("HWPX 내부 파일의 압축률이 안전 제한을 초과합니다.")
            if sum(i.file_size for i in infos) > MAX_TOTAL_SIZE:
                raise InputValidationError("HWPX 압축 해제 크기가 안전 제한을 초과합니다.")
            if "Contents/header.xml" not in names:
                raise InputValidationError("HWPX 필수 파일 Contents/header.xml이 없습니다.")
            sections = sorted(n for n in names if re.fullmatch(r"Contents/section\d+\.xml", n, re.I))
            if not sections:
                raise InputValidationError("HWPX 본문 section XML이 없습니다.")

            totals: dict[str, int] = {k: 0 for k in ("p", "tbl", "pic", "header", "footer", "footnote", "endnote", "equation", "chart", "ole")}
            texts: list[str] = []
            special: set[str] = set()
            for member in ["Contents/header.xml", *sections]:
                info = zf.getinfo(member)
                if info.file_size > MAX_XML_SIZE:
                    raise InputValidationError("HWPX XML 크기가 안전 제한을 초과합니다.")
                raw = zf.read(member)
                try:
                    root = SafeET.fromstring(raw, forbid_dtd=True, forbid_entities=True, forbid_external=True)
                except (DefusedXmlException, SafeET.ParseError, ValueError) as exc:
                    message = "안전하지 않은 XML이 포함되어 있습니다." if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper() else "HWPX XML을 읽을 수 없습니다."
                    raise InputValidationError(message) from exc
                for elem in root.iter():
                    name = _local_name(elem.tag)
                    if name in totals:
                        totals[name] += 1
                    if name in {"t", "text"} and elem.text:
                        texts.append(elem.text)
                    if name in {"equation", "chart", "ole"}:
                        special.add(name)

            return FeatureInventory(
                sections=len(sections), paragraphs=totals["p"], tables=totals["tbl"],
                images=totals["pic"], headers=totals["header"], footers=totals["footer"],
                notes=totals["footnote"] + totals["endnote"], equations=totals["equation"],
                charts=totals["chart"], ole_objects=totals["ole"], text="".join(texts),
                special_features=tuple(sorted(special)),
            )
    except zipfile.BadZipFile as exc:
        raise InputValidationError("손상된 HWPX ZIP 문서입니다.") from exc
