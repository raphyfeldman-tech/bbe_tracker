from __future__ import annotations
"""Per-entity branding loader.

Each entity has a ``branding/`` folder with:
  - logo.png (required)
  - colours.yaml (optional; defaults applied if missing)
  - font.ttf (optional)

The PDF report renderer pulls these into the Jinja template.
"""
from dataclasses import dataclass
from pathlib import Path
import yaml


_DEFAULT_COLOURS = {
    "primary":   "#0A2540",
    "secondary": "#16A34A",
    "accent":    "#F59E0B",
    "body_text": "#111827",
    "muted":     "#6B7280",
}


@dataclass(frozen=True)
class Branding:
    logo_path: Path
    colours: dict[str, str]
    font_path: Path | None = None


def load_branding(folder: Path) -> Branding:
    folder = Path(folder)
    if not folder.exists():
        raise FileNotFoundError(f"branding folder not found: {folder}")

    logo = folder / "logo.png"
    if not logo.exists():
        raise FileNotFoundError(f"branding logo missing: {logo}")

    colours_yaml = folder / "colours.yaml"
    if colours_yaml.exists():
        loaded = yaml.safe_load(colours_yaml.read_text()) or {}
        colours = {**_DEFAULT_COLOURS, **loaded}
    else:
        colours = dict(_DEFAULT_COLOURS)

    font = folder / "font.ttf"
    return Branding(
        logo_path=logo,
        colours=colours,
        font_path=font if font.exists() else None,
    )
