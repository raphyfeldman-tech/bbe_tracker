from __future__ import annotations
"""Top-N action ranker."""
from .financial import Action


def rank_top_n(actions: list[Action], n: int = 10) -> list[Action]:
    """Return the top-N financial actions by lowest R/point.

    Drops actions with `points_gained <= 0`. Ties broken by description.
    """
    eligible = [a for a in actions if a.points_gained > 0]
    return sorted(eligible, key=lambda a: (a.rand_per_point, a.description))[:n]
