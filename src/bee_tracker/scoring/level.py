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


def level_after_priority_breaches(
    score: float, *, breach_count: int, scorecard: Scorecard,
) -> int | str:
    """Apply ICT Sector Code §5.3 priority-element discounting.

    Each priority-element sub-minimum breach drops the BEE level by one
    (higher number is worse). If discounting would push past Level 8, the
    result is 'non_compliant'. A score that's already non_compliant is
    returned unchanged — breaches don't double-penalize.
    """
    base = total_score_to_level(score, scorecard)
    if base == "non_compliant" or breach_count <= 0:
        return base
    # base is an int 1..8
    new = int(base) + int(breach_count)
    if new > 8:
        return "non_compliant"
    return new
