from __future__ import annotations

import sys
from pathlib import Path


def convert(source: Path, destination: Path) -> None:
    import pythoncom
    import win32com.client

    pythoncom.CoInitialize()
    hwp = None
    try:
        hwp = win32com.client.DispatchEx("HWPFrame.HwpObject")
        try:
            hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        except Exception:
            pass
        if not hwp.Open(str(source), "HWPX", "forceopen:true;suspendpassword:true"):
            raise RuntimeError("설치된 한컴오피스가 HWPX를 열지 못했습니다.")
        if not hwp.SaveAs(str(destination), "HWP", "lock:false"):
            raise RuntimeError("설치된 한컴오피스가 HWP 형식으로 저장하지 못했습니다.")
    finally:
        if hwp is not None:
            try: hwp.Clear(1)
            except Exception: pass
            try: hwp.Quit()
            except Exception: pass
        pythoncom.CoUninitialize()


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:
        print("한컴 자동화 인자가 올바르지 않습니다.", file=sys.stderr)
        return 2
    try:
        convert(Path(args[0]), Path(args[1]))
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
