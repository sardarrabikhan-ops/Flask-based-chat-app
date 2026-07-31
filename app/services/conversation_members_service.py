# app/services/conversation_members_service.py

from app.models import ConversationMember, User
from app.services import BaseService

from app.schemas import ServiceResult
from app.constants import UserStatus, ConversationMemberRole

from app.validators import ConversationMemberValidator

from typing import Sequence


class ConversationMemberService(BaseService):
    """Provides relationships between conversations and users."""

    def add_member(
        self, user_id: int | None, conversation_id: int | None, role: str | None
    ) -> ServiceResult[ConversationMember]:
        """
        Add a member to conversation and Add the membership into the database.
        Returns:
            ServiceResult containing the added membership or validation errors.
        """

        if error := ConversationMemberValidator.user_role(role):
            return ServiceResult.fail({"role": error})

        result = self._require_user(user_id)

        if not result.success:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        result = self._require_conversation(conversation_id)

        if not result.success:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert user_id is not None
        assert conversation_id is not None

        membership = self.conversation_member_repository.get_membership(
            user_id, conversation_id
        )

        if membership is not None:
            return ServiceResult.fail(
                {"membership": "User is already a member of this conversation."}
            )

        membership = ConversationMember(
            user_id=user_id, conversation_id=conversation_id, role=role
        )

        membership = self.conversation_member_repository.create(
            conversation_member=membership
        )

        return ServiceResult.ok(membership)

    def get_member(
        self, user_id: int | None, conversation_id: int | None
    ) -> ServiceResult[ConversationMember]:
        """Return the membership for the given user ID and conversation ID."""

        return self._require_membership(user_id, conversation_id)

    def get_conversation_members(
        self,
        conversation_id: int | None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ServiceResult[Sequence[User]]:
        """Return the members for the given conversation ID."""

        result = self._require_conversation(conversation_id)

        if not result.success:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert conversation_id is not None

        memberships = self.conversation_member_repository.get_conversation_members(
            conversation_id, limit, offset
        )

        members: list[User] = []

        for membership in memberships:
            if membership.user.status == UserStatus.DELETED:
                continue
            members.append(membership.user)

        return ServiceResult.ok(members)
