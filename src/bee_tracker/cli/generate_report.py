from __future__ import annotations
"""``bee-generate-report --entity <name>`` entry point."""
import argparse
import logging
from datetime import datetime
from pathlib import Path
from openpyxl import load_workbook
from ..config import load_group_settings, load_scorecard
from ..reporting.branding import load_branding
from ..reporting.pdf import render_pdf, ReportContext
from ..scoring.level import (
    total_score_to_level, level_after_priority_breaches,
)
from ..scoring.yes_initiative import calculate_yes_levels_up, apply_levels_up
from ..workbook.reader import (
    read_ownership, read_employees, read_training, read_learnerships,
    read_bursaries, read_suppliers, read_procurement,
    read_esd_contributions, read_sed_contributions, read_yes_initiative,
    read_settings,
)
from ..scoring.registry import default_registry


log = logging.getLogger("bee_tracker.generate_report")


PRIORITY_ELEMENT_NAMES = {
    "ownership", "skills_development", "enterprise_supplier_dev",
}


def run_generate_report(
    *,
    root: Path,
    entity_name: str,
    report_type: str,
    output: Path,
    templates_dir: Path,
) -> None:
    scorecard = load_scorecard(root / "ict_scorecard.yaml")
    gs = load_group_settings(
        root / "entities" / entity_name / "group_settings.yaml"
    )
    branding = load_branding(
        root / "entities" / entity_name / gs.branding_folder
    )

    wb_path = root / "entities" / entity_name / "BEE_Tracker.xlsx"
    wb = load_workbook(wb_path)

    inputs = {
        "ownership": read_ownership(wb),
        "employees": read_employees(wb),
        "training": read_training(wb),
        "learnerships": read_learnerships(wb),
        "bursaries": read_bursaries(wb),
        "suppliers": read_suppliers(wb),
        "procurement": read_procurement(wb),
        "esd_contributions": read_esd_contributions(wb),
        "sed_contributions": read_sed_contributions(wb),
        "settings": read_settings(wb),
    }
    results = [s.score(inputs, scorecard) for s in default_registry().values()]
    total_score = round(sum(r.subtotal for r in results), 4)
    breach_count = sum(
        1 for r in results
        if r.sub_minimum_breach and r.element in PRIORITY_ELEMENT_NAMES
    )
    base_level = level_after_priority_breaches(
        total_score, breach_count=breach_count, scorecard=scorecard,
    )

    yes_levels_up = 0
    if gs.yes_participating:
        yes_df = read_yes_initiative(wb)
        headcount = (
            len(inputs["employees"]) if not inputs["employees"].empty else 0
        )
        yes_levels_up = calculate_yes_levels_up(
            yes_initiative=yes_df, headcount=headcount, scorecard=scorecard,
        )
    bee_level = apply_levels_up(base_level, yes_levels_up)

    max_score = sum(r.max_points for r in results)

    ctx = ReportContext(
        entity_name=gs.entity_name,
        measurement_period=(
            f"{gs.measurement_period.start.isoformat()} → "
            f"{gs.measurement_period.end.isoformat()}"
        ),
        generated_at=datetime.utcnow(),
        total_score=total_score,
        max_score=max_score,
        bee_level=bee_level,
        yes_levels_up=yes_levels_up,
        elements=[
            {
                "name": r.element.replace("_", " ").title(),
                "subtotal": r.subtotal,
                "max_points": r.max_points,
                "sub_minimum_breach": r.sub_minimum_breach,
            }
            for r in results
        ],
        top_gaps=[],
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    render_pdf(ctx, branding, output, templates_dir=templates_dir)
    log.info("Wrote %s report to %s", report_type, output)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bee-generate-report")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--entity", required=True)
    parser.add_argument("--type", choices=["monthly", "quarterly", "adhoc"],
                        default="adhoc", dest="report_type")
    parser.add_argument("--output", type=Path, required=True,
                        help="Output PDF path")
    parser.add_argument("--templates", type=Path, default=Path("templates"),
                        dest="templates_dir")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    run_generate_report(
        root=args.root,
        entity_name=args.entity,
        report_type=args.report_type,
        output=args.output,
        templates_dir=args.templates_dir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
