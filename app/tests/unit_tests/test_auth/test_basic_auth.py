import base64
import binascii
from typing import Any
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from app.auth.basic_auth import HTTPBasicAuth
from app.exceptions import AuthenticationError


class TestHTTPBasicAuthEncode:
    def test_encode_valid_credentials(self, valid_credentials: tuple[str, str], valid_auth_header: str) -> None:
        encoded = HTTPBasicAuth.encode(valid_credentials)
        assert encoded == valid_auth_header

    @pytest.mark.parametrize(
        "invalid_input",
        [("single_value",), ("user", "pass", "extra"), (123, "pass"), ("user", 123), None, "not_a_tuple"],
    )
    def test_encode_invalid_credentials_raises_error(self, invalid_input: tuple[Any, ...]) -> None:
        with pytest.raises(AuthenticationError):
            HTTPBasicAuth.encode(invalid_input)

    def test_encode_handles_base64_errors(self, mocker: MockerFixture) -> None:
        mocker.patch("base64.b64encode", Mock(side_effect=binascii.Error("Base64 error")))
        with pytest.raises(AuthenticationError, match="Failed to encode credentials"):
            HTTPBasicAuth.encode(("user", "password"))


class TestHTTPBasicAuthDecode:
    def test_decode_valid_header(self, valid_auth_header: str, valid_credentials: tuple[str, str]) -> None:
        credentials = HTTPBasicAuth.decode(valid_auth_header)
        assert credentials == valid_credentials

    def test_decode_missing_colon_raises_error(self) -> None:
        invalid_data = base64.b64encode(b"no_colon_here").decode()
        with pytest.raises(AuthenticationError, match="must be in the format"):
            HTTPBasicAuth.decode(f"Basic {invalid_data}")

    @pytest.mark.parametrize("header", ["Bearer token", "Basic invalid_base64", "Basic " + "A" * 1000, ""])
    def test_decode_invalid_headers_raises_error(self, header: str) -> None:
        with pytest.raises(AuthenticationError):
            HTTPBasicAuth.decode(header)

    def test_decode_handles_base64_errors(self) -> None:
        with pytest.raises(AuthenticationError, match="Failed to decode"):
            HTTPBasicAuth.decode("Basic invalid_base64")

    def test_decode_returns_stripped_credentials(self) -> None:
        credentials = " user : pass "
        encoded = "Basic " + base64.b64encode(credentials.encode()).decode()
        result = HTTPBasicAuth.decode(encoded)
        assert result == ("user", "pass")
