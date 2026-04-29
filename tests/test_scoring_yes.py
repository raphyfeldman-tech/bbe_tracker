from __future__ import annotations
from pathlib import Path
import pytest
from bee_tracker.config import load_scorecard
from bee_tracker.scoring.yes_initiative import calculate_yes_levels_up, apply_levels_up
from tests.fixtures.yes_fixtures import ALL_CASES


@pytest.fixture(scope="module")
def scorecard():
    return load_scorecard(Path("tests/fixtures/sample_ict_scorecard.yaml"))


@pytest.mark.parametrize("case", ALL_CASES, ids=lambda c: c["name"])
def test_yes_levels_up(case, scorecard):
    levels_up = calculate_yes_levels_up(
        yes_initiative=case["yes_initiative"],
        headcount=case["headcount"],
        scorecard=scorecard,
    )
    assert levels_up == case["expected_levels_up"]


def test_apply_levels_up_capped_at_level_1():
    assert apply_levels_up(3, 5) == 1
    assert apply_levels_up(2, 1) == 1
    assert apply_levels_up(8, 2) == 6


def test_apply_levels_up_non_compliant_unchanged():
    assert apply_levels_up("non_compliant", 2) == "non_compliant"
