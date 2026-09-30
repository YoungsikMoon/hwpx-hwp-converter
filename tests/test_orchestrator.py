from __future__ import annotations

import threading
from pathlib import Path

import pytest

import hwpx_hwp_app.orchestrator as module
from hwpx_hwp_app.models import FeatureInventory, JobStatus
from hwpx_hwp_app.orchestrator import convert_one, unique_output_path


def test_unique_output_path_never_overwrites(tmp_path):
    (tmp_path / "문서.hwp").write_bytes(b"x")
    assert unique_output_path(tmp_path, "문서") == tmp_path / "문서 (1).hwp"


def test_falls_back_to_second_engine(tmp_path, monkeypatch):
    source = tmp_path / "문서.hwpx"
    source.write_bytes(b"input")
    monkeypatch.setattr(module, "inspect_hwpx", lambda p: FeatureInventory(paragraphs=1))
    monkeypatch.setattr(module, "inspect_hwp", lambda p: FeatureInventory(paragraphs=1))

    class Failing:
        name = "한컴"
        def convert(self, source, destination, timeout, cancel_event):
            raise RuntimeError("not available")

    class Working:
        name = "오픈소스"
        def convert(self, source, destination, timeout, cancel_event):
            destination.write_bytes(b"hwp")

    result = convert_one(source, tmp_path, [Failing(), Working()], threading.Event())
    assert result.status is JobStatus.SUCCESS
    assert result.engine == "오픈소스"
    assert result.output and result.output.exists()


def test_inventory_difference_becomes_warning(tmp_path, monkeypatch):
    source = tmp_path / "문서.hwpx"
    source.write_bytes(b"input")
    monkeypatch.setattr(module, "inspect_hwpx", lambda p: FeatureInventory(tables=2))
    monkeypatch.setattr(module, "inspect_hwp", lambda p: FeatureInventory(tables=0))

    class Working:
        name = "오픈소스"
        def convert(self, source, destination, timeout, cancel_event): destination.write_bytes(b"hwp")

    result = convert_one(source, tmp_path, [Working()], threading.Event())
    assert result.status is JobStatus.WARNING
    assert any("표" in warning.message for warning in result.warnings)


def test_cancelled_job_does_not_run_engine(tmp_path, monkeypatch):
    source = tmp_path / "문서.hwpx"
    source.write_bytes(b"input")
    monkeypatch.setattr(module, "inspect_hwpx", lambda p: FeatureInventory())
    called = False

    class Engine:
        name = "x"
        def convert(self, *args):
            nonlocal called
            called = True

    event = threading.Event(); event.set()
    result = convert_one(source, tmp_path, [Engine()], event)
    assert result.status is JobStatus.CANCELLED
    assert called is False


def test_unmeasured_output_feature_does_not_create_false_zero_warning():
    from hwpx_hwp_app.comparator import compare_inventories

    warnings = compare_inventories(
        FeatureInventory(tables=3, charts=2),
        FeatureInventory(tables=3, charts=None),
    )
    assert not any(w.code == "charts" for w in warnings)


def test_raw_paragraph_and_control_text_differences_are_not_loss_warnings():
    from hwpx_hwp_app.comparator import compare_inventories

    warnings = compare_inventories(
        FeatureInventory(sections=1, paragraphs=229, tables=14, images=0, text="정상 본문"),
        FeatureInventory(sections=1, paragraphs=228, tables=14, images=0, text="摤獥汬捯정상 본문"),
    )
    assert warnings == ()


def test_stable_table_difference_remains_a_warning():
    from hwpx_hwp_app.comparator import compare_inventories

    warnings = compare_inventories(
        FeatureInventory(sections=1, tables=14, images=0),
        FeatureInventory(sections=1, tables=13, images=0),
    )
    assert [warning.code for warning in warnings] == ["tables"]
