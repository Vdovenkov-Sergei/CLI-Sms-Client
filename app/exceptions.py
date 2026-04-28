"""Custom exception hierarchy for the SMS CLI client."""


class SMSClientError(Exception):
    """Base exception for all SMS client errors."""

    ...


class ConfigError(SMSClientError):
    """Raised when configuration is missing, unreadable, or malformed."""

    ...


class NetworkError(SMSClientError):
    """Raised on socket-level connection or I/O failures."""

    ...


class ValidationError(SMSClientError):
    """Raised when input data fails validation rules."""

    ...


class AuthenticationError(SMSClientError):
    """Raised on authentication failures (encoding, decoding, or invalid credentials)."""

    ...


class HTTPMessageError(SMSClientError):
    """Base exception for HTTP message parsing and construction errors."""

    ...


class HTTPRequestError(HTTPMessageError):
    """Raised when an HTTP request cannot be built or sent."""

    ...


class HTTPResponseError(HTTPMessageError):
    """Raised when an HTTP response cannot be parsed or is structurally invalid."""

    ...


class PhoneNumberError(ValidationError):
    """Raised when a phone number does not match the expected format."""

    ...


class MessageError(ValidationError):
    """Raised when an SMS message text is invalid (e.g. blank)."""

    ...


class SerializationError(SMSClientError):
    """Raised when JSON serialisation or deserialisation fails."""

    ...
