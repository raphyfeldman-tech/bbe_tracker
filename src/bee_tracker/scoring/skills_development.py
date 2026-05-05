from __future__ import annotations
import pandas as pd
from ..config import Scorecard
from .base import ElementResult, ElementScorer


_BLACK_RACES = {"Black African", "Coloured", "Indian"}
_QUALIFYING_CATEGORIES = {"B", "C", "D", "E", "F", "G"}


def _is_black_race(value) -> bool:
    return str(value) in _BLACK_RACES


def score_skills_development(
    *,
    training: pd.DataFrame,
    learnerships: pd.DataFrame,
    bursaries: pd.DataFrame,
    employees: pd.DataFrame,
    settings: dict,
    scorecard: Scorecard,
) -> ElementResult:
    cfg = scorecard.elements["skills_development"]
    leviable_payroll = settings.get("leviable_payroll") or 0
    npat = settings.get("npat_current") or 0
    headcount = len(employees) if not employees.empty else 0

    # Indicator: training_spend_pct (Categories B-G only)
    training_spend = 0.0
    if not training.empty and not employees.empty and "employee_id" in employees.columns:
        emp_lookup = employees.set_index("employee_id")["is_black"].to_dict()
        for _, row in training.iterrows():
            if not emp_lookup.get(row.get("employee_id"), False):
                continue
            category = str(row.get("training_category", "")).strip().upper()
            if category not in _QUALIFYING_CATEGORIES:
                continue
            training_spend += float(row.get("training_spend") or 0)
    training_pct = (training_spend / leviable_payroll * 100.0) if leviable_payroll else 0.0

    # learnership_participation_pct
    learnership_count = 0
    if not learnerships.empty and "race" in learnerships.columns:
        learnership_count = int(learnerships["race"].apply(_is_black_race).sum())
    learnership_pct = (learnership_count / headcount * 100.0) if headcount else 0.0

    # bursary_spend_pct
    bursary_spend = 0.0
    if not bursaries.empty and "amount" in bursaries.columns:
        bursary_spend = float(bursaries["amount"].fillna(0).sum())
    bursary_pct = (bursary_spend / npat * 100.0) if npat else 0.0

    indicator_actuals = {
        "training_spend_pct": training_pct,
        "learnership_participation_pct": learnership_pct,
        "bursary_spend_pct": bursary_pct,
    }
    indicator_points: dict[str, float] = {}
    for indicator, target in cfg.indicators.items():
        actual = indicator_actuals.get(indicator, 0.0)
        ratio = 0.0 if target.target_pct == 0 else actual / target.target_pct
        ratio = min(ratio, 1.0)
        indicator_points[indicator] = round(ratio * target.weighting, 4)

    subtotal = round(sum(indicator_points.values()), 4)
    sub_min_pct = cfg.sub_minimum_pct or 40
    sub_minimum_breach = (subtotal / cfg.total_points * 100.0) < sub_min_pct

    return ElementResult(
        element="skills_development",
        indicator_points=indicator_points,
        subtotal=subtotal,
        max_points=cfg.total_points,
        sub_minimum_breach=sub_minimum_breach,
    )


class SkillsDevScorer(ElementScorer):
    element_name = "skills_development"

    def score(self, inputs: dict, scorecard: Scorecard) -> ElementResult:
        return score_skills_development(
            training=inputs["training"],
            learnerships=inputs["learnerships"],
            bursaries=inputs["bursaries"],
            employees=inputs["employees"],
            settings=inputs["settings"],
            scorecard=scorecard,
        )
