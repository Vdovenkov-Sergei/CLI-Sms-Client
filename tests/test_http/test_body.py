"""Tests for `HTTPBody` — serialisation and field validation."""

from dataclasses import dataclass

import pytest

from app.exceptions import SerializationError, ValidationError
from app.http.body import HTTPBody


@dataclass
class SampleBody(HTTPBody):
    """Minimal concrete `HTTPBody` subclass used for testing."""

    value: str


class TestHTTPBody:
    """Tests for `HTTPBody` base class."""

    def test_to_dict(self) -> None:
        """Returns a plain dictionary of all instance fields."""
        body = SampleBody(value="hello")
        assert body.to_dict() == {"value": "hello"}

    def test_to_json(self) -> None:
        """Serialises the body to a valid JSON string."""
        body = SampleBody(value="hello")
        assert body.to_json() == '{"value": "hello"}'

    def test_validate_type_mismatch(self) -> None:
        """Raises `ValidationError` when a field value does not match its declared type."""
        with pytest.raises(ValidationError, match="must be of type"):
            SampleBody(value=123)  # type: ignore

    def test_to_json_non_serialisable(self) -> None:
        """Raises `SerializationError` when a field value is not JSON-serialisable."""
        body = object.__new__(SampleBody)
        body.value = object()  # type: ignore

        with pytest.raises(SerializationError, match="Error serializing body to JSON"):
            body.to_json()
