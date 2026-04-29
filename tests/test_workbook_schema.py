from __future__ import annotations
from bee_tracker.workbook.schema import SHEETS, EXPECTED_SHEET_NAMES, headers_for


def test_sheets_table_has_27_entries():
    assert len(SHEETS) == 27


def test_expected_sheet_names_in_order():
    assert EXPECTED_SHEET_NAMES[0] == "Dashboard"
    assert EXPECTED_SHEET_NAMES[-1] == "RunQueue"
    assert "Evidence" in EXPECTED_SHEET_NAMES


def test_headers_for_ownership():
    assert headers_for("Ownership")[0] == "shareholder_name"


def test_headers_for_unknown_sheet_returns_empty():
    assert headers_for("Nonexistent") == []
