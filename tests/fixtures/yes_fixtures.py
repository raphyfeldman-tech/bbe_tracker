from __future__ import annotations
"""Hand-calculated Y.E.S. tier cases.

Tier 1: absorption_pct >= 2.5 → +1 level
Tier 2: cohort_pct >= 1.5 × 2.5 = 3.75% of headcount AND absorption_pct >= 5 → +1 level
Tier 3: cohort_pct >= 2 × 2.5 = 5% of headcount AND absorption_pct >= 5 → +2 levels
"""
import pandas as pd


# Headcount 100, cohort 10 (10%), 5 absorbed (50%):
# - Tier 3 satisfied (cohort 10% ≥ 5%, absorption 50% ≥ 5%) → +2 levels
CASE_TIER_3 = {
    "name": "tier_3",
    "yes_initiative": pd.DataFrame([
        *[{"participant_id": f"Y{i}", "absorbed": True,  "twelve_months_completed": True}
          for i in range(1, 6)],
        *[{"participant_id": f"Y{i}", "absorbed": False, "twelve_months_completed": True}
          for i in range(6, 11)],
    ]),
    "headcount": 100,
    "expected_levels_up": 2,
}


# Headcount 100, cohort 4 (4%), 2 absorbed (50%):
# - Tier 3? cohort 4% < 5% → no
# - Tier 2? cohort 4% ≥ 3.75% ✓, absorption 50% ≥ 5% ✓ → +1 level
CASE_TIER_2 = {
    "name": "tier_2",
    "yes_initiative": pd.DataFrame([
        {"participant_id": "Y1", "absorbed": True,  "twelve_months_completed": True},
        {"participant_id": "Y2", "absorbed": True,  "twelve_months_completed": True},
        {"participant_id": "Y3", "absorbed": False, "twelve_months_completed": True},
        {"participant_id": "Y4", "absorbed": False, "twelve_months_completed": True},
    ]),
    "headcount": 100,
    "expected_levels_up": 1,
}


# Headcount 100, cohort 10 (10%), 1 absorbed (10%):
# - Tier 3? absorption 10% ≥ 5% ✓ AND cohort 10% ≥ 5% ✓ → +2 levels
# Wait — need a Tier 1 case where cohort is large but absorption is small
# Headcount 100, cohort 2 (2%), 1 absorbed (50%):
# - Tier 3? cohort 2% < 5% → no
# - Tier 2? cohort 2% < 3.75% → no
# - Tier 1? absorption 50% ≥ 2.5% → +1 level
CASE_TIER_1 = {
    "name": "tier_1",
    "yes_initiative": pd.DataFrame([
        {"participant_id": "Y1", "absorbed": True,  "twelve_months_completed": True},
        {"participant_id": "Y2", "absorbed": False, "twelve_months_completed": True},
    ]),
    "headcount": 100,
    "expected_levels_up": 1,
}


# Headcount 100, cohort 10, 0 absorbed (0%):
# - Tier 3? absorption 0 < 5 → no
# - Tier 2? absorption 0 < 5 → no
# - Tier 1? absorption 0 < 2.5 → no
# → 0 levels
CASE_NO_ABSORPTION = {
    "name": "no_absorption",
    "yes_initiative": pd.DataFrame([
        {"participant_id": f"Y{i}", "absorbed": False, "twelve_months_completed": True}
        for i in range(1, 11)
    ]),
    "headcount": 100,
    "expected_levels_up": 0,
}


# Empty cohort
CASE_NO_YES = {
    "name": "no_yes",
    "yes_initiative": pd.DataFrame(),
    "headcount": 100,
    "expected_levels_up": 0,
}


ALL_CASES = [CASE_TIER_3, CASE_TIER_2, CASE_TIER_1, CASE_NO_ABSORPTION, CASE_NO_YES]
