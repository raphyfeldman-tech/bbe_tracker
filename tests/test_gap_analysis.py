from __future__ import annotations
from pathlib import Path
import pandas as pd
import pytest
from bee_tracker.config import load_scorecard
from bee_tracker.scoring.registry import default_registry
from bee_tracker.gap_analysis.financial import (
    enumerate_financial_actions, Action,
)
from bee_tracker.gap_analysis.non_financial import (
    enumerate_non_financial_opportunities, Opportunity,
)
from bee_tracker.gap_analysis.ranker import rank_top_n


@pytest.fixture(scope="module")
def scorecard():
    return load_scorecard(Path("tests/fixtures/sample_ict_scorecard.yaml"))


def _baseline_inputs():
    return {
        "ownership": pd.DataFrame([
            {"shareholder_name": "A",
             "black_voting_rights_pct": 10, "black_economic_interest_pct": 10,
             "black_women_voting_rights_pct": 5, "black_women_economic_interest_pct": 5,
             "black_designated_groups_pct": 1,
             "net_value_pct": 5, "new_entrants_pct": 0},
        ]),
        "employees": pd.DataFrame([
            {"employee_id": "E1", "is_black": True,
             "occupational_level": "Senior Mgmt", "is_executive_director": False,
             "fte_months_in_period": 12},
            {"employee_id": "E2", "is_black": False,
             "occupational_level": "Senior Mgmt", "is_executive_director": False,
             "fte_months_in_period": 12},
        ]),
        "training": pd.DataFrame(),
        "learnerships": pd.DataFrame(),
        "bursaries": pd.DataFrame(),
        "suppliers": pd.DataFrame([
            {"supplier_id": "S1", "supplier_name": "L4 Sup", "cert_level": 4,
             "cert_type": "Generic", "is_51pct_black_owned": False,
             "is_30pct_black_women_owned": False, "is_emp_qse_51pct_black": False},
        ]),
        "procurement": pd.DataFrame([
            {"supplier_id": "S1", "period_spend_ex_vat": 1_000_000,
             "period_excluded_spend": 0},
        ]),
        "esd_contributions": pd.DataFrame(),
        "sed_contributions": pd.DataFrame(),
        "settings": {"npat_current": 5_000_000, "leviable_payroll": 10_000_000},
    }


def _baseline_results(inputs, scorecard):
    return [s.score(inputs, scorecard) for s in default_registry().values()]


def test_financial_actions_include_procurement_shift(scorecard):
    inputs = _baseline_inputs()
    baseline = _baseline_results(inputs, scorecard)
    actions = enumerate_financial_actions(inputs, scorecard, baseline)
    procurement_actions = [a for a in actions if "Level 1" in a.description]
    assert procurement_actions, "expected at least one procurement-shift action"


def test_financial_actions_include_skills_topup(scorecard):
    inputs = _baseline_inputs()
    baseline = _baseline_results(inputs, scorecard)
    actions = enumerate_financial_actions(inputs, scorecard, baseline)
    skills_actions = [a for a in actions if "training spend" in a.description]
    assert skills_actions, "expected a skills training-spend action"
    assert all(a.points_gained > 0 for a in skills_actions)


def test_financial_actions_include_ed_sd(scorecard):
    inputs = _baseline_inputs()
    baseline = _baseline_results(inputs, scorecard)
    actions = enumerate_financial_actions(inputs, scorecard, baseline)
    ed_sd = [a for a in actions if "ED contribution" in a.description
             or "SD contribution" in a.description]
    assert len(ed_sd) >= 2


def test_financial_actions_include_sed(scorecard):
    inputs = _baseline_inputs()
    baseline = _baseline_results(inputs, scorecard)
    actions = enumerate_financial_actions(inputs, scorecard, baseline)
    sed = [a for a in actions if "SED contribution" in a.description]
    assert len(sed) == 1
    assert sed[0].points_gained > 0


def test_non_financial_opportunities_include_headcount(scorecard):
    inputs = _baseline_inputs()
    baseline = _baseline_results(inputs, scorecard)
    opps = enumerate_non_financial_opportunities(inputs, scorecard, baseline)
    headcount = [o for o in opps if "Senior Mgmt" in o.description
                 or "Middle Mgmt" in o.description
                 or "Junior Mgmt" in o.description]
    assert headcount, "expected at least one headcount opportunity"


def test_non_financial_opportunities_include_ownership(scorecard):
    inputs = _baseline_inputs()
    baseline = _baseline_results(inputs, scorecard)
    opps = enumerate_non_financial_opportunities(inputs, scorecard, baseline)
    own = [o for o in opps if o.element == "ownership"]
    assert own, "expected an ownership opportunity (net_value below target)"


def test_rank_top_n_orders_by_rand_per_point():
    actions = [
        Action("a-expensive", "x", 1000, 0.5, 2000.0, ""),
        Action("b-cheap", "y", 100, 0.5, 200.0, ""),
        Action("c-medium", "z", 500, 0.5, 1000.0, ""),
        Action("zero", "z", 100, 0.0, float("inf"), ""),  # excluded
    ]
    top = rank_top_n(actions, n=2)
    assert [a.description for a in top] == ["b-cheap", "c-medium"]


def test_rank_top_n_drops_zero_or_negative_points():
    actions = [
        Action("good", "x", 100, 1.0, 100.0, ""),
        Action("zero", "x", 100, 0.0, float("inf"), ""),
    ]
    assert [a.description for a in rank_top_n(actions, n=10)] == ["good"]
