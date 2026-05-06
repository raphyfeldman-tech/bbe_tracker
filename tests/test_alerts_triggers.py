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


import pandas as pd
from datetime import date
from bee_tracker.alerts.triggers import (
    detect_cert_expiries, CertExpiry, Severity,
)


def test_detect_cert_expiries_classifies_red_and_amber():
    today = date(2026, 5, 4)
    suppliers = pd.DataFrame([
        {"supplier_id": "S1", "supplier_name": "Already Expired",
         "cert_expiry_date": "2026-04-01"},
        {"supplier_id": "S2", "supplier_name": "Expires Soon",
         "cert_expiry_date": "2026-05-20"},
        {"supplier_id": "S3", "supplier_name": "Expiring Amber",
         "cert_expiry_date": "2026-06-25"},
        {"supplier_id": "S4", "supplier_name": "Plenty of Time",
         "cert_expiry_date": "2027-01-01"},
    ])
    out = detect_cert_expiries(suppliers, today=today)
    by_id = {e.supplier_id: e for e in out}
    assert by_id["S1"].severity is Severity.RED
    assert by_id["S2"].severity is Severity.RED
    assert by_id["S3"].severity is Severity.AMBER
    assert "S4" not in by_id


def test_detect_cert_expiries_handles_empty_or_missing():
    today = date(2026, 5, 4)
    assert detect_cert_expiries(pd.DataFrame(), today=today) == []
    suppliers = pd.DataFrame([
        {"supplier_id": "S1", "supplier_name": "No Date",
         "cert_expiry_date": None},
    ])
    assert detect_cert_expiries(suppliers, today=today) == []
