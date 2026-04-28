from __future__ import annotations
from dataclasses import dataclass
import requests
from .auth import GraphAuth
from ..errors import GraphError, ConcurrencyError


BASE_URL = "https://graph.microsoft.com/v1.0"


@dataclass(frozen=True)
class ItemMetadata:
    etag: str
    last_modified: str  # ISO-8601 as returned by Graph


@dataclass(frozen=True)
class FolderChild:
    id: str
    name: str


class GraphClient:
    def __init__(self, auth: GraphAuth, session: requests.Session | None = None):
        self._auth = auth
        self._session = session or requests.Session()

    def _headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        h = {"Authorization": f"Bearer {self._auth.token()}"}
        if extra:
            h.update(extra)
        return h

    def download_item(self, drive_id: str, item_id: str) -> tuple[bytes, ItemMetadata]:
        meta_url = f"{BASE_URL}/drives/{drive_id}/items/{item_id}"
        resp = self._session.get(meta_url, headers=self._headers())
        if resp.status_code != 200:
            raise GraphError(f"Metadata fetch failed ({resp.status_code}): {resp.text}")
        meta = resp.json()
        dl_url = meta.get("@microsoft.graph.downloadUrl")
        if not dl_url:
            raise GraphError("No downloadUrl in item metadata")
        dl = self._session.get(dl_url)
        if dl.status_code != 200:
            raise GraphError(f"Download failed ({dl.status_code})")
        return dl.content, ItemMetadata(
            etag=meta["eTag"],
            last_modified=meta["lastModifiedDateTime"],
        )

    def upload_item(
        self, drive_id: str, item_id: str, content: bytes, *, if_match: str
    ) -> ItemMetadata:
        url = f"{BASE_URL}/drives/{drive_id}/items/{item_id}/content"
        headers = self._headers({
            "If-Match": if_match,
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        })
        resp = self._session.put(url, data=content, headers=headers)
        if resp.status_code == 412:
            raise ConcurrencyError(
                "Workbook was modified remotely during run (If-Match precondition failed)"
            )
        if resp.status_code not in (200, 201):
            raise GraphError(f"Upload failed ({resp.status_code}): {resp.text}")
        meta = resp.json()
        return ItemMetadata(
            etag=meta["eTag"],
            last_modified=meta["lastModifiedDateTime"],
        )

    def list_folders(self, drive_id: str, folder_id: str) -> list[FolderChild]:
        url = f"{BASE_URL}/drives/{drive_id}/items/{folder_id}/children"
        resp = self._session.get(url, headers=self._headers())
        if resp.status_code != 200:
            raise GraphError(f"List failed ({resp.status_code}): {resp.text}")
        return [
            FolderChild(id=c["id"], name=c["name"])
            for c in resp.json().get("value", [])
            if "folder" in c
        ]
