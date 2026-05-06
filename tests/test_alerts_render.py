from __future__ import annotations
from datetime import date
from pathlib import Path
from bee_tracker.alerts.render import (
    render_priority_breach, render_cert_expiry, render_level_drop,
)
from bee_tracker.alerts.triggers import Breach, CertExpiry, Severity


TEMPLATES = Path("templates")


def test_render_priority_breach():
    breaches = [
        Breach(element="ownership", subtotal=5.0, max_points=25.0),
        Breach(element="skills_development", subtotal=4.0, max_points=15.0),
    ]
    body = render_priority_breach(
        entity_name="Sample Entity", breaches=breaches, templates_dir=TEMPLATES,
    )
    assert "Sample Entity" in body
    assert "ownership" in body.lower()
    assert "skills_development" in body or "Skills Development" in body
    assert "BREACH" in body.upper()


def test_render_cert_expiry():
    expiries = [
        CertExpiry(supplier_id="S1", supplier_name="Acme",
                   expiry_date=date(2026, 5, 20),
                   days_until_expiry=16, severity=Severity.RED),
    ]
    body = render_cert_expiry(
        entity_name="Sample", expiries=expiries, templates_dir=TEMPLATES,
    )
    assert "Acme" in body
    assert "16" in body or "2026-05-20" in body


def test_render_level_drop():
    body = render_level_drop(
        entity_name="Sample",
        prior_level=2, current_level=4, templates_dir=TEMPLATES,
    )
    assert "Sample" in body
    assert "2" in body
    assert "4" in body
