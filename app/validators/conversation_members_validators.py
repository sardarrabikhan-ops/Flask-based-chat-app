# app/validators/conversation_members_validators.py

from app.validators import BaseValidator

from app.constants import ConversationMemberRole

class ConversationMemberValidator(BaseValidator):

    @staticmethod
    def role(role: str | None) -> str | None:
        return ConversationMemberValidator._validate_enum(role, "User role", ConversationMemberRole)