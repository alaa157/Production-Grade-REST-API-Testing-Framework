"""Reusable test-data factories (Phase 4).

All payloads mirror the verified contract in docs/api-inventory.md.
Invalid/boundary entries record the *observed* 2026-10-03 behavior in
``expected_note`` — assertions must match reality, not assumptions.
"""

from __future__ import annotations

import time
import uuid

from src.config import get_password, get_username


# ---------------------------------------------------------------------------
# Valid data
# ---------------------------------------------------------------------------
def valid_booking_payload(**overrides) -> dict:
    """Standard booking; override any field, including nested ``bookingdates``.

    Example:
        valid_booking_payload(totalprice=200, bookingdates={"checkin": ..., ...})
    """
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-05"},
        "additionalneeds": "Breakfast",
    }
    if "bookingdates" in overrides and isinstance(overrides["bookingdates"], dict):
        payload["bookingdates"] = {
            **payload["bookingdates"],
            **overrides.pop("bookingdates"),
        }
    payload.update(overrides)
    return payload


def unique_booking_payload(prefix: str = "E2E", **overrides) -> dict:
    """Self-created, cross-traffic-safe payload (unique firstname per run).

    The public host is shared; unique names let a run identify its own
    bookings via ``GET /booking?firstname=...`` without asserting counts.
    """
    stamp = f"{prefix}-{time.strftime('%H%M%S')}-{uuid.uuid4().hex[:6]}"
    return valid_booking_payload(firstname=stamp, **overrides)


def valid_booking_variants() -> dict[str, dict]:
    """Named valid variants (deposit true/false, prices, dates, needs)."""
    return {
        "standard": valid_booking_payload(),
        "deposit_false": valid_booking_payload(depositpaid=False),
        "no_additional_needs": valid_booking_payload(additionalneeds=None),
        "high_price": valid_booking_payload(totalprice=9999),
        "long_stay": valid_booking_payload(
            bookingdates={"checkin": "2026-06-01", "checkout": "2026-06-30"}
        ),
        "alt_names": valid_booking_payload(
            firstname="Sally", lastname="Brown", additionalneeds="Lunch"
        ),
    }


# ---------------------------------------------------------------------------
# Invalid data (each observed 2026-10-03 unless marked re-verify)
# ---------------------------------------------------------------------------
def invalid_booking_payloads() -> dict[str, dict]:
    """Payloads for NEG scenarios: (payload, observed behavior)."""
    base = valid_booking_payload()
    no_first = dict(base)
    del no_first["firstname"]
    no_dates = dict(base)
    del no_dates["bookingdates"]
    return {
        # NEG-001: missing required field -> 500 (crash, top defect candidate)
        "missing_firstname": {
            "payload": no_first,
            "expected_note": "observed 500 Internal Server Error",
        },
        # NEG-002/003: siblings of NEG-001, all 500 (probed 2026-10-03)
        "missing_lastname": {
            "payload": {k: v for k, v in base.items() if k != "lastname"},
            "expected_note": "observed 500 Internal Server Error",
        },
        "missing_bookingdates": {
            "payload": no_dates,
            "expected_note": "observed 500 Internal Server Error",
        },
        # NEG-004: wrong-type price coerced to null, still 200
        "price_as_string": {
            "payload": valid_booking_payload(totalprice="not-a-number"),
            "expected_note": "observed 200 with totalprice=null",
        },
        # NEG-005: string boolean coerced to true, still 200
        "deposit_as_string": {
            "payload": valid_booking_payload(depositpaid="yes"),
            "expected_note": "observed 200 with depositpaid=true",
        },
        # NEG-006: bad date string -> JS-Date artifact, still 200
        "bad_date_format": {
            "payload": valid_booking_payload(
                bookingdates={"checkin": "not-a-date", "checkout": "2026-01-05"}
            ),
            "expected_note": 'observed 200 with checkin="0NaN-aN-aN"',
        },
        # NEG-007: empty strings accepted as-is, 200
        "empty_firstname": {
            "payload": valid_booking_payload(firstname=""),
            "expected_note": "observed 200, stored empty string",
        },
        # NEG-009: unknown fields silently dropped, 200
        "extra_unknown_field": {
            "payload": valid_booking_payload(surprise="hello"),
            "expected_note": "observed 200, extra field ignored",
        },
        # NEG-010: null optional stored as null, 200
        "null_additional_needs": {
            "payload": valid_booking_payload(additionalneeds=None),
            "expected_note": "observed 200, stored null",
        },
    }


def boundary_booking_payloads() -> dict[str, dict]:
    """Payloads for BND scenarios."""
    return {
        # BND-001..004: all observed 200, stored as-is (no validation)
        "zero_price": {
            "payload": valid_booking_payload(totalprice=0),
            "expected_note": "observed 200, stored 0",
        },
        "negative_price": {
            "payload": valid_booking_payload(totalprice=-50),
            "expected_note": "observed 200, stored -50",
        },
        "huge_price": {
            "payload": valid_booking_payload(totalprice=999999999),
            "expected_note": "observed 200, stored as-is",
        },
        "inverted_dates": {
            "payload": valid_booking_payload(
                bookingdates={"checkin": "2026-01-10", "checkout": "2026-01-05"}
            ),
            "expected_note": "observed 200, stored as-is (no range check)",
        },
        # BND-005: 500-char name stored verbatim (observed 200, 2026-10-03)
        "long_name": {
            "payload": valid_booking_payload(firstname="B" * 500),
            "expected_note": "observed 200, stored verbatim full-length",
        },
    }


# ---------------------------------------------------------------------------
# Authentication data (usernames/passwords via env at runtime; shapes here)
# ---------------------------------------------------------------------------
def auth_payloads(
    username: str | None = None, password: str | None = None
) -> dict[str, dict]:
    """Auth bodies for AUTH scenarios, using configured credentials by default."""
    username = username if username is not None else get_username()
    password = password if password is not None else get_password()
    return {
        "valid": {"username": username, "password": password},
        "wrong_password": {"username": username, "password": "wrong-password"},
        "unknown_user": {"username": "invalid-user", "password": "invalid-password"},
        "empty_body": {},
        "empty_strings": {"username": "", "password": ""},
    }
