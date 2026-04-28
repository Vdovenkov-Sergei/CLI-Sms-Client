"""HTTP Basic Authentication encoding and decoding utilities."""

import base64
import binascii

from app.exceptions import AuthenticationError


class HTTPBasicAuth:
    """Provides static methods for HTTP Basic Authentication header handling."""

    @staticmethod
    def encode(credentials: tuple[str, str]) -> str:
        """Encodes `(username, password)` tuple as an HTTP Basic Auth header.

        Args:
            credentials: A 2-tuple of `(username, password)` strings.

        Returns:
            A header value string in the form `"Basic <base64>"`.

        Raises:
            AuthenticationError: If credentials is not a 2-tuple of strings,
                or if encoding fails.
        """
        if not isinstance(credentials, tuple) or len(credentials) != 2:
            raise AuthenticationError("Credentials must be a tuple (username, password)")

        username, password = credentials
        if not isinstance(username, str) or not isinstance(password, str):
            raise AuthenticationError("Both username and password must be strings")

        try:
            encoded = base64.b64encode(f"{username}:{password}".encode()).decode()
            return f"Basic {encoded}"
        except (UnicodeEncodeError, binascii.Error) as err:
            raise AuthenticationError(f"Failed to encode credentials: {err}")

    @staticmethod
    def decode(auth_header: str) -> tuple[str, str]:
        """Decodes an HTTP Basic Auth header into `(username, password)` tuple.

        Args:
            auth_header: The value of the `Authorization` header.

        Returns:
            A tuple of `(username, password)` with leading/trailing
            whitespace stripped.

        Raises:
            AuthenticationError: If the header does not start with `"Basic "`,
                if the payload cannot be decoded, or if the decoded
                string does not contain a `":"` separator.
        """
        if not auth_header.startswith("Basic "):
            raise AuthenticationError("Authorization header should start with 'Basic '")

        encoded_credentials = auth_header[len("Basic ") :]
        try:
            decoded_bytes = base64.b64decode(encoded_credentials)
            decoded_credentials = decoded_bytes.decode()

            if ":" not in decoded_credentials:
                raise AuthenticationError("Decoded credentials must be in the format 'username:password'")

            username, password = decoded_credentials.split(":", 1)
            return username.strip(), password.strip()

        except (binascii.Error, UnicodeDecodeError) as err:
            raise AuthenticationError(f"Failed to decode 'Authorization' header: {err}")
