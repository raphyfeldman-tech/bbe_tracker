from __future__ import annotations
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


TEMPLATES = Path("templates")


def _render(context: dict) -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=True)
    return env.get_template("report.html.j2").render(**context)


def _basic_context() -> dict:
    return {
        "entity_name": "Sample Entity (Pty) Ltd",
        "measurement_period": "2025-10-01 → 2026-09-30",
        "generated_at": datetime(2026, 4, 30, 12, 0).isoformat(),
        "logo_uri": "file:///tmp/logo.png",
        "colours": {
            "primary": "#0A2540", "secondary": "#16A34A",
            "accent": "#F59E0B", "body_text": "#111827", "muted": "#6B7280",
        },
        "total_score": 72.5,
        "max_score": 105,
        "bee_level": 4,
        "yes_levels_up": 0,
        "elements": [
            {"name": "Ownership", "subtotal": 18.5, "max_points": 25,
             "sub_minimum_breach": False},
            {"name": "Skills Development", "subtotal": 4.0, "max_points": 15,
             "sub_minimum_breach": True},
        ],
        "top_gaps": [
            {"description": "Shift R840k to Level 1 supplier",
             "rand_required": 840000, "points_gained": 1.4,
             "rand_per_point": 600000},
        ],
    }


def test_template_includes_entity_and_period():
    html = _render(_basic_context())
    assert "Sample Entity (Pty) Ltd" in html
    assert "2025-10-01" in html


def test_template_includes_bee_level_and_total():
    html = _render(_basic_context())
    assert "Level 4" in html
    assert "72.5" in html
    assert "105" in html


def test_template_flags_breach_in_table():
    html = _render(_basic_context())
    assert "breach" in html.lower()
    assert "Skills Development" in html


def test_template_includes_top_gaps():
    html = _render(_basic_context())
    assert "Shift R840k to Level 1 supplier" in html
    assert "1.4" in html


def test_template_uses_brand_primary_colour():
    html = _render(_basic_context())
    assert "#0A2540" in html


def test_template_renders_yes_annotation_when_applied():
    ctx = _basic_context()
    ctx["yes_levels_up"] = 2
    html = _render(ctx)
    assert "Y.E.S." in html or "+2 levels" in html


def test_template_omits_yes_annotation_when_zero():
    html = _render(_basic_context())
    assert "+0 levels" not in html
