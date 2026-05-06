from __future__ import annotations
"""Hand-calculated Management Control scoring cases.

Targets from sample_ict_scorecard.yaml (Plan 2 Task 4):
  black_board_voting: target 50, weighting 4
  black_executive_directors: target 50, weighting 3
  black_senior_mgmt: target 60, weighting 4
  black_middle_mgmt: target 75, weighting 4
  black_junior_mgmt: target 88, weighting 4

Plan 3b Task 1 black-female sub-indicators:
  black_female_senior_mgmt: target 30, weighting 2
  black_female_middle_mgmt: target 40, weighting 2
  black_female_junior_mgmt: target 50, weighting 1

Plan 3d Tasks 1-4 EAP demographic weighting (within-black shares):
  African: 76.4 / 88.8 = 0.86036
  Coloured: 9.7 / 88.8 = 0.10923
  Indian:  2.7 / 88.8 = 0.03041
The 5 main "black at level" indicators now split target + weight by these
shares; black_female_* and black_disabled stay aggregate-black.

EAP race-weights for the canonical sample scorecard:
  weight 4 → African 3.4414, Coloured 0.4369, Indian 0.1216
  weight 3 → African 2.5811, Coloured 0.3277, Indian 0.0912

Indicator percentage = sum(fte) where (race AND matches level) / sum(fte) where (matches level) × 100
Then apply min(actual/race_target, 1) × race_weight per race, sum across races.
"""
import pandas as pd


# CASE_FULL: every "black at level" indicator at-or-above target. All blacks
# are tagged race="African" (no Coloured/Indian present), so only the African
# race-portion of each weight is earned. Black-female + black-disabled
# indicators are unchanged from Plan 3b.
#  - weight 4 indicators: African portion 3.4414
#  - weight 3 indicator (exec director): African portion 2.5811
# Subtotal: 3.4414 + 2.5811 + 3.4414 + 3.4414 + 3.4414 = 16.3467
CASE_FULL = {
    "name": "all_targets_met",
    "employees": pd.DataFrame([
        # Board: 2 of 2 black = 100% → African ratio cap → 3.4414 pts
        {"is_black": True,  "race": "African", "gender": "Male", "occupational_level": "Board", "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": True,  "race": "African", "gender": "Male", "occupational_level": "Board", "is_executive_director": False, "fte_months_in_period": 12},
        # Exec directors: 1 of 2 black = 50% → African ratio cap → 2.5811 pts
        {"is_black": True,  "race": "African", "gender": "Male", "occupational_level": "Exec",  "is_executive_director": True,  "fte_months_in_period": 12},
        {"is_black": False, "race": "White",   "gender": "Male", "occupational_level": "Exec",  "is_executive_director": True,  "fte_months_in_period": 12},
        # Senior: 3 of 5 black = 60% → African ratio cap → 3.4414 pts
        {"is_black": True,  "race": "African", "gender": "Male", "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": True,  "race": "African", "gender": "Male", "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": True,  "race": "African", "gender": "Male", "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": False, "race": "White",   "gender": "Male", "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": False, "race": "White",   "gender": "Male", "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
        # Middle: 6 of 8 black = 75% → African ratio cap → 3.4414 pts
        *[{"is_black": True,  "race": "African", "gender": "Male", "occupational_level": "Middle Mgmt", "is_executive_director": False, "fte_months_in_period": 12} for _ in range(6)],
        *[{"is_black": False, "race": "White",   "gender": "Male", "occupational_level": "Middle Mgmt", "is_executive_director": False, "fte_months_in_period": 12} for _ in range(2)],
        # Junior: 9 of 10 black = 90% > target 88 → African ratio cap → 3.4414 pts
        *[{"is_black": True,  "race": "African", "gender": "Male", "occupational_level": "Junior Mgmt", "is_executive_director": False, "fte_months_in_period": 12} for _ in range(9)],
        *[{"is_black": False, "race": "White",   "gender": "Male", "occupational_level": "Junior Mgmt", "is_executive_director": False, "fte_months_in_period": 12} for _ in range(1)],
    ]),
    "expected_points": {
        "black_board_voting": 3.4414,
        "black_executive_directors": 2.5811,
        "black_senior_mgmt": 3.4414,
        "black_middle_mgmt": 3.4414,
        "black_junior_mgmt": 3.4414,
        "black_female_senior_mgmt": 0.0,
        "black_female_middle_mgmt": 0.0,
        "black_female_junior_mgmt": 0.0,
        "black_disabled": 0.0,
    },
    "expected_subtotal": 16.3467,
    "sub_minimum_breach": False,
}


# CASE_ZERO: no employees of any black race anywhere → 0 across the board
CASE_ZERO = {
    "name": "all_non_black",
    "employees": pd.DataFrame([
        {"is_black": False, "race": "White", "gender": "Male", "occupational_level": "Board",       "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": False, "race": "White", "gender": "Male", "occupational_level": "Exec",        "is_executive_director": True,  "fte_months_in_period": 12},
        {"is_black": False, "race": "White", "gender": "Male", "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": False, "race": "White", "gender": "Male", "occupational_level": "Middle Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": False, "race": "White", "gender": "Male", "occupational_level": "Junior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
    ]),
    "expected_points": {
        "black_board_voting": 0.0,
        "black_executive_directors": 0.0,
        "black_senior_mgmt": 0.0,
        "black_middle_mgmt": 0.0,
        "black_junior_mgmt": 0.0,
        "black_female_senior_mgmt": 0.0,
        "black_female_middle_mgmt": 0.0,
        "black_female_junior_mgmt": 0.0,
        "black_disabled": 0.0,
    },
    "expected_subtotal": 0.0,
    "sub_minimum_breach": False,
}


# CASE_FTE_WEIGHTED: senior mgmt — 1 African @ 6mo + 1 White @ 12mo
# African actual at senior = 6 / (6+12) = 33.33%
# African target = 60 × 0.86036 = 51.6216, ratio = 33.33/51.62 = 0.6457
# African weight = 4 × 0.86036 = 3.4414, points = 0.6457 × 3.4414 ≈ 2.2222
# Coloured/Indian both 0%, contribute 0. Total: 2.2222
CASE_FTE_WEIGHTED = {
    "name": "fte_weighted",
    "employees": pd.DataFrame([
        {"is_black": True,  "race": "African", "gender": "Male", "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 6},
        {"is_black": False, "race": "White",   "gender": "Male", "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
    ]),
    "expected_points": {
        "black_board_voting": 0.0,
        "black_executive_directors": 0.0,
        "black_senior_mgmt": round((6.0 / 18.0) / 0.60 * 4, 4),
        "black_middle_mgmt": 0.0,
        "black_junior_mgmt": 0.0,
        "black_female_senior_mgmt": 0.0,
        "black_female_middle_mgmt": 0.0,
        "black_female_junior_mgmt": 0.0,
        "black_disabled": 0.0,
    },
    "expected_subtotal": round((6.0 / 18.0) / 0.60 * 4, 4),
    "sub_minimum_breach": False,
}


# CASE_BLACK_FEMALE: 3 black-female senior managers (African), 1 black-male
# (African), 1 white-male.
# Senior pool = 5 × 12 = 60 fte-months total.
# African actual at senior = 4/5 = 80% ≥ African target 51.62% → cap → 3.4414 pts
# Coloured/Indian both 0% → 0 pts
# Black-female share at senior = 3/5 = 60% → ratio min(60/30, 1) → cap → 2 pts
# Subtotal = 3.4414 + 2.0 = 5.4414
CASE_BLACK_FEMALE = {
    "name": "black_female_senior",
    "employees": pd.DataFrame([
        {"is_black": True,  "race": "African", "gender": "Female", "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": True,  "race": "African", "gender": "Female", "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": True,  "race": "African", "gender": "Female", "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": True,  "race": "African", "gender": "Male",   "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
        {"is_black": False, "race": "White",   "gender": "Male",   "occupational_level": "Senior Mgmt", "is_executive_director": False, "fte_months_in_period": 12},
    ]),
    "expected_points": {
        "black_board_voting": 0.0,
        "black_executive_directors": 0.0,
        "black_senior_mgmt": 3.4414,
        "black_middle_mgmt": 0.0,
        "black_junior_mgmt": 0.0,
        "black_female_senior_mgmt": 2.0,
        "black_female_middle_mgmt": 0.0,
        "black_female_junior_mgmt": 0.0,
        "black_disabled": 0.0,
    },
    "expected_subtotal": 5.4414,
    "sub_minimum_breach": False,
}


# CASE_BLACK_DISABLED: 100 African-male junior managers, first 3 are disabled.
# African actual at junior = 100% ≥ African target 88 × 0.86036 = 75.71% → cap
#   → African weight 3.4414 pts. Coloured/Indian both 0 → 0 pts.
# Black-disabled share = 3/100 = 3% > target 2% → cap → 2 pts.
# Subtotal: 3.4414 + 2.0 = 5.4414
CASE_BLACK_DISABLED = {
    "name": "black_disabled",
    "employees": pd.DataFrame([
        {"is_black": True, "race": "African", "gender": "Male", "occupational_level": "Junior Mgmt",
         "disability": (i < 3),
         "is_executive_director": False, "fte_months_in_period": 12}
        for i in range(100)
    ]),
    "expected_points": {
        "black_board_voting": 0.0,
        "black_executive_directors": 0.0,
        "black_senior_mgmt": 0.0,
        "black_middle_mgmt": 0.0,
        "black_junior_mgmt": 3.4414,
        "black_female_senior_mgmt": 0.0,
        "black_female_middle_mgmt": 0.0,
        "black_female_junior_mgmt": 0.0,
        "black_disabled": 2.0,
    },
    "expected_subtotal": 5.4414,
    "sub_minimum_breach": False,
}


# CASE_EAP_PROPORTIONAL: 100 senior managers split per EAP within black
# (86 African + 11 Coloured + 3 Indian).
# - African actual 86%, target 51.62% → cap → African weight 3.4414
# - Coloured actual 11%, target 6.55% → cap → Coloured weight 0.4369
# - Indian actual 3%, target 1.83% → cap → Indian weight 0.1216
# Total black_senior_mgmt = 3.4414 + 0.4369 + 0.1216 = 3.9999 (rounding artifact)
CASE_EAP_PROPORTIONAL = {
    "name": "eap_proportional_senior",
    "employees": pd.DataFrame([
        *[{"is_black": True, "race": "African", "gender": "Male",
           "occupational_level": "Senior Mgmt",
           "is_executive_director": False, "fte_months_in_period": 12}
          for _ in range(86)],
        *[{"is_black": True, "race": "Coloured", "gender": "Male",
           "occupational_level": "Senior Mgmt",
           "is_executive_director": False, "fte_months_in_period": 12}
          for _ in range(11)],
        *[{"is_black": True, "race": "Indian", "gender": "Male",
           "occupational_level": "Senior Mgmt",
           "is_executive_director": False, "fte_months_in_period": 12}
          for _ in range(3)],
    ]),
    "expected_points": {
        "black_board_voting": 0.0,
        "black_executive_directors": 0.0,
        "black_senior_mgmt": 3.9999,    # 3.4414 + 0.4369 + 0.1216
        "black_middle_mgmt": 0.0,
        "black_junior_mgmt": 0.0,
        "black_female_senior_mgmt": 0.0,
        "black_female_middle_mgmt": 0.0,
        "black_female_junior_mgmt": 0.0,
        "black_disabled": 0.0,
    },
    "expected_subtotal": 3.9999,
    "sub_minimum_breach": False,
}


# CASE_EAP_INDIAN_ONLY: 100 senior managers, ALL Indian. Demonstrates the
# EAP discipline — even though aggregate-black share is 100%, only the Indian
# race portion of the weight (0.1216) is earned.
CASE_EAP_INDIAN_ONLY = {
    "name": "eap_indian_only_senior",
    "employees": pd.DataFrame([
        *[{"is_black": True, "race": "Indian", "gender": "Male",
           "occupational_level": "Senior Mgmt",
           "is_executive_director": False, "fte_months_in_period": 12}
          for _ in range(100)],
    ]),
    "expected_points": {
        "black_board_voting": 0.0,
        "black_executive_directors": 0.0,
        "black_senior_mgmt": 0.1216,
        "black_middle_mgmt": 0.0,
        "black_junior_mgmt": 0.0,
        "black_female_senior_mgmt": 0.0,
        "black_female_middle_mgmt": 0.0,
        "black_female_junior_mgmt": 0.0,
        "black_disabled": 0.0,
    },
    "expected_subtotal": 0.1216,
    "sub_minimum_breach": False,
}


ALL_CASES = [
    CASE_FULL, CASE_ZERO, CASE_FTE_WEIGHTED,
    CASE_BLACK_FEMALE, CASE_BLACK_DISABLED,
    CASE_EAP_PROPORTIONAL, CASE_EAP_INDIAN_ONLY,
]
