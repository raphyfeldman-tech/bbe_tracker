from __future__ import annotations
"""Hand-calculated Management Control scoring cases.

Targets from sample_ict_scorecard.yaml (Plan 2 Task 4):
  black_board_voting: target 50, weighting 4
  black_executive_directors: target 50, weighting 3
  black_senior_mgmt: target 60, weighting 4
  black_middle_mgmt: target 75, weighting 4
  black_junior_mgmt: target 88, weighting 4

Indicator percentage = sum(fte) where (is_black AND matches level) / sum(fte) where (matches level) × 100
Then apply min(actual/target, 1) × weighting.
"""
import pandas as pd


# CASE_FULL: every indicator at or above target → 4+3+4+4+4 = 19
CASE_FULL = {
    "name": "all_targets_met",
    "employees": pd.DataFrame([
        # Board: 2 of 2 black = 100% → cap → 4 pts
        {"is_black": True,  "occupational_level": "Board", "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": True,  "occupational_level": "Board", "is_executive_director": False, "fte_months_in_period": 12},
        # Exec directors: 1 of 2 black = 50% → 1.0 × 3 = 3 pts
        {"is_black": True,  "occupational_level": "Exec",  "is_executive_director": True,  "fte_months_in_period": 12},
        {"is_black": False, "occupational_level": "Exec",  "is_executive_director": True,  "fte_months_in_period": 12},
        # Senior: 3 of 5 black = 60% → 1.0 × 4 = 4 pts
        {"is_black": True,  "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": True,  "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": True,  "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": False, "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": False, "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
        # Middle: 6 of 8 black = 75% → 1.0 × 4 = 4 pts
        *[{"is_black": True,  "occupational_level": "Middle Mgmt", "is_executive_director": False, "fte_months_in_period": 12} for _ in range(6)],
        *[{"is_black": False, "occupational_level": "Middle Mgmt", "is_executive_director": False, "fte_months_in_period": 12} for _ in range(2)],
        # Junior: 9 of 10 black = 90% > target 88 → cap → 4 pts
        *[{"is_black": True,  "occupational_level": "Junior Mgmt", "is_executive_director": False, "fte_months_in_period": 12} for _ in range(9)],
        *[{"is_black": False, "occupational_level": "Junior Mgmt", "is_executive_director": False, "fte_months_in_period": 12} for _ in range(1)],
    ]),
    "expected_points": {
        "black_board_voting": 4.0,
        "black_executive_directors": 3.0,
        "black_senior_mgmt": 4.0,
        "black_middle_mgmt": 4.0,
        "black_junior_mgmt": 4.0,
    },
    "expected_subtotal": 19.0,
    "sub_minimum_breach": False,
}


# CASE_ZERO: no black anywhere → 0 across the board
CASE_ZERO = {
    "name": "all_non_black",
    "employees": pd.DataFrame([
        {"is_black": False, "occupational_level": "Board",       "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": False, "occupational_level": "Exec",        "is_executive_director": True,  "fte_months_in_period": 12},
        {"is_black": False, "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": False, "occupational_level": "Middle Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": False, "occupational_level": "Junior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
    ]),
    "expected_points": {
        "black_board_voting": 0.0,
        "black_executive_directors": 0.0,
        "black_senior_mgmt": 0.0,
        "black_middle_mgmt": 0.0,
        "black_junior_mgmt": 0.0,
    },
    "expected_subtotal": 0.0,
    "sub_minimum_breach": False,
}


# CASE_FTE_WEIGHTED: senior mgmt — 1 black @ 6mo + 1 non-black @ 12mo
# black FTE share = 6 / (6+12) = 33.33% of target 60 → 0.5556 × 4 = 2.2222
CASE_FTE_WEIGHTED = {
    "name": "fte_weighted",
    "employees": pd.DataFrame([
        {"is_black": True,  "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 6},
        {"is_black": False, "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
    ]),
    "expected_points": {
        "black_board_voting": 0.0,
        "black_executive_directors": 0.0,
        "black_senior_mgmt": round((6.0 / 18.0) / 0.60 * 4, 4),
        "black_middle_mgmt": 0.0,
        "black_junior_mgmt": 0.0,
    },
    "expected_subtotal": round((6.0 / 18.0) / 0.60 * 4, 4),
    "sub_minimum_breach": False,
}


ALL_CASES = [CASE_FULL, CASE_ZERO, CASE_FTE_WEIGHTED]
