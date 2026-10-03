"""Central configuration — reads from environment, no secrets committed."""

import os

from dotenv import load_dotenv

load_dotenv()  # loads .env locally if present; CI uses env vars / secrets


def get_base_url() -> str:
    return os.getenv("API_BASE_URL", "https://restful-booker.herokuapp.com")


def get_username() -> str:
    return os.getenv("API_USERNAME", "admin")


def get_password() -> str:
    return os.getenv("API_PASSWORD", "password123")


def get_timeout() -> int:
    try:
        return int(os.getenv("API_TIMEOUT", "10"))
    except ValueError:
        return 10
