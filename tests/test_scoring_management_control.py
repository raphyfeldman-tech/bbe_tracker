from __future__ import annotations
from pathlib import Path
import pytest
from bee_tracker.config import load_scorecard
from bee_tracker.scoring.management_control import score_management_control
from tests.fixtures.management_control_fixtures import ALL_CASES


@pytest.fixture(scope="module")
def scorecard():
    return load_scorecard(Path("tests/fixtures/sample_ict_scorecard.yaml"))


@pytest.mark.parametrize("case", ALL_CASES, ids=lambda c: c["name"])
def test_management_control_indicator_points(case, scorecard):
    result = score_management_control(case["employees"], scorecard)
    for indicator, expected in case["expected_points"].items():
        actual = result.indicator_points[indicator]
        assert abs(actual - expected) < 0.01, (
            f"{case['name']}/{indicator}: expected {expected}, got {actual}"
        )


@pytest.mark.parametrize("case", ALL_CASES, ids=lambda c: c["name"])
def test_management_control_subtotal(case, scorecard):
    result = score_management_control(case["employees"], scorecard)
    assert abs(result.subtotal - case["expected_subtotal"]) < 0.01


def test_management_control_empty_employees(scorecard):
    import pandas as pd
    result = score_management_control(pd.DataFrame(), scorecard)
    assert result.subtotal == 0.0
    assert all(v == 0.0 for v in result.indicator_points.values())


def test_eap_scorer_accepts_black_african_workbook_convention(scorecard):
    """Real workbook data uses 'Black African' (BEE convention) not 'African'.

    Both forms must produce the same EAP-weighted score; before this fix,
    'Black African' silently scored 0 across all 5 main indicators.
    """
    import pandas as pd
    from bee_tracker.scoring.management_control import score_management_control

    # Same demographic mix; only the race-string spelling differs.
    employees_african = pd.DataFrame([
        {"is_black": True, "race": "African", "gender": "Male",
         "occupational_level": "Senior Mgmt", "is_executive_director": False,
         "fte_months_in_period": 12},
    ])
    employees_black_african = pd.DataFrame([
        {"is_black": True, "race": "Black African", "gender": "Male",
         "occupational_level": "Senior Mgmt", "is_executive_director": False,
         "fte_months_in_period": 12},
    ])

    r1 = score_management_control(employees_african, scorecard)
    r2 = score_management_control(employees_black_african, scorecard)
    assert r1.indicator_points["black_senior_mgmt"] == r2.indicator_points["black_senior_mgmt"]
    assert r1.indicator_points["black_senior_mgmt"] > 0   # both should score
