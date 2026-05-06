# Developer Guide

## Layout

```
src/bee_tracker/
├── reporting/                # NEW: PDF report generation
│   ├── branding.py           # per-entity branding loader (logo + colours.yaml)
│   └── pdf.py                # WeasyPrint renderer + ReportContext dataclass
├── cli/                # Console-script entry points
│   ├── calculate_score.py
│   ├── validate_data.py
│   ├── run_queue_daemon.py
│   └── generate_report.py    # NEW: bee-generate-report entry point
├── config.py           # YAML loaders + frozen dataclasses
├── errors.py           # Exception hierarchy
├── gap_analysis/       # Gap analysis + ranker
│   ├── financial.py    # Cost-of-point Action generator (procurement / skills / ESD / SED)
│   ├── non_financial.py # Opportunity generator (headcount / ownership)
│   └── ranker.py       # Top-N ranking across Action + Opportunity
├── graph/              # Microsoft Graph wrapper
│   ├── auth.py         # MSAL client-credentials, token cache
│   └── client.py       # REST: download / upload (If-Match) / list folders
├── rendering/
│   └── dashboard.py    # Dashboard sheet rendering
├── run_queue.py        # RunQueue read + status updates
├── scoring/            # Element scoring engine
│   ├── base.py         # ElementScorer ABC + ElementResult dataclass
│   ├── ownership.py    # Ownership scorer
│   ├── management_control.py # Management Control scorer (5 indicators)
│   ├── skills_development.py # Skills Development scorer (3 indicators)
│   ├── procurement.py  # Procurement / PP scorer
│   ├── esd_pp.py       # ESD + PP combined scorer
│   ├── sed.py          # SED scorer
│   ├── yes_initiative.py # Y.E.S. tier level-up logic
│   ├── level.py        # total_score_to_level(score, scorecard)
│   └── registry.py     # element_name → scorer dispatch
├── validation/
│   ├── rules.py        # structural, evidence-id, cert expiry, demographics, settings, threshold checks
│   └── report.py       # HTML report rendering
├── whatif.py           # apply_overrides(inputs, overrides) for WhatIf scenarios
└── workbook/
    ├── backends.py     # WorkbookBackend ABC + Local + Graph
    ├── reader.py       # Sheet → DataFrame readers
    ├── schema.py       # SHEETS table (relocated from scripts/)
    └── writer.py       # DataFrame/result → sheet writers

templates/
└── report.html.j2            # NEW: PDF report Jinja template
```

## Key abstractions

- **`WorkbookBackend`** — indirection over file storage.
  Production: `GraphBackend`. Tests + local dev: `LocalFolderBackend`.
- **`ElementScorer`** — one implementation per BEE element.
  Plan 2 ships all 5 (`OwnershipScorer`, `ManagementControlScorer`,
  `SkillsDevelopmentScorer`, `EsdPpScorer`, `SedScorer`); all are
  registered in `scoring.registry.default_registry()`.
- **`Action`** (financial) and **`Opportunity`** (non-financial) value
  objects in `gap_analysis/` — surfaced by the ranker into the Dashboard's
  top-5 gaps table.
- **`apply_overrides(inputs, overrides)`** — applies WhatIf overrides to
  a copy of the scoring inputs before the scorer runs.
- **`total_score_to_level(score, scorecard)`** — looks up BEE Level
  (1–8 / non-compliant) from the scorecard's level table.
- **`level_after_priority_breaches(score, breach_count, scorecard)`** —
  applies the §5.3 sub-minimum discount to the BEE level (one level per
  priority-element breach).
- **`apply_levels_up(level, levels_up)`** — adds Y.E.S. tier bumps after
  the breach discount.
- **`append_change_log(wb, ...)`** — writes a record to the ChangeLog
  sheet (timestamp, actor, scope, summary).
- **`write_gap_analysis(wb, ranked_actions, opportunities)`** — writes
  the GapAnalysis sheet (Section A ranked financial actions, Section B
  non-financial opportunities).
- **`RunQueue` functions** — `read_queued`, `mark_running`, `mark_completed`,
  `mark_failed`. Row identity is `request_id`.
- **`Branding`** dataclass (logo + colours + optional font) +
  **`load_branding(folder)`** — reads branding from a per-entity folder.
- **`ReportContext`** + **`render_pdf(ctx, branding, output_path)`** —
  renders the Jinja template through WeasyPrint to a PDF.
- **`_QUALIFYING_CATEGORIES = {"B","C","D","E","F","G"}`** in
  `skills_development.py` filters Skills Dev training rows
  (excludes Category A orientation training).
- **`_SALARY_CAP_PCT = 0.15`** caps the
  `salary_cost_during_training` contribution to 15% of total payroll.
- **`_BLACK_FEMALE_INDICATORS`** + **`_black_female_share_pct`** in
  `management_control.py` — gender filter for senior/middle/junior
  black-female sub-indicators (2+2+1 pts).
- **`_black_disabled_share_pct`** in `management_control.py` — disability
  indicator (2 pts).
- **`Scorecard.eap`** field — race percentages (african, coloured, indian,
  white) loaded from the scorecard YAML.
- **`_eap_split(target_pct, weight, eap)`** in `management_control.py` —
  splits a (target, weight) pair across African / Coloured / Indian by
  within-black EAP share.
- **`_race_actual_pct_at_level(employees, predicate, race_name)`** —
  FTE-weighted per-race share at a given occupational level.
- **`_eap_weighted_points(employees, predicate, target_pct, weight, eap)`**
  — EAP-weighted total points across the 3 black-race contributions; falls
  back to aggregate-black scoring when EAP is empty (preserves backwards
  compat).
- **`_BLACK_LEVEL_INDICATORS`** dispatch map — the 5 main Management
  Control indicators (board, exec directors, senior/middle/junior
  management) routed through EAP.
- **`payment_terms_30_day_bonus`** indicator in `score_esd_pp` — uses the
  new `row_predicate=` arg on `_recognised_total` to filter for 30-day
  payment terms (2 bonus pts).
- **`write_calc_element(wb, sheet_name, result)`** — generic writer in
  `workbook/writer.py`; the 5 per-element shims (`write_ownership`,
  `write_management_control`, `write_skills_development`,
  `write_esd_pp`, `write_sed`) now each delegate in a single line.
- **`_strip_dc_modified`** helper in `scripts/make_template.py` — post-save
  pass that removes the `dcterms:modified` element from `core.xml` and pins
  each zip entry's mtime, giving cross-process byte-deterministic template
  output.
- **`_request_with_retry(method, url, **kwargs)`** on `GraphClient` —
  retries 429/503 up to 4 times respecting `Retry-After`.
- **`MAX_RETRIES = 4`** and **`RETRY_STATUS_CODES = {429, 503}`**
  constants in `graph/client.py`.
- Pagination on `list_folders` via `@odata.nextLink`.
- **`alerts/email.send_email(client, *, from_user, to, subject, html_body)`**
  — Graph `sendMail` wrapper.
- **`alerts/triggers.{detect_priority_breaches, detect_cert_expiries, detect_level_drop}`**
  + **`Breach`** / **`CertExpiry`** / **`Severity`** value objects.
- **`alerts/render.{render_priority_breach, render_cert_expiry, render_level_drop}`**
  — Jinja-render alert email bodies.
- **`evidence_pack.build_evidence_pack(root, entity_name, *, output_zip)`**
  — zip workbook + referenced evidence + validation_latest.html.

## Testing

- `pytest` runs the suite (215 passed + 2 skipped — PDF-render tests
  skip when WeasyPrint can't import).
- Graph client is tested with `responses` — no real network.
- Backend abstraction means end-to-end tests run against a temp folder;
  GraphBackend gets exercised by targeted unit tests only. Plan 3 will
  add a manual smoke test against a real SharePoint tenant.

## Local-dev caveats

### WeasyPrint requires system libraries

PDF rendering uses WeasyPrint, which depends on Cairo, Pango, and GDK-Pixbuf
system libraries. Without them, `from weasyprint import HTML` fails at import
time. The two PDF-render tests (`tests/test_reporting_pdf.py` and the CLI
test in `tests/test_cli_generate_report.py`) use `pytest.importorskip` so
they skip cleanly on machines without the libs.

To enable PDF rendering:

- macOS: `brew install cairo pango gdk-pixbuf libffi` then `pip install -e ".[pdf]"`
- Ubuntu: `apt install libpango-1.0-0 libcairo2 libgdk-pixbuf2.0-0` then `pip install -e ".[pdf]"`

The renderer module itself imports cleanly without WeasyPrint — the import
is deferred until `render_pdf()` is called — so all non-PDF tests run
green regardless.

## Regenerating the workbook template

```bash
python scripts/make_template.py
cp templates/workbook_template.xlsx tests/fixtures/sample_workbook.xlsx
pytest tests/test_workbook_template.py
```

The `build_template` function pins workbook timestamps to a fixed datetime so
regenerations are byte-identical (verified by `test_template_is_byte_deterministic`).
Cross-process byte-determinism is enforced by stripping the `dcterms:modified`
element from `core.xml` and pinning each zip entry's mtime in the saved file —
both are essential because openpyxl resets `wb.properties.modified` at save
time and the OOXML zip writer otherwise stamps each entry with the wall-clock
time. See Plan 3b commit `0e8668a` for the implementation.

## Adding a new element

The Plan 2 scorers are now the canonical reference. The simplest pattern
is `scoring/management_control.py` — read it first when adding a new
element or sub-indicator.

1. New `src/bee_tracker/scoring/<element>.py` implementing `ElementScorer`
   (model on `management_control.py`).
2. New reader function in `workbook/reader.py`.
3. New writer function in `workbook/writer.py` — call the generic
   `write_calc_element(wb, sheet_name, result)` from a one-line shim
   (the 5 existing element writers all now delegate this way).
4. Register in `scoring/registry.default_registry()`.
5. Add fixtures + tests (hand-calculate the expected score first).
6. Extend `cli/calculate_score.run_score` to dispatch to the new scorer.

## Python version

Target is Python 3.9 (the system Python on the build machine). Every new
module starts with `from __future__ import annotations` so PEP 604 union
syntax (`X | None`) and builtin generics (`list[X]`, `dict[K, V]`) work
under 3.9 — annotations become strings at runtime.

When the runtime moves to 3.11+, the `from __future__` imports can be
removed and `datetime.utcnow()` (deprecated in 3.12) can be replaced with
`datetime.now(timezone.utc)`.

## Deferred tech debt (carry to Plan 3)

- EAP weighting on black-female sub-indicators
- EAP weighting on black-disabled
- Service-install scripts (manual per `docs/OPERATIONS.md`)
- Scheduled tasks (manual per `docs/OPERATIONS.md`)
- Real SharePoint smoke test (manual per `docs/OPERATIONS.md`)
- Promote `Action`/`Opportunity` from `gap_analysis/` to a typed CSV
  export for the Dashboard's "Top Gaps" table
- Drop the unused `apply_overrides` import from
  `gap_analysis/financial.py` (cosmetic)
- Replace `cfg.sub_minimum_pct or 40` fallback with explicit
  `None`-check in scorers (a literal `0` value is currently coerced)
- Replace `datetime.utcnow()` with `datetime.now(timezone.utc)` once
  Python ≥3.12 is the target

## Run-time troubleshooting

- **`PreconditionFailedError` (412) from `GraphClient.upload_item`** — the
  workbook was modified remotely between download and upload. The daemon
  should mark the request `failed` and re-queue.
- **MSAL `invalid_client`** — check `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`,
  `GRAPH_CLIENT_SECRET` env vars.
- **`bee-calculate-score: command not found`** — re-run `pip install -e ".[dev]"`
  inside the venv.

## Plan 2 simplifications (deferred to Plan 3)

The following are Plan 3 stretch items — Plan 2 ships a workable
baseline that scores the elements correctly for typical Generic
entities but doesn't yet model every edge case in the ICT Sector Code.

- **Management Control:** Full EAP race-by-level demographic weighting
  still deferred. Black-female (senior/middle/junior, 2+2+1 pts) and
  black-disabled (2 pts) sub-indicators landed in Plan 3b — element grew
  19 → 26 pts.
- **Skills Development:** Black-women target still deferred. Categories
  B–G filter (excludes Category A orientation) and 15% salary cap on
  `salary_cost_during_training` landed in Plan 3b.
- **ESD/PP:** Designated-group sub-indicator and detailed QSE thresholds
  still deferred. 30-day payment bonus indicator (2 pts) landed in Plan 3b
  — element grew 47 → 49 pts.
- **SED:** 1 indicator. No 5-year average NPAT denominator override.
- **Y.E.S.:** 3-tier ladder. Doesn't model the "must maintain prior-year
  contributor status" qualifier.

## Criticals fix sprint (post-Plan-2 review)

After Plan 2 closed, an independent code review caught 5 Critical gaps
between the README and the runtime — features the documentation said
were done but that the integrated CLI never invoked. All 5 plus one
"Important" item are now fixed:

| ID | Fix |
|---|---|
| C1 | Y.E.S. tier level-up wired into `cli/calculate_score.run_score`; Dashboard shows `(Y.E.S. +N levels)` |
| C2 | Priority-element sub-minimum breach discounts the BEE level by 1 per breach (`level_after_priority_breaches`) |
| C3 | `bee-run-queue-daemon` now routes all workbook I/O through `WorkbookBackend` (`--backend graph` works end-to-end) |
| C4 | `GapAnalysis` sheet populated with ranked financial actions + non-financial opportunities |
| C5 | `ChangeLog` sheet appended on every recalc |
| I1 | `RunQueue` sheet hidden by default in the template generator |

Test count grew from 144 to 158.

## Plan 3b: Math refinements + small tech debt

After Plan 3a (PDF reports), Plan 3b closed the math gaps that previously
made the scorer untrustworthy for real entity analysis, plus 3 small
tech-debt items:

| ID | Fix |
|---|---|
| 1  | Black-female sub-indicators (senior/middle/junior) in Management Control |
| 2  | Black-disabled indicator in Management Control (total: 9 indicators, 26 pts) |
| 3  | Skills Development: Category B–G filter (excludes orientation/Category A) |
| 4  | Skills Development: 15% cap on `salary_cost_during_training` |
| 5  | PP: 30-day payment bonus indicator (49 pts total) |
| 6  | WhatIf sheet ships with key/value headers |
| 7  | Generic `write_calc_element` writer (5 per-element wrappers are now shims) |
| 8  | Cross-process byte-determinism: dcterms:modified strip + per-entry zip mtime pin |

Test count grew 169 → 180.

Still deferred to later plans: full EAP demographic weighting (race-by-level
targets) in Management Control, email alerts, evidence-pack export, service-
install scripts, scheduled tasks, real SharePoint smoke test, 429/503 retry,
pagination on list_folders, GraphBackend wiring for bee-validate-data.

## Plan 3d: Full EAP demographic weighting

Plan 3d closed the last big math gap: the 5 main Management Control "black at
level" indicators now apply EAP-weighted scoring per the ICT Sector Code. Each
indicator's target and weight split across African / Coloured / Indian
race-specific sub-targets in EAP proportions; an entity's actual race share at
the level is judged against each race-target separately. An all-Indian senior
team only earns the Indian portion of the credit (~3% of the indicator's full
weight), not the full black weight.

The EAP machinery falls back gracefully to aggregate-black scoring when the
scorecard YAML omits the `eap:` block — useful for older configs and for the
gap-analysis synthetic perturbations.

Black-female sub-indicators and black-disabled remain on aggregate-black
scoring (EAP extension is a future-plan candidate).

Notable downstream effect: the synthetic "+1 black employee" rows in
`gap_analysis/non_financial.py::_headcount_opportunities` are now tagged
`race: "African"` (the dominant SA EAP race; highest-yield modelled appointment)
so the EAP-weighted scorer attributes points correctly.

Test count grew 180 → 186.

## Plan 3c: Operations + alerts + evidence pack

Plan 3c made the BEE Tracker production-reliable: Graph 429/503 retry with
`Retry-After` backoff and `list_folders` pagination so transient throttling
and entity-tree growth no longer abort runs. Three new CLIs landed:

- `bee-send-alerts` — emails priority-breach / cert-expiry / level-drop
  notifications via Graph `sendMail`. Recipients per entity via
  `group_settings.yaml` `alerts:` block.
- `bee-export-evidence-pack` — zips the workbook + every file referenced
  in the `Evidence` sheet (skipping missing files with a warning) for
  verification-agency hand-off.
- `bee-validate-data --backend graph` — validation now runs against
  SharePoint workbooks too.

Operations infrastructure (service install, scheduled tasks, real-tenant
smoke test) is documented in `docs/OPERATIONS.md` rather than automated
here — those steps depend on the user's deployment target.

Test count grew 186 → 215.
