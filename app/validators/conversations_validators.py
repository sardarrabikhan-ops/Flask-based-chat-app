# app/validators/conversations_validators.py

from app.validators import BaseValidator
from app.constants import (
    CONVERSATION_NAME_MAX_LENGTH,
    CONVERSATION_NAME_MIN_LENGTH,
    CONVERSATION_NAME_ALLOWED_SPECIAL_CHARACTERS,
)


class ConversationValidator(BaseValidator):

    @staticmethod
    def name(name: str | None) -> str | None:
        if error := ConversationValidator._validate_name(
            name,
            "Conversation name",
            CONVERSATION_NAME_MIN_LENGTH,
            CONVERSATION_NAME_MAX_LENGTH,
            CONVERSATION_NAME_ALLOWED_SPECIAL_CHARACTERS,
        ):
            return error

        assert name is not None

        if not all(char.isspace() or char.isalnum() for char in name):
            return f"Conversation name can only contain letters, digits, spaces, and {CONVERSATION_NAME_ALLOWED_SPECIAL_CHARACTERS}."

        return None
