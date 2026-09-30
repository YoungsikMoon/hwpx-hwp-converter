from pathlib import Path

import pytest

from hwpx_hwp_app.engines import EngineUnavailable, JavaConverterEngine


def test_java_engine_reports_missing_runtime(tmp_path):
    engine = JavaConverterEngine(app_root=tmp_path)
    with pytest.raises(EngineUnavailable, match="Java 런타임"):
        engine.command(Path("in.hwpx"), Path("out.hwp"))


def test_java_command_preserves_paths_as_separate_arguments(tmp_path):
    java = tmp_path / "runtime" / "java" / "bin" / "java.exe"
    jar = tmp_path / "vendor" / "hwp-converter" / "hwpConverter.jar"
    lib = jar.parent / "lib"
    java.parent.mkdir(parents=True); java.write_bytes(b"")
    lib.mkdir(parents=True); jar.write_bytes(b"")
    source = Path("C:/한글 문서/입력.hwpx")
    output = Path("C:/결과 폴더/출력.hwp")
    command = JavaConverterEngine(app_root=tmp_path).command(source, output)
    assert command[-2:] == [str(source), str(output)]
    assert command[0] == str(java)
    assert command[command.index("-cp") + 1] == f"{jar};{lib / '*'}"
