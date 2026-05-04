from __future__ import annotations
from pathlib import Path
import shutil
import pytest
from bee_tracker.reporting.branding import load_branding, Branding


FIX = Path("tests/fixtures/sample_branding")


def _make_branding(tmp_path: Path) -> Path:
    folder = tmp_path / "branding"
    folder.mkdir()
    shutil.copy(FIX / "colours.yaml", folder / "colours.yaml")
    shutil.copy(FIX / "logo.png", folder / "logo.png")
    return folder


def test_load_branding_with_logo_and_colours(tmp_path):
    folder = _make_branding(tmp_path)
    branding = load_branding(folder)
    assert isinstance(branding, Branding)
    assert branding.logo_path == folder / "logo.png"
    assert branding.colours["primary"] == "#0A2540"
    assert branding.font_path is None  # no font.ttf in fixture


def test_load_branding_with_optional_font(tmp_path):
    folder = _make_branding(tmp_path)
    (folder / "font.ttf").write_bytes(b"\x00")  # stub font file
    branding = load_branding(folder)
    assert branding.font_path == folder / "font.ttf"


def test_load_branding_missing_folder_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="branding folder not found"):
        load_branding(tmp_path / "no_such_folder")


def test_load_branding_missing_colours_uses_defaults(tmp_path):
    folder = tmp_path / "branding"
    folder.mkdir()
    shutil.copy(FIX / "logo.png", folder / "logo.png")
    branding = load_branding(folder)
    assert "primary" in branding.colours
