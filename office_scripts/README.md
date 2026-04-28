# Office Scripts

## Install `run_assessment.ts`

1. Open `BEE_Tracker.xlsx` in Excel Online (or desktop Excel with Office Scripts enabled).
2. Automate tab → New Script → paste contents of `run_assessment.ts` → Save as `Run Assessment`.
3. On the Dashboard sheet, insert → shape (rectangle) labelled "Run Assessment".
4. Right-click the shape → Assign Script → `Run Assessment`.
5. (Optional) duplicate shape per scope: Score / WhatIf / Monthly / Quarterly / Evidence Pack.
   Each shape calls the same script with a different hard-coded `scope` argument
   by wrapping in small trampoline scripts (e.g. `run_assessment_whatif.ts`).

## Manual verification

1. Ensure a `Settings` sheet row has `B2` = your email (so `requested_by` is captured).
2. Click the button.
3. Unhide `RunQueue` (right-click tab → Unhide). A new row should appear with
   `status = queued` and a fresh `request_id`.
4. With the daemon running (see `README.md` at repo root), wait up to
   `--interval` seconds. The row's status should flip to `running` then
   `completed`, and the Dashboard should refresh.
