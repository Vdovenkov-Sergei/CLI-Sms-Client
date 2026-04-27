import pytest

from app.exceptions import MessageError, PhoneNumberError, SerializationError, ValidationError
from app.http_client.schemas import HTTPBody, SMSMessage


class TestSMSMessage:
    def test_valid_sms_message(self) -> None:
        msg = SMSMessage(sender="+12345678901", recipient="+19876543210", message="Hello!")
        assert msg.to_dict() == {"sender": "+12345678901", "recipient": "+19876543210", "message": "Hello!"}
        assert isinstance(msg.to_json(), str)

    @pytest.mark.parametrize(
        "sender, recipient, message, expected_exception",
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
    )
    def test_invalid_inputs(self, sender: str | int, recipient: str, message: str, expected_exception: type) -> None:
        with pytest.raises(expected_exception):
            SMSMessage(sender=sender, recipient=recipient, message=message)  # type: ignore


class TestHTTPBody:
    def test_to_dict(self, http_body: HTTPBody) -> None:
        http_body.sender = "+12345678901"  # type: ignore
        http_body.recipient = "+19876543210"  # type: ignore

        assert http_body.to_dict() == {"sender": "+12345678901", "recipient": "+19876543210"}

    def test_valid_to_json(self, http_body: HTTPBody) -> None:
        http_body.sender = "+12345678901"  # type: ignore
        http_body.recipient = "+19876543210"  # type: ignore

        json_str = http_body.to_json()
        assert isinstance(json_str, str)
        assert '"sender": "+12345678901"' in json_str

    def test_invalid_to_json(self, http_body: HTTPBody) -> None:
        http_body.sender = object()  # type: ignore
        with pytest.raises(SerializationError):
            http_body.to_json()
