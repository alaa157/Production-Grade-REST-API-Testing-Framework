import warnings
from types import SimpleNamespace

import pytest

from tests.conftest import _cleanup_booking


def test_cleanup_warns_when_delete_returns_unsuccessful_status():
    client = SimpleNamespace(
        delete=lambda *_args, **_kwargs: SimpleNamespace(
            status_code=403, text="Forbidden"
        )
    )

    with pytest.warns(RuntimeWarning, match="HTTP 403: Forbidden"):
        _cleanup_booking(client, 123, "token")


def test_cleanup_does_not_warn_when_delete_succeeds():
    client = SimpleNamespace(
        delete=lambda *_args, **_kwargs: SimpleNamespace(
            status_code=201, text="Created"
        )
    )

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        _cleanup_booking(client, 123, "token")
    assert not captured
