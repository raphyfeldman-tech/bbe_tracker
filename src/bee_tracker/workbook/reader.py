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
