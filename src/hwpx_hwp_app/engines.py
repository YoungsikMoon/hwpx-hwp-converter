from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from pathlib import Path


class EngineUnavailable(RuntimeError):
    pass


class ConversionProcessError(RuntimeError):
    pass


def _run(command: list[str], timeout: int, cancel_event: threading.Event) -> None:
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", creationflags=flags)
    deadline = time.monotonic() + timeout
    while process.poll() is None:
        if cancel_event.is_set():
            process.kill(); process.wait()
            raise ConversionProcessError("변환이 취소되었습니다.")
        if time.monotonic() > deadline:
            process.kill(); process.wait()
            raise ConversionProcessError("변환 제한 시간을 초과했습니다.")
        time.sleep(0.1)
    stdout, stderr = process.communicate()
    if process.returncode:
        detail = (stderr or stdout or "알 수 없는 오류").strip()[-2000:]
        raise ConversionProcessError(detail)


class JavaConverterEngine:
    name = "내장 오픈소스 엔진"

    def __init__(self, app_root: Path | None = None):
        self.app_root = Path(app_root) if app_root else Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))

    def command(self, source: Path, destination: Path) -> list[str]:
        java = self.app_root / "runtime" / "java" / "bin" / "java.exe"
        vendor = self.app_root / "vendor" / "hwp-converter"
        jar, lib = vendor / "hwpConverter.jar", vendor / "lib"
        if not java.is_file():
            raise EngineUnavailable("내장 Java 런타임을 찾을 수 없습니다.")
        if not jar.is_file() or not lib.is_dir():
            raise EngineUnavailable("내장 HWP 변환 엔진을 찾을 수 없습니다.")
        classpath = f"{jar}{os.pathsep}{lib / '*'}"
        return [str(java), "-Xmx1024m", "-Dfile.encoding=UTF-8", "-cp", classpath,
                "kr.n.nframe.newfeature.HwpConverterCli", str(source), str(destination)]

    def convert(self, source: Path, destination: Path, timeout: int, cancel_event: threading.Event) -> None:
        _run(self.command(source, destination), timeout, cancel_event)


class HancomAutomationEngine:
    name = "설치된 한컴오피스"

    def convert(self, source: Path, destination: Path, timeout: int, cancel_event: threading.Event) -> None:
        command = [sys.executable]
        if getattr(sys, "frozen", False):
            command += ["--hancom-worker"]
        else:
            command += ["-m", "hwpx_hwp_app.hancom_worker"]
        command += [str(source), str(destination)]
        _run(command, min(timeout, 90), cancel_event)
