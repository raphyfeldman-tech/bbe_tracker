from __future__ import annotations
from .base import ElementScorer
from .ownership import OwnershipScorer
from .management_control import MgmtControlScorer
from .skills_development import SkillsDevScorer


def default_registry() -> dict[str, ElementScorer]:
    return {
        "ownership": OwnershipScorer(),
        "management_control": MgmtControlScorer(),
        "skills_development": SkillsDevScorer(),
    }
