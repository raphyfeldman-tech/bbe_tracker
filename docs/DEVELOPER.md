# Developer Guide

## Layout

```
src/bee_tracker/
├── cli/                # Console-script entry points
│   ├── calculate_score.py
│   ├── validate_data.py
│   └── run_queue_daemon.py
├── config.py           # YAML loaders + frozen dataclasses
├── errors.py           # Exception hierarchy
├── graph/              # Microsoft Graph wrapper
│   ├── auth.py         # MSAL client-credentials, token cache
│   └── client.py       # REST: download / upload (If-Match) / list folders
├── rendering/
│   └── dashboard.py    # Dashboard sheet rendering
├── run_queue.py        # RunQueue read + status updates
├── scoring/            # Element scoring engine
│   ├── base.py         # ElementScorer ABC + ElementResult dataclass
│   ├── ownership.py    # Ownership scorer
│   └── registry.py     # element_name → scorer dispatch
├── validation/
│   ├── rules.py        # Structural + evidence-id rules
│   └── report.py       # HTML report rendering
└── workbook/
    ├── backends.py     # WorkbookBackend ABC + Local + Graph
    ├── reader.py       # Sheet → DataFrame readers
    └── writer.py       # DataFrame/result → sheet writers
```

## Key abstractions

- **`WorkbookBackend`** — indirection over file storage.
  Production: `GraphBackend`. Tests + local dev: `LocalFolderBackend`.
- **`ElementScorer`** — one implementation per BEE element.
  Plan 1 ships `OwnershipScorer`. Plan 2 adds the others; the registry
  lookup in `scoring.registry.default_registry()` is the only wiring point.
- **`RunQueue` functions** — `read_queued`, `mark_running`, `mark_completed`,
  `mark_failed`. Row identity is `request_id`.

## Testing

- `pytest` runs the suite (52 tests at end of Plan 1).
- Graph client is tested with `responses` — no real network.
- Backend abstraction means end-to-end tests run against a temp folder;
  GraphBackend gets exercised by targeted unit tests only. Plan 2/3 will
  add a manual smoke test against a real SharePoint tenant.

## Regenerating the workbook template

```bash
python scripts/make_template.py
cp templates/workbook_template.xlsx tests/fixtures/sample_workbook.xlsx
pytest tests/test_workbook_template.py
```

The `build_template` function pins workbook timestamps to a fixed datetime so
regenerations are byte-identical (verified by `test_template_is_byte_deterministic`).
If you see that test flake on the full suite, rerun in isolation — it's a
known minor instability we're tracking for follow-up.

## Adding a new element (Plan 2 preview)

1. New `src/bee_tracker/scoring/<element>.py` implementing `ElementScorer`.
2. New reader function in `workbook/reader.py`.
3. New writer function in `workbook/writer.py`.
4. Register in `scoring/registry.default_registry()`.
5. Add fixtures + tests.
6. Extend `cli/calculate_score.run_score` to dispatch to the new scorer.

## Python version

Target is Python 3.9 (the system Python on the build machine). Every new
module starts with `from __future__ import annotations` so PEP 604 union
syntax (`X | None`) and builtin generics (`list[X]`, `dict[K, V]`) work
under 3.9 — annotations become strings at runtime.

When the runtime moves to 3.11+, the `from __future__` imports can be
removed and `datetime.utcnow()` (deprecated in 3.12) can be replaced with
`datetime.now(timezone.utc)`.

## Deferred tech debt (carry to Plan 2)

- `GraphBackend` is unit-tested with mocks but not wired into the CLI; CLI
  uses `LocalFolderBackend` only. Plan 2 wires it up.
- `_read_table` in `workbook/reader.py` is private; Plan 2 will need it for
  many readers — consider promoting to public.
- `make_template.py`'s SHEETS table lives in `scripts/`, not on
  `pythonpath`; Plan 2 should move it under `src/bee_tracker/workbook/`.
- Test coverage on `make_template.py` covers 4 of 13 header-bearing sheets;
  Plan 2 should iterate the schema for full coverage.
- 429 / 503 retry on Graph calls is not implemented; Plan 2 must add this
  before the daemon runs unattended in production.
- `LocalFolderBackend.save` does not check mtime drift; mismatch with
  `GraphBackend` semantics. Add a token check there for symmetry.
- The byte-determinism test (`test_template_is_byte_deterministic`) flakes
  occasionally; investigate whether openpyxl is overwriting our pinned
  `wb.properties.modified` during save.
- Coverage for `GraphBackend._resolve` and eTag plumbing — three small
  mock-based unit tests would close the gap.

## Run-time troubleshooting

- **`PreconditionFailedError` (412) from `GraphClient.upload_item`** — the
  workbook was modified remotely between download and upload. The daemon
  should mark the request `failed` and re-queue.
- **MSAL `invalid_client`** — check `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`,
  `GRAPH_CLIENT_SECRET` env vars.
- **`bee-calculate-score: command not found`** — re-run `pip install -e ".[dev]"`
  inside the venv.
