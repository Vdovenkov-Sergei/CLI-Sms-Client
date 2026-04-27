import json
import re
from dataclasses import dataclass
from typing import Any, Self, get_type_hints

from exceptions import MessageError, PhoneNumberError, SerializationError, ValidationError


@dataclass
class HTTPBody:
    def __post_init__(self) -> None:
        self.validate()

    def to_dict(self) -> dict[str, Any]:
        return {key: str(value) for key, value in self.__dict__.items()}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        try:
            instance = cls(**data)
        except TypeError as err:
            raise ValidationError(f"Error initializing {cls.__name__} from dictionary: {err}")
        except ValueError as err:
            raise ValidationError(f"Invalid data for {cls.__name__}: {err}")
        return instance

    def to_json(self) -> str:
        try:
            return json.dumps(self.to_dict(), ensure_ascii=False)
        except TypeError as err:
            raise SerializationError(f"Error serializing body to JSON: {err}")

    def validate(self) -> None:
        pass


class PhoneNumber:
    PHONE_PATTERN = r"^\+?\d{10,15}$"

    def __init__(self, phone: str):
        if not isinstance(phone, str):
            raise PhoneNumberError(f"Phone number must be a string, got {type(phone)}")
        if not self.is_valid_phone(phone):
            raise PhoneNumberError(f"Invalid phone number: {phone}")
        self.phone = phone

    def __str__(self) -> str:
        return self.phone

    @classmethod
    def is_valid_phone(cls, phone: str) -> bool:
        return bool(re.match(cls.PHONE_PATTERN, phone))


@dataclass
class SMSMessage(HTTPBody):
    sender: PhoneNumber
    recipient: PhoneNumber
    message: str

    def validate(self) -> None:
        annotations = get_type_hints(self.__class__)
        for field, expected_type in annotations.items():
            value = getattr(self, field)
            if not isinstance(value, expected_type):
                raise ValidationError(f"Field '{field}' must be of type {expected_type}, but got {type(value)}")
        if not self.message.strip():
            raise MessageError("Message cannot be empty")
