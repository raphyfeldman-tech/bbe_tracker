from __future__ import annotations
import pandas as pd
from ..config import Scorecard
from .base import ElementResult, ElementScorer


# Maps indicator name (config) -> column name (Ownership sheet)
_COLUMN_FOR_INDICATOR = {
    "black_voting_rights": "black_voting_rights_pct",
    "black_women_voting_rights": "black_women_voting_rights_pct",
    "black_economic_interest": "black_economic_interest_pct",
    "black_women_economic_interest": "black_women_economic_interest_pct",
    "net_value": "net_value_pct",
    "new_entrants": "new_entrants_pct",
    "designated_groups": "black_designated_groups_pct",
}


def _sum_pct(rows: pd.DataFrame, column: str) -> float:
    if rows.empty or column not in rows.columns:
        return 0.0
    return float(rows[column].fillna(0).sum())


def score_ownership(rows: pd.DataFrame, scorecard: Scorecard) -> ElementResult:
    """Score the Ownership element per ICT spec section 5.2.1.

    Formula per indicator: min(actual / target, 1) * weighting
    Sub-minimum: net_value points must be >= sub_minimum_pct% of its weighting.
    """
    cfg = scorecard.elements["ownership"]
    indicator_points: dict[str, float] = {}

    for indicator, target in cfg.indicators.items():
        column = _COLUMN_FOR_INDICATOR.get(indicator)
        if column is None:
            indicator_points[indicator] = 0.0
            continue
        actual = _sum_pct(rows, column)
        ratio = 0.0 if target.target_pct == 0 else actual / target.target_pct
        ratio = min(ratio, 1.0)
        indicator_points[indicator] = round(ratio * target.weighting, 4)

    subtotal = round(sum(indicator_points.values()), 4)

    net_value_points = indicator_points.get("net_value", 0.0)
    net_value_weighting = cfg.indicators["net_value"].weighting
    sub_min_pct = cfg.sub_minimum_pct or 40
    sub_minimum_breach = (
        net_value_points / net_value_weighting * 100 < sub_min_pct
    ) if net_value_weighting else True

    return ElementResult(
        element="ownership",
        indicator_points=indicator_points,
        subtotal=subtotal,
        max_points=cfg.total_points,
        sub_minimum_breach=sub_minimum_breach,
    )


class OwnershipScorer(ElementScorer):
    element_name = "ownership"

    def score(self, inputs: dict, scorecard: Scorecard) -> ElementResult:
        return score_ownership(inputs["ownership"], scorecard)
