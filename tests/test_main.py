from hwpx_hwp_app.main import self_test

import importlib.util
from pathlib import Path


def test_self_test_converts_bundled_sample():
    assert self_test() == 0


def test_pyinstaller_style_top_level_entry_can_run_self_test():
    main_path = Path(__file__).parents[1] / "src" / "hwpx_hwp_app" / "main.py"
    spec = importlib.util.spec_from_file_location("packaged_main", main_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert module.self_test() == 0
