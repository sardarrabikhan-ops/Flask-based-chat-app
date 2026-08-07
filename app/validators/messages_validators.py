# app/validators/messages_validators.py

from app.validators import BaseValidator
from app.constants import MESSAGE_MAX_LENGTH


class MessageValidator(BaseValidator):

    @staticmethod
    def validate_content(content: str | None) -> str | None:
        if content is None or not content.strip():
            return "Message content is required."

        if len(content) > MESSAGE_MAX_LENGTH:
            return f"Message must not exceed {MESSAGE_MAX_LENGTH} characters."

        return None
