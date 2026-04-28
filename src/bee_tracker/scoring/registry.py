from __future__ import annotations
from .base import ElementScorer
from .ownership import OwnershipScorer


def default_registry() -> dict[str, ElementScorer]:
    """Plan 1 only registers Ownership. Plan 2 adds the remaining elements."""
    return {
        "ownership": OwnershipScorer(),
    }
