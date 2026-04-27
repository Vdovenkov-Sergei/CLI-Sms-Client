import json
from typing import Callable, Generator, Optional
from unittest.mock import MagicMock, patch

import pytest

from app.http_client.http_message import HTTPResponse
from app.http_client.schemas import HTTPBody


@pytest.fixture
def mock_response() -> Callable[[int, Optional[str], bool], MagicMock]:
    def _factory(status_code: int = 200, body: Optional[str] = None, is_json: bool = True) -> MagicMock:
        response = MagicMock(spec=HTTPResponse)
        response.status_code = status_code
        response.body = json.dumps(body) if is_json and body else body
        return response

    return _factory


@pytest.fixture
def mock_console() -> Generator[MagicMock, None, None]:
    with patch("app.utils.console.console") as mock:
        yield mock


@pytest.fixture
def mock_create_connection() -> Generator[MagicMock, None, None]:
    with patch("socket.create_connection") as mock:
        yield mock


@pytest.fixture
def valid_credentials() -> tuple[str, str]:
    return ("test_user", "test_password")


@pytest.fixture
def valid_auth_header() -> str:
    # test_user:test_password
    return "Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ="


@pytest.fixture
def http_body() -> HTTPBody:
    return HTTPBody()
