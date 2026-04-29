from __future__ import annotations
"""Non-financial opportunity enumeration — headcount + ownership levers."""
from dataclasses import dataclass
import pandas as pd
from ..config import Scorecard
from ..scoring.base import ElementResult
from ..scoring.registry import default_registry


@dataclass(frozen=True)
class Opportunity:
    description: str
    element: str
    points_gained: float
    notes: str


def _total_score(results: list[ElementResult]) -> float:
    return round(sum(r.subtotal for r in results), 4)


def _score_all(inputs: dict, scorecard: Scorecard) -> list[ElementResult]:
    registry = default_registry()
    return [scorer.score(inputs, scorecard) for scorer in registry.values()]


def _headcount_opportunities(
    inputs: dict, scorecard: Scorecard, baseline_total: float,
) -> list[Opportunity]:
    """For each Mgmt Control level below target, model "+1 black employee at that level"."""
    out: list[Opportunity] = []
    employees = inputs.get("employees")
    if employees is None or employees.empty:
        return out

    levels = ["Senior Mgmt", "Middle Mgmt", "Junior Mgmt"]
    for level in levels:
        new_row = {
            "employee_id": f"SYN-{level.replace(' ', '')}",
            "is_black": True,
            "occupational_level": level,
            "is_executive_director": False,
            "fte_months_in_period": 12,
        }
        scenario_emps = pd.concat([employees, pd.DataFrame([new_row])], ignore_index=True)
        scenario_inputs = {**inputs, "employees": scenario_emps}
        scenario_results = _score_all(scenario_inputs, scorecard)
        gained = round(_total_score(scenario_results) - baseline_total, 4)
        if gained <= 0:
            continue
        out.append(Opportunity(
            description=f"Appoint 1 more black employee at {level} level",
            element="management_control",
            points_gained=gained,
            notes="Hiring or promotion required",
        ))
    return out


def _ownership_opportunities(
    inputs: dict, scorecard: Scorecard, baseline_total: float,
) -> list[Opportunity]:
    """Model raising ownership.net_value_pct to the next 5% increment up to target."""
    out: list[Opportunity] = []
    ownership = inputs.get("ownership")
    if ownership is None or ownership.empty or "net_value_pct" not in ownership.columns:
        return out

    target = scorecard.elements.get("ownership", None)
    if target is None or "net_value" not in target.indicators:
        return out
    target_pct = target.indicators["net_value"].target_pct

    current_max = float(ownership["net_value_pct"].fillna(0).max())
    next_step = min(((current_max // 5) + 1) * 5, target_pct)
    if next_step <= current_max:
        return out

    scenario_own = ownership.copy()
    scenario_own["net_value_pct"] = next_step
    scenario_inputs = {**inputs, "ownership": scenario_own}
    scenario_results = _score_all(scenario_inputs, scorecard)
    gained = round(_total_score(scenario_results) - baseline_total, 4)
    if gained <= 0:
        return out
    out.append(Opportunity(
        description=f"Raise ownership net value from {current_max:.1f}% to {next_step:.1f}%",
        element="ownership",
        points_gained=gained,
        notes="Strategic equity transaction",
    ))
    return out


def enumerate_non_financial_opportunities(
    inputs: dict, scorecard: Scorecard, baseline_results: list[ElementResult],
) -> list[Opportunity]:
    baseline_total = _total_score(baseline_results)
    out: list[Opportunity] = []
    out.extend(_headcount_opportunities(inputs, scorecard, baseline_total))
    out.extend(_ownership_opportunities(inputs, scorecard, baseline_total))
    return out
