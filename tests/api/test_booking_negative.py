"""Observed booking and authentication failure contracts (NEG scenarios)."""

import pytest

from src.api_client import auth_headers
from src.test_data import valid_booking_payload

pytestmark = pytest.mark.negative


def _assert_created_booking_is_removed(api_client, auth_token, response):
    if response.status_code == 200:
        bookingid = response.json()["bookingid"]
        deleted = api_client.delete(
            f"/booking/{bookingid}", headers=auth_headers(auth_token)
        )
        assert deleted.status_code == 201


@pytest.mark.parametrize(
    ("field", "invalid_value", "expected_value"),
    [
        ("totalprice", "not-a-number", None),
        ("depositpaid", "yes", True),
    ],
)
def test_create_records_observed_type_coercion(
    api_client, auth_token, field, invalid_value, expected_value
):
    payload = valid_booking_payload(**{field: invalid_value})
    response = api_client.post("/booking", json=payload)
    try:
        assert response.status_code == 200
        assert response.json()["booking"][field] == expected_value
    finally:
        _assert_created_booking_is_removed(api_client, auth_token, response)


def test_create_with_invalid_date_records_observed_artifact(api_client, auth_token):
    payload = valid_booking_payload(
        bookingdates={"checkin": "not-a-date", "checkout": "2026-01-05"}
    )
    response = api_client.post("/booking", json=payload)
    try:
        assert response.status_code == 200
        assert (
            response.json()["booking"]["bookingdates"]["checkin"] == "0NaN-aN-aN"
        )
    finally:
        _assert_created_booking_is_removed(api_client, auth_token, response)


def test_create_with_malformed_json_returns_400(api_client):
    response = api_client.post("/booking", data="{bad json")

    assert response.status_code == 400
    assert "text/plain" in response.headers.get("Content-Type", "")


def test_create_ignores_unknown_field(api_client, auth_token):
    payload = valid_booking_payload(surprise="unexpected")
    response = api_client.post("/booking", json=payload)
    try:
        assert response.status_code == 200
        assert "surprise" not in response.json()["booking"]
    finally:
        _assert_created_booking_is_removed(api_client, auth_token, response)


def test_create_preserves_null_optional_field(api_client, auth_token):
    payload = valid_booking_payload(additionalneeds=None)
    response = api_client.post("/booking", json=payload)
    try:
        assert response.status_code == 200
        assert response.json()["booking"]["additionalneeds"] is None
    finally:
        _assert_created_booking_is_removed(api_client, auth_token, response)


@pytest.mark.parametrize(
    "missing_field",
    ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"],
)
def test_create_without_required_field_returns_observed_500(
    api_client, missing_field
):
    """NEG-001/002/003 + BND-007: any missing core field crashes (500)."""
    payload = valid_booking_payload()
    payload.pop(missing_field)

    response = api_client.post("/booking", json=payload)

    assert response.status_code == 500
    assert "text/plain" in response.headers.get("Content-Type", "")


def test_create_with_empty_firstname_is_stored_verbatim(
    api_client, auth_token
):
    """NEG-007: empty strings are accepted as-is (200)."""
    payload = valid_booking_payload(firstname="")
    response = api_client.post("/booking", json=payload)
    try:
        assert response.status_code == 200
        assert response.json()["booking"]["firstname"] == ""
    finally:
        _assert_created_booking_is_removed(api_client, auth_token, response)


@pytest.mark.parametrize("totalprice", [0, -50, 999999999])
def test_create_with_boundary_price_is_stored_as_is(
    api_client, auth_token, totalprice
):
    """BND-001/002/003: zero, negative, and huge prices accepted (200)."""
    payload = valid_booking_payload(totalprice=totalprice)
    response = api_client.post("/booking", json=payload)
    try:
        assert response.status_code == 200
        assert response.json()["booking"]["totalprice"] == totalprice
    finally:
        _assert_created_booking_is_removed(api_client, auth_token, response)


def test_create_with_inverted_dates_is_stored_without_range_check(
    api_client, auth_token
):
    """BND-004: checkout-before-checkin accepted as-is (200)."""
    payload = valid_booking_payload(
        bookingdates={"checkin": "2026-01-10", "checkout": "2026-01-05"}
    )
    response = api_client.post("/booking", json=payload)
    try:
        assert response.status_code == 200
        assert response.json()["booking"]["bookingdates"] == {
            "checkin": "2026-01-10",
            "checkout": "2026-01-05",
        }
    finally:
        _assert_created_booking_is_removed(api_client, auth_token, response)


def test_create_with_very_long_name_is_stored_verbatim(
    api_client, auth_token
):
    """BND-005: 500-char firstname stored full-length (200)."""
    payload = valid_booking_payload(firstname="B" * 500)
    response = api_client.post("/booking", json=payload)
    try:
        assert response.status_code == 200
        assert response.json()["booking"]["firstname"] == "B" * 500
    finally:
        _assert_created_booking_is_removed(api_client, auth_token, response)


@pytest.mark.parametrize("booking_id", ["999999", "9999999999", "abc"])
def test_get_invalid_booking_id_returns_404(api_client, booking_id):
    response = api_client.get(f"/booking/{booking_id}")

    assert response.status_code == 404
    assert "text/plain" in response.headers.get("Content-Type", "")


def test_delete_invalid_token_is_forbidden(api_client, created_booking):
    response = api_client.delete(
        f"/booking/{created_booking['bookingid']}",
        headers=auth_headers("invalid123"),
    )

    assert response.status_code == 403
    assert response.text == "Forbidden"


def test_put_invalid_token_is_forbidden(api_client, created_booking):
    response = api_client.put(
        f"/booking/{created_booking['bookingid']}",
        json=created_booking["payload"],
        headers=auth_headers("invalid123"),
    )

    assert response.status_code == 403
    assert response.text == "Forbidden"


def test_patch_invalid_token_is_forbidden(api_client, created_booking):
    response = api_client.patch(
        f"/booking/{created_booking['bookingid']}",
        json={"firstname": "MustNotPersist"},
        headers=auth_headers("invalid123"),
    )

    assert response.status_code == 403
    assert response.text == "Forbidden"
