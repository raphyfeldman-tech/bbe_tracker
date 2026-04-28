from __future__ import annotations
"""Hand-calculated Ownership scoring cases.

Targets are drawn from tests/fixtures/sample_ict_scorecard.yaml:
  black_voting_rights       target 25.1, weighting 4
  black_women_voting_rights target 10,   weighting 2
  black_economic_interest   target 25.1, weighting 4
  black_women_econ_interest target 10,   weighting 2
  net_value                 target 25,   weighting 8
  new_entrants              target 2,    weighting 2
  designated_groups         target 3,    weighting 3

Each case provides: name, per-indicator actuals, expected per-indicator points,
expected subtotal, expected sub_minimum_breach.
"""
import pandas as pd


CASE_FULL_SCORE = {
    "name": "full_score",
    "rows": pd.DataFrame([
        {
            "shareholder_name": "A",
            "black_voting_rights_pct": 30.0,
            "black_women_voting_rights_pct": 15.0,
            "black_economic_interest_pct": 30.0,
            "black_women_economic_interest_pct": 15.0,
            "net_value_pct": 25.0,
            "new_entrants_pct": 2.0,
            "black_designated_groups_pct": 3.0,
        }
    ]),
    "expected_points": {
        "black_voting_rights": 4.0,
        "black_women_voting_rights": 2.0,
        "black_economic_interest": 4.0,
        "black_women_economic_interest": 2.0,
        "net_value": 8.0,
        "new_entrants": 2.0,
        "designated_groups": 3.0,
    },
    "expected_subtotal": 25.0,
    "sub_minimum_breach": False,
}


CASE_PARTIAL = {
    "name": "partial",
    "rows": pd.DataFrame([
        {
            "shareholder_name": "A",
            "black_voting_rights_pct": 12.55,   # 50% of target 25.1 -> 2.0 of 4
            "black_women_voting_rights_pct": 5.0,  # 50% of target -> 1.0 of 2
            "black_economic_interest_pct": 12.55,  # 2.0 of 4
            "black_women_economic_interest_pct": 5.0,  # 1.0 of 2
            "net_value_pct": 12.5,                 # 50% of target 25 -> 4.0 of 8
            "new_entrants_pct": 1.0,                # 50% -> 1.0 of 2
            "black_designated_groups_pct": 1.5,     # 50% -> 1.5 of 3
        }
    ]),
    "expected_points": {
        "black_voting_rights": 2.0,
        "black_women_voting_rights": 1.0,
        "black_economic_interest": 2.0,
        "black_women_economic_interest": 1.0,
        "net_value": 4.0,
        "new_entrants": 1.0,
        "designated_groups": 1.5,
    },
    "expected_subtotal": 12.5,
    "sub_minimum_breach": False,   # net value 4.0 / 8 = 50% > 40%
}


CASE_SUB_MIN_BREACH = {
    "name": "sub_minimum_breach",
    "rows": pd.DataFrame([
        {
            "shareholder_name": "A",
            "black_voting_rights_pct": 30.0,
            "black_women_voting_rights_pct": 15.0,
            "black_economic_interest_pct": 30.0,
            "black_women_economic_interest_pct": 15.0,
            "net_value_pct": 5.0,    # 5/25 = 20% -> 1.6 of 8 -> 20% of weighting -> BREACH (<40%)
            "new_entrants_pct": 2.0,
            "black_designated_groups_pct": 3.0,
        }
    ]),
    "expected_points": {
        "black_voting_rights": 4.0,
        "black_women_voting_rights": 2.0,
        "black_economic_interest": 4.0,
        "black_women_economic_interest": 2.0,
        "net_value": 1.6,
        "new_entrants": 2.0,
        "designated_groups": 3.0,
    },
    "expected_subtotal": 18.6,
    "sub_minimum_breach": True,
}


CASE_OVER_TARGET_CAPS_AT_WEIGHTING = {
    "name": "over_target_caps",
    "rows": pd.DataFrame([
        {
            "shareholder_name": "A",
            "black_voting_rights_pct": 100.0,      # way over target -> capped at weighting 4
            "black_women_voting_rights_pct": 100.0, # capped at 2
            "black_economic_interest_pct": 100.0,
            "black_women_economic_interest_pct": 100.0,
            "net_value_pct": 100.0,
            "new_entrants_pct": 100.0,
            "black_designated_groups_pct": 100.0,
        }
    ]),
    "expected_points": {
        "black_voting_rights": 4.0,
        "black_women_voting_rights": 2.0,
        "black_economic_interest": 4.0,
        "black_women_economic_interest": 2.0,
        "net_value": 8.0,
        "new_entrants": 2.0,
        "designated_groups": 3.0,
    },
    "expected_subtotal": 25.0,
    "sub_minimum_breach": False,
}


ALL_CASES = [
    CASE_FULL_SCORE,
    CASE_PARTIAL,
    CASE_SUB_MIN_BREACH,
    CASE_OVER_TARGET_CAPS_AT_WEIGHTING,
]
