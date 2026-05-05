from __future__ import annotations
"""Management Control element scorer.

Plan 2 simplification: 5 indicators (board, exec directors, senior/middle/junior mgmt).
Plan 3 stretch: black female sub-indicators, EAP weighting, disabled.
"""
import pandas as pd
from ..config import Scorecard
from .base import ElementResult, ElementScorer


def _board(row) -> bool:
    return row["occupational_level"] == "Board"


def _exec_director(row) -> bool:
    return bool(row.get("is_executive_director"))


def _senior_mgmt(row) -> bool:
    return row["occupational_level"] == "Senior Mgmt"


def _middle_mgmt(row) -> bool:
    return row["occupational_level"] == "Middle Mgmt"


def _junior_mgmt(row) -> bool:
    return row["occupational_level"] == "Junior Mgmt"


_INDICATOR_PREDICATES = {
    "black_board_voting": _board,
    "black_executive_directors": _exec_director,
    "black_senior_mgmt": _senior_mgmt,
    "black_middle_mgmt": _middle_mgmt,
    "black_junior_mgmt": _junior_mgmt,
}


_BLACK_FEMALE_INDICATORS = {
    "black_female_senior_mgmt": "Senior Mgmt",
    "black_female_middle_mgmt": "Middle Mgmt",
    "black_female_junior_mgmt": "Junior Mgmt",
}


def _black_share_pct(employees: pd.DataFrame, predicate) -> float:
    """FTE-weighted percentage of black employees among those matching the predicate."""
    if employees.empty:
        return 0.0
    mask = employees.apply(predicate, axis=1)
    pool = employees[mask]
    if pool.empty:
        return 0.0
    total_fte = pool["fte_months_in_period"].fillna(0).sum()
    if total_fte == 0:
        return 0.0
    black_fte = pool[pool["is_black"].fillna(False)]["fte_months_in_period"].fillna(0).sum()
    return float(black_fte / total_fte * 100.0)


def _black_female_share_pct(employees: pd.DataFrame, level: str) -> float:
    """Black-female FTE share at a given occupational level."""
    if employees.empty:
        return 0.0
    if "gender" not in employees.columns:
        return 0.0
    at_level = employees[employees["occupational_level"] == level]
    if at_level.empty:
        return 0.0
    total_fte = at_level["fte_months_in_period"].fillna(0).sum()
    if total_fte == 0:
        return 0.0
    bf = at_level[
        at_level["is_black"].fillna(False)
        & (at_level["gender"].fillna("") == "Female")
    ]
    bf_fte = bf["fte_months_in_period"].fillna(0).sum()
    return float(bf_fte / total_fte * 100.0)


def score_management_control(employees: pd.DataFrame, scorecard: Scorecard) -> ElementResult:
    cfg = scorecard.elements["management_control"]
    indicator_points: dict[str, float] = {}
    for indicator, target in cfg.indicators.items():
        if indicator in _BLACK_FEMALE_INDICATORS:
            level = _BLACK_FEMALE_INDICATORS[indicator]
            actual_pct = _black_female_share_pct(employees, level)
        else:
            predicate = _INDICATOR_PREDICATES.get(indicator)
            if predicate is None:
                indicator_points[indicator] = 0.0
                continue
            actual_pct = _black_share_pct(employees, predicate)
        ratio = 0.0 if target.target_pct == 0 else actual_pct / target.target_pct
        ratio = min(ratio, 1.0)
        indicator_points[indicator] = round(ratio * target.weighting, 4)

    subtotal = round(sum(indicator_points.values()), 4)
    return ElementResult(
        element="management_control",
        indicator_points=indicator_points,
        subtotal=subtotal,
        max_points=cfg.total_points,
        sub_minimum_breach=False,
    )


class MgmtControlScorer(ElementScorer):
    element_name = "management_control"

    def score(self, inputs: dict, scorecard: Scorecard) -> ElementResult:
        return score_management_control(inputs["employees"], scorecard)
