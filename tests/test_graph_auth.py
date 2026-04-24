from __future__ import annotations
from unittest.mock import patch, MagicMock
import pytest
from bee_tracker.graph.auth import GraphAuth
from bee_tracker.errors import GraphError


def test_graph_auth_acquires_token_from_msal():
    fake_result = {"access_token": "abc123", "expires_in": 3599}
    with patch("bee_tracker.graph.auth.ConfidentialClientApplication") as MockApp:
        instance = MockApp.return_value
        instance.acquire_token_for_client.return_value = fake_result

        auth = GraphAuth(
            tenant_id="t", client_id="c", client_secret="s"
        )
        token = auth.token()
        assert token == "abc123"
        instance.acquire_token_for_client.assert_called_once_with(
            scopes=["https://graph.microsoft.com/.default"]
        )


def test_graph_auth_raises_on_acquire_failure():
    fake_result = {"error": "invalid_client", "error_description": "bad secret"}
    with patch("bee_tracker.graph.auth.ConfidentialClientApplication") as MockApp:
        MockApp.return_value.acquire_token_for_client.return_value = fake_result
        auth = GraphAuth(tenant_id="t", client_id="c", client_secret="s")
        with pytest.raises(GraphError, match="invalid_client"):
            auth.token()


def test_graph_auth_caches_token_until_near_expiry():
    # First call returns a long-lived token; second call should reuse
    fake_result = {"access_token": "cached", "expires_in": 3599}
    with patch("bee_tracker.graph.auth.ConfidentialClientApplication") as MockApp:
        inst = MockApp.return_value
        inst.acquire_token_for_client.return_value = fake_result
        auth = GraphAuth(tenant_id="t", client_id="c", client_secret="s")
        assert auth.token() == "cached"
        assert auth.token() == "cached"
        assert inst.acquire_token_for_client.call_count == 1
