# app/services/conversation_members_service.py

from sqlalchemy.orm import Session

from app.models import ConversationMember, User, Conversation
from app.services import BaseService

from app.schemas import ServiceResult
from app.constants import UserStatus, ConversationStatus

from typing import Sequence


class ConversationMemberService(BaseService):
    """Provides relationships between conversations and users."""

    def add_member(
        self, user_id: int | None, conversation_id: int | None
    ) -> ServiceResult[ConversationMember]:
        """
        Add a member to conversation and Add the membership into the database.
        Returns:
            ServiceResult containing the added membership or validation errors.
        """

        if user_id is None:
            return ServiceResult.fail({"user_id": "User ID is required."})

        if conversation_id is None:
            return ServiceResult.fail(
                {"conversation_id": "Conversation ID is required."}
            )

        user = self.user_repository.get_by_id(user_id)

        if user is None or user.status == UserStatus.DELETED:
            return ServiceResult.fail({"user_id": "User not found."})

        if user.status == UserStatus.BLOCKED:
            return ServiceResult.fail({"user_id": "User is blocked."})

        conversation = self.conversation_repository.get_by_id(conversation_id)

        if conversation is None or conversation.status == ConversationStatus.DELETED:
            return ServiceResult.fail({"conversation_id": "Conversation not found."})

        membership = self.conversation_member_repository.get(user_id, conversation_id)

        if membership is not None:
            return ServiceResult.fail(
                {"membership": "User is already a member of this conversation."}
            )

        membership = ConversationMember(
            user_id=user_id, conversation_id=conversation_id
        )

        membership = self.conversation_member_repository.create(conversation_member=membership)

        return ServiceResult.ok(membership)

    def get_member(
        self, user_id: int | None, conversation_id: int | None
    ) -> ServiceResult[ConversationMember]:
        """Return the membership for the given user ID and conversation ID."""

        if user_id is None:
            return ServiceResult.fail({"user_id": "User ID is required."})

        if conversation_id is None:
            return ServiceResult.fail(
                {"conversation_id": "Conversation ID is required."}
            )

        membership = self.conversation_member_repository.get(user_id, conversation_id)

        if membership is None:
            return ServiceResult.fail({"membership": "Membership not found."})

        return ServiceResult.ok(membership)

    def get_members(
        self,
        conversation_id: int | None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ServiceResult[Sequence[User]]:
        """Return the members for the given conversation ID."""

        if conversation_id is None:
            return ServiceResult.fail(
                {"conversation_id": "Conversation ID is required."}
            )

        conversation = self.conversation_repository.get_by_id(conversation_id)

        if conversation is None or conversation.status == ConversationStatus.DELETED:
            return ServiceResult.fail({"conversation_id": "Conversation not found."})

        memberships = self.conversation_member_repository.get_by_conversation_id(
            conversation_id, limit, offset
        )

        members = [membership.user for membership in memberships]

        return ServiceResult.ok(members)

    def get_conversations(
        self,
        user_id: int | None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ServiceResult[Sequence[Conversation]]:
        """Return the conversations for the given user ID."""

        if user_id is None:
            return ServiceResult.fail({"user_id": "User ID is required."})

        user = self.user_repository.get_by_id(user_id)

        if user is None or user.status == UserStatus.DELETED:
            return ServiceResult.fail({"user_id": "User not found."})

        if user.status == UserStatus.BLOCKED:
            return ServiceResult.fail({"user_id": "User is blocked."})

        memberships = self.conversation_member_repository.get_by_user_id(user_id, limit, offset)

        conversations = [membership.conversation for membership in memberships]

        return ServiceResult.ok(conversations)
