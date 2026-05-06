from __future__ import annotations
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from .triggers import Breach, CertExpiry


def _env(templates_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=True,
    )


def render_priority_breach(
    *, entity_name: str, breaches: list[Breach], templates_dir: Path,
) -> str:
    return _env(templates_dir).get_template("alert_email.html.j2").render(
        kind="priority_breach", entity_name=entity_name, breaches=breaches,
    )


def render_cert_expiry(
    *, entity_name: str, expiries: list[CertExpiry], templates_dir: Path,
) -> str:
    return _env(templates_dir).get_template("alert_email.html.j2").render(
        kind="cert_expiry", entity_name=entity_name, expiries=expiries,
    )


def render_level_drop(
    *, entity_name: str, prior_level, current_level, templates_dir: Path,
) -> str:
    return _env(templates_dir).get_template("alert_email.html.j2").render(
        kind="level_drop", entity_name=entity_name,
        prior_level=prior_level, current_level=current_level,
    )
