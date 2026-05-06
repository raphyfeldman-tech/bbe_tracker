from __future__ import annotations
import responses
from bee_tracker.graph.client import GraphClient


class FakeAuth:
    def token(self) -> str:
        return "t0ken"


BASE = "https://graph.microsoft.com/v1.0"


@responses.activate
def test_list_folders_follows_nextlink():
    responses.get(
        f"{BASE}/drives/DRV/items/FOLDER/children",
        json={
            "value": [
                {"id": "A", "name": "entity_a", "folder": {}},
                {"id": "B", "name": "entity_b", "folder": {}},
            ],
            "@odata.nextLink": f"{BASE}/drives/DRV/items/FOLDER/children?$skip=2",
        },
        status=200,
    )
    responses.get(
        f"{BASE}/drives/DRV/items/FOLDER/children?$skip=2",
        json={
            "value": [
                {"id": "C", "name": "entity_c", "folder": {}},
            ],
        },
        status=200,
        match_querystring=True,
    )
    gc = GraphClient(FakeAuth())
    result = gc.list_folders("DRV", "FOLDER")
    names = [f.name for f in result]
    assert names == ["entity_a", "entity_b", "entity_c"]


@responses.activate
def test_list_folders_no_pagination_single_page():
    responses.get(
        f"{BASE}/drives/DRV/items/FOLDER/children",
        json={
            "value": [{"id": "A", "name": "entity_a", "folder": {}}],
        },
        status=200,
    )
    gc = GraphClient(FakeAuth())
    result = gc.list_folders("DRV", "FOLDER")
    assert [f.name for f in result] == ["entity_a"]
