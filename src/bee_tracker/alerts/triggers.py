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
