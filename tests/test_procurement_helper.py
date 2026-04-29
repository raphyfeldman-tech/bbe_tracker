from __future__ import annotations
from pathlib import Path
import pandas as pd
import pytest
from bee_tracker.config import load_scorecard
from bee_tracker.scoring.procurement import (
    total_measured_procurement_spend, recognised_spend_for_supplier,
)


@pytest.fixture(scope="module")
def scorecard():
    return load_scorecard(Path("tests/fixtures/sample_ict_scorecard.yaml"))


def test_tmps_excludes_period_excluded_spend():
    procurement = pd.DataFrame([
        {"supplier_id": "S1", "period_spend_ex_vat": 1000000, "period_excluded_spend": 200000},
        {"supplier_id": "S2", "period_spend_ex_vat": 500000,  "period_excluded_spend": 0},
    ])
    assert total_measured_procurement_spend(procurement) == 1300000


def test_tmps_empty_returns_zero():
    assert total_measured_procurement_spend(pd.DataFrame()) == 0.0


def test_tmps_handles_missing_excluded_column():
    procurement = pd.DataFrame([
        {"supplier_id": "S1", "period_spend_ex_vat": 1000000},
    ])
    assert total_measured_procurement_spend(procurement) == 1000000


def test_recognition_for_level_1_supplier(scorecard):
    spend = recognised_spend_for_supplier(
        measured_spend=1000000, cert_level=1, scorecard=scorecard,
    )
    assert spend == 1350000


def test_recognition_for_level_4_supplier(scorecard):
    spend = recognised_spend_for_supplier(
        measured_spend=1000000, cert_level=4, scorecard=scorecard,
    )
    assert spend == 1000000


def test_recognition_for_non_compliant(scorecard):
    spend = recognised_spend_for_supplier(
        measured_spend=1000000, cert_level="non_compliant", scorecard=scorecard,
    )
    assert spend == 0.0


def test_recognition_for_unknown_cert_level_returns_zero(scorecard):
    spend = recognised_spend_for_supplier(
        measured_spend=1000000, cert_level=None, scorecard=scorecard,
    )
    assert spend == 0.0
