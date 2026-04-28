from __future__ import annotations
from pathlib import Path
from openpyxl import load_workbook
import shutil
from bee_tracker.scoring.base import ElementResult
from bee_tracker.workbook.writer import write_calc_ownership


FIXTURE = Path("tests/fixtures/sample_workbook.xlsx")


def test_write_calc_ownership_populates_sheet(tmp_path: Path):
    out = tmp_path / "wb.xlsx"
    shutil.copy(FIXTURE, out)
    wb = load_workbook(out)

    result = ElementResult(
        element="ownership",
        indicator_points={
            "black_voting_rights": 4.0,
            "net_value": 8.0,
        },
        subtotal=12.0,
        max_points=25.0,
        sub_minimum_breach=False,
    )
    write_calc_ownership(wb, result)
    wb.save(out)

    reopened = load_workbook(out)
    ws = reopened["Calc_Ownership"]
    # Row 1 = headers
    assert [c.value for c in ws[1]] == [
        "indicator", "points_earned", "max_points_check"
    ]
    # Subsequent rows = indicator points
    indicator_rows = {ws.cell(row=r, column=1).value: ws.cell(row=r, column=2).value
                      for r in range(2, ws.max_row + 1)
                      if ws.cell(row=r, column=1).value and ws.cell(row=r, column=1).value != "SUBTOTAL"}
    assert indicator_rows["black_voting_rights"] == 4.0
    assert indicator_rows["net_value"] == 8.0

    # Summary rows at bottom
    bottom_values = {ws.cell(row=r, column=1).value: ws.cell(row=r, column=2).value
                     for r in range(2, ws.max_row + 1)}
    assert bottom_values["SUBTOTAL"] == 12.0
    assert bottom_values["MAX_POINTS"] == 25.0
    assert bottom_values["SUB_MINIMUM_BREACH"] in (False, "False", 0)
