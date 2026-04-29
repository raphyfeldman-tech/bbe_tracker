# BEE Tracker — Plan 1 + Plan 2

End-to-end BEE scorecard tool: scores all 5 ICT-Generic elements (Ownership,
Management Control, Skills Development, ESD/PP, SED), applies Y.E.S. tier
level-up, runs WhatIf scenarios, and generates a Dashboard with BEE level +
top-5 gaps.

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

## Run a full scorecard

```bash
# One-shot recalc (single entity)
bee-calculate-score --root /tmp/bee --entity sample --requested-by you@example -v

# With WhatIf scenario
bee-calculate-score --root /tmp/bee --entity sample --whatif -v

# Multi-entity daemon (processes every entity under /tmp/bee/entities/)
bee-run-queue-daemon --root /tmp/bee --interval 60

# Validation report
bee-validate-data --root /tmp/bee --entity sample --report /tmp/bee/validation.html
```

## Test

```bash
pytest -v
```

(144 tests at the end of Plan 2.)

## Scope (Plan 1 + Plan 2)

What's done:
- All 5 element scorers (Ownership, Management Control, Skills Development, ESD/PP, SED) with hand-calculated test fixtures
- Y.E.S. tier level-up logic (3 tiers)
- Total score → BEE Level (1–8 / non-compliant) lookup
- WhatIf scenario path (`--whatif` flag) with Dashboard scenario column
- GapAnalysis: cost-of-point ranker for financial levers (procurement / skills / ESD / SED) + non-financial opportunities (headcount / ownership)
- Dashboard with BEE Level tile + top-5 gaps + element breakdown
- Validation: structural, evidence-id, cert expiry, demographics, NPAT/payroll, ESD/SED thresholds, Y.E.S. age range, HTML report
- Multi-entity daemon (no `--entity` arg → process all under `entities/`)
- GraphBackend wired into `bee-calculate-score --backend graph` (with `from_env(locator_yaml)`)
- Office Script Run Assessment button + RunQueue round-trip
- 144 tests, all green

Deferred to Plan 3:
- PDF reports with per-entity branding
- Email alerts (priority breach / cert expiry / level drop)
- Evidence-pack export (`export_evidence_pack.py`)
- Service-install scripts for the daemon (Windows Service / systemd)
- Scheduled-task setup for nightly recalc + daily cert-expiry alerts
- Real SharePoint integration smoke test against a tenant
- Black-female + EAP weighting in Management Control
- Category B–G split + salary cap in Skills Development
- 30-day payment bonus in PP
- 429/503 retry on Graph calls
- Pagination on `list_folders`
- Byte-determinism flake investigation (template generator)
- GraphBackend wiring for `bee-validate-data` and `bee-run-queue-daemon` (currently `bee-calculate-score` only)
- WhatIf sheet header row (`["key", "value"]`) auto-created by template generator
- Generic `write_calc_element(wb, sheet, result)` writer to deduplicate the 5 per-element writers
