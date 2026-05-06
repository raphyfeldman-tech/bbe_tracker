from __future__ import annotations
"""Alert trigger detectors — priority breach, level drop, cert expiry."""
from dataclasses import dataclass
from ..scoring.base import ElementResult


PRIORITY_ELEMENT_NAMES = frozenset({
    "ownership", "skills_development", "enterprise_supplier_dev",
})


@dataclass(frozen=True)
class Breach:
    element: str
    subtotal: float
    max_points: float


def detect_priority_breaches(
    element_results: list[ElementResult],
) -> list[Breach]:
    return [
        Breach(
            element=r.element,
            subtotal=r.subtotal,
            max_points=r.max_points,
        )
        for r in element_results
        if r.sub_minimum_breach and r.element in PRIORITY_ELEMENT_NAMES
    ]


_LEVEL_RANK = {
    1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8,
    "non_compliant": 99,
}


def detect_level_drop(current_level, prior_level) -> bool:
    """Return True if current_level is worse than prior_level."""
    return _LEVEL_RANK.get(current_level, 99) > _LEVEL_RANK.get(prior_level, 99)


from datetime import date, datetime
from enum import Enum
import pandas as pd


class Severity(Enum):
    RED = "red"
    AMBER = "amber"


@dataclass(frozen=True)
class CertExpiry:
    supplier_id: str
    supplier_name: str
    expiry_date: date
    days_until_expiry: int
    severity: Severity


def _parse_date(value) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def detect_cert_expiries(
    suppliers: pd.DataFrame,
    *,
    today: date,
    red_days: int = 30,
    amber_days: int = 60,
) -> list[CertExpiry]:
    if suppliers.empty or "cert_expiry_date" not in suppliers.columns:
        return []
    out: list[CertExpiry] = []
    for _, row in suppliers.iterrows():
        expiry = _parse_date(row.get("cert_expiry_date"))
        if expiry is None:
            continue
        days = (expiry - today).days
        if days < red_days:
            severity = Severity.RED
        elif days < amber_days:
            severity = Severity.AMBER
        else:
            continue
        out.append(CertExpiry(
            supplier_id=str(row.get("supplier_id") or ""),
            supplier_name=str(row.get("supplier_name") or ""),
            expiry_date=expiry,
            days_until_expiry=days,
            severity=severity,
        ))
    return out
