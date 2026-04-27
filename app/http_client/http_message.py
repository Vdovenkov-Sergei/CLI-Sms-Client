from abc import ABC, abstractmethod
from typing import Optional, Self

from app.auth.basic_auth import HTTPBasicAuth
from app.exceptions import AuthenticationError, HTTPMessageError, HTTPRequestError, HTTPResponseError


class HTTPMessage(ABC):
    def __init__(self, *, headers: Optional[dict[str, str]] = None, body: Optional[str] = None):
        self.headers = headers or {}
        self.body = body or ""

    @property
    @abstractmethod
    def start_line(self) -> str:
        pass

    @classmethod
    @abstractmethod
    def from_bytes(cls, binary_data: bytes) -> Self:
        pass

    def _update_headers(self) -> None:
        self.headers["Content-Length"] = str(len(self.body))

    def to_bytes(self) -> bytes:
        self._update_headers()
        headers = "\r\n".join(f"{key}: {value}" for key, value in self.headers.items())
        return f"{self.start_line}\r\n{headers}\r\n\r\n{self.body}".encode()

    @staticmethod
    def _parse_message(binary_data: bytes) -> tuple[list[str], dict[str, str], str]:
        try:
            data = binary_data.decode()
        except UnicodeDecodeError:
            raise HTTPMessageError("Failed to decode binary data.")

        lines = data.split("\r\n")
        if not lines or not lines[0]:
            raise HTTPMessageError("Invalid message format: No start line found.")

        start_line, *lines = lines
        headers, body = {}, ""
        blank_line_idx = lines.index("") if "" in lines else len(lines)

        try:
            for line in lines[:blank_line_idx]:
                key, value = line.split(": ", 1)
                headers[key] = value
        except ValueError:
            raise HTTPMessageError("Invalid header format. Expected 'key: value'.")

        if blank_line_idx + 1 < len(lines):
            body = "\r\n".join(lines[blank_line_idx + 1 :])

        parts = start_line.split(" ", 2)
        if len(parts) != 3:
            raise HTTPMessageError(f"Invalid start line format: {start_line}")

        if body:
            content_length_str = headers.get("Content-Length")
            if content_length_str is None:
                raise HTTPMessageError("Content-Length header is missing for non-empty body.")
            try:
                content_length = int(content_length_str)
            except ValueError:
                raise HTTPMessageError(f"Invalid Content-Length value: {content_length_str}")
            if content_length != len(body):
                raise HTTPMessageError(f"Content-Length mismatch: expected {content_length}, got {len(body)}")

        return parts, headers, body


class HTTPRequest(HTTPMessage):
    ALLOWED_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "CONNECT", "TRACE"}

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
        return f"{self.method} {self.path} HTTP/1.1"

    def _update_headers(self) -> None:
        super()._update_headers()
        self.headers["Host"] = self.host
        if self.auth:
            self.headers["Authorization"] = HTTPBasicAuth.encode(self.auth)
        else:
            self.headers.pop("Authorization", None)

    @classmethod
    def from_bytes(cls, binary_data: bytes) -> Self:
        parts, headers, body = cls._parse_message(binary_data)
        method, path, _ = parts

        if method not in cls.ALLOWED_METHODS:
            raise HTTPRequestError(f"Invalid HTTP method: {method}")

        if not path.startswith("/"):
            raise HTTPRequestError(f"Invalid path in request: {path}")

        host = headers.get("Host")
        if host is None or not host.strip():
            raise HTTPRequestError("Missing 'Host' header in the request.")

        auth = None
        if "Authorization" in headers:
            try:
                auth = HTTPBasicAuth.decode(headers["Authorization"])
            except AuthenticationError:
                raise HTTPRequestError("Invalid Authorization header.")

        return cls(method, host, path, auth=auth, headers=headers, body=body)


class HTTPResponse(HTTPMessage):
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
        return f"HTTP/1.1 {self.status_code} {self.status_message}"

    @classmethod
    def from_bytes(cls, binary_data: bytes) -> Self:
        parts, headers, body = cls._parse_message(binary_data)
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
