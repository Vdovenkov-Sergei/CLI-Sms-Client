"""HTTP client for making raw socket-based HTTP requests."""

import json
import re
import socket
from typing import Any, ClassVar, Optional, Union

from app.exceptions import HTTPRequestError, NetworkError, SerializationError, ValidationError
from app.http.body import HTTPBody
from app.http.message import HTTPRequest, HTTPResponse
from app.utils.logging import get_logger

logger = get_logger("http")


class Request:
    """Sends HTTP requests over raw TCP sockets."""

    BUFF_SIZE: ClassVar[int] = 4096
    URL_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^(https?)://([^:/]+)(?::(\d+))?(/.*)?$", re.IGNORECASE)

    @staticmethod
    def parse_url(url: str) -> tuple[str, str, int, str]:
        """Parses a URL string into its components.

        Args:
            url: A full URL string.

        Returns:
            A tuple of `(protocol, host, port, path)`.

        Raises:
            HTTPRequestError: If *url* is not a string or does not match the
                expected `http(s)://host[:port][/path]` format, or if the
                port number is outside the valid 0-65535 range.
        """
        if not isinstance(url, str):
            raise HTTPRequestError("URL must be a string")

        match = Request.URL_PATTERN.match(url)
        if not match:
            raise HTTPRequestError(f"Invalid URL format: {url}")

        protocol, host, port_str, path = match.groups()
        path = path or "/"

        if port_str:
            port = int(port_str)
            if port < 0 or port > 65535:
                raise HTTPRequestError(f"Port number out of range: {port}")
        else:
            port = 443 if protocol == "https" else 80

        return protocol, host, port, path

    @staticmethod
    def prepare_body(body: Union[HTTPBody, dict[str, Any], str]) -> tuple[str, dict[str, str]]:
        """Serialises a request body and returns appropriate Content-* headers.

        Args:
            body: The request payload.

        Returns:
            A tuple of body string and a dict of headers to include in the request.

        Raises:
            SerializationError: If *body* cannot be JSON-serialised.
            ValidationError: If *body* is an unsupported type.
        """
        headers: dict[str, str] = {}
        if isinstance(body, dict):
            try:
                body = json.dumps(body)
            except TypeError as err:
                raise SerializationError(f"Error serializing body to JSON: {err}")
            headers.setdefault("Content-Type", "application/json")
        elif isinstance(body, HTTPBody):
            body = body.to_json()
            headers.setdefault("Content-Type", "application/json")
        elif isinstance(body, str):
            headers.setdefault("Content-Type", "text/plain")
        else:
            raise ValidationError(f"Unsupported body type: {type(body)}")
        headers.setdefault("Content-Length", str(len(body)))

        return body, headers

    @staticmethod
    def method(
        method: str,
        url: str,
        *,
        auth: Optional[tuple[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        body: Optional[Union[HTTPBody, dict[str, Any], str]] = None,
    ) -> HTTPResponse:
        """Sends an HTTP request and returns the parsed response.

        Args:
            method: HTTP method string.
            url: Target URL.
            auth: Optional `(username, password)` tuple for Basic auth.
            headers: Optional extra request headers.
            body: Optional request body.

        Returns:
            The parsed HTTP response.

        Raises:
            NetworkError: On socket-level connection or timeout errors.
            HTTPRequestError: On any other error during request preparation or
                sending.
        """
        try:
            _, host, port, path = Request.parse_url(url)
            body_str: Optional[str] = None
            if body is not None:
                body_str, body_headers = Request.prepare_body(body)
                headers = {**(headers or {}), **body_headers}

            request = HTTPRequest(method, host, path, auth=auth, headers=headers, body=body_str)
            logger.info("→ %s %s:%d%s", method, host, port, path)
            if body_str:
                logger.debug("Request body: %s", request.body)

            with socket.create_connection((host, port)) as sock:
                sock.sendall(request.to_bytes())
                response_data = b""
                while True:
                    chunk = sock.recv(Request.BUFF_SIZE)
                    response_data += chunk
                    if len(chunk) < Request.BUFF_SIZE:
                        break

            response = HTTPResponse.from_bytes(response_data)
            logger.info("← %d %s", response.status_code, response.status_message)
            if response.body:
                logger.debug("Response body: %s", response.body)
            return response

        except (socket.error, socket.timeout) as err:
            raise NetworkError(f"Network error: {err}")
        except Exception as err:
            raise HTTPRequestError(f"Request failed: {err}")

    @staticmethod
    def post(
        url: str,
        *,
        auth: Optional[tuple[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
        body: Optional[Union[HTTPBody, dict[str, Any], str]] = None,
    ) -> HTTPResponse:
        """Sends an HTTP POST request.

        Args:
            url: Target URL.
            auth: Optional `(username, password)` tuple for Basic auth.
            headers: Optional extra request headers.
            body: Optional request body.

        Returns:
            The parsed HTTP response.
        """
        return Request.method("POST", url, auth=auth, headers=headers, body=body)
