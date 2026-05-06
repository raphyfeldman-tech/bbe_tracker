from __future__ import annotations
import pytest
from bee_tracker.scoring.base import ElementResult
from bee_tracker.alerts.triggers import (
    detect_priority_breaches, detect_level_drop, Breach,
)


def _result(name, breach):
    return ElementResult(
        element=name, indicator_points={}, subtotal=10.0,
        max_points=25.0, sub_minimum_breach=breach,
    )


def test_detect_priority_breaches_returns_priority_only():
    results = [
        _result("ownership", True),
        _result("management_control", True),
        _result("skills_development", False),
        _result("enterprise_supplier_dev", True),
    ]
    breaches = detect_priority_breaches(results)
    assert sorted(b.element for b in breaches) == [
        "enterprise_supplier_dev", "ownership",
    ]


def test_detect_priority_breaches_all_clear():
    results = [_result("ownership", False), _result("skills_development", False)]
    assert detect_priority_breaches(results) == []


@pytest.mark.parametrize("current,prior,expected", [
    (3, 2, True),
    (2, 3, False),
    (3, 3, False),
    ("non_compliant", 5, True),
    (5, "non_compliant", False),
    ("non_compliant", "non_compliant", False),
])
def test_detect_level_drop(current, prior, expected):
    assert detect_level_drop(current, prior) is expected
