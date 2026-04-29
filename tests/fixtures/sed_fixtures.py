from __future__ import annotations
"""Hand-calculated SED scoring cases.

Indicator: sed_spend_npat_pct (qualifying spend / NPAT × 100), target 1.5%, weight 5.
Qualifying = sum(cash_value + in_kind_value) where black_beneficiary_pct >= 75.
"""
import pandas as pd


# CASE_FULL: 75k qualifying / 5m NPAT = 1.5% → cap → 5 pts
CASE_FULL = {
    "name": "target_met",
    "sed_contributions": pd.DataFrame([
        {"beneficiary_name": "Trust", "black_beneficiary_pct": 80, "cash_value": 75000, "in_kind_value": 0},
    ]),
    "settings": {"npat_current": 5000000},
    "expected_points": {"sed_spend_npat_pct": 5.0},
    "expected_subtotal": 5.0,
    "sub_minimum_breach": False,
}


# CASE_PARTIAL: 37.5k / 5m = 0.75% → 0.5 × 5 = 2.5 pts
CASE_PARTIAL = {
    "name": "partial",
    "sed_contributions": pd.DataFrame([
        {"beneficiary_name": "Trust", "black_beneficiary_pct": 80, "cash_value": 37500, "in_kind_value": 0},
    ]),
    "settings": {"npat_current": 5000000},
    "expected_points": {"sed_spend_npat_pct": 2.5},
    "expected_subtotal": 2.5,
    "sub_minimum_breach": False,
}


# CASE_NON_QUALIFYING: beneficiary 70% black (< 75 threshold) → 0 qualifying spend
CASE_NON_QUALIFYING = {
    "name": "non_qualifying_beneficiary",
    "sed_contributions": pd.DataFrame([
        {"beneficiary_name": "Mixed", "black_beneficiary_pct": 70, "cash_value": 100000, "in_kind_value": 0},
    ]),
    "settings": {"npat_current": 5000000},
    "expected_points": {"sed_spend_npat_pct": 0.0},
    "expected_subtotal": 0.0,
    "sub_minimum_breach": False,
}


# CASE_NO_NPAT: 0 settings → 0 points
CASE_NO_NPAT = {
    "name": "no_npat",
    "sed_contributions": pd.DataFrame([
        {"beneficiary_name": "Trust", "black_beneficiary_pct": 80, "cash_value": 75000, "in_kind_value": 0},
    ]),
    "settings": {"npat_current": None},
    "expected_points": {"sed_spend_npat_pct": 0.0},
    "expected_subtotal": 0.0,
    "sub_minimum_breach": False,
}


ALL_CASES = [CASE_FULL, CASE_PARTIAL, CASE_NON_QUALIFYING, CASE_NO_NPAT]
