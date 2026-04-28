from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from openpyxl import Workbook


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class Finding:
    severity: Severity
    sheet: str | None
    row: int | None
    message: str


EXPECTED_SHEETS = [
    "Dashboard", "GapAnalysis", "WhatIf",
    "Ownership", "Employees", "MgmtControl_Summary",
    "Training", "Learnerships", "Bursaries",
    "Suppliers", "Procurement",
    "ESD_Contributions", "SED_Contributions", "YES_Initiative",
    "Evidence",
    "Calc_Ownership", "Calc_MgmtControl", "Calc_SkillsDev",
    "Calc_ESD", "Calc_SED", "Calc_WhatIf",
    "History", "Settings",
    "Ref_Scorecard", "Ref_RecognitionLevels", "ChangeLog",
    "RunQueue",
]

# Which sheets carry evidence_id references
EVIDENCE_REF_SHEETS = [
    "Ownership", "Training", "Learnerships", "Bursaries",
    "Procurement", "ESD_Contributions", "SED_Contributions",
    "YES_Initiative",
]


def check_structural(wb: Workbook) -> list[Finding]:
    missing = [s for s in EXPECTED_SHEETS if s not in wb.sheetnames]
    return [
        Finding(Severity.ERROR, None, None, f"Missing expected sheet: {s}")
        for s in missing
    ]


def _collect_evidence_ids(wb: Workbook) -> set[str]:
    if "Evidence" not in wb.sheetnames:
        return set()
    ws = wb["Evidence"]
    headers = [c.value for c in ws[1]]
    if "evidence_id" not in headers:
        return set()
    col = headers.index("evidence_id") + 1
    return {ws.cell(row=r, column=col).value
            for r in range(2, ws.max_row + 1)
            if ws.cell(row=r, column=col).value}


def check_evidence_references(wb: Workbook) -> list[Finding]:
    known = _collect_evidence_ids(wb)
    findings: list[Finding] = []
    for sheet in EVIDENCE_REF_SHEETS:
        if sheet not in wb.sheetnames:
            continue
        ws = wb[sheet]
        headers = [c.value for c in ws[1]]
        # Find evidence_id-shaped columns (may include cert_evidence_id too)
        cols = [(i + 1, h) for i, h in enumerate(headers)
                if h and str(h).endswith("evidence_id")]
        for col_idx, col_name in cols:
            for row_idx in range(2, ws.max_row + 1):
                v = ws.cell(row=row_idx, column=col_idx).value
                if v is None or v == "":
                    continue
                if v not in known:
                    findings.append(Finding(
                        Severity.ERROR,
                        sheet,
                        row_idx,
                        f"Orphan {col_name}: {v!r} in {sheet}!{col_name} "
                        f"row {row_idx} (not present in Evidence sheet)",
                    ))
    return findings


def run_all_rules(wb: Workbook) -> list[Finding]:
    out: list[Finding] = []
    out.extend(check_structural(wb))
    out.extend(check_evidence_references(wb))
    return out
