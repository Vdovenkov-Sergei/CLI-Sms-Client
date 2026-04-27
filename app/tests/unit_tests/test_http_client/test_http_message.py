import pytest

from app.exceptions import HTTPMessageError, HTTPRequestError, HTTPResponseError
from app.http_client.http_message import HTTPRequest, HTTPResponse


class TestHTTPRequest:
    def test_start_line(self) -> None:
        request = HTTPRequest(method="GET", host="example.com", path="/test", auth=None)
        assert request.start_line == "GET /test HTTP/1.1"

    def test_to_bytes(self) -> None:
        request = HTTPRequest(method="POST", host="example.com", path="/test", auth=None, body="Hello")
        bytes_data = request.to_bytes()
        assert isinstance(bytes_data, bytes)
        assert b"POST /test HTTP/1.1" in bytes_data
        assert b"Host: example.com" in bytes_data
        assert b"Content-Length: 5" in bytes_data
        assert b"Hello" in bytes_data

    def test_to_bytes_empty_body(self) -> None:
        request = HTTPRequest(method="GET", host="example.com", path="/test")
        bytes_data = request.to_bytes()
        assert b"Content-Length: 0" in bytes_data

    def test_from_bytes_valid(self) -> None:
        binary_data = (
            b"GET /test HTTP/1.1\r\nHost: example.com\r\nAuthorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=\r\n"
            b"Content-Length: 9\r\n\r\nTest body"
        )
        request = HTTPRequest.from_bytes(binary_data)

        assert request.method == "GET"
        assert request.host == "example.com"
        assert request.path == "/test"
        assert request.body == "Test body"
        assert request.headers["Authorization"] == "Basic dXNlcm5hbWU6cGFzc3dvcmQ="
        assert "Content-Length" in request.headers
        assert request.headers["Content-Length"] == "9"

    @pytest.mark.parametrize(
        "binary_data, expected_exception, match_text",
        [
            (b"INVALID /test HTTP/1.1\r\nHost: example.com\r\n\r\n", HTTPRequestError, "Invalid HTTP method"),
            (b"GET /test HTTP/1.1\r\nContent-Length: abc\r\n\r\nHello", HTTPMessageError, "Invalid Content-Length"),
            (b"GET /test HTTP/1.1\r\nContent-Length: 10\r\n\r\nHello", HTTPMessageError, "Content-Length mismatch"),
            (b"GET test HTTP/1.1\r\nHost: example.com\r\n\r\n", HTTPRequestError, "Invalid path in request"),
            (b"GET /test HTTP/1.1\r\nHost: \r\n\r\n", HTTPRequestError, "Missing 'Host' header"),
            (b"GET /test\r\nHost: example.com\r\n\r\n", HTTPMessageError, "Invalid start line format"),
            (b"GET /test HTTP/1.1\r\n\r\nHello", HTTPMessageError, "Content-Length header is missing"),
            (b"", HTTPMessageError, "No start line found"),
            (b"GET /test HTTP/1.1\r\nContent-Length;5\r\n\r\nHello", HTTPMessageError, "Invalid header format"),
            (
                b"GET /test HTTP/1.1\r\nHost: example.com\r\nAuthorization: Invalid\r\n\r\n",
                HTTPRequestError,
                "Invalid Authorization header",
            ),
        ],
    )
    def test_invalid_requests(self, binary_data: bytes, expected_exception: type, match_text: str) -> None:
        with pytest.raises(expected_exception, match=match_text):
            HTTPRequest.from_bytes(binary_data)


class TestHTTPResponse:
    def test_start_line_valid(self) -> None:
        response = HTTPResponse(status_code=200, status_message="OK")
        assert response.start_line == "HTTP/1.1 200 OK"

    def test_to_bytes_valid(self) -> None:
        response = HTTPResponse(status_code=200, status_message="OK", headers=None, body="Response body")
        bytes_data = response.to_bytes()
        assert isinstance(bytes_data, bytes)
        assert b"HTTP/1.1 200 OK" in bytes_data
        assert b"Content-Length: 13" in bytes_data
        assert b"Response body" in bytes_data

    def test_to_bytes_empty_body(self) -> None:
        response = HTTPResponse(status_code=204, status_message="No Content")
        bytes_data = response.to_bytes()
        assert b"Content-Length: 0" in bytes_data

    def test_from_bytes_valid(self) -> None:
        binary_data = b"HTTP/1.1 404 Not Found\r\nContent-Length: 9\r\n\r\nNot Found"
        response = HTTPResponse.from_bytes(binary_data)
        assert response.status_code == 404
        assert response.status_message == "Not Found"
        assert response.body == "Not Found"

    @pytest.mark.parametrize(
        "binary_data, expected_exception, match_text",
        [
            (b"HTTP/1.1 600 OK\r\n\r\n", HTTPResponseError, "Status code out of range"),
            (b"HTTP/1.1 invalid OK\r\nContent-Length: 4\r\n\r\nBody", HTTPResponseError, "Invalid status code:"),
            (b"HTTP/1.1 200  \r\nContent-Length: 4\r\n\r\nBody", HTTPResponseError, "Missing status message"),
        ],
    )
    def test_from_bytes_invalid(self, binary_data: bytes, expected_exception: type, match_text: str) -> None:
        with pytest.raises(expected_exception, match=match_text):
            HTTPResponse.from_bytes(binary_data)
