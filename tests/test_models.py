from dataclasses import FrozenInstanceError

import pytest

from hwpx_hwp_app.models import ConversionResult, FeatureInventory, JobStatus


@pytest.mark.parametrize(
    ("status", "label"),
    [
        (JobStatus.SUCCESS, "성공"),
        (JobStatus.WARNING, "성공(경고)"),
        (JobStatus.FAILED, "실패"),
        (JobStatus.CANCELLED, "취소"),
    ],
)
def test_job_status_has_exact_korean_label(status, label):
    assert status.label == label


def test_feature_inventory_is_immutable_and_has_tuple_defaults():
    inventory = FeatureInventory()
    assert inventory.special_features == ()
    with pytest.raises(FrozenInstanceError):
        inventory.paragraphs = 1


def test_conversion_result_is_immutable():
    result = ConversionResult(status=JobStatus.SUCCESS)
    with pytest.raises(FrozenInstanceError):
        result.engine = "changed"
