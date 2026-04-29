from __future__ import annotations
from pathlib import Path
import pytest
from bee_tracker.config import load_scorecard
from bee_tracker.scoring.esd_pp import score_esd_pp
from tests.fixtures.esd_pp_fixtures import ALL_CASES


@pytest.fixture(scope="module")
def scorecard():
    return load_scorecard(Path("tests/fixtures/sample_ict_scorecard.yaml"))


@pytest.mark.parametrize("case", ALL_CASES, ids=lambda c: c["name"])
def test_esd_pp_indicator_points(case, scorecard):
    result = score_esd_pp(
        suppliers=case["suppliers"],
        procurement=case["procurement"],
        esd_contributions=case["esd_contributions"],
        settings=case["settings"],
        scorecard=scorecard,
    )
    for indicator, expected in case["expected_points"].items():
        actual = result.indicator_points[indicator]
        assert abs(actual - expected) < 0.01, (
            f"{case['name']}/{indicator}: expected {expected}, got {actual}"
        )


@pytest.mark.parametrize("case", ALL_CASES, ids=lambda c: c["name"])
def test_esd_pp_subtotal_and_breach(case, scorecard):
    result = score_esd_pp(
        suppliers=case["suppliers"],
        procurement=case["procurement"],
        esd_contributions=case["esd_contributions"],
        settings=case["settings"],
        scorecard=scorecard,
    )
    assert abs(result.subtotal - case["expected_subtotal"]) < 0.01
    assert result.sub_minimum_breach is case["sub_minimum_breach"]
