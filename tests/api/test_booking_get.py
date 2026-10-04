"""Booking retrieval + listing/filtering (BOOK-003/004/005, FILT-001/002)."""

import pytest

from tests.schema_validation import validate_schema


def test_get_existing_booking_returns_created_payload(api_client, created_booking):
    response = api_client.get(f"/booking/{created_booking['bookingid']}")

    assert response.status_code == 200
    assert "application/json" in response.headers.get("Content-Type", "")
    validate_schema(response.json(), "booking-schema.json")
    data = response.json()
    assert data["firstname"] == created_booking["payload"]["firstname"]
    assert data["lastname"] == created_booking["payload"]["lastname"]
    assert isinstance(data["totalprice"], (int, float))
    assert isinstance(data["depositpaid"], bool)
    assert set(data["bookingdates"]) == {"checkin", "checkout"}


def test_get_nonexistent_booking_returns_404(api_client):
    response = api_client.get("/booking/999999")

    assert response.status_code == 404
    assert "text/plain" in response.headers.get("Content-Type", "")


def test_get_malformed_booking_id_returns_404_not_400(api_client):
    response = api_client.get("/booking/abc")

    assert response.status_code == 404
    assert response.text == "Not Found"
    assert "text/plain" in response.headers.get("Content-Type", "")


def test_list_bookings_returns_id_array_shape_only(api_client):
    response = api_client.get("/booking")

    assert response.status_code == 200
    validate_schema(response.json(), "booking-list-schema.json")
    data = response.json()
    assert isinstance(data, list) and len(data) > 0
    for entry in data[:20]:
        assert isinstance(entry.get("bookingid"), int)


@pytest.mark.positive
def test_filter_by_firstname_narrows_results(api_client, created_booking):
    firstname = created_booking["payload"]["firstname"]

    response = api_client.get("/booking", params={"firstname": firstname})

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(e.get("bookingid") == created_booking["bookingid"] for e in data)
