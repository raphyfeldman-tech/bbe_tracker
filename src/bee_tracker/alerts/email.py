from __future__ import annotations
"""Microsoft Graph sendMail wrapper."""
import json
from urllib.parse import quote
from ..graph.client import GraphClient, BASE_URL, DEFAULT_TIMEOUT
from ..errors import GraphError


def send_email(
    client: GraphClient,
    *,
    from_user: str,
    to: list[str],
    subject: str,
    html_body: str,
) -> None:
    """Send an HTML email via /users/{from_user}/sendMail."""
    url = f"{BASE_URL}/users/{quote(from_user)}/sendMail"
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": html_body},
            "toRecipients": [
                {"emailAddress": {"address": addr}} for addr in to
            ],
        },
        "saveToSentItems": False,
    }
    headers = {
        "Authorization": f"Bearer {client._auth.token()}",
        "Content-Type": "application/json",
    }
    resp = client._session.post(
        url, data=json.dumps(payload).encode("utf-8"),
        headers=headers, timeout=DEFAULT_TIMEOUT,
    )
    if resp.status_code != 202:
        raise GraphError(f"sendMail failed ({resp.status_code}): {resp.text}")
