import base64
import binascii

from app.exceptions import AuthenticationError


class HTTPBasicAuth:
    @staticmethod
    def encode(credentials: tuple[str, str]) -> str:
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
