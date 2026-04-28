# BEE Tracker — Plan 1 MVP

End-to-end walking skeleton for the B-BBEE ICT Sector Code Tracker.
Plan 1 covers Ownership scoring only; later plans fill in the remaining
elements, reports, and alerts.

## Components

- `bee-calculate-score` — CLI: compute scores for a single entity.
- `bee-validate-data` — CLI: structural + evidence-link checks, optional HTML report.
- `bee-run-queue-daemon` — long-running: polls a single entity's `RunQueue`
  and dispatches `score` requests.
- `office_scripts/run_assessment.ts` — Office Script for the Dashboard button.

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Requires Python 3.9+.

## Seed a local entity

```bash
mkdir -p /tmp/bee/entities/sample
python scripts/make_template.py
cp templates/workbook_template.xlsx /tmp/bee/entities/sample/BEE_Tracker.xlsx
cp tests/fixtures/sample_group_settings.yaml /tmp/bee/entities/sample/group_settings.yaml
cp tests/fixtures/sample_ict_scorecard.yaml /tmp/bee/ict_scorecard.yaml
```

## Score once (CLI)

```bash
bee-calculate-score --root /tmp/bee --entity sample --requested-by raphy@core.co.za -v
```

## Run the polling daemon

```bash
bee-run-queue-daemon --root /tmp/bee --entity sample --interval 60
```

Pass `--once` for a single iteration (useful for testing).

## Validate workbook

```bash
bee-validate-data --root /tmp/bee --entity sample --report /tmp/bee/validation.html
```

## Deploy the Office Script button

See [office_scripts/README.md](office_scripts/README.md).

## Test

```bash
pytest -v
```

(52 tests at the end of Plan 1.)

## Plan 1 scope (what's done, what's not)

Done:
- Ownership scoring with sub-minimum check (BEE math verified by hand-calculated fixtures)
- Dashboard (entity, total score, priority status, element breakdown, last-run footer)
- RunQueue round-trip via Office Script + daemon
- Structural + evidence-id validation with HTML report
- LocalFolderBackend (used in tests and CLI today); GraphBackend implemented but not yet wired into the CLI

Not in Plan 1 (deferred to Plans 2 & 3):
- Management Control, Skills Development, ESD, SED, YES scoring
- WhatIf scenario runs
- GapAnalysis with cost-of-point ranker
- PDF reports, email alerts, evidence-pack export
- Multi-entity iteration in the daemon
- GraphBackend wiring into the CLI (currently only LocalFolderBackend is used)
- Real SharePoint integration test
