from __future__ import annotations
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from .rules import Finding, Severity


def render_html(findings: list[Finding], template_dir: Path) -> str:
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=True,
    )
    tmpl = env.get_template("validation_report.html.j2")
    counts = {
        "error": sum(1 for f in findings if f.severity is Severity.ERROR),
        "warning": sum(1 for f in findings if f.severity is Severity.WARNING),
        "info": sum(1 for f in findings if f.severity is Severity.INFO),
    }
    return tmpl.render(findings=findings, counts=counts)
