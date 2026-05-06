from __future__ import annotations
from pathlib import Path
import shutil
from unittest.mock import MagicMock, patch
from openpyxl import load_workbook
from bee_tracker.cli.send_alerts import run_send_alerts


FIXTURE = Path("tests/fixtures/sample_workbook.xlsx")
SCORECARD = Path("tests/fixtures/sample_ict_scorecard.yaml")
GROUP_SETTINGS = Path("tests/fixtures/sample_group_settings.yaml")


def _seed(tmp_path):
    root = tmp_path / "bee_tracker"
    entity = root / "entities" / "sample"
    entity.mkdir(parents=True)
    shutil.copy(FIXTURE, entity / "BEE_Tracker.xlsx")
    shutil.copy(GROUP_SETTINGS, entity / "group_settings.yaml")
    shutil.copy(SCORECARD, root / "ict_scorecard.yaml")
    return root


def test_send_alerts_dispatches_priority_breach(tmp_path):
    root = _seed(tmp_path)
    wb_path = root / "entities" / "sample" / "BEE_Tracker.xlsx"
    wb = load_workbook(wb_path)
    wb["Settings"].append(["entity_name", "Sample"])
    wb["Settings"].append(["leviable_payroll", 10_000_000])
    wb["Settings"].append(["npat_current", 5_000_000])
    wb.save(wb_path)

    fake_send = MagicMock()
    with patch("bee_tracker.cli.send_alerts.send_email", fake_send):
        run_send_alerts(
            root=root, entity_name="sample",
            graph_client=MagicMock(),
            from_user="bee-tracker@example",
            templates_dir=Path("templates"),
        )
    assert fake_send.called
    sent_subjects = [call.kwargs["subject"] for call in fake_send.call_args_list]
    assert any("BREACH" in s.upper() for s in sent_subjects)


def test_send_alerts_skips_when_no_recipients_configured(tmp_path):
    root = _seed(tmp_path)
    gs_path = root / "entities" / "sample" / "group_settings.yaml"
    text = gs_path.read_text()
    import yaml
    data = yaml.safe_load(text)
    data["alerts"] = {}
    gs_path.write_text(yaml.dump(data))

    fake_send = MagicMock()
    with patch("bee_tracker.cli.send_alerts.send_email", fake_send):
        run_send_alerts(
            root=root, entity_name="sample",
            graph_client=MagicMock(),
            from_user="bee-tracker@example",
            templates_dir=Path("templates"),
        )
    fake_send.assert_not_called()
