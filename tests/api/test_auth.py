"""Authentication contract (AUTH-001..005)."""

import pytest

from src.api_client import auth_headers
from src.test_data import auth_payloads, unique_booking_payload
from tests.schema_validation import validate_schema

pytestmark = pytest.mark.auth


def _auth(api_client, body: dict):
    return api_client.post("/auth", json=body)


def test_authenticate_with_valid_credentials_returns_usable_token(api_client):
    creds = auth_payloads()
    response = _auth(api_client, creds["valid"])

    assert response.status_code == 200
    validate_schema(response.json(), "auth-schema.json")
    assert "application/json" in response.headers.get("Content-Type", "")
    token = response.json().get("token")
    assert isinstance(token, str) and len(token) > 0

    # The token must actually authorize a write (AUTH-001/006).
    payload = unique_booking_payload(prefix="Auth")
    bookingid = api_client.post("/booking", json=payload).json()["bookingid"]
    try:
        updated = api_client.put(
            f"/booking/{bookingid}",
            json={**payload, "firstname": payload["firstname"] + "-ok"},
            headers=auth_headers(token),
        )
        assert updated.status_code == 200
        assert updated.json()["firstname"] == payload["firstname"] + "-ok"
    finally:
        api_client.delete(f"/booking/{bookingid}", headers=auth_headers(token))


@pytest.mark.parametrize(
    "credentials",
    ["wrong_password", "unknown_user", "empty_body", "empty_strings"],
)
def test_authenticate_with_invalid_credentials_reports_bad_credentials(
    api_client, credentials
):
    response = _auth(api_client, auth_payloads()[credentials])

    assert response.status_code == 200
    validate_schema(response.json(), "auth-schema.json")
    assert response.json() == {"reason": "Bad credentials"}
