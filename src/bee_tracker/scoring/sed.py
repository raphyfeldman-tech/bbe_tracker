from __future__ import annotations
import pandas as pd
from ..config import Scorecard
from .base import ElementResult, ElementScorer


def _qualifying_spend(sed_contributions: pd.DataFrame) -> float:
    """Sum of cash + in_kind on beneficiaries with black_beneficiary_pct >= 75."""
    if sed_contributions.empty or "black_beneficiary_pct" not in sed_contributions.columns:
        return 0.0
    qualifying = sed_contributions[
        sed_contributions["black_beneficiary_pct"].fillna(0) >= 75
    ]
    if qualifying.empty:
        return 0.0
    cash = qualifying.get("cash_value", pd.Series(dtype=float)).fillna(0).sum()
    in_kind = qualifying.get("in_kind_value", pd.Series(dtype=float)).fillna(0).sum()
    return float(cash + in_kind)


def score_sed(
    *,
    sed_contributions: pd.DataFrame,
    settings: dict,
    scorecard: Scorecard,
) -> ElementResult:
    cfg = scorecard.elements["socio_economic_dev"]
    npat = settings.get("npat_current") or 0
    spend = _qualifying_spend(sed_contributions)
    actual_pct = (spend / npat * 100.0) if npat else 0.0
    target = cfg.indicators["sed_spend_npat_pct"]
    ratio = 0.0 if target.target_pct == 0 else actual_pct / target.target_pct
    ratio = min(ratio, 1.0)
    points = round(ratio * target.weighting, 4)
    return ElementResult(
        element="socio_economic_dev",
        indicator_points={"sed_spend_npat_pct": points},
        subtotal=points,
        max_points=cfg.total_points,
        sub_minimum_breach=False,
    )


class SEDScorer(ElementScorer):
    element_name = "socio_economic_dev"

    def score(self, inputs: dict, scorecard: Scorecard) -> ElementResult:
        return score_sed(
            sed_contributions=inputs["sed_contributions"],
            settings=inputs["settings"],
            scorecard=scorecard,
        )
