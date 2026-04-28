from __future__ import annotations
from openpyxl import Workbook
import pandas as pd


def _read_table(wb: Workbook, sheet: str) -> pd.DataFrame:
    ws = wb[sheet]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return pd.DataFrame()
    headers = list(rows[0])
    data = [r for r in rows[1:] if any(cell is not None for cell in r)]
    return pd.DataFrame(data, columns=headers)


def read_ownership(wb: Workbook) -> pd.DataFrame:
    return _read_table(wb, "Ownership")
