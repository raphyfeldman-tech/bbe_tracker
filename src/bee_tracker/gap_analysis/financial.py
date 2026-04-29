from __future__ import annotations
"""Financial action enumeration for GapAnalysis.

Generates synthetic perturbations (Rand-denominated) and computes the
marginal points each one would gain. Plan 2 ships these levers:
  - Procurement: shift each non-Level-1 supplier's spend to a Level 1 alternative
  - Skills: add R50,000 of training spend on a black employee
  - ED: add R50,000 to an Enterprise Development contribution (>=51% black recipient)
  - SD: add R50,000 to a Supplier Development contribution
  - SED: add R50,000 to an SED beneficiary (>=75% black)
"""
from dataclasses import dataclass
import pandas as pd
from ..config import Scorecard
from ..scoring.base import ElementResult
from ..scoring.registry import default_registry
from ..whatif import apply_overrides


_SKILLS_INCREMENT = 50_000
_ED_INCREMENT = 50_000
_SD_INCREMENT = 50_000
_SED_INCREMENT = 50_000


@dataclass(frozen=True)
class Action:
    description: str
    element: str
    rand_required: float
    points_gained: float
    rand_per_point: float
    reason: str


def _total_score(results: list[ElementResult]) -> float:
    return round(sum(r.subtotal for r in results), 4)


def _score_all(inputs: dict, scorecard: Scorecard) -> list[ElementResult]:
    registry = default_registry()
    return [scorer.score(inputs, scorecard) for scorer in registry.values()]


def _delta_points(baseline_total: float, scenario_results: list[ElementResult]) -> float:
    return round(_total_score(scenario_results) - baseline_total, 4)


def _procurement_actions(
    inputs: dict, scorecard: Scorecard, baseline_total: float,
) -> list[Action]:
    """For each non-Level-1 supplier, simulate shifting their spend to a Level 1 alternative."""
    actions: list[Action] = []
    suppliers = inputs.get("suppliers")
    procurement = inputs.get("procurement")
    if suppliers is None or suppliers.empty or procurement is None or procurement.empty:
        return actions

    sup_idx = suppliers.set_index("supplier_id")
    for _, row in procurement.iterrows():
        sid = row.get("supplier_id")
        if sid not in sup_idx.index:
            continue
        cert_level = sup_idx.loc[sid].get("cert_level")
        if cert_level == 1:
            continue
        spend = float(row.get("period_spend_ex_vat") or 0)
        excluded = float(row.get("period_excluded_spend") or 0)
        measured = spend - excluded
        if measured <= 0:
            continue

        # Synthetic override: pretend this supplier is a Level 1 alternative.
        # A Level 1 generic supplier is by definition >=51% black-owned,
        # which also lifts the spend_with_51pct_black indicator.
        scenario_inputs = {k: (v.copy() if isinstance(v, pd.DataFrame)
                              else dict(v) if isinstance(v, dict) else v)
                           for k, v in inputs.items()}
        sup_df = scenario_inputs["suppliers"].copy()
        mask = sup_df["supplier_id"] == sid
        sup_df.loc[mask, "cert_level"] = 1
        if "is_51pct_black_owned" in sup_df.columns:
            sup_df.loc[mask, "is_51pct_black_owned"] = True
        scenario_inputs["suppliers"] = sup_df

        scenario_results = _score_all(scenario_inputs, scorecard)
        gained = _delta_points(baseline_total, scenario_results)
        if gained <= 0:
            continue
        rand_per_point = measured / gained
        actions.append(Action(
            description=f"Shift R{measured:,.0f} from supplier {sid} (Level {cert_level}) "
                        f"to a Level 1 alternative",
            element="enterprise_supplier_dev",
            rand_required=measured,
            points_gained=gained,
            rand_per_point=round(rand_per_point, 2),
            reason=f"Recognition multiplier increases from {cert_level} to 1",
        ))
    return actions


def _skills_action(
    inputs: dict, scorecard: Scorecard, baseline_total: float,
) -> list[Action]:
    """Add R50k of training spend on a black employee."""
    employees = inputs.get("employees")
    training = inputs.get("training")
    if employees is None or employees.empty:
        return []
    black_emps = employees[employees["is_black"].fillna(False)] if "is_black" in employees.columns else employees
    if black_emps.empty:
        return []

    target_eid = black_emps.iloc[0]["employee_id"]
    new_training = (training.copy() if training is not None and not training.empty
                    else pd.DataFrame(columns=["employee_id", "training_spend",
                                               "salary_cost_during_training"]))
    new_row = {"employee_id": target_eid, "training_spend": _SKILLS_INCREMENT,
               "salary_cost_during_training": 0}
    new_training = pd.concat([new_training, pd.DataFrame([new_row])], ignore_index=True)

    scenario_inputs = {**inputs, "training": new_training}
    scenario_results = _score_all(scenario_inputs, scorecard)
    gained = _delta_points(baseline_total, scenario_results)
    if gained <= 0:
        return []
    return [Action(
        description=f"Add R{_SKILLS_INCREMENT:,.0f} of discretionary training spend "
                    f"on a black employee",
        element="skills_development",
        rand_required=_SKILLS_INCREMENT,
        points_gained=gained,
        rand_per_point=round(_SKILLS_INCREMENT / gained, 2),
        reason="Increases training_spend_pct toward target",
    )]


def _esd_actions(
    inputs: dict, scorecard: Scorecard, baseline_total: float,
) -> list[Action]:
    """Add R50k to an ED and to an SD contribution."""
    out: list[Action] = []
    base = inputs.get("esd_contributions")
    base_df = base.copy() if base is not None and not base.empty else pd.DataFrame()

    for kind, increment, label in (
        ("Enterprise Development", _ED_INCREMENT, "ED"),
        ("Supplier Development", _SD_INCREMENT, "SD"),
    ):
        new_row = {
            "type": kind, "cash_value": increment, "in_kind_value": 0,
            "recognition_multiplier": 1.0,
        }
        new_df = pd.concat([base_df, pd.DataFrame([new_row])], ignore_index=True)
        scenario_inputs = {**inputs, "esd_contributions": new_df}
        scenario_results = _score_all(scenario_inputs, scorecard)
        gained = _delta_points(baseline_total, scenario_results)
        if gained <= 0:
            continue
        out.append(Action(
            description=f"Add R{increment:,.0f} of {label} contribution",
            element="enterprise_supplier_dev",
            rand_required=float(increment),
            points_gained=gained,
            rand_per_point=round(increment / gained, 2),
            reason=f"Increases {label.lower()}_spend_npat_pct",
        ))
    return out


def _sed_action(
    inputs: dict, scorecard: Scorecard, baseline_total: float,
) -> list[Action]:
    """Add R50k to an SED contribution to a >=75% black beneficiary."""
    base = inputs.get("sed_contributions")
    base_df = base.copy() if base is not None and not base.empty else pd.DataFrame()
    new_row = {
        "beneficiary_name": "Synthetic SED top-up",
        "black_beneficiary_pct": 100,
        "cash_value": _SED_INCREMENT,
        "in_kind_value": 0,
    }
    new_df = pd.concat([base_df, pd.DataFrame([new_row])], ignore_index=True)
    scenario_inputs = {**inputs, "sed_contributions": new_df}
    scenario_results = _score_all(scenario_inputs, scorecard)
    gained = _delta_points(0, scenario_results)
    # Compare to baseline
    gained = round(_total_score(scenario_results) - baseline_total, 4)
    if gained <= 0:
        return []
    return [Action(
        description=f"Add R{_SED_INCREMENT:,.0f} of SED contribution to a "
                    f"100% black beneficiary",
        element="socio_economic_dev",
        rand_required=float(_SED_INCREMENT),
        points_gained=gained,
        rand_per_point=round(_SED_INCREMENT / gained, 2),
        reason="Increases sed_spend_npat_pct",
    )]


def enumerate_financial_actions(
    inputs: dict, scorecard: Scorecard, baseline_results: list[ElementResult],
) -> list[Action]:
    baseline_total = _total_score(baseline_results)
    actions: list[Action] = []
    actions.extend(_procurement_actions(inputs, scorecard, baseline_total))
    actions.extend(_skills_action(inputs, scorecard, baseline_total))
    actions.extend(_esd_actions(inputs, scorecard, baseline_total))
    actions.extend(_sed_action(inputs, scorecard, baseline_total))
    return actions
