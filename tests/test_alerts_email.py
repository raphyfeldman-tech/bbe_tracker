from __future__ import annotations
import responses
import pytest
from bee_tracker.alerts.email import send_email
from bee_tracker.errors import GraphError
from bee_tracker.graph.client import GraphClient


class FakeAuth:
    def token(self) -> str:
        return "t0ken"


BASE = "https://graph.microsoft.com/v1.0"


@responses.activate
def test_send_email_posts_to_send_mail():
    responses.post(
        f"{BASE}/users/from%40example.com/sendMail",
        status=202,
    )
    gc = GraphClient(FakeAuth())
    send_email(
        gc,
        from_user="from@example.com",
        to=["raphy@example.com", "exec@example.com"],
        subject="BEE Alert",
        html_body="<p>Hello</p>",
    )
    assert responses.calls[0].request.headers["Authorization"] == "Bearer t0ken"
    body = responses.calls[0].request.body
    assert b"BEE Alert" in body
    assert b"raphy@example.com" in body
    assert b"exec@example.com" in body


@responses.activate
def test_send_email_raises_on_non_202():
    responses.post(
        f"{BASE}/users/from%40example.com/sendMail",
        status=400,
        json={"error": {"code": "ErrorInvalidRecipients", "message": "bad"}},
    )
    gc = GraphClient(FakeAuth())
    with pytest.raises(GraphError, match="sendMail failed"):
        send_email(
            gc,
            from_user="from@example.com",
            to=["raphy@example.com"],
            subject="x", html_body="x",
        )
