from __future__ import annotations
from pathlib import Path
import shutil
from datetime import datetime
import pytest


FIX_BRANDING = Path("tests/fixtures/sample_branding")

# Skip the whole module if WeasyPrint can't import (no Cairo/Pango on this machine)
pytest.importorskip("weasyprint", reason="WeasyPrint requires Cairo/Pango system libraries")


def _branding(tmp_path):
    from bee_tracker.reporting.branding import load_branding
    folder = tmp_path / "branding"
    folder.mkdir()
    shutil.copy(FIX_BRANDING / "colours.yaml", folder / "colours.yaml")
    shutil.copy(FIX_BRANDING / "logo.png", folder / "logo.png")
    return load_branding(folder)


def _ctx():
    from bee_tracker.reporting.pdf import ReportContext
    return ReportContext(
        entity_name="Sample Entity",
        measurement_period="2025-10-01 → 2026-09-30",
        generated_at=datetime(2026, 4, 30, 12, 0),
        total_score=72.5,
        max_score=105,
        bee_level=4,
        yes_levels_up=0,
        elements=[
            {"name": "Ownership", "subtotal": 18.5, "max_points": 25,
             "sub_minimum_breach": False},
        ],
        top_gaps=[],
    )


def test_render_pdf_writes_pdf_file(tmp_path):
    from bee_tracker.reporting.pdf import render_pdf
    branding = _branding(tmp_path)
    out = tmp_path / "report.pdf"
    render_pdf(_ctx(), branding, out, templates_dir=Path("templates"))
    assert out.exists()
    assert out.read_bytes()[:4] == b"%PDF"


def test_render_pdf_writes_a4(tmp_path):
    from bee_tracker.reporting.pdf import render_pdf
    branding = _branding(tmp_path)
    out = tmp_path / "report.pdf"
    render_pdf(_ctx(), branding, out, templates_dir=Path("templates"))
    assert out.stat().st_size > 3000
