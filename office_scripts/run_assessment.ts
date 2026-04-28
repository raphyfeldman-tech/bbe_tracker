// office_scripts/run_assessment.ts
// Triggered by the "Run Assessment" button on the Dashboard sheet.
// Appends a row to the hidden RunQueue sheet for the daemon to pick up.

function main(workbook: ExcelScript.Workbook, scope: string = "score"): string {
    const validScopes = [
        "score", "score_with_whatif",
        "report_monthly", "report_quarterly",
        "evidence_pack",
    ];
    if (!validScopes.includes(scope)) {
        throw new Error(`Invalid scope: ${scope}`);
    }

    const runQueue = workbook.getWorksheet("RunQueue");
    if (!runQueue) {
        throw new Error("RunQueue sheet missing from workbook");
    }

    const requestId = `r-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const requestedAt = new Date().toISOString();
    // Excel Online exposes the signed-in user's email via the context; fall
    // back to a sentinel if unavailable.
    let requestedBy = "unknown@local";
    try {
        // Note: workbook.getApplication() does not expose identity in Office
        // Scripts API. Prefer a named range 'CurrentUser' on the Settings
        // sheet that the admin populates, or pass through a parameter.
        const settings = workbook.getWorksheet("Settings");
        const userRange = settings?.getRange("B2");  // by convention
        const v = userRange?.getValue();
        if (typeof v === "string" && v.includes("@")) {
            requestedBy = v;
        }
    } catch (_e) {
        // ignore and keep sentinel
    }

    const usedRange = runQueue.getUsedRange();
    const nextRow = usedRange ? usedRange.getRowCount() + 1 : 2;
    const target = runQueue.getRangeByIndexes(nextRow - 1, 0, 1, 9);
    target.setValues([[
        requestId,
        requestedAt,
        requestedBy,
        scope,
        "queued",
        null, null, null, null,
    ]]);

    return requestId;
}
