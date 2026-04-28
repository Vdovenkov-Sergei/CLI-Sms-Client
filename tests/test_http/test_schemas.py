"""Tests for `SMSMessage` — validation and serialisation."""

import pytest

from app.exceptions import MessageError, PhoneNumberError, ValidationError
from app.http.schemas import SMSMessage


class TestSMSMessage:
    """Tests for `SMSMessage` field validation and JSON serialisation."""

    def test_valid_sms_message(self) -> None:
        """Creates a valid SMSMessage and verifies dict and JSON output."""
        msg = SMSMessage(sender="+12345678901", recipient="+19876543210", message="Hello!")
        assert msg.to_dict() == {"sender": "+12345678901", "recipient": "+19876543210", "message": "Hello!"}
        assert isinstance(msg.to_json(), str)

    @pytest.mark.parametrize(
        ["sender", "recipient", "message", "expected_exception"],
        [
            ("", "+12345678901", "Test", PhoneNumberError),
            ("123", "+12345678901", "Test", PhoneNumberError),
            ("+abc", "+12345678901", "Test", PhoneNumberError),
            ("+123456", "+12345678901", "Test", PhoneNumberError),
            ("+12345678901", "", "Test", PhoneNumberError),
            ("+12345678901", "++999", "Test", PhoneNumberError),
            ("+12345678901", "not_a_number", "Test", PhoneNumberError),
            ("+12345678901", "+19876543210", "   ", MessageError),
            (12345, "+19876543210", "Hello", ValidationError),
        ],
        ids=[
            "empty sender",
            "too short sender",
            "non-numeric sender",
            "too short sender",
            "empty recipient",
            "invalid recipient format",
            "non-numeric recipient",
            "empty message",
            "non-string sender",
        ],
    )
    def test_invalid_inputs(self, sender: str | int, recipient: str, message: str, expected_exception: type) -> None:
        """Raises the expected exception for each category of invalid input."""
        with pytest.raises(expected_exception):
            SMSMessage(sender=sender, recipient=recipient, message=message)  # type: ignore
