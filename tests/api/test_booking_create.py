"""Booking creation + data integrity (BOOK-001/002)."""

import pytest

from src.api_client import auth_headers
from tests.schema_validation import validate_schema

pytestmark = pytest.mark.positive


def test_create_booking_returns_booking_id_and_matching_echo(
    api_client, auth_token, valid_booking_payload
):
    response = api_client.post("/booking", json=valid_booking_payload)

    assert response.status_code == 200
    assert "application/json" in response.headers.get("Content-Type", "")
    body = response.json()
    validate_schema(body, "booking-response-schema.json")
    assert isinstance(body.get("bookingid"), int)
    assert body["booking"] == valid_booking_payload

    # Cleanup: creation tests own their data (best-effort on shared host).
    api_client.delete(
        f"/booking/{body['bookingid']}",
        headers=auth_headers(auth_token),
    )


def test_created_booking_round_trips_identically(api_client, created_booking):
    bookingid = created_booking["bookingid"]
    expected = created_booking["payload"]

    response = api_client.get(f"/booking/{bookingid}")

    assert response.status_code == 200
    validate_schema(response.json(), "booking-schema.json")
    assert response.json() == expected
