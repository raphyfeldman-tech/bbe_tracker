from __future__ import annotations
"""`bee-calculate-score --entity <name>` entry point."""
import argparse
import logging
from datetime import datetime
from pathlib import Path
from ..config import load_scorecard, load_group_settings
from ..workbook.backends import LocalFolderBackend
from ..workbook.reader import (
    read_ownership, read_employees, read_training,
    read_learnerships, read_bursaries, read_settings,
    read_suppliers, read_procurement, read_esd_contributions,
    read_sed_contributions, read_whatif,
)
from ..workbook.writer import (
    write_calc_ownership, write_calc_mgmt_control, write_calc_skills_dev,
    write_calc_esd, write_calc_sed, write_calc_whatif,
)
from ..rendering.dashboard import DashboardContext, render_dashboard
from ..scoring.registry import default_registry
from ..scoring.level import total_score_to_level
from ..gap_analysis.financial import enumerate_financial_actions
from ..gap_analysis.ranker import rank_top_n
from ..whatif import apply_overrides


log = logging.getLogger("bee_tracker.calculate_score")


def run_score(*, root: Path, entity_name: str, requested_by: str,
              whatif: bool = False) -> None:
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
        "training": read_training(wb),
        "learnerships": read_learnerships(wb),
        "bursaries": read_bursaries(wb),
        "suppliers": read_suppliers(wb),
        "procurement": read_procurement(wb),
        "esd_contributions": read_esd_contributions(wb),
        "sed_contributions": read_sed_contributions(wb),
        "settings": read_settings(wb),
    }
    registry = default_registry()
    baseline_results = []
    for element_name, scorer in registry.items():
        result = scorer.score(inputs, scorecard)
        baseline_results.append(result)
        if element_name == "ownership":
            write_calc_ownership(wb, result)
        elif element_name == "management_control":
            write_calc_mgmt_control(wb, result)
        elif element_name == "skills_development":
            write_calc_skills_dev(wb, result)
        elif element_name == "enterprise_supplier_dev":
            write_calc_esd(wb, result)
        elif element_name == "socio_economic_dev":
            write_calc_sed(wb, result)

    scenario_results = None
    if whatif:
        whatif_df = read_whatif(wb)
        scenario_inputs = apply_overrides(inputs, whatif_df)
        scenario_results = []
        for element_name, scorer in registry.items():
            scenario_results.append(scorer.score(scenario_inputs, scorecard))
        write_calc_whatif(wb, scenario_results)

    total_score = round(sum(r.subtotal for r in baseline_results), 4)
    bee_level = total_score_to_level(total_score, scorecard)

    # Top gaps
    financial_actions = enumerate_financial_actions(inputs, scorecard, baseline_results)
    top5 = rank_top_n(financial_actions, n=5)
    top_gaps = [
        {
            "description": a.description,
            "element": a.element,
            "rand_required": a.rand_required,
            "points_gained": a.points_gained,
            "rand_per_point": a.rand_per_point,
        }
        for a in top5
    ]

    ctx = DashboardContext(
        entity_name=gs.entity_name,
        measurement_period=(
            f"{gs.measurement_period.start.isoformat()} → "
            f"{gs.measurement_period.end.isoformat()}"
        ),
        last_run_at=datetime.utcnow(),
        last_run_by=requested_by,
        element_results=baseline_results,
        bee_level=bee_level,
        scenario_element_results=scenario_results,
        top_gaps=top_gaps,
    )
    render_dashboard(wb, ctx)

    backend.save(handle)
    log.info("Score run complete for entity=%s subtotals=%s", entity_name,
             {r.element: r.subtotal for r in baseline_results})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bee-calculate-score")
    parser.add_argument("--root", type=Path, required=True,
                        help="Root folder containing ict_scorecard.yaml and entities/")
    parser.add_argument("--entity", required=True,
                        help="Entity folder name under entities/")
    parser.add_argument("--requested-by", default="cli",
                        help="Identifier recorded on Dashboard and ChangeLog")
    parser.add_argument("--whatif", action="store_true",
                        help="Apply WhatIf sheet overrides as a scenario, "
                             "writing Calc_WhatIf and a scenario column on Dashboard")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    run_score(root=args.root, entity_name=args.entity,
              requested_by=args.requested_by, whatif=args.whatif)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
