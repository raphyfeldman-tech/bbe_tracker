from __future__ import annotations
import pandas as pd
from ..config import Scorecard


def calculate_yes_levels_up(
    *,
    yes_initiative: pd.DataFrame,
    headcount: int,
    scorecard: Scorecard,
) -> int:
    """Return the number of BEE levels to add based on Y.E.S. tier achievement.

    Tiers (from yes_initiative config):
      tier 3 takes priority if its cohort + absorption thresholds are met.
      tier 2 next, tier 1 last. Returns 0 if no tier qualifies.
    """
    if yes_initiative.empty or headcount == 0:
        return 0
    cohort_size = len(yes_initiative)
    cohort_pct = cohort_size / headcount * 100.0
    absorbed = int(
        yes_initiative.get("absorbed", pd.Series(dtype=bool)).fillna(False).sum()
    )
    absorption_pct = (absorbed / cohort_size * 100.0) if cohort_size else 0.0

    tiers = scorecard.yes_initiative
    if not tiers:
        return 0

    base_target = tiers.get("tier_1", {}).get("target_absorption_pct", 2.5)

    t3 = tiers.get("tier_3", {})
    if t3:
        if (cohort_pct >= base_target * t3.get("target_multiplier", 2.0)
                and absorption_pct >= t3.get("target_absorption_pct", 5.0)):
            return int(t3.get("levels_up", 2))

    t2 = tiers.get("tier_2", {})
    if t2:
        if (cohort_pct >= base_target * t2.get("target_multiplier", 1.5)
                and absorption_pct >= t2.get("target_absorption_pct", 5.0)):
            return int(t2.get("levels_up", 1))

    t1 = tiers.get("tier_1", {})
    if t1:
        if absorption_pct >= t1.get("target_absorption_pct", 2.5):
            return int(t1.get("levels_up", 1))

    return 0


def apply_levels_up(level, levels_up: int):
    """Move up `levels_up` (lower number = better). Cap at Level 1.

    `level` is either an int 1..8 or the string 'non_compliant'. The latter
    is returned unchanged — Y.E.S. doesn't rescue a non-compliant scorecard.
    """
    if level == "non_compliant":
        return level
    return max(1, int(level) - int(levels_up))
