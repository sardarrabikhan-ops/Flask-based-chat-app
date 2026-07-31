# app/validators/base_validators.py

from enum import Enum
from app.utils import format_set


class BaseValidator:

    @staticmethod
    def _validate_string(string: str | None, field: str) -> str | None:
        if string in (None, ""):
            return f"{field} is required."

        if string.isspace():
            return f"{field} cannot consist only of whitespace."

        return None

    @staticmethod
    def _validate_name(
        name: str | None,
        field: str,
        min_length: int,
        max_length: int,
        allowed_characters: set[str],
    ) -> str | None:

        if error := BaseValidator._validate_string(name, field):
            return error

        assert name is not None

        length = len(name)

        if length < min_length:
            return f"{field} must be at least {min_length} characters long."

        if length > max_length:
            return f"{field} cannot exceed {max_length} characters."

        if not all(char.isalpha() or char in allowed_characters for char in name):
            return f"{field} can only contain letters and {format_set(allowed_characters)}."

        return None

    @staticmethod
    def _validate_enum(string: str | None, field: str, enums: type[Enum]) -> str | None:
        if error := BaseValidator._validate_string(string, field):
            return error

        allowed_values: list[str] = [value.value for value in enums]

        if string not in allowed_values:
            return f"{field} must be one of {allowed_values}."

        return None