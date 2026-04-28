from __future__ import annotations
from pathlib import Path
from openpyxl import load_workbook
import pandas as pd
import pytest
from bee_tracker.workbook.reader import read_ownership


FIXTURE = Path("tests/fixtures/sample_workbook.xlsx")


def _seed_ownership(tmp_path: Path) -> Path:
    import shutil
    out = tmp_path / "BEE_Tracker.xlsx"
    shutil.copy(FIXTURE, out)
    wb = load_workbook(out)
    ws = wb["Ownership"]
    ws.append([
        "Shareholder A", 30.0, 30.0, 15.0, 15.0, 5.0, 25.0, 0.0, "2025-10-01", "EV-0001"
    ])
    ws.append([
        "Shareholder B", 10.0, 10.0,  0.0,  0.0, 0.0, 10.0, 0.0, "2025-10-01", "EV-0001"
    ])
    wb.save(out)
    return out


def test_read_ownership_returns_dataframe(tmp_path: Path):
    path = _seed_ownership(tmp_path)
    wb = load_workbook(path)
    df = read_ownership(wb)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == [
        "shareholder_name",
        "black_voting_rights_pct",
        "black_economic_interest_pct",
        "black_women_voting_rights_pct",
        "black_women_economic_interest_pct",
        "black_designated_groups_pct",
        "net_value_pct",
        "new_entrants_pct",
        "effective_date",
        "evidence_id",
    ]
    assert df.iloc[0]["shareholder_name"] == "Shareholder A"
    assert df.iloc[0]["black_voting_rights_pct"] == 30.0


def test_read_ownership_empty_returns_empty_df():
    wb = load_workbook(FIXTURE)
    df = read_ownership(wb)
    assert df.empty
    assert "shareholder_name" in df.columns
