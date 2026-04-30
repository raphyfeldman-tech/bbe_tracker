from __future__ import annotations
"""Polls each entity's RunQueue and dispatches jobs.

Plan 1 scope: one entity at a time, 'score' scope only.
Plan 2 expands: multiple entities, full scope coverage (reports, evidence pack).
"""
import argparse
import logging
import time
from datetime import datetime
from pathlib import Path
from ..run_queue import read_queued, mark_running, mark_completed, mark_failed
from ..workbook.backends import WorkbookBackend, LocalFolderBackend
from .calculate_score import run_score


log = logging.getLogger("bee_tracker.run_queue_daemon")


def process_one_entity(
    *, root: Path, entity_name: str,
    backend: WorkbookBackend | None = None,
) -> int:
    """Process all queued rows for a single entity. Returns count processed.

    `backend` defaults to LocalFolderBackend(root). When the daemon runs
    against SharePoint, pass a GraphBackend instead.
    """
    if backend is None:
        backend = LocalFolderBackend(root)

    # Open via backend to read queued rows
    handle = backend.open_entity_workbook(entity_name)
    queued = read_queued(handle.workbook)
    if not queued:
        return 0

    processed = 0
    for req in queued:
        # Mark running and save (this refreshes etag on the handle)
        mark_running(handle.workbook, req.request_id, started_at=datetime.utcnow())
        backend.save(handle)

        try:
            if req.scope == "score":
                run_score(
                    root=root,
                    entity_name=entity_name,
                    requested_by=req.requested_by,
                    backend=backend,
                )
                # Re-open to pick up the changes run_score made (Calc_*, Dashboard, ChangeLog)
                # so our subsequent mark_completed write doesn't clobber them.
                handle = backend.open_entity_workbook(entity_name)
                mark_completed(
                    handle.workbook, req.request_id,
                    completed_at=datetime.utcnow(),
                    result_path="(in-workbook)",
                )
            else:
                raise ValueError(f"Unsupported scope in Plan 1: {req.scope}")
        except Exception as exc:
            handle = backend.open_entity_workbook(entity_name)
            mark_failed(
                handle.workbook, req.request_id,
                completed_at=datetime.utcnow(),
                error_message=str(exc),
            )
            log.exception("Request %s failed", req.request_id)

        backend.save(handle)
        processed += 1

    return processed


def process_all_entities(
    *, root: Path, backend: WorkbookBackend | None = None,
) -> int:
    """Iterate every directory under root/entities/ and call process_one_entity."""
    if backend is None:
        backend = LocalFolderBackend(root)
    entities_root = root / "entities"
    if not entities_root.exists():
        return 0
    total = 0
    for child in sorted(entities_root.iterdir()):
        if not child.is_dir():
            continue
        try:
            total += process_one_entity(
                root=root, entity_name=child.name, backend=backend,
            )
        except Exception:
            log.exception("Entity %s failed; continuing", child.name)
    return total


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bee-run-queue-daemon")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--entity", default=None,
                        help="Process only this entity (default: process all entities under root/entities/)")
    parser.add_argument("--interval", type=int, default=60,
                        help="Seconds between polls")
    parser.add_argument("--once", action="store_true",
                        help="Run one iteration and exit")
    parser.add_argument(
        "--backend", choices=["local", "graph"], default="local",
        help="Workbook storage backend (default: local)",
    )
    parser.add_argument(
        "--graph-locator", type=Path, default=Path("graph_locator.yaml"),
        help="YAML mapping entity_name → drive_id/item_id (used with --backend graph)",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.backend == "graph":
        from ..workbook.backends import GraphBackend
        backend = GraphBackend.from_env(args.graph_locator)
    else:
        backend = LocalFolderBackend(args.root)

    while True:
        try:
            if args.entity:
                n = process_one_entity(
                    root=args.root, entity_name=args.entity, backend=backend,
                )
            else:
                n = process_all_entities(root=args.root, backend=backend)
            if n:
                log.info("Processed %d request(s)", n)
        except Exception:
            log.exception("Iteration failed; continuing")
        if args.once:
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
