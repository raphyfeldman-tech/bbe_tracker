from __future__ import annotations
import pandas as pd
from bee_tracker.whatif import apply_overrides


def test_apply_overrides_settings():
    inputs = {"settings": {"npat_current": 5_000_000, "leviable_payroll": 10_000_000}}
    overrides = pd.DataFrame([
        {"key": "settings.npat_current", "value": 8_000_000},
    ])
    new_inputs = apply_overrides(inputs, overrides)
    assert new_inputs["settings"]["npat_current"] == 8_000_000
    assert new_inputs["settings"]["leviable_payroll"] == 10_000_000  # unchanged
    # baseline not mutated
    assert inputs["settings"]["npat_current"] == 5_000_000


def test_apply_overrides_ownership_column():
    inputs = {"ownership": pd.DataFrame([
        {"shareholder_name": "A", "net_value_pct": 10.0},
        {"shareholder_name": "B", "net_value_pct": 5.0},
    ])}
    overrides = pd.DataFrame([
        {"key": "ownership.net_value_pct", "value": 25.0},
    ])
    new_inputs = apply_overrides(inputs, overrides)
    assert (new_inputs["ownership"]["net_value_pct"] == 25.0).all()
    # baseline not mutated
    assert inputs["ownership"]["net_value_pct"].iloc[0] == 10.0


def test_apply_overrides_procurement_row():
    inputs = {"procurement": pd.DataFrame([
        {"supplier_id": "S1", "period_spend_ex_vat": 100000, "period_excluded_spend": 0},
        {"supplier_id": "S2", "period_spend_ex_vat": 200000, "period_excluded_spend": 0},
    ])}
    overrides = pd.DataFrame([
        {"key": "procurement.S1.period_spend_ex_vat", "value": 999999},
    ])
    new_inputs = apply_overrides(inputs, overrides)
    df = new_inputs["procurement"]
    assert df.loc[df["supplier_id"] == "S1", "period_spend_ex_vat"].iloc[0] == 999999
    assert df.loc[df["supplier_id"] == "S2", "period_spend_ex_vat"].iloc[0] == 200000


def test_apply_overrides_empty_returns_same_inputs():
    inputs = {"settings": {"npat_current": 5_000_000}}
    new_inputs = apply_overrides(inputs, pd.DataFrame())
    assert new_inputs == inputs


def test_apply_overrides_skips_blank_or_nan_keys():
    inputs = {"settings": {"npat_current": 5_000_000}}
    overrides = pd.DataFrame([
        {"key": "", "value": 1},
        {"key": "settings.npat_current", "value": pd.NA},
        {"key": "settings.npat_current", "value": 7_000_000},
    ])
    new_inputs = apply_overrides(inputs, overrides)
    assert new_inputs["settings"]["npat_current"] == 7_000_000
