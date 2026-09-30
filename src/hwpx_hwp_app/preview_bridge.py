from __future__ import annotations

import sys
import base64
from dataclasses import dataclass
from pathlib import Path


class PreviewAssetError(RuntimeError):
    pass


class PreviewFileError(ValueError):
    pass


MAX_PREVIEW_BYTES = 200 * 1024 * 1024


@dataclass(frozen=True)
class PreviewPayload:
    left_base64: str
    right_base64: str
    left_name: str
    right_name: str

    @classmethod
    def from_files(cls, source: Path, output: Path) -> "PreviewPayload":
        paths = (Path(source), Path(output))
        for path in paths:
            if not path.is_file():
                raise PreviewFileError("미리보기 문서 파일을 찾을 수 없습니다.")
            if path.stat().st_size > MAX_PREVIEW_BYTES:
                raise PreviewFileError("200MB를 초과하는 문서는 미리볼 수 없습니다.")
        return cls(
            base64.b64encode(paths[0].read_bytes()).decode("ascii"),
            base64.b64encode(paths[1].read_bytes()).decode("ascii"),
            paths[0].name,
            paths[1].name,
        )


@dataclass(frozen=True)
class PreviewAssets:
    root: Path
    javascript: Path
    wasm: Path
    license: Path
    version: Path
    html: Path


def application_root() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))


def preview_assets(root: Path | None = None) -> PreviewAssets:
    base = Path(root) if root is not None else application_root()
    vendor = base / "vendor" / "rhwp"
    assets = PreviewAssets(vendor, vendor / "rhwp.js", vendor / "rhwp_bg.wasm", vendor / "LICENSE", vendor / "VERSION", vendor / "index.html")
    if not all(path.is_file() for path in (assets.javascript, assets.wasm, assets.license, assets.version, assets.html)):
        raise PreviewAssetError("내장 미리보기 엔진 파일을 찾을 수 없습니다.")
    return assets
