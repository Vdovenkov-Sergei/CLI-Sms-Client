import base64
from typing import Optional


class HTTPRequest:
    def __init__(
        self,
        method: str,
        host: str,
        path: str,
        *,
        auth: Optional[tuple[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        body: Optional[str] = "",
    ):
        self.method = method
        self.host = host
        self.path = path
        self.auth = auth or ()
        self.headers = headers or {}
        self.body = body

    @classmethod
    def from_bytes(cls, binary_data: bytes) -> "HTTPRequest":
        data = binary_data.decode()
        request_line, *lines = data.split("\r\n")
        method, path, _ = request_line.split(" ", 2)

        headers, body = {}, ""
        blank_line_idx = lines.index("") if "" in lines else len(lines)

        for line in lines[:blank_line_idx]:
            key, value = line.split(": ", 1)
            headers[key] = value

        if blank_line_idx + 1 < len(lines):
            body = "\r\n".join(lines[blank_line_idx + 1 :])

        host = headers.get("Host", "")
        auth = None
        if "Authorization" in headers:
            auth_header = headers["Authorization"]
            if auth_header.startswith("Basic "):
                encoded_credentials = auth_header.replace("Basic ", "")
                decoded_credentials = base64.b64decode(encoded_credentials).decode()
                auth = tuple(decoded_credentials.split(":", 1))

        return cls(method, host, path, auth, headers, body)

    def __update_headers(self) -> None:
        self.headers["Host"] = self.host

        if self.auth:
            auth = base64.b64encode(":".join(self.auth).encode()).decode()
            self.headers["Authorization"] = f"Basic {auth}"

        self.headers["Content-Type"] = "application/json"
        self.headers["Content-Length"] = str(len(self.body))

    def to_bytes(self) -> bytes:
        request_line = f"{self.method} {self.path} HTTP/1.1"
        self.__update_headers()
        headers = "\r\n".join(f"{key}: {value}" for key, value in self.headers.items())
        http_request = f"{request_line}\r\n{headers}\r\n\r\n{self.body}"
        return http_request.encode()
