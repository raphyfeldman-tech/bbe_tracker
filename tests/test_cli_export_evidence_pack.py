from __future__ import annotations
from pathlib import Path
import shutil
import zipfile
from openpyxl import load_workbook
from bee_tracker.cli.export_evidence_pack import main


FIXTURE = Path("tests/fixtures/sample_workbook.xlsx")
GROUP_SETTINGS = Path("tests/fixtures/sample_group_settings.yaml")
SCORECARD = Path("tests/fixtures/sample_ict_scorecard.yaml")


def test_cli_export_evidence_pack(tmp_path):
    root = tmp_path / "bee_tracker"
    entity = root / "entities" / "sample"
    entity.mkdir(parents=True)
    shutil.copy(FIXTURE, entity / "BEE_Tracker.xlsx")
    shutil.copy(GROUP_SETTINGS, entity / "group_settings.yaml")
    shutil.copy(SCORECARD, root / "ict_scorecard.yaml")

    (entity / "evidence" / "ownership").mkdir(parents=True)
    (entity / "evidence" / "ownership" / "ev-0001.pdf").write_bytes(b"%PDF-1.4 fake")

    wb = load_workbook(entity / "BEE_Tracker.xlsx")
    wb["Evidence"].append([
        "EV-0001", "Ownership", "Cert", "evidence/ownership/ev-0001.pdf",
        "2025-10-01", "r@x", "2025-10-01T10:00:00",
    ])
    wb.save(entity / "BEE_Tracker.xlsx")

    out_zip = tmp_path / "pack.zip"
    rc = main([
        "--root", str(root), "--entity", "sample",
        "--output", str(out_zip),
    ])
    assert rc == 0
    assert out_zip.exists()
    with zipfile.ZipFile(out_zip) as z:
        names = z.namelist()
        assert any("ev-0001.pdf" in n for n in names)
        assert any("BEE_Tracker.xlsx" in n for n in names)
