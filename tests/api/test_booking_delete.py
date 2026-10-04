"""Booking deletion tests (BOOK-010..012)."""

import pytest

from src.api_client import auth_headers


@pytest.mark.positive
def test_delete_removes_booking(api_client, auth_token, created_booking):
    bookingid = created_booking["bookingid"]

    deleted = api_client.delete(
        f"/booking/{bookingid}", headers=auth_headers(auth_token)
    )

    assert deleted.status_code == 201
    assert deleted.text == "Created"
    created_booking["_deleted"] = True

    fetched = api_client.get(f"/booking/{bookingid}")
    assert fetched.status_code == 404
    assert fetched.text == "Not Found"


@pytest.mark.negative
@pytest.mark.parametrize("cookie", [None, "token=invalid123"], ids=["missing", "invalid"])
def test_delete_without_valid_auth_is_forbidden_and_booking_survives(
    api_client, created_booking, cookie
):
    bookingid = created_booking["bookingid"]
    headers = {"Cookie": cookie} if cookie else {}

    response = api_client.delete(f"/booking/{bookingid}", headers=headers)

    assert response.status_code == 403
    assert response.text == "Forbidden"
    fetched = api_client.get(f"/booking/{bookingid}")
    assert fetched.status_code == 200
    assert fetched.json() == created_booking["payload"]


@pytest.mark.negative
def test_redelete_returns_405(api_client, auth_token, created_booking):
    bookingid = created_booking["bookingid"]
    headers = auth_headers(auth_token)
    deleted = api_client.delete(f"/booking/{bookingid}", headers=headers)
    assert deleted.status_code == 201
    created_booking["_deleted"] = True

    response = api_client.delete(f"/booking/{bookingid}", headers=headers)

    assert response.status_code == 405
    assert response.text == "Method Not Allowed"
    assert "text/plain" in response.headers.get("Content-Type", "")
