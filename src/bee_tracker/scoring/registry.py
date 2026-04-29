from __future__ import annotations
from .base import ElementScorer
from .ownership import OwnershipScorer
from .management_control import MgmtControlScorer


def default_registry() -> dict[str, ElementScorer]:
    """Plan 1 + Plan 2 progress: Ownership and Management Control. Plan 2 will register more."""
    return {
        "ownership": OwnershipScorer(),
        "management_control": MgmtControlScorer(),
    }
