"""Shared pytest fixtures (Phase 14).

Scopes: ``api_client`` / ``base_url`` / ``auth_token`` are session-scoped
(cheap, stateless — the shared session never carries credentials);
``valid_booking_payload`` / ``created_booking`` are function-scoped so every
test gets fresh, isolated data (Rule 8).

Contract validation uses ``tests.schema_validation`` and the schemas in
``tests/schemas/``.
"""

import warnings

import pytest

from src import config
from src.api_client import ApiClient, auth_headers


def _cleanup_booking(api_client: ApiClient, bookingid: int, token: str) -> None:
    try:
        response = api_client.delete(
            f"/booking/{bookingid}", headers=auth_headers(token)
        )
        if response.status_code != 201:
            warnings.warn(
                f"cleanup delete of booking {bookingid} returned HTTP "
                f"{response.status_code}: {response.text[:200]}",
                RuntimeWarning,
                stacklevel=2,
            )
    except Exception as exc:  # noqa: BLE001 - best-effort cleanup only
        warnings.warn(
            f"cleanup delete of booking {bookingid} failed: {exc}",
            RuntimeWarning,
            stacklevel=2,
        )


@pytest.fixture(scope="session")
def api_client() -> ApiClient:
    return ApiClient()


@pytest.fixture(scope="session")
def base_url() -> str:
    return config.get_base_url()


@pytest.fixture
def valid_booking_payload() -> dict:
    from src.test_data import valid_booking_payload as factory

    return factory()


@pytest.fixture(scope="session")
def auth_token(api_client) -> str:
    """Live token for the session. Never stored on the shared client session.

    Authenticated calls pass ``Cookie: token=...`` explicitly per request so
    unauthenticated tests on the shared ``api_client`` stay honest.
    """
    resp = api_client.post(
        "/auth",
        json={"username": config.get_username(), "password": config.get_password()},
    )
    assert resp.status_code == 200, f"setup: auth failed: {resp.status_code} {resp.text[:200]}"
    token = resp.json().get("token")
    assert isinstance(token, str) and token, "setup: no token in auth response"
    return token


@pytest.fixture
def created_booking(api_client, auth_token) -> dict:
    """Create a booking, yield ``{"bookingid", "payload"}``, delete afterwards.

    Function scope: every test gets a fresh, isolated booking (Rule 8).
    Cleanup is best-effort (shared public host): teardown problems are
    reported, never fail the test that already passed.
    """
    from src.test_data import unique_booking_payload

    payload = unique_booking_payload()
    created = api_client.post("/booking", json=payload)
    assert created.status_code == 200, f"setup: create failed: {created.status_code}"
    bookingid = created.json()["bookingid"]
    booking = {"bookingid": bookingid, "payload": payload}
    yield booking
    if booking.get("_deleted"):
        return
    _cleanup_booking(api_client, bookingid, auth_token)
