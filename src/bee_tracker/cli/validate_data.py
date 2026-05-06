from __future__ import annotations
import argparse
import logging
from pathlib import Path
from ..validation.rules import run_all_rules, Severity
from ..validation.report import render_html
from ..workbook.backends import LocalFolderBackend, GraphBackend


log = logging.getLogger("bee_tracker.validate_data")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bee-validate-data")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--entity", required=True)
    parser.add_argument("--report", type=Path, default=None,
                        help="Output HTML report path (optional)")
    parser.add_argument("--templates", type=Path, default=Path("templates"))
    parser.add_argument("--backend", choices=["local", "graph"], default="local",
                        help="Workbook storage backend (default: local)")
    parser.add_argument("--graph-locator", type=Path,
                        default=Path("graph_locator.yaml"),
                        help="YAML mapping entity_name → drive_id/item_id "
                             "(used with --backend graph)")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO)

    if args.backend == "graph":
        backend = GraphBackend.from_env(args.graph_locator)
    else:
        backend = LocalFolderBackend(args.root)

    handle = backend.open_entity_workbook(args.entity)
    wb = handle.workbook

    findings = run_all_rules(wb)
    errors = [f for f in findings if f.severity is Severity.ERROR]
    warnings = [f for f in findings if f.severity is Severity.WARNING]
    log.info("Validation: %d errors, %d warnings", len(errors), len(warnings))

    if args.report:
        html = render_html(findings, args.templates)
        args.report.write_text(html)
        log.info("Report written to %s", args.report)

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
