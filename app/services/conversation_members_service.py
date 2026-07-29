# app/services/conversation_members_service.py

from app.models import ConversationMember, User, Conversation
from app.services import BaseService
from app.schemas import ServiceResult

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

        result = self._require_user(user_id)

        if result.success is False:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        result = self._require_conversation(conversation_id)

        if result.success is False:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert user_id is not None
        assert conversation_id is not None

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

        return self._require_membership(user_id, conversation_id)

    def get_members(
        self,
        conversation_id: int | None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ServiceResult[Sequence[User]]:
        """Return the members for the given conversation ID."""

        result = self._require_conversation(conversation_id)

        if result.success is False:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert conversation_id is not None

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

        result = self._require_user(user_id)

        if result.success is False:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert user_id is not None

        memberships = self.conversation_member_repository.get_by_user_id(user_id, limit, offset)

        conversations = [membership.conversation for membership in memberships]

        return ServiceResult.ok(conversations)
