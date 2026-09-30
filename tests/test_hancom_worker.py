from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType

from hwpx_hwp_app.hancom_worker import convert


def test_conversion_discards_open_document_before_quit(monkeypatch, tmp_path):
    events = []

    class FakeHwp:
        def RegisterModule(self, *args): events.append("register")
        def Open(self, *args): events.append("open"); return True
        def SaveAs(self, *args): events.append("save_as"); return True
        def Clear(self, option): events.append(("clear", option))
        def Quit(self): events.append("quit")

    pythoncom = ModuleType("pythoncom")
    pythoncom.CoInitialize = lambda: events.append("coinitialize")
    pythoncom.CoUninitialize = lambda: events.append("couninitialize")
    client = ModuleType("win32com.client")
    client.DispatchEx = lambda name: FakeHwp()
    win32com = ModuleType("win32com"); win32com.client = client
    monkeypatch.setitem(sys.modules, "pythoncom", pythoncom)
    monkeypatch.setitem(sys.modules, "win32com", win32com)
    monkeypatch.setitem(sys.modules, "win32com.client", client)

    convert(tmp_path / "입력.hwpx", tmp_path / "출력.hwp")

    assert events.index(("clear", 1)) < events.index("quit")
