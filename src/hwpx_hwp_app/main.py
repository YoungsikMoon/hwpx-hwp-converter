from __future__ import annotations

import sys
import tempfile
import threading
from pathlib import Path


def app_root() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))


def self_test() -> int:
    from hwpx_hwp_app import __version__
    from hwpx_hwp_app.engines import JavaConverterEngine
    from hwpx_hwp_app.hwp_validator import inspect_hwp
    from hwpx_hwp_app.preview_bridge import preview_assets

    root = app_root()
    sample = root / "assets" / "self-test.hwpx"
    try:
        preview = preview_assets(root)
        if preview.wasm.stat().st_size < 1_000_000:
            raise RuntimeError("내장 미리보기 엔진이 올바르지 않습니다.")
        if __version__ != "1.0.0" or not (root / "licenses" / "LGPL-3.0-Qt.txt").is_file():
            raise RuntimeError("버전 또는 오픈소스 라이선스 자산이 올바르지 않습니다.")
        with tempfile.TemporaryDirectory(prefix="hwpx-hwp-selftest-") as temp:
            output = Path(temp) / "self-test.hwp"
            JavaConverterEngine(root).convert(sample, output, 60, threading.Event())
            inventory = inspect_hwp(output)
            if inventory.sections < 1:
                raise RuntimeError("본문 섹션이 없습니다.")
        print("SELF-TEST OK: 실제 HWP 5.x 생성 및 검증 완료")
        return 0
    except Exception as exc:
        print(f"SELF-TEST FAILED: {exc}", file=sys.stderr)
        return 1


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] == "--self-test":
        return self_test()
    if args and args[0] == "--hancom-worker":
        from hwpx_hwp_app.hancom_worker import main as worker_main
        return worker_main(args[1:])

    from PySide6.QtWidgets import QApplication
    from hwpx_hwp_app import __version__
    from hwpx_hwp_app.gui import MainWindow
    app = QApplication([sys.argv[0], *args])
    app.setApplicationName("HWPX-HWP 변환기")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("문영식")
    window = MainWindow(); window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
