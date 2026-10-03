"""Health-check contract (HLTH-001..003)."""

import pytest

pytestmark = pytest.mark.smoke


def test_get_ping_returns_201_created(api_client):
    response = api_client.get("/ping")

    assert response.status_code == 201
    assert "text/plain" in response.headers.get("Content-Type", "")
    assert response.text == "Created"


def test_head_ping_returns_201_with_empty_body(api_client):
    response = api_client.head("/ping")

    assert response.status_code == 201
    assert response.text == ""
