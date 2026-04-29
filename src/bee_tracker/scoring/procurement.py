from __future__ import annotations
"""Procurement helpers shared across PP scoring and gap analysis."""
import pandas as pd
from ..config import Scorecard


def total_measured_procurement_spend(procurement: pd.DataFrame) -> float:
    """TMPS = sum(period_spend_ex_vat - period_excluded_spend).

    Both columns may carry NaN; missing exclusions default to 0. An empty
    DataFrame yields 0.
    """
    if procurement.empty:
        return 0.0
    zeros = pd.Series(0.0, index=procurement.index)
    spend = procurement.get("period_spend_ex_vat", zeros).fillna(0)
    excluded = procurement.get("period_excluded_spend", zeros).fillna(0)
    return float((spend - excluded).sum())


def recognised_spend_for_supplier(
    *, measured_spend: float, cert_level, scorecard: Scorecard,
) -> float:
    """Apply the BEE recognition multiplier.

    Level 1 → 1.35, Level 4 → 1.00, Level 8 → 0.10, non_compliant → 0.0.
    Unknown cert_level (including None) → 0.0.
    """
    multiplier = scorecard.recognition_levels.get(cert_level, 0.0)
    return float(measured_spend) * float(multiplier)
