"""Tests for `Request` — URL parsing, body preparation, and HTTP method execution."""

import socket
from dataclasses import dataclass
from unittest import mock

import pytest

from app.exceptions import HTTPRequestError, NetworkError, SerializationError, ValidationError
from app.http.body import HTTPBody
from app.http.client import Request


class TestRequest:
    """Tests for `Request` class."""

    @pytest.mark.parametrize(
        ["url", "expected_result"],
        [
            ("https://example.com", ("https", "example.com", 443, "/")),
            ("http://example.com", ("http", "example.com", 80, "/")),
            ("http://example.com:8080/path", ("http", "example.com", 8080, "/path")),
            ("https://example.com/path/to/resource", ("https", "example.com", 443, "/path/to/resource")),
        ],
    )
    def test_parse_url(self, url: str, expected_result: tuple[str, str, int, str]) -> None:
        """Parses valid URLs into (protocol, host, port, path) tuples."""
        assert Request.parse_url(url) == expected_result

    @pytest.mark.parametrize(
        "url",
        [
            1234,
            "invalid_url",
            "http://example.com:invalid_port",
            "http:\\example.com",
            "http://example.com:99999",
            "http://:8080/path",
            "https://:443",
        ],
    )
    def test_parse_url_invalid(self, url: int | str) -> None:
        """Raises `HTTPRequestError` for malformed or non-string URLs."""
        with pytest.raises(HTTPRequestError):
            Request.parse_url(url)  # type: ignore

    def test_parse_url_missing_path(self) -> None:
        """Defaults path to '/' when the URL has no explicit path."""
        assert Request.parse_url("http://example.com") == ("http", "example.com", 80, "/")

    def test_prepare_body_dict(self) -> None:
        """Serialises a dict body to JSON and sets `Content-Type` and `Content-Length`."""
        body = {"key": "value"}
        result, headers = Request.prepare_body(body)
        assert result == '{"key": "value"}'
        assert headers["Content-Type"] == "application/json"
        assert headers["Content-Length"] == str(len(result))

    def test_prepare_body_httpbody(self) -> None:
        """Serialises an `HTTPBody` instance to JSON."""

        @dataclass
        class TestHTTPBody(HTTPBody):
            data: dict[str, str]

        http_body = TestHTTPBody(data={"key": "value"})
        result, headers = Request.prepare_body(http_body)
        assert isinstance(result, str)
        assert headers["Content-Type"] == "application/json"
        assert headers["Content-Length"] == str(len(result))

    def test_prepare_body_str(self) -> None:
        """Passes a string body through unchanged with `text/plain` content type."""
        body = "Test message"
        result, headers = Request.prepare_body(body)
        assert result == "Test message"
        assert headers["Content-Type"] == "text/plain"
        assert headers["Content-Length"] == str(len(result))

    def test_prepare_body_invalid(self) -> None:
        """Raises ValidationError for unsupported body types."""
        with pytest.raises(ValidationError, match="Unsupported body type"):
            Request.prepare_body(None)  # type: ignore

    def test_prepare_body_dict_invalid(self) -> None:
        """Raises `SerializationError` when a dict value is not JSON-serialisable."""
        with pytest.raises(SerializationError, match="Error serializing body to JSON"):
            Request.prepare_body({"key": object()})

    def test_post_success(self, mock_create_connection: mock.MagicMock) -> None:
        """Sends a POST request and parses the response correctly."""
        mock_socket = mock.Mock()
        mock_socket.recv.return_value = b"HTTP/1.1 200 OK\r\nContent-Length: 12\r\n\r\nBody content"
        mock_create_connection.return_value.__enter__.return_value = mock_socket

        response = Request.post("http://example.com", body="Test message")
        assert response.start_line == "HTTP/1.1 200 OK"
        assert response.body == "Body content"
        assert response.headers["Content-Length"] == "12"

    def test_post_network_error(self, mock_create_connection: mock.MagicMock) -> None:
        """Raises `NetworkError` when the socket raises `socket.error`."""
        mock_create_connection.side_effect = socket.error("Network error")
        with pytest.raises(NetworkError):
            Request.post("http://example.com", body="Test message")

    def test_post_timeout_error(self, mock_create_connection: mock.MagicMock) -> None:
        """Raises `NetworkError` when the connection times out."""
        mock_create_connection.side_effect = socket.timeout("Timeout error")
        with pytest.raises(NetworkError):
            Request.post("http://example.com", body="Test message")

    def test_post_request_error(self, mock_create_connection: mock.MagicMock) -> None:
        """Raises `HTTPRequestError` for unexpected exceptions during the request."""
        mock_create_connection.side_effect = Exception("General error")
        with pytest.raises(HTTPRequestError):
            Request.post("http://example.com", body="Test message")

    def test_get_success(self, mock_create_connection: mock.MagicMock) -> None:
        """Sends a GET request with no body and parses an empty-body response."""
        mock_socket = mock.Mock()
        mock_socket.recv.return_value = b"HTTP/1.1 200 OK\r\n\r\n"
        mock_create_connection.return_value.__enter__.return_value = mock_socket

        response = Request.method("GET", "http://example.com")
        assert response.start_line == "HTTP/1.1 200 OK"
        assert response.body == ""
