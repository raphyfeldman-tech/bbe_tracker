from __future__ import annotations
"""`bee-calculate-score --entity <name>` entry point."""
import argparse
import logging
from datetime import datetime
from pathlib import Path
from ..config import load_scorecard, load_group_settings
from ..workbook.backends import LocalFolderBackend
from ..workbook.reader import read_ownership, read_employees
from ..workbook.writer import write_calc_ownership, write_calc_mgmt_control
from ..rendering.dashboard import DashboardContext, render_dashboard
from ..scoring.registry import default_registry


log = logging.getLogger("bee_tracker.calculate_score")


def run_score(*, root: Path, entity_name: str, requested_by: str) -> None:
    scorecard = load_scorecard(root / "ict_scorecard.yaml")
    gs = load_group_settings(
        root / "entities" / entity_name / "group_settings.yaml"
    )

    backend = LocalFolderBackend(root)
    handle = backend.open_entity_workbook(entity_name)
    wb = handle.workbook

    inputs = {
        "ownership": read_ownership(wb),
        "employees": read_employees(wb),
    }
    registry = default_registry()
    results = []
    for element_name, scorer in registry.items():
        result = scorer.score(inputs, scorecard)
        results.append(result)
        if element_name == "ownership":
            write_calc_ownership(wb, result)
        elif element_name == "management_control":
            write_calc_mgmt_control(wb, result)

    ctx = DashboardContext(
        entity_name=gs.entity_name,
        measurement_period=(
            f"{gs.measurement_period.start.isoformat()} → "
            f"{gs.measurement_period.end.isoformat()}"
        ),
        last_run_at=datetime.utcnow(),
        last_run_by=requested_by,
        element_results=results,
    )
    render_dashboard(wb, ctx)

    backend.save(handle)
    log.info("Score run complete for entity=%s subtotals=%s", entity_name,
             {r.element: r.subtotal for r in results})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bee-calculate-score")
    parser.add_argument("--root", type=Path, required=True,
                        help="Root folder containing ict_scorecard.yaml and entities/")
    parser.add_argument("--entity", required=True,
                        help="Entity folder name under entities/")
    parser.add_argument("--requested-by", default="cli",
                        help="Identifier recorded on Dashboard and ChangeLog")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    run_score(root=args.root, entity_name=args.entity, requested_by=args.requested_by)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
