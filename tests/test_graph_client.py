from __future__ import annotations
import io
import responses
import pytest
from bee_tracker.graph.client import GraphClient
from bee_tracker.errors import GraphError, ConcurrencyError


class FakeAuth:
    def token(self) -> str:
        return "t0ken"


BASE = "https://graph.microsoft.com/v1.0"


@responses.activate
def test_download_item_returns_bytes_and_etag():
    responses.get(
        f"{BASE}/drives/DRV/items/ITEM",
        json={"@microsoft.graph.downloadUrl": "https://cdn/file",
              "eTag": '"abc"',
              "lastModifiedDateTime": "2026-04-24T10:00:00Z"},
    )
    responses.get("https://cdn/file", body=b"EXCELBYTES", status=200)

    gc = GraphClient(FakeAuth())
    data, metadata = gc.download_item("DRV", "ITEM")
    assert data == b"EXCELBYTES"
    assert metadata.etag == '"abc"'
    assert metadata.last_modified == "2026-04-24T10:00:00Z"


@responses.activate
def test_upload_item_passes_if_match_header():
    responses.put(
        f"{BASE}/drives/DRV/items/ITEM/content",
        json={"id": "ITEM", "eTag": '"def"',
              "lastModifiedDateTime": "2026-04-24T10:05:00Z"},
        status=200,
    )
    gc = GraphClient(FakeAuth())
    meta = gc.upload_item("DRV", "ITEM", b"NEW", if_match='"abc"')
    assert meta.etag == '"def"'
    assert responses.calls[0].request.headers["If-Match"] == '"abc"'


@responses.activate
def test_upload_raises_concurrency_error_on_412():
    responses.put(
        f"{BASE}/drives/DRV/items/ITEM/content",
        json={"error": {"code": "preconditionFailed"}},
        status=412,
    )
    gc = GraphClient(FakeAuth())
    with pytest.raises(ConcurrencyError):
        gc.upload_item("DRV", "ITEM", b"NEW", if_match='"stale"')


@responses.activate
def test_list_folder_returns_children():
    responses.get(
        f"{BASE}/drives/DRV/items/FOLDER/children",
        json={"value": [
            {"id": "A", "name": "entity_a", "folder": {}},
            {"id": "B", "name": "entity_b", "folder": {}},
            {"id": "C", "name": "ict_scorecard.yaml", "file": {}},
        ]},
    )
    gc = GraphClient(FakeAuth())
    folders = gc.list_folders("DRV", "FOLDER")
    assert [f.name for f in folders] == ["entity_a", "entity_b"]
