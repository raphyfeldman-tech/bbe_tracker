from __future__ import annotations
"""PDF report renderer using Jinja + WeasyPrint."""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from .branding import Branding


@dataclass(frozen=True)
class ReportContext:
    entity_name: str
    measurement_period: str
    generated_at: datetime
    total_score: float
    max_score: float
    bee_level: int | str
    yes_levels_up: int = 0
    elements: list[dict] = field(default_factory=list)
    top_gaps: list[dict] = field(default_factory=list)


def render_pdf(
    ctx: ReportContext,
    branding: Branding,
    output_path: Path,
    *,
    templates_dir: Path,
) -> None:
    """Render the PDF report to ``output_path``."""
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=True,
    )
    template = env.get_template("report.html.j2")
    html = template.render(
        entity_name=ctx.entity_name,
        measurement_period=ctx.measurement_period,
        generated_at=ctx.generated_at.isoformat(timespec="seconds"),
        logo_uri=branding.logo_path.resolve().as_uri(),
        colours=branding.colours,
        total_score=ctx.total_score,
        max_score=ctx.max_score,
        bee_level=ctx.bee_level,
        yes_levels_up=ctx.yes_levels_up,
        elements=ctx.elements,
        top_gaps=ctx.top_gaps,
    )

    # Lazy import — keeps the module loadable on systems without Cairo/Pango.
    from weasyprint import HTML
    HTML(string=html, base_url=str(templates_dir.resolve())).write_pdf(
        target=str(output_path),
    )
