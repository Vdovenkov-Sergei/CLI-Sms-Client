from typing import Optional


class HTTPResponse:
    def __init__(
        self,
        status_code: int,
        status_message: str,
        *,
        headers: Optional[dict[str, str]] = None,
        body: str = "",
    ):
        self.status_code = status_code
        self.status_message = status_message
        self.headers = headers or {}
        self.body = body

    @property
    def status_line(self) -> str:
        return f"HTTP/1.1 {self.status_code} {self.status_message}"

    @classmethod
    def from_bytes(cls, binary_data: bytes) -> "HTTPResponse":
        data = binary_data.decode()
        status_line, *lines = data.split("\r\n")

        _, status_code, status_message = status_line.split(" ", 2)

        headers, body = {}, ""
        blank_line_idx = lines.index("") if "" in lines else len(lines)

        for line in lines[:blank_line_idx]:
            key, value = line.split(": ", 1)
            headers[key] = value

        if blank_line_idx + 1 < len(lines):
            body = "\r\n".join(lines[blank_line_idx + 1 :])

        return cls(int(status_code), status_message, headers=headers, body=body)

    def __update_headers(self) -> None:
        self.headers["Content-Type"] = "application/json"
        self.headers["Content-Length"] = str(len(self.body))

    def to_bytes(self) -> bytes:
        self.__update_headers()
        headers = "\r\n".join(f"{key}: {value}" for key, value in self.headers.items())
        http_response = f"{self.status_line}\r\n{headers}\r\n\r\n{self.body}"
        return http_response.encode()
