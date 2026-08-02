# app/validators/conversations_validators.py

from app.validators import BaseValidator
from app.constants import (
    CONVERSATION_NAME_MAX_LENGTH,
    CONVERSATION_NAME_MIN_LENGTH,
    CONVERSATION_NAME_ALLOWED_SPECIAL_CHARACTERS,
)
from app.utils import format_set


class ConversationValidator(BaseValidator):

    @staticmethod
    def name(name: str | None) -> str | None:
        if error := ConversationValidator._validate_string(name, "Conversation name"):
            return error

        assert name is not None

        length = len(name)

        if length < CONVERSATION_NAME_MIN_LENGTH:
            return f"Conversation name must be at least {CONVERSATION_NAME_MIN_LENGTH} characters long."

        if length > CONVERSATION_NAME_MAX_LENGTH:
            return f"Conversation name cannot exceed {CONVERSATION_NAME_MAX_LENGTH} characters."

        if not all(
            char.isspace()
            or char.isalnum()
            or char in CONVERSATION_NAME_ALLOWED_SPECIAL_CHARACTERS
            for char in name
        ):
            return f"Conversation name can only contain letters, digits, spaces, and {format_set(CONVERSATION_NAME_ALLOWED_SPECIAL_CHARACTERS)}."

        return None
