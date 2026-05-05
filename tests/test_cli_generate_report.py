from __future__ import annotations
from pathlib import Path
import shutil
import pytest
from openpyxl import load_workbook


FIXTURE = Path("tests/fixtures/sample_workbook.xlsx")
SCORECARD = Path("tests/fixtures/sample_ict_scorecard.yaml")
GROUP_SETTINGS = Path("tests/fixtures/sample_group_settings.yaml")
BRANDING_FIX = Path("tests/fixtures/sample_branding")


# Skip when WeasyPrint can't be imported (no Cairo/Pango on the dev machine)
pytest.importorskip("weasyprint", reason="WeasyPrint requires Cairo/Pango")


def _seed_entity_with_score(tmp_path):
    from bee_tracker.cli.calculate_score import run_score
    root = tmp_path / "bee_tracker"
    entity = root / "entities" / "sample"
    entity.mkdir(parents=True)
    shutil.copy(FIXTURE, entity / "BEE_Tracker.xlsx")
    shutil.copy(GROUP_SETTINGS, entity / "group_settings.yaml")
    shutil.copy(SCORECARD, root / "ict_scorecard.yaml")
    (entity / "branding").mkdir()
    shutil.copy(BRANDING_FIX / "colours.yaml", entity / "branding" / "colours.yaml")
    shutil.copy(BRANDING_FIX / "logo.png", entity / "branding" / "logo.png")

    wb = load_workbook(entity / "BEE_Tracker.xlsx")
    wb["Settings"].append(["entity_name", "Sample Entity"])
    wb["Settings"].append(["leviable_payroll", 10_000_000])
    wb["Settings"].append(["npat_current", 5_000_000])
    wb.save(entity / "BEE_Tracker.xlsx")

    run_score(root=root, entity_name="sample", requested_by="r@x")
    return root


def test_generate_report_writes_pdf(tmp_path):
    from bee_tracker.cli.generate_report import run_generate_report
    root = _seed_entity_with_score(tmp_path)
    out_path = tmp_path / "report.pdf"
    run_generate_report(
        root=root, entity_name="sample",
        report_type="adhoc", output=out_path,
        templates_dir=Path("templates"),
    )
    assert out_path.exists()
    assert out_path.read_bytes()[:4] == b"%PDF"
