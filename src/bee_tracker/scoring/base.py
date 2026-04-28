from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import pandas as pd
from ..config import Scorecard


@dataclass(frozen=True)
class ElementResult:
    element: str
    indicator_points: dict[str, float]
    subtotal: float
    max_points: float
    sub_minimum_breach: bool
    notes: list[str] = field(default_factory=list)


class ElementScorer(ABC):
    """Each element of the scorecard implements this interface."""

    element_name: str  # e.g. "ownership"

    @abstractmethod
    def score(self, inputs: dict, scorecard: Scorecard) -> ElementResult: ...
