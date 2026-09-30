from __future__ import annotations

import shutil
import tempfile
import threading
import time
from pathlib import Path
from typing import Iterable

from .comparator import compare_inventories
from .hwp_validator import inspect_hwp
from .input_validator import inspect_hwpx
from .models import ConversionResult, JobStatus


def unique_output_path(output_dir: Path, stem: str) -> Path:
    candidate = Path(output_dir) / f"{stem}.hwp"
    index = 1
    while candidate.exists():
        candidate = Path(output_dir) / f"{stem} ({index}).hwp"
        index += 1
    return candidate


def convert_one(source: Path, output_dir: Path, engines: Iterable, cancel_event: threading.Event, timeout: int = 180) -> ConversionResult:
    started = time.monotonic()
    source, output_dir = Path(source), Path(output_dir)
    try:
        before = inspect_hwpx(source)
    except Exception as exc:
        return ConversionResult(JobStatus.FAILED, source=source, message=str(exc), elapsed_seconds=time.monotonic() - started)
    if cancel_event.is_set():
        return ConversionResult(JobStatus.CANCELLED, source=source, message="사용자가 변환을 취소했습니다.")

    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="hwpx-hwp-") as temp:
        temp_output = Path(temp) / "converted.hwp"
        for engine in engines:
            if cancel_event.is_set():
                return ConversionResult(JobStatus.CANCELLED, source=source, message="사용자가 변환을 취소했습니다.")
            try:
                engine.convert(source, temp_output, timeout, cancel_event)
                after = inspect_hwp(temp_output)
                warnings = compare_inventories(before, after)
                final = unique_output_path(output_dir, source.stem)
                output_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(temp_output), str(final))
                status = JobStatus.WARNING if warnings else JobStatus.SUCCESS
                return ConversionResult(status, source, final, engine.name, "변환이 완료되었습니다.", warnings, time.monotonic() - started)
            except Exception as exc:
                errors.append(f"{getattr(engine, 'name', '엔진')}: {exc}")
                temp_output.unlink(missing_ok=True)
    return ConversionResult(JobStatus.FAILED, source=source, message=" / ".join(errors) or "사용 가능한 변환 엔진이 없습니다.", elapsed_seconds=time.monotonic() - started)
