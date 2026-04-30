from __future__ import annotations
"""Canonical workbook schema definitions.

The single source of truth for sheet names, tab colours, and column headers.
Imported by ``scripts/make_template.py`` (template generator),
``bee_tracker.validation.rules`` (structural checks), and the readers in
``bee_tracker.workbook`` (header lookups).
"""


TAB_COLOURS = {
    "green":  "00B050",
    "blue":   "4472C4",
    "grey":   "BFBFBF",
    "red":    "C00000",
}

SHEETS: list[tuple[str, str, list[str]]] = [
    ("Dashboard", "green", []),
    ("GapAnalysis", "green", []),
    ("WhatIf", "blue", []),
    ("Ownership", "blue", [
        "shareholder_name",
        "black_voting_rights_pct",
        "black_economic_interest_pct",
        "black_women_voting_rights_pct",
        "black_women_economic_interest_pct",
        "black_designated_groups_pct",
        "net_value_pct",
        "new_entrants_pct",
        "effective_date",
        "evidence_id",
    ]),
    ("Employees", "blue", [
        "employee_id", "full_name", "race", "is_black", "gender",
        "disability", "foreign_national", "occupational_level",
        "is_executive_director", "is_non_executive_director",
        "start_date", "end_date", "fte_months_in_period", "annual_salary",
    ]),
    ("MgmtControl_Summary", "green", []),
    ("Training", "blue", [
        "event_id", "employee_id", "course_name", "training_category",
        "accredited", "training_spend", "salary_cost_during_training",
        "hours", "start_date", "end_date", "is_discretionary", "evidence_id",
    ]),
    ("Learnerships", "blue", [
        "participant_id", "is_employee", "race", "gender", "disability",
        "learnership_type", "saqa_registered", "start_date", "end_date",
        "stipend_paid", "absorbed", "evidence_id",
    ]),
    ("Bursaries", "blue", [
        "beneficiary_id", "race", "gender", "disability",
        "institution", "internal_or_external", "academic_year",
        "amount", "evidence_id",
    ]),
    ("Suppliers", "blue", [
        "supplier_id", "supplier_name", "cert_level", "cert_type",
        "black_ownership_pct", "black_women_ownership_pct",
        "is_51pct_black_owned", "is_30pct_black_women_owned",
        "is_emp_qse_51pct_black", "is_designated_group_supplier",
        "cert_issue_date", "cert_expiry_date", "cert_evidence_id",
    ]),
    ("Procurement", "blue", [
        "supplier_id", "period_spend_ex_vat", "period_excluded_spend",
        "exclusion_notes", "avg_payment_terms_days", "evidence_id",
    ]),
    ("ESD_Contributions", "blue", [
        "contribution_id", "type", "recipient_name",
        "recipient_black_ownership_pct", "recipient_entity_type",
        "contribution_form", "cash_value", "in_kind_value",
        "recognition_multiplier", "date", "evidence_id",
    ]),
    ("SED_Contributions", "blue", [
        "contribution_id", "beneficiary_name", "beneficiary_type",
        "black_beneficiary_pct", "contribution_form",
        "cash_value", "in_kind_value", "date", "evidence_id",
    ]),
    ("YES_Initiative", "blue", [
        "participant_id", "race", "gender", "disability",
        "age_at_start", "start_date", "end_date",
        "twelve_months_completed", "absorbed",
        "quality_job_indicator", "monthly_stipend", "evidence_id",
    ]),
    ("Evidence", "blue", [
        "evidence_id", "element", "description",
        "filepath", "date", "uploaded_by", "uploaded_at",
    ]),
    ("Calc_Ownership", "green", []),
    ("Calc_MgmtControl", "green", []),
    ("Calc_SkillsDev", "green", []),
    ("Calc_ESD", "green", []),
    ("Calc_SED", "green", []),
    ("Calc_WhatIf", "green", []),
    ("History", "grey", []),
    ("Settings", "grey", ["key", "value"]),
    ("Ref_Scorecard", "grey", []),
    ("Ref_RecognitionLevels", "grey", ["level", "recognition_pct"]),
    ("ChangeLog", "grey", [
        "timestamp", "actor", "scope", "summary",
    ]),
    ("RunQueue", "red", [
        "request_id", "requested_at", "requested_by", "scope",
        "status", "started_at", "completed_at",
        "error_message", "result_path",
    ]),
]

EXPECTED_SHEET_NAMES: list[str] = [name for name, _, _ in SHEETS]

# Sheets that should be hidden by default in the generated template.
# Users can unhide them in Excel for debugging, but the daemon doesn't
# rely on visibility.
HIDDEN_SHEETS = {"RunQueue"}


def headers_for(sheet_name: str) -> list[str]:
    """Return a copy of the header list for ``sheet_name``, or ``[]`` if unknown."""
    for name, _, headers in SHEETS:
        if name == sheet_name:
            return list(headers)
    return []
