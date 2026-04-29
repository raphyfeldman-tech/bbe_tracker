from __future__ import annotations
from pathlib import Path
import pytest
from bee_tracker.config import load_scorecard
from bee_tracker.scoring.sed import score_sed
from tests.fixtures.sed_fixtures import ALL_CASES


@pytest.fixture(scope="module")
def scorecard():
    return load_scorecard(Path("tests/fixtures/sample_ict_scorecard.yaml"))


@pytest.mark.parametrize("case", ALL_CASES, ids=lambda c: c["name"])
def test_sed_scoring(case, scorecard):
    result = score_sed(
        sed_contributions=case["sed_contributions"],
        settings=case["settings"],
        scorecard=scorecard,
    )
    for indicator, expected in case["expected_points"].items():
        assert abs(result.indicator_points[indicator] - expected) < 0.01
    assert abs(result.subtotal - case["expected_subtotal"]) < 0.01
    assert result.sub_minimum_breach is case["sub_minimum_breach"]


def test_sed_empty_contributions(scorecard):
    import pandas as pd
    result = score_sed(
        sed_contributions=pd.DataFrame(),
        settings={"npat_current": 5000000},
        scorecard=scorecard,
    )
    assert result.subtotal == 0.0
