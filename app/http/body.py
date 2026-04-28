"""Base class for HTTP request body schemas."""

import json
from dataclasses import dataclass
from typing import Any, get_origin, get_type_hints

from app.exceptions import SerializationError, ValidationError


@dataclass
class HTTPBody:
    """Base class for HTTP request body schemas."""

    def __post_init__(self) -> None:
        self.validate()

    def to_dict(self) -> dict[str, Any]:
        """Returns the instance fields as a plain dictionary.

        Returns:
            A dictionary mapping field names to their current values.
        """
        return dict(self.__dict__.items())

    def to_json(self) -> str:
        """Serialises the body to a JSON string.

        Returns:
            A JSON-encoded string representation of the body.

        Raises:
            SerializationError: If any field value is not JSON-serialisable.
        """
        try:
            return json.dumps(self.to_dict(), ensure_ascii=False)
        except Exception as err:
            raise SerializationError(f"Error serializing body to JSON: {err}")

    def validate(self) -> None:
        """Validates that all annotated fields match their declared types.

        Raises:
            ValidationError: If a field value does not match its declared type.
        """
        annotations = get_type_hints(self.__class__)
        for field_name, expected_type in annotations.items():
            value = getattr(self, field_name)
            check_type = get_origin(expected_type) or expected_type
            if not isinstance(value, check_type):
                raise ValidationError(f"Field '{field_name}' must be of type {expected_type}, but got {type(value)}")
