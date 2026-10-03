"""Raw request-header cases that Postman injects automatically."""

import json

import pytest
import requests

from src import config
from src.test_data import valid_booking_payload

pytestmark = pytest.mark.negative


def test_booking_create_without_content_type_returns_observed_server_error() -> None:
    response = requests.post(
        f"{config.get_base_url().rstrip('/')}/booking",
        data=json.dumps(valid_booking_payload()),
        headers={"Accept": "application/json"},
        timeout=config.get_timeout(),
    )

    assert response.request.headers.get("Content-Type") is None
    assert response.status_code == 500
    assert response.headers.get("Content-Type", "").startswith("text/plain")
