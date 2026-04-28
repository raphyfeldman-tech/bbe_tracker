from __future__ import annotations
from pathlib import Path
import pytest
from bee_tracker.config import load_scorecard
from bee_tracker.scoring.ownership import score_ownership
from tests.fixtures.ownership_fixtures import ALL_CASES


@pytest.fixture(scope="module")
def scorecard():
    return load_scorecard(Path("tests/fixtures/sample_ict_scorecard.yaml"))


@pytest.mark.parametrize("case", ALL_CASES, ids=lambda c: c["name"])
def test_ownership_per_indicator_points(case, scorecard):
    result = score_ownership(case["rows"], scorecard)
    for indicator, expected in case["expected_points"].items():
        actual = result.indicator_points[indicator]
        assert abs(actual - expected) < 0.01, (
            f"{case['name']} / {indicator}: expected {expected}, got {actual}"
        )


@pytest.mark.parametrize("case", ALL_CASES, ids=lambda c: c["name"])
def test_ownership_subtotal(case, scorecard):
    result = score_ownership(case["rows"], scorecard)
    assert abs(result.subtotal - case["expected_subtotal"]) < 0.01


@pytest.mark.parametrize("case", ALL_CASES, ids=lambda c: c["name"])
def test_ownership_sub_minimum_flag(case, scorecard):
    result = score_ownership(case["rows"], scorecard)
    assert result.sub_minimum_breach is case["sub_minimum_breach"]


def test_ownership_empty_rows_yields_zero(scorecard):
    import pandas as pd
    result = score_ownership(pd.DataFrame(), scorecard)
    assert result.subtotal == 0.0
    assert result.sub_minimum_breach is True   # 0 < 40%
