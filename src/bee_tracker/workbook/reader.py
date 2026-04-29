from __future__ import annotations
from openpyxl import Workbook
import pandas as pd


def read_table(wb: Workbook, sheet: str) -> pd.DataFrame:
    """Read a sheet's used range into a DataFrame.

    Headers come from row 1. Trailing fully-blank rows are dropped. Empty
    sheets that have only a header row return a 0-row DataFrame with named
    columns.
    """
    ws = wb[sheet]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return pd.DataFrame()
    headers = list(rows[0])
    data = [r for r in rows[1:] if any(cell is not None for cell in r)]
    return pd.DataFrame(data, columns=headers)


def read_ownership(wb: Workbook) -> pd.DataFrame:
    return read_table(wb, "Ownership")


def read_employees(wb: Workbook) -> pd.DataFrame:
    return read_table(wb, "Employees")


def read_training(wb: Workbook) -> pd.DataFrame:
    return read_table(wb, "Training")


def read_learnerships(wb: Workbook) -> pd.DataFrame:
    return read_table(wb, "Learnerships")


def read_bursaries(wb: Workbook) -> pd.DataFrame:
    return read_table(wb, "Bursaries")


def read_suppliers(wb: Workbook) -> pd.DataFrame:
    return read_table(wb, "Suppliers")


def read_procurement(wb: Workbook) -> pd.DataFrame:
    return read_table(wb, "Procurement")


def read_esd_contributions(wb: Workbook) -> pd.DataFrame:
    return read_table(wb, "ESD_Contributions")


def read_sed_contributions(wb: Workbook) -> pd.DataFrame:
    return read_table(wb, "SED_Contributions")


def read_yes_initiative(wb: Workbook) -> pd.DataFrame:
    return read_table(wb, "YES_Initiative")


def read_whatif(wb: Workbook) -> pd.DataFrame:
    return read_table(wb, "WhatIf")


def read_settings(wb: Workbook) -> dict[str, object]:
    """Settings is a 2-column key/value sheet. Returns a dict.

    The Settings sheet has headers `key` and `value` (per the workbook
    template). Empty Settings (no rows beyond the header) returns {}.
    """
    df = read_table(wb, "Settings")
    if df.empty or "key" not in df.columns:
        return {}
    return dict(zip(df["key"], df["value"]))
