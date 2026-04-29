from __future__ import annotations
"""Hand-calculated ESD + PP scoring cases.

Targets: total_b_bbee_pp_pct (80%, 19pts), spend_with_51pct_black (40%, 9pts),
         spend_with_emes_qses (15%, 4pts), ed_spend_npat_pct (2%, 5pts),
         sd_spend_npat_pct (2%, 10pts). Sub-min 40% of 47 = 18.8.

Recognition multipliers (sample_ict_scorecard.yaml):
  Level 1 → 1.35,  Level 4 → 1.00,  Level 8 → 0.10,  non_compliant → 0.0
"""
import pandas as pd


# CASE_FULL: TMPS = 1,000,000.
# All spend with one Level-1, 51%-black, Generic supplier.
# Recognised = 1m × 1.35 = 1,350,000 → 135% of TMPS → cap at 100% of target 80% → 19 pts
# 51%-black recognised / TMPS = 1.35m / 1m = 135% → cap at 100% of target 40% → 9 pts
# EME/QSE recognised / TMPS = 0 → 0% → 0 pts (Generic, not EME/QSE)
# ED: 100k cash, multiplier 1.0 = 100k → 100k / 5m NPAT × 100 = 2% → 1.0 × 5 = 5 pts
# SD: 100k cash, multiplier 1.0 = 100k → 100k / 5m NPAT × 100 = 2% → 1.0 × 10 = 10 pts
# Subtotal: 19 + 9 + 0 + 5 + 10 = 43 → no breach (43/47 = 91.5%)
CASE_FULL = {
    "name": "all_pp_high_no_emes",
    "suppliers": pd.DataFrame([
        {
            "supplier_id": "S1",
            "supplier_name": "Acme Generic",
            "cert_level": 1,
            "cert_type": "Generic",
            "is_51pct_black_owned": True,
            "is_30pct_black_women_owned": False,
            "is_emp_qse_51pct_black": False,
        },
    ]),
    "procurement": pd.DataFrame([
        {"supplier_id": "S1", "period_spend_ex_vat": 1000000, "period_excluded_spend": 0},
    ]),
    "esd_contributions": pd.DataFrame([
        {"type": "Enterprise Development", "cash_value": 100000, "in_kind_value": 0, "recognition_multiplier": 1.0},
        {"type": "Supplier Development",  "cash_value": 100000, "in_kind_value": 0, "recognition_multiplier": 1.0},
    ]),
    "settings": {"npat_current": 5000000},
    "expected_points": {
        "total_b_bbee_pp_pct": 19.0,
        "spend_with_51pct_black": 9.0,
        "spend_with_emes_qses": 0.0,
        "ed_spend_npat_pct": 5.0,
        "sd_spend_npat_pct": 10.0,
    },
    "expected_subtotal": 43.0,
    "sub_minimum_breach": False,
}


# CASE_MIXED:
# TMPS = 1,000,000 (S1 800k, S2 200k).
# S1: Level 4 (1.0 multi), 51%-black, Generic → recognised 800k.
# S2: Level 8 (0.10 multi), EME (51% black), QSE-style → recognised 20k.
# Total recognised = 820k → 82% of TMPS → cap at 100% of 80 target → 19 pts
# 51%-black recognised: S1 (800k × 1.0 = 800k) + S2 (51%-black? assume yes) = 820k / 1m = 82% → cap → 9 pts
# EME/QSE recognised: only S2 = 20k / 1m = 2% → 2/15 = 0.1333 × 4 = 0.5333 pts
# ED: 50k × 1.0 = 50k. 50k/5m × 100 = 1% → 0.5 × 5 = 2.5 pts
# SD: 0 → 0 pts
# Subtotal: 19 + 9 + 0.5333 + 2.5 + 0 = 31.0333 → no breach (31/47=66%)
CASE_MIXED = {
    "name": "mixed_levels",
    "suppliers": pd.DataFrame([
        {"supplier_id": "S1", "supplier_name": "Acme L4", "cert_level": 4, "cert_type": "Generic",
         "is_51pct_black_owned": True,  "is_30pct_black_women_owned": False, "is_emp_qse_51pct_black": False},
        {"supplier_id": "S2", "supplier_name": "Beta EME", "cert_level": 8, "cert_type": "EME-affidavit",
         "is_51pct_black_owned": True,  "is_30pct_black_women_owned": False, "is_emp_qse_51pct_black": True},
    ]),
    "procurement": pd.DataFrame([
        {"supplier_id": "S1", "period_spend_ex_vat": 800000, "period_excluded_spend": 0},
        {"supplier_id": "S2", "period_spend_ex_vat": 200000, "period_excluded_spend": 0},
    ]),
    "esd_contributions": pd.DataFrame([
        {"type": "Enterprise Development", "cash_value": 50000, "in_kind_value": 0, "recognition_multiplier": 1.0},
    ]),
    "settings": {"npat_current": 5000000},
    "expected_points": {
        "total_b_bbee_pp_pct": 19.0,
        "spend_with_51pct_black": 9.0,
        "spend_with_emes_qses": round(2.0 / 15.0 * 4, 4),
        "ed_spend_npat_pct": 2.5,
        "sd_spend_npat_pct": 0.0,
    },
    "expected_subtotal": round(19.0 + 9.0 + 2.0/15.0*4 + 2.5 + 0.0, 4),
    "sub_minimum_breach": False,
}


# CASE_BREACH:
# TMPS = 1,000,000 (S1 1m).
# S1: non_compliant (mult 0). Recognised total = 0.
# All PP indicators 0. ED 0, SD 0. Subtotal 0 → 0/47=0% < 40% → BREACH
CASE_BREACH = {
    "name": "all_zero_breach",
    "suppliers": pd.DataFrame([
        {"supplier_id": "S1", "supplier_name": "BadSup", "cert_level": "non_compliant",
         "cert_type": "Generic", "is_51pct_black_owned": False,
         "is_30pct_black_women_owned": False, "is_emp_qse_51pct_black": False},
    ]),
    "procurement": pd.DataFrame([
        {"supplier_id": "S1", "period_spend_ex_vat": 1000000, "period_excluded_spend": 0},
    ]),
    "esd_contributions": pd.DataFrame(),
    "settings": {"npat_current": 5000000},
    "expected_points": {
        "total_b_bbee_pp_pct": 0.0,
        "spend_with_51pct_black": 0.0,
        "spend_with_emes_qses": 0.0,
        "ed_spend_npat_pct": 0.0,
        "sd_spend_npat_pct": 0.0,
    },
    "expected_subtotal": 0.0,
    "sub_minimum_breach": True,
}


ALL_CASES = [CASE_FULL, CASE_MIXED, CASE_BREACH]
