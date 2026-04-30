from __future__ import annotations
from pathlib import Path
import pytest
from bee_tracker.config import load_scorecard
from bee_tracker.scoring.level import total_score_to_level, level_after_priority_breaches


@pytest.fixture(scope="module")
def scorecard():
    return load_scorecard(Path("tests/fixtures/sample_ict_scorecard.yaml"))


@pytest.mark.parametrize("score,expected_level", [
    (105, 1),
    (100, 1),
    (99, 2),
    (95, 2),
    (94, 3),
    (90, 3),
    (89, 4),
    (80, 4),
    (75, 5),
    (70, 6),
    (55, 7),
    (40, 8),
    (39, "non_compliant"),
    (0, "non_compliant"),
])
def test_total_score_to_level(scorecard, score, expected_level):
    assert total_score_to_level(score, scorecard) == expected_level


def test_level_after_priority_breaches_no_breach(scorecard):
    # Score 95 → Level 2 base, no breaches → stays Level 2
    assert level_after_priority_breaches(95, breach_count=0, scorecard=scorecard) == 2


def test_level_after_priority_breaches_one_breach(scorecard):
    # Score 95 → Level 2 base, 1 breach → discounted to Level 3
    assert level_after_priority_breaches(95, breach_count=1, scorecard=scorecard) == 3


def test_level_after_priority_breaches_multiple_breaches(scorecard):
    # Score 95 → Level 2 base, 2 breaches → discounted to Level 4
    assert level_after_priority_breaches(95, breach_count=2, scorecard=scorecard) == 4


def test_level_after_priority_breaches_capped_at_non_compliant(scorecard):
    # Score 100 → Level 1, 8 breaches → max discount = level 8 → next breach → non_compliant
    assert level_after_priority_breaches(100, breach_count=8, scorecard=scorecard) == "non_compliant"


def test_level_after_priority_breaches_score_already_non_compliant(scorecard):
    # Score 30 → already non_compliant; breaches don't double-penalize
    assert level_after_priority_breaches(30, breach_count=2, scorecard=scorecard) == "non_compliant"
