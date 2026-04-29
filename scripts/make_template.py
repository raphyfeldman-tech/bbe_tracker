from __future__ import annotations
"""Regenerate templates/workbook_template.xlsx from scratch.

Run: python scripts/make_template.py
"""
from datetime import datetime
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from bee_tracker.workbook.schema import SHEETS, TAB_COLOURS


def _write_sheet(ws: Worksheet, tab_colour_key: str, headers: list[str]) -> None:
    ws.sheet_properties.tabColor = TAB_COLOURS[tab_colour_key]
    if headers:
        for col, h in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col, value=h)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(
                start_color="E7E6E6", end_color="E7E6E6", fill_type="solid"
            )
        ws.freeze_panes = "A2"


def build_template(out: Path) -> None:
    wb = Workbook()
    # Pin timestamps so successive regenerations are byte-identical.
    # Without this, openpyxl stamps wall-clock time into docProps/core.xml
    # and the committed binary churns every time anyone runs this script.
    pinned = datetime(2026, 1, 1)
    wb.properties.created = pinned
    wb.properties.modified = pinned
    # openpyxl creates a default sheet; delete it
    default = wb.active
    wb.remove(default)
    for name, colour, headers in SHEETS:
        ws = wb.create_sheet(name)
        _write_sheet(ws, colour, headers)
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)


if __name__ == "__main__":
    target = Path("templates/workbook_template.xlsx")
    build_template(target)
    print(f"Wrote {target}")
