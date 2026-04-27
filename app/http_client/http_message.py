from abc import ABC, abstractmethod
from typing import Optional, Self

from auth.basic_auth import HTTPBasicAuth


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
        if self.body:
            self.headers["Content-Length"] = str(len(self.body))
        else:
            self.headers.pop("Content-Length", None)

    def to_bytes(self) -> bytes:
        self._update_headers()
        headers = "\r\n".join(f"{key}: {value}" for key, value in self.headers.items())
        return f"{self.start_line}\r\n{headers}\r\n\r\n{self.body}".encode()

    @staticmethod
    def _parse_message(binary_data: bytes) -> tuple[str, dict[str, str], str]:
        try:
            data = binary_data.decode()
        except UnicodeDecodeError:
            raise ValueError("Failed to decode binary data.")

        lines = data.split("\r\n")
        if not lines or not lines[0]:
            raise ValueError("Invalid message format: No start line found.")

        start_line, *lines = lines
        headers, body = {}, None
        blank_line_idx = lines.index("") if "" in lines else len(lines)

        try:
            for line in lines[:blank_line_idx]:
                key, value = line.split(": ", 1)
                headers[key] = value
        except ValueError:
            raise ValueError("Invalid header format. Expected 'key: value'.")

        if blank_line_idx + 1 < len(lines):
            body = "\r\n".join(lines[blank_line_idx + 1 :])

        return start_line, headers, body


class HTTPRequest(HTTPMessage):
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
        start_line, headers, body = cls._parse_message(binary_data)

        parts = start_line.split(" ", 2)
        if len(parts) != 3:
            raise ValueError(f"Invalid start line format: {start_line}")

        method, path, _ = parts
        host = headers.get("Host")
        if not host:
            raise ValueError("Missing 'Host' header in the request.")

        auth = None
        if "Authorization" in headers:
            auth = HTTPBasicAuth.decode(headers["Authorization"])

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
        start_line, headers, body = cls._parse_message(binary_data)

        parts = start_line.split(" ", 2)
        if len(parts) != 3:
            raise ValueError(f"Invalid start line format: {start_line}")
        _, status_code, status_message = parts

        return cls(int(status_code), status_message, headers=headers, body=body)
