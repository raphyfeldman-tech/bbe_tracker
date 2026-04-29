from __future__ import annotations
from io import BytesIO
from unittest.mock import MagicMock
import pytest
from openpyxl import Workbook
from bee_tracker.workbook.backends import GraphBackend
from bee_tracker.graph.client import ItemMetadata
from bee_tracker.errors import WorkbookError


def _make_workbook_bytes() -> bytes:
    wb = Workbook()
    wb.active.title = "Settings"
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_graph_backend_resolve_unknown_entity_raises():
    backend = GraphBackend(MagicMock(), {})
    with pytest.raises(WorkbookError, match="Unknown entity"):
        backend.open_entity_workbook("nope")


def test_graph_backend_open_populates_etag_token():
    client = MagicMock()
    client.download_item.return_value = (
        _make_workbook_bytes(),
        ItemMetadata(etag='"abc"', last_modified="2026-01-01T00:00:00Z"),
    )
    backend = GraphBackend(client, {"sample": ("DRV", "ITEM")})
    handle = backend.open_entity_workbook("sample")
    assert handle.entity_name == "sample"
    assert handle.original_token == '"abc"'


def test_graph_backend_save_passes_if_match_then_refreshes_token():
    client = MagicMock()
    client.download_item.return_value = (
        _make_workbook_bytes(),
        ItemMetadata(etag='"abc"', last_modified="2026-01-01T00:00:00Z"),
    )
    client.upload_item.return_value = ItemMetadata(
        etag='"def"', last_modified="2026-01-02T00:00:00Z",
    )
    backend = GraphBackend(client, {"sample": ("DRV", "ITEM")})
    handle = backend.open_entity_workbook("sample")
    backend.save(handle)
    # Verify If-Match was the original eTag
    _, kwargs = client.upload_item.call_args
    assert kwargs.get("if_match") == '"abc"'
    # Verify token refreshed (Plan 1 Task 6 fix)
    assert handle.original_token == '"def"'
