from __future__ import annotations
import time
from msal import ConfidentialClientApplication
from ..errors import GraphError


class GraphAuth:
    """App-only auth via MSAL client-credentials flow with in-memory token cache."""

    SCOPES = ["https://graph.microsoft.com/.default"]
    RENEW_BUFFER_SECONDS = 120

    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self._app = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
        )
        self._token: str | None = None
        self._expires_at: float = 0.0

    def token(self) -> str:
        now = time.time()
        if self._token and now < self._expires_at - self.RENEW_BUFFER_SECONDS:
            return self._token
        result = self._app.acquire_token_for_client(scopes=self.SCOPES)
        if "access_token" not in result:
            err = result.get("error", "unknown")
            desc = result.get("error_description", "")
            raise GraphError(f"Token acquisition failed: {err} — {desc}")
        self._token = result["access_token"]
        self._expires_at = now + result.get("expires_in", 3600)
        return self._token
