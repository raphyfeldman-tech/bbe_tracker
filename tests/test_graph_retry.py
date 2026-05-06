from __future__ import annotations
import pytest
import responses
from bee_tracker.graph.client import GraphClient
from bee_tracker.errors import GraphError


class FakeAuth:
    def token(self) -> str:
        return "t0ken"


BASE = "https://graph.microsoft.com/v1.0"


@responses.activate
def test_list_folders_retries_on_429_then_succeeds():
    responses.get(
        f"{BASE}/drives/DRV/items/FOLDER/children",
        json={"error": {"code": "TooManyRequests"}},
        status=429,
        headers={"Retry-After": "0"},
    )
    responses.get(
        f"{BASE}/drives/DRV/items/FOLDER/children",
        json={"value": [{"id": "A", "name": "entity_a", "folder": {}}]},
        status=200,
    )

    gc = GraphClient(FakeAuth())
    result = gc.list_folders("DRV", "FOLDER")
    assert [f.name for f in result] == ["entity_a"]
    assert len(responses.calls) == 2


@responses.activate
def test_download_retries_on_503():
    responses.get(
        f"{BASE}/drives/DRV/items/ITEM",
        status=503,
        headers={"Retry-After": "0"},
    )
    responses.get(
        f"{BASE}/drives/DRV/items/ITEM",
        json={"@microsoft.graph.downloadUrl": "https://cdn/file",
              "eTag": '"abc"',
              "lastModifiedDateTime": "2026-05-04T10:00:00Z"},
        status=200,
    )
    responses.get("https://cdn/file", body=b"BYTES", status=200)

    gc = GraphClient(FakeAuth())
    data, meta = gc.download_item("DRV", "ITEM")
    assert data == b"BYTES"


@responses.activate
def test_retry_gives_up_after_max_attempts():
    for _ in range(5):
        responses.get(
            f"{BASE}/drives/DRV/items/FOLDER/children",
            status=429,
            headers={"Retry-After": "0"},
        )
    gc = GraphClient(FakeAuth())
    with pytest.raises(GraphError, match="429"):
        gc.list_folders("DRV", "FOLDER")


@responses.activate
def test_no_retry_on_4xx_other_than_429():
    """A 404 should NOT be retried — it's a client error."""
    responses.get(
        f"{BASE}/drives/DRV/items/FOLDER/children",
        status=404,
    )
    gc = GraphClient(FakeAuth())
    with pytest.raises(GraphError, match="404"):
        gc.list_folders("DRV", "FOLDER")
    assert len(responses.calls) == 1
