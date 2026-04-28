"""Shared pytest fixtures used across the test suite."""

from typing import Generator
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_create_connection() -> Generator[MagicMock, None, None]:
    """Patches `socket.create_connection` for the duration of a test."""
    with patch("socket.create_connection") as mock:
        yield mock


@pytest.fixture
def valid_credentials() -> tuple[str, str]:
    """Fixture that returns a valid `(username, password)` tuple for `Basic Auth` tests."""
    return ("test_user", "test_password")


@pytest.fixture
def valid_auth_header() -> str:
    """Fixture that returns the encoded `Basic Auth` header for `test_user:test_password`."""
    return "Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ="
