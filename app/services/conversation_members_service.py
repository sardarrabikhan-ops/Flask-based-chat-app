# app/services/conversation_members_service.py

from app.models import ConversationMember, User
from app.services import BaseService

from app.schemas import ServiceResult
from app.constants import (
    UserStatus,
    ConversationMemberRole,
    ConversationType,
    ConversationMemberStatus,
)

from app.validators import ConversationMemberValidator

from typing import Sequence


class ConversationMemberService(BaseService):
    """Provides relationships between conversations and users."""

    def add_member(
        self,
        user_id: int | None,
        conversation_id: int | None,
        role: str | None,
        actor_id: int | None,
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

        assert user_id is not None

        result = self._require_conversation(conversation_id)

        if not result.success:
            assert result.errors is not None
            return ServiceResult.fail(result.errors)

        assert conversation_id is not None
        assert result.data is not None

        conversation = result.data

        membership = self.conversation_member_repository.get_membership(
            user_id, conversation_id, removed=True
        )

        if (
            membership is not None
            and membership.status == ConversationMemberStatus.ACTIVE
        ):
            return ServiceResult.fail(
                {"membership": "User is already a member of this conversation."}
            )

        if membership is not None:
            membership.status = ConversationMemberStatus.ACTIVE
            membership.is_archived = False
            membership.is_hidden = False

        if conversation.conversation_type == ConversationType.PRIVATE:
            return ServiceResult.fail(
                {"conversation": "Private conversations can only contain two members."}
            )

        actor_membership_result = self._require_membership(actor_id, conversation_id)

        if not actor_membership_result.success:
            return actor_membership_result

        assert actor_membership_result.data is not None

        actor_membership = actor_membership_result.data

        if actor_membership.role != ConversationMemberRole.ADMIN:
            return ServiceResult.fail(
                {"permission": "Only administrators can add members."}
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

    def remove_member(
        self, actor_id: int | None, user_id: int | None, conversation_id: int | None
    ) -> ServiceResult[ConversationMember]:
        """Soft-delete the membership of the given ID's by marking it's status as REMOVED."""

        actor_membership_result = self._require_membership(actor_id, conversation_id)

        if not actor_membership_result.success:
            return actor_membership_result

        assert actor_membership_result.data is not None

        actor_membership = actor_membership_result.data

        if actor_membership.role != ConversationMemberRole.ADMIN:
            return ServiceResult.fail(
                {"permission": "Only administrators can remove members."}
            )

        result = self._require_membership(user_id, conversation_id)

        if not result.success:
            return result

        assert result.data is not None

        membership = result.data

        membership.status = ConversationMemberStatus.REMOVED
        membership.is_hidden = True

        return ServiceResult.ok(membership)

    def leave(
        self, user_id: int | None, conversation_id: int | None
    ) -> ServiceResult[ConversationMember]:
        """Soft-delete the membership of the given ID's by marking it's status as REMOVED."""

        result = self._require_membership(user_id, conversation_id)

        if not result.success:
            return result

        assert result.data is not None

        membership = result.data

        membership.status = ConversationMemberStatus.LEFT
        membership.is_hidden = True

        return ServiceResult.ok(membership)
