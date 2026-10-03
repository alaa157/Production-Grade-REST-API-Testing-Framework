"""Reusable API client (Phase 13).

Thin wrapper around ``requests.Session`` that centralizes base URL, default
headers, timeout, and the auth-cookie convention. Deliberately small (Rule 5):
no retry/auth-manager abstractions — tests pass ``Cookie`` or ``Authorization``
per request via :func:`auth_headers`, and the shared session is never mutated
with credentials so unauthenticated tests stay honest.
"""

from __future__ import annotations

import requests

from src import config


def auth_headers(token: str) -> dict[str, str]:
    """Cookie header for token-authenticated writes (``Cookie: token=...``)."""
    return {"Cookie": f"token={token}"}


class ApiClient:
    """Session wrapper with centralized base URL, headers, and timeout."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: int | None = None,
        token: str | None = None,
    ) -> None:
        self.base_url = (base_url or config.get_base_url()).rstrip("/")
        self.timeout = timeout if timeout is not None else config.get_timeout()
        self.session = requests.Session()
        # Pinned JSON contract (inventory §4); override per request if needed
        # (e.g. the XML-negotiation probe sets Accept explicitly).
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )
        if token:
            self.set_token(token)

    def set_token(self, token: str) -> None:
        # RESTful Booker uses Cookie: token=<value> for authenticated calls.
        # Prefer per-request auth_headers() on shared clients; use set_token
        # only for intentionally stateful workflow clients.
        self.session.headers.update({"Cookie": f"token={token}"})

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.session.get(self._url(path), timeout=self.timeout, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.session.post(self._url(path), timeout=self.timeout, **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        return self.session.put(self._url(path), timeout=self.timeout, **kwargs)

    def patch(self, path: str, **kwargs) -> requests.Response:
        return self.session.patch(self._url(path), timeout=self.timeout, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.session.delete(self._url(path), timeout=self.timeout, **kwargs)

    def head(self, path: str, **kwargs) -> requests.Response:
        return self.session.head(self._url(path), timeout=self.timeout, **kwargs)
