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

For PDF report generation, install the optional `pdf` extra:
    pip install -e ".[dev,pdf]"
This adds WeasyPrint, which requires Cairo and Pango system libraries:
    macOS:  brew install cairo pango gdk-pixbuf libffi
    Ubuntu: apt install libpango-1.0-0 libcairo2 libgdk-pixbuf2.0-0

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

# PDF report (requires the entity's branding/ folder + the [pdf] extra installed)
bee-generate-report --root /tmp/bee --entity sample --output /tmp/bee/report.pdf

# Email alerts (requires GRAPH_* env vars + alert recipients in group_settings.yaml)
bee-send-alerts --root /tmp/bee --entity sample --from-user bee-tracker@example.com

# Evidence pack for the verifier
bee-export-evidence-pack --root /tmp/bee --entity sample --output /tmp/bee/pack.zip
```

## Test

```bash
pytest -v
```

(215 passed + 2 skipped — the 2 skips are PDF-render tests that skip when WeasyPrint can't import.)

## Scope (Plan 1 + Plan 2)

What's done:
- All 5 element scorers (Ownership, Management Control, Skills Development, ESD/PP, SED) with hand-calculated test fixtures
- Y.E.S. tier level-up logic (3 tiers), wired into the score pipeline (Y.E.S. annotation on Dashboard when applied)
- Total score → BEE Level (1–8 / non-compliant) lookup
- BEE Level with priority-element breach discount + Y.E.S. tier bump applied end-to-end
- WhatIf scenario path (`--whatif` flag) with Dashboard scenario column
- GapAnalysis sheet populated with ranked financial actions (procurement / skills / ESD / SED) + non-financial opportunities (headcount / ownership)
- Dashboard with BEE Level tile + top-5 gaps + element breakdown
- ChangeLog appended on every recalc
- RunQueue hidden by default in the template
- Validation: structural, evidence-id, cert expiry, demographics, NPAT/payroll, ESD/SED thresholds, Y.E.S. age range, HTML report
- Multi-entity daemon (no `--entity` arg → process all under `entities/`)
- GraphBackend wired into `bee-calculate-score --backend graph` (with `from_env(locator_yaml)`)
- Daemon (`bee-run-queue-daemon`) supports `--backend graph` end-to-end
- Office Script Run Assessment button + RunQueue round-trip
- PDF reports with per-entity branding (`bee-generate-report`) — install `pip install -e ".[pdf]"` for WeasyPrint
- Black-female sub-indicators (senior / middle / junior management) and black-disabled indicator in Management Control (now 9 indicators, 26 points)
- Skills Development: Category B–G filter (excludes orientation training) + 15% salary cap on `salary_cost_during_training`
- 30-day payment bonus indicator in Preferential Procurement (49 pts total)
- WhatIf sheet template ships with `key` / `value` headers
- Generic `write_calc_element` writer (refactor; 5 per-element wrappers are now one-line shims)
- Cross-process byte-determinism for the workbook template generator (`dcterms:modified` strip + per-entry zip mtime pin)
- EAP demographic weighting (race × level) on the 5 main Management Control indicators (board, exec directors, senior/middle/junior management). African / Coloured / Indian per-race targets at SA EAP proportions; an all-Indian senior team only earns the Indian race-weight portion of the indicator.
- Graph 429/503 retry with `Retry-After` backoff
- Graph `list_folders` pagination via `@odata.nextLink`
- `bee-validate-data --backend graph` (Graph backend wiring on the validation CLI)
- `bee-send-alerts` — email alerts via Microsoft Graph (priority breach / cert expiry / level drop)
- `bee-export-evidence-pack` — one-click zip export of workbook + referenced evidence
- Operations manual at `docs/OPERATIONS.md` (Azure app registration, daemon-as-service for systemd / Task Scheduler / launchd, cron scheduling, real-tenant smoke test)
- 215 passed + 2 skipped tests

Deferred to Plan 3:
- EAP weighting on black-female sub-indicators (currently aggregate-black)
- EAP weighting on black-disabled (currently aggregate-black)
- Service-install scripts (Windows Service / systemd) — see `docs/OPERATIONS.md` for manual setup
- Scheduled tasks — see `docs/OPERATIONS.md`
- Real SharePoint integration smoke test — see `docs/OPERATIONS.md`
