from __future__ import annotations
"""Hand-calculated Skills Development scoring cases.

Targets from sample_ict_scorecard.yaml (Plan 2 Task 5):
  training_spend_pct: target 6%, weight 8 (training spend on black employees / leviable_payroll × 100)
  learnership_participation_pct: target 2.5%, weight 4 (black learnerships / total headcount × 100)
  bursary_spend_pct: target 2.5%, weight 3 (bursary amount / NPAT × 100)
Sub-minimum: 40% of total 15 = 6.0
"""
import pandas as pd


# CASE_FULL: every indicator at or above target → full 15
# Leviable payroll R10m, NPAT R5m
# Training: 2 black employees E1+E2, R600k total spend → 6% → cap → 8 pts
# Headcount: 10 employees (E1+E2 black, E3..E10 not), 2 black learnerships
#   → 2/10 = 20%; capped at 2.5 → 4 pts (full weight)
# Bursary: R200k / R5m = 4% → cap → 3 pts
# Subtotal 8+4+3 = 15
CASE_FULL = {
    "name": "all_targets_met",
    "training": pd.DataFrame([
        {"employee_id": "E1", "training_spend": 300000, "training_category": "B", "salary_cost_during_training": 0},
        {"employee_id": "E2", "training_spend": 300000, "training_category": "B", "salary_cost_during_training": 0},
    ]),
    "learnerships": pd.DataFrame([
        {"is_employee": True, "race": "Black African", "gender": "F"},
        {"is_employee": True, "race": "Coloured",      "gender": "M"},
    ]),
    "bursaries": pd.DataFrame([
        {"amount": 200000, "race": "Black African"},
    ]),
    "employees": pd.DataFrame([
        {"employee_id": f"E{i}", "is_black": (i <= 2), "fte_months_in_period": 12}
        for i in range(1, 11)
    ]),
    "settings": {"leviable_payroll": 10000000, "npat_current": 5000000},
    "expected_points": {
        "training_spend_pct": 8.0,
        "learnership_participation_pct": 4.0,
        "bursary_spend_pct": 3.0,
    },
    "expected_subtotal": 15.0,
    "sub_minimum_breach": False,
}


# CASE_BREACH: training R300k → 3% → 0.5 × 8 = 4. No learnerships, no bursary.
# Subtotal 4 of 15 = 26.7% < 40% → BREACH
CASE_BREACH = {
    "name": "sub_minimum_breach",
    "training": pd.DataFrame([
        {"employee_id": "E1", "training_spend": 300000, "training_category": "B", "salary_cost_during_training": 0},
    ]),
    "learnerships": pd.DataFrame(),
    "bursaries": pd.DataFrame(),
    "employees": pd.DataFrame([
        {"employee_id": f"E{i}", "is_black": True, "fte_months_in_period": 12}
        for i in range(1, 11)
    ]),
    "settings": {"leviable_payroll": 10000000, "npat_current": 5000000},
    "expected_points": {
        "training_spend_pct": 4.0,
        "learnership_participation_pct": 0.0,
        "bursary_spend_pct": 0.0,
    },
    "expected_subtotal": 4.0,
    "sub_minimum_breach": True,
}


# CASE_NO_PAYROLL: leviable_payroll missing → training_spend_pct = 0
# (denominator zero); breach because subtotal 0 < 40% sub-min
CASE_NO_PAYROLL = {
    "name": "no_leviable_payroll",
    "training": pd.DataFrame([
        {"employee_id": "E1", "training_spend": 300000, "training_category": "B", "salary_cost_during_training": 0},
    ]),
    "learnerships": pd.DataFrame(),
    "bursaries": pd.DataFrame(),
    "employees": pd.DataFrame([
        {"employee_id": "E1", "is_black": True, "fte_months_in_period": 12},
    ]),
    "settings": {"leviable_payroll": None, "npat_current": 5000000},
    "expected_points": {
        "training_spend_pct": 0.0,
        "learnership_participation_pct": 0.0,
        "bursary_spend_pct": 0.0,
    },
    "expected_subtotal": 0.0,
    "sub_minimum_breach": True,
}


# CASE_CATEGORY_A_EXCLUDED:
# Leviable payroll R10m, NPAT R5m
# Training: E1 = R300k Category B (counts), E2 = R300k Category A (EXCLUDED)
# Recognised training spend = R300k → 3% of R10m payroll
# ratio = 3/6 = 0.5; points = 0.5 × 8 = 4.0
# Subtotal 4.0; 4/15 = 26.67% < 40% → BREACH
CASE_CATEGORY_A_EXCLUDED = {
    "name": "category_a_excluded",
    "training": pd.DataFrame([
        {"employee_id": "E1", "training_spend": 300000, "training_category": "B",
         "salary_cost_during_training": 0},
        {"employee_id": "E2", "training_spend": 300000, "training_category": "A",
         "salary_cost_during_training": 0},
    ]),
    "learnerships": pd.DataFrame(),
    "bursaries": pd.DataFrame(),
    "employees": pd.DataFrame([
        {"employee_id": f"E{i}", "is_black": (i <= 2), "fte_months_in_period": 12}
        for i in range(1, 11)
    ]),
    "settings": {"leviable_payroll": 10000000, "npat_current": 5000000},
    "expected_points": {
        "training_spend_pct": 4.0,
        "learnership_participation_pct": 0.0,
        "bursary_spend_pct": 0.0,
    },
    "expected_subtotal": 4.0,
    "sub_minimum_breach": True,
}


ALL_CASES = [CASE_FULL, CASE_BREACH, CASE_NO_PAYROLL, CASE_CATEGORY_A_EXCLUDED]
