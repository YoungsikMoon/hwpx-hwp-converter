from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class JobStatus(Enum):
    PENDING = "대기"
    RUNNING = "변환 중"
    SUCCESS = "성공"
    WARNING = "성공(경고)"
    FAILED = "실패"
    CANCELLED = "취소"

    @property
    def label(self) -> str:
        return self.value


@dataclass(frozen=True)
class FeatureInventory:
    sections: int | None = None
    paragraphs: int | None = None
    tables: int | None = None
    images: int | None = None
    headers: int | None = None
    footers: int | None = None
    notes: int | None = None
    equations: int | None = None
    charts: int | None = None
    ole_objects: int | None = None
    text: str = ""
    special_features: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConversionWarning:
    code: str
    message: str


@dataclass(frozen=True)
class ConversionResult:
    status: JobStatus
    source: Path | None = None
    output: Path | None = None
    engine: str = ""
    message: str = ""
    warnings: tuple[ConversionWarning, ...] = ()
    elapsed_seconds: float = 0.0
