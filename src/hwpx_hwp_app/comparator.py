from __future__ import annotations

from .models import ConversionWarning, FeatureInventory

LABELS = {
    "sections": "구역", "tables": "표", "images": "이미지",
    "headers": "머리말", "footers": "꼬리말", "notes": "각주/미주",
    "equations": "수식", "charts": "차트", "ole_objects": "OLE 개체",
}


def compare_inventories(before: FeatureInventory, after: FeatureInventory) -> tuple[ConversionWarning, ...]:
    warnings: list[ConversionWarning] = []
    for field, label in LABELS.items():
        source_count = getattr(before, field)
        output_count = getattr(after, field)
        if source_count is None or output_count is None:
            continue
        if source_count != output_count:
            warnings.append(ConversionWarning(field, f"{label} 수가 원본 {source_count}개, 결과 {output_count}개로 다릅니다."))
    for feature in before.special_features:
        warnings.append(ConversionWarning("special", f"특수 요소({feature})는 변환 후 육안 확인이 필요합니다."))
    return tuple(warnings)
