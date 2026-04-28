"""Application-level HTTP body schemas with domain validation."""

import re
from dataclasses import dataclass

from app.exceptions import MessageError, PhoneNumberError
from app.http.body import HTTPBody

PHONE_PATTERN: re.Pattern[str] = re.compile(r"^\+\d{10,15}$")


@dataclass
class SMSMessage(HTTPBody):
    """Represents a single SMS message payload.

    Attributes:
        sender: The sender's phone number (E.164 format, 10-15 digits).
        recipient: The recipient's phone number (E.164 format, 10-15 digits).
        message: The SMS text content (must be non-empty after stripping whitespace).
    """

    sender: str
    recipient: str
    message: str

    def validate(self) -> None:
        """Validates phone numbers and message content.

        Raises:
            PhoneNumberError: If *sender* or *recipient* is not a valid phone number.
            MessageError: If *message* is blank or contains only whitespace.
        """
        super().validate()
        if not PHONE_PATTERN.match(self.sender):
            raise PhoneNumberError(f"Invalid sender phone number: {self.sender}")
        if not PHONE_PATTERN.match(self.recipient):
            raise PhoneNumberError(f"Invalid recipient phone number: {self.recipient}")
        if not self.message.strip():
            raise MessageError("Message cannot be empty")
