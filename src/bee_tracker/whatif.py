from __future__ import annotations
"""WhatIf override application — turn a key/value DataFrame into an overridden inputs dict."""
import pandas as pd


def _shallow_copy_inputs(inputs: dict) -> dict:
    """Shallow-copy at the top level, deep-copy DataFrames so mutations stay local."""
    out: dict = {}
    for k, v in inputs.items():
        if isinstance(v, pd.DataFrame):
            out[k] = v.copy()
        elif isinstance(v, dict):
            out[k] = dict(v)
        else:
            out[k] = v
    return out


def apply_overrides(inputs: dict, overrides: pd.DataFrame) -> dict:
    """Return a new inputs dict with WhatIf overrides applied.

    `overrides` is a 2-col DataFrame with `key` and `value` columns. Keys are
    dotted paths:
      - settings.<k>
      - ownership.<column>
      - procurement.<supplier_id>.<column>

    Empty / NaN values, blank keys, and unknown paths are silently skipped.
    The baseline `inputs` is never mutated.
    """
    if overrides.empty or "key" not in overrides.columns:
        return inputs

    new = _shallow_copy_inputs(inputs)

    for _, row in overrides.iterrows():
        raw_key = row.get("key")
        if raw_key is None or (isinstance(raw_key, float) and pd.isna(raw_key)):
            continue
        key = str(raw_key).strip()
        if not key:
            continue
        value = row.get("value")
        if value is None or (isinstance(value, float) and pd.isna(value)):
            continue
        # pd.NA does not pass the float-NaN check above; handle generically:
        try:
            if pd.isna(value):
                continue
        except (TypeError, ValueError):
            pass

        parts = key.split(".")
        if parts[0] == "settings" and len(parts) == 2:
            new["settings"] = {**new.get("settings", {}), parts[1]: value}
        elif parts[0] == "ownership" and len(parts) == 2:
            df = new.get("ownership")
            if df is not None and not df.empty and parts[1] in df.columns:
                df = df.copy()
                df[parts[1]] = value
                new["ownership"] = df
        elif parts[0] == "procurement" and len(parts) == 3:
            df = new.get("procurement")
            if df is not None and not df.empty and "supplier_id" in df.columns:
                df = df.copy()
                df.loc[df["supplier_id"] == parts[1], parts[2]] = value
                new["procurement"] = df
    return new
