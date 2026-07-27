# app/validators/conversations_validators.py

from app.constants import (
    ConversationType,
    CONVERSATION_NAME_MAX_LENGTH,
    CONVERSATION_NAME_MIN_LENGTH,
    NAME_ALLOWED_SPECIAL_CHARACTERS,
)


class ConversationValidator:

    @staticmethod
    def name(name: str | None) -> str | None:
        if name is None:
            return "Conversation name is required."

        name = name.strip()

        if not name:
            return "Conversation name is required."

        length = len(name)

        if length < CONVERSATION_NAME_MIN_LENGTH:
            return f"Conversation name must be at least {CONVERSATION_NAME_MIN_LENGTH} characters long."

        if length > CONVERSATION_NAME_MAX_LENGTH:
            return f"Conversation name cannot exceed {CONVERSATION_NAME_MAX_LENGTH} characters."

        if not all(
            char.isalpha() or char in NAME_ALLOWED_SPECIAL_CHARACTERS for char in name
        ):
            return "Conversation name can only contain letters, spaces, apostrophes, and hyphens."

        return None

    @staticmethod
    def conversation_type(conversation_type: str | None) -> str | None:
        if not conversation_type or not conversation_type.strip():
            return "Conversation type is required."

        conversation_type = conversation_type.strip()

        allowed_values: list[str] = [value.value for value in ConversationType]

        if conversation_type not in allowed_values:
            return f"Conversation type must be one of {allowed_values}."

        return None

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
