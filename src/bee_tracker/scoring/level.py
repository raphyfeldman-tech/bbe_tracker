from __future__ import annotations
from ..config import Scorecard


def total_score_to_level(score: float, scorecard: Scorecard) -> int | str:
    """Return the BEE level (1–8) or 'non_compliant' for a given total score.

    `level_thresholds` from the YAML maps each level to its minimum score.
    The function returns the highest level whose threshold is <= score, or
    'non_compliant' if no numeric level qualifies.
    """
    # Numeric levels (1..8) sorted descending by score threshold.
    numeric = sorted(
        ((lvl, threshold) for lvl, threshold in scorecard.level_thresholds.items()
         if isinstance(lvl, int)),
        key=lambda kv: kv[1],
        reverse=True,
    )
    for lvl, threshold in numeric:
        if score >= threshold:
            return lvl
    return "non_compliant"
