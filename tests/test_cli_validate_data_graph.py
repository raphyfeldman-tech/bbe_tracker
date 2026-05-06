from __future__ import annotations
from pathlib import Path
from unittest.mock import MagicMock, patch
import shutil
from openpyxl import load_workbook
from bee_tracker.cli.validate_data import main


FIXTURE = Path("tests/fixtures/sample_workbook.xlsx")


def test_validate_data_uses_local_backend_by_default(tmp_path):
    """Default --backend local: reads from disk; exits 0 or 1 (not crash)."""
    root = tmp_path / "bee_tracker"
    entity = root / "entities" / "sample"
    entity.mkdir(parents=True)
    shutil.copy(FIXTURE, entity / "BEE_Tracker.xlsx")
    rc = main([
        "--root", str(root), "--entity", "sample",
    ])
    # Empty fixture triggers Settings-required-field errors; exit 1 is fine.
    assert rc in (0, 1)


def test_validate_data_with_backend_graph_invokes_graphbackend(tmp_path):
    """--backend graph constructs a GraphBackend (mocked) and uses it to load the workbook."""
    root = tmp_path / "bee_tracker"
    locator = tmp_path / "locator.yaml"
    locator.write_text("sample:\n  drive_id: DRV\n  item_id: ITEM\n")

    fake_backend = MagicMock()
    fake_handle = MagicMock()
    fake_handle.workbook = load_workbook(FIXTURE)
    fake_backend.open_entity_workbook.return_value = fake_handle

    with patch("bee_tracker.cli.validate_data.GraphBackend") as MockGraph:
        MockGraph.from_env.return_value = fake_backend
        rc = main([
            "--root", str(root), "--entity", "sample",
            "--backend", "graph",
            "--graph-locator", str(locator),
        ])
    MockGraph.from_env.assert_called_once_with(locator)
    fake_backend.open_entity_workbook.assert_called_once_with("sample")
    assert rc in (0, 1)
