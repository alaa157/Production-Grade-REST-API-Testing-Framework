"""Booking update / partial-update tests (BOOK-006..009)."""

import pytest

from src.api_client import auth_headers
from tests.schema_validation import validate_schema


@pytest.mark.positive
def test_put_replaces_booking_and_persists(api_client, auth_token, created_booking):
    bookingid = created_booking["bookingid"]
    replacement = {
        **created_booking["payload"],
        "firstname": "PutUpdated",
        "totalprice": 275,
        "depositpaid": False,
    }

    updated = api_client.put(
        f"/booking/{bookingid}",
        json=replacement,
        headers=auth_headers(auth_token),
    )

    assert updated.status_code == 200
    validate_schema(updated.json(), "booking-schema.json")
    assert updated.json() == replacement

    fetched = api_client.get(f"/booking/{bookingid}")
    assert fetched.status_code == 200
    validate_schema(fetched.json(), "booking-schema.json")
    assert fetched.json() == replacement


@pytest.mark.negative
@pytest.mark.parametrize("cookie", [None, "token=invalid123"], ids=["missing", "invalid"])
def test_put_without_valid_auth_is_forbidden_and_does_not_change_booking(
    api_client, created_booking, cookie
):
    bookingid = created_booking["bookingid"]
    headers = {"Cookie": cookie} if cookie else {}
    replacement = {**created_booking["payload"], "firstname": "MustNotPersist"}

    response = api_client.put(
        f"/booking/{bookingid}",
        json=replacement,
        headers=headers,
    )

    assert response.status_code == 403
    assert response.text == "Forbidden"
    unchanged = api_client.get(f"/booking/{bookingid}")
    assert unchanged.status_code == 200
    assert unchanged.json() == created_booking["payload"]


@pytest.mark.positive
def test_patch_merges_fields_and_persists(api_client, auth_token, created_booking):
    bookingid = created_booking["bookingid"]
    patch = {"firstname": "PatchUpdated"}

    response = api_client.patch(
        f"/booking/{bookingid}",
        json=patch,
        headers=auth_headers(auth_token),
    )

    expected = {**created_booking["payload"], **patch}
    assert response.status_code == 200
    validate_schema(response.json(), "booking-schema.json")
    assert response.json() == expected

    fetched = api_client.get(f"/booking/{bookingid}")
    assert fetched.status_code == 200
    validate_schema(fetched.json(), "booking-schema.json")
    assert fetched.json() == expected


@pytest.mark.negative
@pytest.mark.parametrize("cookie", [None, "token=invalid123"], ids=["missing", "invalid"])
def test_patch_without_valid_auth_is_forbidden_and_does_not_change_booking(
    api_client, created_booking, cookie
):
    bookingid = created_booking["bookingid"]
    headers = {"Cookie": cookie} if cookie else {}

    response = api_client.patch(
        f"/booking/{bookingid}",
        json={"firstname": "MustNotPersist"},
        headers=headers,
    )

    assert response.status_code == 403
    assert response.text == "Forbidden"
    unchanged = api_client.get(f"/booking/{bookingid}")
    assert unchanged.status_code == 200
    assert unchanged.json() == created_booking["payload"]
