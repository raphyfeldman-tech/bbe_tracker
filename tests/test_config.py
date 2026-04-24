from __future__ import annotations
from pathlib import Path
import pytest
from bee_tracker.config import load_scorecard, load_group_settings, GroupSettings, Scorecard
from bee_tracker.errors import ConfigError

FIX = Path(__file__).parent / "fixtures"


def test_load_scorecard_returns_versioned_scorecard():
    sc = load_scorecard(FIX / "sample_ict_scorecard.yaml")
    assert isinstance(sc, Scorecard)
    assert sc.version == "ICT-2022-amended"
    assert sc.level_thresholds[1] == 100
    assert "ownership" in sc.elements


def test_load_scorecard_missing_file_raises():
    with pytest.raises(ConfigError, match="not found"):
        load_scorecard(FIX / "nope.yaml")


def test_load_group_settings_returns_entity():
    gs = load_group_settings(FIX / "sample_group_settings.yaml")
    assert isinstance(gs, GroupSettings)
    assert gs.entity_name == "Sample Entity (Pty) Ltd"
    assert gs.measurement_period.start.year == 2025
    assert gs.scorecard_applied == "ICT_GENERIC"


def test_load_group_settings_missing_required_field_raises():
    bad = FIX / "broken_group_settings.yaml"
    bad.write_text("entity_name: Only Field\n")
    try:
        with pytest.raises(ConfigError, match="measurement_period"):
            load_group_settings(bad)
    finally:
        bad.unlink()
