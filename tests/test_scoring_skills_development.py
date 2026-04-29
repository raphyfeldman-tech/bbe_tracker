from __future__ import annotations
from pathlib import Path
import pytest
from bee_tracker.config import load_scorecard
from bee_tracker.scoring.skills_development import score_skills_development
from tests.fixtures.skills_development_fixtures import ALL_CASES


@pytest.fixture(scope="module")
def scorecard():
    return load_scorecard(Path("tests/fixtures/sample_ict_scorecard.yaml"))


@pytest.mark.parametrize("case", ALL_CASES, ids=lambda c: c["name"])
def test_skills_development_points(case, scorecard):
    result = score_skills_development(
        training=case["training"],
        learnerships=case["learnerships"],
        bursaries=case["bursaries"],
        employees=case["employees"],
        settings=case["settings"],
        scorecard=scorecard,
    )
    for indicator, expected in case["expected_points"].items():
        actual = result.indicator_points[indicator]
        assert abs(actual - expected) < 0.01


@pytest.mark.parametrize("case", ALL_CASES, ids=lambda c: c["name"])
def test_skills_development_subtotal_and_breach(case, scorecard):
    result = score_skills_development(
        training=case["training"],
        learnerships=case["learnerships"],
        bursaries=case["bursaries"],
        employees=case["employees"],
        settings=case["settings"],
        scorecard=scorecard,
    )
    assert abs(result.subtotal - case["expected_subtotal"]) < 0.01
    assert result.sub_minimum_breach is case["sub_minimum_breach"]
