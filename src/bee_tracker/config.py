from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any
import yaml
from .errors import ConfigError


@dataclass(frozen=True)
class Period:
    start: date
    end: date


@dataclass(frozen=True)
class IndicatorTarget:
    target_pct: float
    weighting: float


@dataclass(frozen=True)
class ElementConfig:
    total_points: float
    priority: bool
    sub_minimum_pct: float | None
    indicators: dict[str, IndicatorTarget]


@dataclass(frozen=True)
class Scorecard:
    version: str
    level_thresholds: dict[int | str, float]
    elements: dict[str, ElementConfig]
    recognition_levels: dict[int | str, float]


@dataclass(frozen=True)
class GroupSettings:
    entity_name: str
    sharepoint_folder_id: str
    measurement_period: Period
    prior_period: Period
    financials: dict[str, float | None]
    scorecard_applied: str
    yes_participating: bool
    alerts: dict[str, list[str]]
    branding_folder: str
    calc_sheet_protection_password: str | None


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")
    with path.open() as f:
        return yaml.safe_load(f)


def load_scorecard(path: Path) -> Scorecard:
    data = _read_yaml(path)
    try:
        elements = {
            name: ElementConfig(
                total_points=e["total_points"],
                priority=e.get("priority", False),
                sub_minimum_pct=e.get("sub_minimum_pct"),
                indicators={
                    ind_name: IndicatorTarget(**ind)
                    for ind_name, ind in e.get("indicators", {}).items()
                },
            )
            for name, e in data["elements"].items()
        }
        return Scorecard(
            version=data["version"],
            level_thresholds=data["level_thresholds"],
            elements=elements,
            recognition_levels=data["recognition_levels"],
        )
    except KeyError as e:
        raise ConfigError(f"Missing key in scorecard YAML {path}: {e}") from e


def load_group_settings(path: Path) -> GroupSettings:
    data = _read_yaml(path)
    required = [
        "entity_name",
        "sharepoint_folder_id",
        "measurement_period",
        "prior_period",
        "financials",
        "scorecard_applied",
        "yes_participating",
    ]
    missing = [k for k in required if k not in data]
    if missing:
        raise ConfigError(
            f"Missing required keys in group settings YAML {path}: {', '.join(missing)}"
        )
    try:
        return GroupSettings(
            entity_name=data["entity_name"],
            sharepoint_folder_id=data["sharepoint_folder_id"],
            measurement_period=Period(**data["measurement_period"]),
            prior_period=Period(**data["prior_period"]),
            financials=data["financials"],
            scorecard_applied=data["scorecard_applied"],
            yes_participating=data["yes_participating"],
            alerts=data.get("alerts", {}),
            branding_folder=data.get("branding", {}).get("folder", "./branding"),
            calc_sheet_protection_password=data.get("calc_sheet_protection_password"),
        )
    except KeyError as e:
        raise ConfigError(f"Missing key in group settings YAML {path}: {e}") from e
