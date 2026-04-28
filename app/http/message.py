"""Low-level HTTP/1.1 message abstractions built on raw bytes."""

from abc import ABC, abstractmethod
from typing import ClassVar, Optional, Self

from app.exceptions import AuthenticationError, HTTPMessageError, HTTPRequestError, HTTPResponseError
from app.http.auth import HTTPBasicAuth


class HTTPMessage(ABC):
    """Abstract base for HTTP/1.1 messages (requests and responses).

    Attributes:
        headers: A dictionary of HTTP header name-value pairs.
        body: The message body as a plain string.
    """

    def __init__(self, *, headers: Optional[dict[str, str]] = None, body: Optional[str] = None):
        self.headers: dict[str, str] = dict(headers) if headers else {}
        self.body = body or ""

    @property
    @abstractmethod
    def start_line(self) -> str:
        """Returns the HTTP start line for this message."""
        ...

    @classmethod
    @abstractmethod
    def from_bytes(cls, binary_data: bytes) -> Self:
        """Parses a raw HTTP message from bytes.

        Args:
            binary_data: The raw HTTP message bytes.

        Returns:
            A new instance of the concrete subclass.

        Raises:
            HTTPMessageError: If the bytes cannot be decoded or parsed.
        """
        ...

    def _build_headers(self) -> dict[str, str]:
        """Returns a copy of the headers with `Content-Length` set."""
        headers = dict(self.headers)
        headers["Content-Length"] = str(len(self.body))
        return headers

    def to_bytes(self) -> bytes:
        """Serialises the HTTP message to bytes including CRLF line endings.

        Returns:
            The full HTTP message.
        """
        headers = self._build_headers()
        headers_str = "\r\n".join(f"{key}: {value}" for key, value in headers.items())
        return f"{self.start_line}\r\n{headers_str}\r\n\r\n{self.body}".encode()

    @staticmethod
    def parse_message(binary_data: bytes) -> tuple[list[str], dict[str, str], str]:
        """Parses raw HTTP message bytes into start-line parts, headers, and body.

        Args:
            binary_data: The raw HTTP message bytes.

        Returns:
            A tuple of `(start line, headers, body)`.

        Raises:
            HTTPMessageError: If the bytes cannot be decoded, or if the message
                structure, header format, or Content-Length is invalid.
        """
        try:
            data = binary_data.decode()
        except UnicodeDecodeError:
            raise HTTPMessageError("Failed to decode binary data")

        lines = data.split("\r\n")
        if not lines or not lines[0].strip():
            raise HTTPMessageError("Invalid message format: No start line found")

        start_line, *lines = lines
        headers: dict[str, str] = {}
        body = ""
        blank_line_idx = lines.index("") if "" in lines else len(lines)

        try:
            for line in lines[:blank_line_idx]:
                key, value = line.split(": ", 1)
                headers[key] = value
        except ValueError:
            raise HTTPMessageError("Invalid header format. Expected 'key: value'")

        if blank_line_idx + 1 < len(lines):
            body = "\r\n".join(lines[blank_line_idx + 1 :])

        parts = start_line.split(" ", 2)
        if len(parts) != 3:
            raise HTTPMessageError(f"Invalid start line format: {start_line}")

        if body:
            content_length_str = headers.get("Content-Length")
            if content_length_str is None:
                raise HTTPMessageError("`Content-Length` header is missing for non-empty body")
            try:
                content_length = int(content_length_str)
            except ValueError:
                raise HTTPMessageError(f"Invalid `Content-Length` value: {content_length_str}")
            if content_length != len(body):
                raise HTTPMessageError(f"`Content-Length` mismatch: expected {content_length}, got {len(body)}")

        return parts, headers, body


class HTTPRequest(HTTPMessage):
    """Represents an outgoing HTTP/1.1 request.

    Attributes:
        method: The HTTP method.
        host: The target host (used in the `Host` header).
        path: The request path.
        auth: Optional `(username, password)` tuple for Basic authentication.
    """

    ALLOWED_METHODS: ClassVar[set[str]] = {
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "HEAD",
        "OPTIONS",
        "CONNECT",
        "TRACE",
    }

    def __init__(
        self,
        method: str,
        host: str,
        path: str,
        *,
        auth: Optional[tuple[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        body: Optional[str] = None,
    ):
        super().__init__(headers=headers, body=body)
        self.method = method
        self.host = host
        self.path = path
        self.auth = auth

    @property
    def start_line(self) -> str:
        """Returns the request line."""
        return f"{self.method} {self.path} HTTP/1.1"

    def _build_headers(self) -> dict[str, str]:
        """Returns headers with `Content-Length`, `Host`, and optional `Authorization`."""
        headers = super()._build_headers()
        headers["Host"] = self.host
        if self.auth:
            headers["Authorization"] = HTTPBasicAuth.encode(self.auth)
        else:
            headers.pop("Authorization", None)
        return headers

    @classmethod
    def from_bytes(cls, binary_data: bytes) -> Self:
        """Parses an HTTP request from raw bytes.

        Args:
            binary_data: The raw HTTP request bytes.

        Returns:
            A new `HTTPRequest` instance.

        Raises:
            HTTPRequestError: If the method, path, or `Host` header is invalid.
        """
        parts, headers, body = cls.parse_message(binary_data)
        method, path, _ = parts

        if method not in cls.ALLOWED_METHODS:
            raise HTTPRequestError(f"Invalid HTTP method: {method}")

        if not path.startswith("/"):
            raise HTTPRequestError(f"Invalid path in request: {path}")

        host = headers.get("Host")
        if host is None or not host.strip():
            raise HTTPRequestError("Missing 'Host' header in the request")

        auth = None
        if "Authorization" in headers:
            try:
                auth = HTTPBasicAuth.decode(headers["Authorization"])
            except AuthenticationError:
                raise HTTPRequestError("Invalid Authorization header.")

        return cls(method, host, path, auth=auth, headers=headers, body=body)


class HTTPResponse(HTTPMessage):
    """Represents an incoming HTTP/1.1 response.

    Attributes:
        status_code: The numeric HTTP status code (100-599).
        status_message: The reason phrase.
    """

    def __init__(
        self,
        status_code: int,
        status_message: str,
        *,
        headers: Optional[dict[str, str]] = None,
        body: Optional[str] = None,
    ):
        super().__init__(headers=headers, body=body)
        self.status_code = status_code
        self.status_message = status_message

    @property
    def start_line(self) -> str:
        """Returns the status line."""
        return f"HTTP/1.1 {self.status_code} {self.status_message}"

    @classmethod
    def from_bytes(cls, binary_data: bytes) -> Self:
        """Parses an HTTP response from raw bytes.

        Args:
            binary_data: The raw HTTP response bytes.

        Returns:
            A new `HTTPResponse` instance.

        Raises:
            HTTPResponseError: If the status code is out of range, non-numeric,
                or the status message is missing.
        """
        parts, headers, body = cls.parse_message(binary_data)
        _, status_code_str, status_message = parts

        try:
            status_code = int(status_code_str)
            if status_code < 100 or status_code > 599:
                raise HTTPResponseError(f"Status code out of range: {status_code}")
        except ValueError:
            raise HTTPResponseError(f"Invalid status code: {status_code_str}")

        if not status_message.strip():
            raise HTTPResponseError(f"Missing status message in response: {parts}")

        return cls(status_code, status_message, headers=headers, body=body)
