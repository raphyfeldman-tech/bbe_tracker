from __future__ import annotations
from pathlib import Path
import pytest
from bee_tracker.config import load_scorecard
from bee_tracker.scoring.level import total_score_to_level


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
