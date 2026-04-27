import json
import re
import socket
from typing import Any, Optional, Union

from exceptions import HTTPRequestError, NetworkError, SerializationError, ValidationError
from http_client.http_message import HTTPRequest, HTTPResponse
from http_client.schemas import HTTPBody
from utils.logging import logger


class Request:
    BUFF_SIZE = 4096

    @staticmethod
    def parse_url(url: str) -> tuple[str, str, int, str]:
        if not isinstance(url, str):
            raise HTTPRequestError("URL must be a string")

        pattern = re.compile(r"^(https?)://([^:/]+)(?::(\d+))?(/.*)?$", re.IGNORECASE)
        match = pattern.match(url)
        if not match:
            raise HTTPRequestError(f"Invalid URL format: {url}")

        protocol = match.group(1)
        host = match.group(2)
        port_str = match.group(3)
        path = match.group(4) or "/"

        if port_str:
            try:
                port = int(port_str)
            except ValueError:
                raise HTTPRequestError(f"Invalid port number in URL: {port_str}")
        else:
            port = 443 if protocol == "https" else 80

        return protocol, host, port, path

    @staticmethod
    def prepare_body(body: Optional[Union[HTTPBody, dict[str, Any], str]]) -> tuple[str, dict[str, str]]:
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
        try:
            _, host, port, path = Request.parse_url(url)
            body, body_headers = Request.prepare_body(body)
            headers = {**(headers or {}), **body_headers}

            request = HTTPRequest(method, host, path, auth=auth, headers=headers, body=body)
            logger.info(f"Request: {request.start_line}")
            if body:
                logger.debug(f"Request Body: {request.body}")

            with socket.create_connection((host, port)) as sock:
                sock.sendall(request.to_bytes())
                response_data = sock.recv(Request.BUFF_SIZE)

            response = HTTPResponse.from_bytes(response_data)
            logger.info(f"Response: {response.start_line}")
            logger.debug(f"Response Body: {response.body}")
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
        return Request.method("POST", url, auth=auth, headers=headers, body=body)
