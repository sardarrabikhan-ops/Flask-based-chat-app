# app/validators/conversations_validators.py

from app.validators import BaseValidator
from app.constants import (
    ConversationType,
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

    @staticmethod
    def conversation_type(conversation_type: str | None) -> str | None:
        return ConversationValidator._validate_enum(conversation_type, "Conversation type", ConversationType)

    @classmethod
    def create(
        cls,
        name: str | None,
        conversation_type: str | None,
    ) -> dict[str, str]:
        errors: dict[str, str] = {}

        if error := cls.conversation_type(conversation_type):
            errors["conversation_type"] = error
            return errors

        assert conversation_type is not None

        conversation_type_enum = ConversationType(conversation_type.strip())

        if conversation_type_enum == ConversationType.GROUP:
            if error := cls.name(name):
                errors["name"] = error
        else:
            clean_name = name.strip() if name is not None else ""
            if clean_name:
                errors["name"] = "Private conversations cannot have a name."

        return errors
