import json
import re
from dataclasses import dataclass
from typing import Any, get_type_hints

from app.exceptions import MessageError, PhoneNumberError, SerializationError, ValidationError


@dataclass
class HTTPBody:
    def __post_init__(self) -> None:
        self.validate()

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__

    def to_json(self) -> str:
        try:
            return json.dumps(self.to_dict(), ensure_ascii=False)
        except TypeError as err:
            raise SerializationError(f"Error serializing body to JSON: {err}")

    def validate(self) -> None:
        annotations = get_type_hints(self.__class__)
        for field, expected_type in annotations.items():
            value = getattr(self, field)
            if not isinstance(value, expected_type):
                raise ValidationError(f"Field '{field}' must be of type {expected_type}, but got {type(value)}")


@dataclass
class SMSMessage(HTTPBody):
    sender: str
    recipient: str
    message: str

    PHONE_PATTERN = r"^\+?\d{10,15}$"

    def validate(self) -> None:
        super().validate()
        if not self._is_valid_phone(self.sender):
            raise PhoneNumberError(f"Invalid sender phone number: {self.sender}")
        if not self._is_valid_phone(self.recipient):
            raise PhoneNumberError(f"Invalid recipient phone number: {self.recipient}")
        if not self.message.strip():
            raise MessageError("Message cannot be empty")

    @classmethod
    def _is_valid_phone(cls, phone: str) -> bool:
        return bool(re.match(cls.PHONE_PATTERN, phone))
