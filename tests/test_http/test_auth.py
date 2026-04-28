"""Tests for `HTTPBasicAuth` — Base64 encoding and decoding of Basic Auth headers."""

import base64
import binascii
from typing import Any
from unittest.mock import Mock, patch

import pytest

from app.exceptions import AuthenticationError
from app.http.auth import HTTPBasicAuth


class TestHTTPBasicAuthEncode:
    """Tests for encoding `HTTPBasicAuth`."""

    def test_encode_valid_credentials(self, valid_credentials: tuple[str, str], valid_auth_header: str) -> None:
        """Encodes a valid tuple and checks the resulting header value."""
        encoded = HTTPBasicAuth.encode(valid_credentials)
        assert encoded == valid_auth_header

    @pytest.mark.parametrize(
        "invalid_input",
        [("single_value",), ("user", "pass", "extra"), (123, "pass"), ("user", 123), None, "not_a_tuple"],
        ids=[
            "single_value",
            "too_many_values",
            "non_string_username",
            "non_string_password",
            "none_input",
            "not_a_tuple",
        ],
    )
    def test_encode_invalid_credentials_raises_error(self, invalid_input: tuple[Any, ...]) -> None:
        """Raises `AuthenticationError` for non-string or malformed credential inputs."""
        with pytest.raises(AuthenticationError):
            HTTPBasicAuth.encode(invalid_input)

    def test_encode_handles_base64_errors(self) -> None:
        """Raises `AuthenticationError` when the underlying Base64 call fails."""
        with patch("base64.b64encode", Mock(side_effect=binascii.Error("Base64 error"))):
            with pytest.raises(AuthenticationError, match="Failed to encode credentials"):
                HTTPBasicAuth.encode(("user", "password"))


class TestHTTPBasicAuthDecode:
    """Tests for decoding `HTTPBasicAuth`."""

    def test_decode_valid_header(self, valid_auth_header: str, valid_credentials: tuple[str, str]) -> None:
        """Decodes a well-formed header and returns the original credentials."""
        credentials = HTTPBasicAuth.decode(valid_auth_header)
        assert credentials == valid_credentials

    def test_decode_missing_colon_raises_error(self) -> None:
        """Raises `AuthenticationError` when the decoded payload has no colon separator."""
        invalid_data = base64.b64encode(b"no_colon_here").decode()
        with pytest.raises(AuthenticationError, match="must be in the format"):
            HTTPBasicAuth.decode(f"Basic {invalid_data}")

    @pytest.mark.parametrize(
        "header",
        ["Bearer token", "Basic invalid_base64", "Basic " + "A" * 1000, ""],
        ids=["wrong_scheme", "invalid_base64", "too_long", "empty"],
    )
    def test_decode_invalid_headers_raises_error(self, header: str) -> None:
        """Raises `AuthenticationError` for headers with wrong scheme or invalid Base64."""
        with pytest.raises(AuthenticationError):
            HTTPBasicAuth.decode(header)

    def test_decode_handles_base64_errors(self) -> None:
        """Raises `AuthenticationError` when Base64 decoding fails."""
        with pytest.raises(AuthenticationError, match="Failed to decode"):
            HTTPBasicAuth.decode("Basic invalid base64")

    def test_decode_returns_stripped_credentials(self) -> None:
        """Strips leading and trailing whitespace from decoded username and password."""
        credentials = " user : pass "
        encoded = "Basic " + base64.b64encode(credentials.encode()).decode()
        result = HTTPBasicAuth.decode(encoded)
        assert result == ("user", "pass")
