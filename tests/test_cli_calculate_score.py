from __future__ import annotations
from pathlib import Path
import shutil
from datetime import datetime
import pytest
from openpyxl import load_workbook
from bee_tracker.cli.calculate_score import run_score


FIXTURE = Path("tests/fixtures/sample_workbook.xlsx")
SCORECARD = Path("tests/fixtures/sample_ict_scorecard.yaml")
GROUP_SETTINGS = Path("tests/fixtures/sample_group_settings.yaml")


def _seed_entity(tmp_path: Path) -> Path:
    root = tmp_path / "bee_tracker"
    entity = root / "entities" / "sample"
    entity.mkdir(parents=True)
    shutil.copy(FIXTURE, entity / "BEE_Tracker.xlsx")
    shutil.copy(GROUP_SETTINGS, entity / "group_settings.yaml")
    shutil.copy(SCORECARD, root / "ict_scorecard.yaml")
    # seed ownership data
    wb = load_workbook(entity / "BEE_Tracker.xlsx")
    wb["Ownership"].append([
        "Shareholder A", 30.0, 30.0, 15.0, 15.0, 5.0, 25.0, 2.0, "2025-10-01", "EV-0001"
    ])
    wb.save(entity / "BEE_Tracker.xlsx")
    return root


def test_run_score_writes_calc_ownership_and_dashboard(tmp_path: Path):
    root = _seed_entity(tmp_path)
    run_score(root=root, entity_name="sample", requested_by="tester@example")
    wb = load_workbook(root / "entities" / "sample" / "BEE_Tracker.xlsx")

    # Calc_Ownership populated
    calc = wb["Calc_Ownership"]
    headers = [c.value for c in calc[1]]
    assert headers == ["indicator", "points_earned", "max_points_check"]
    assert calc.max_row > 3

    # Dashboard populated — iter_rows(values_only=True) yields tuples of values
    dash = wb["Dashboard"]
    text = "|".join(str(v) for row in dash.iter_rows(values_only=True)
                    for v in row if v is not None)
    assert "Sample Entity (Pty) Ltd" in text
    assert "Ownership" in text


def test_run_score_does_not_touch_ownership_input(tmp_path: Path):
    root = _seed_entity(tmp_path)
    wb_before = load_workbook(root / "entities" / "sample" / "BEE_Tracker.xlsx")
    before = [[c.value for c in row] for row in wb_before["Ownership"].iter_rows()]

    run_score(root=root, entity_name="sample", requested_by="tester@example")

    wb_after = load_workbook(root / "entities" / "sample" / "BEE_Tracker.xlsx")
    after = [[c.value for c in row] for row in wb_after["Ownership"].iter_rows()]
    assert before == after
