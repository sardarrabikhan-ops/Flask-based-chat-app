# app/services/conversation_members_service.py

from app.models import ConversationMember, User
from app.services import BaseService

from app.constants import (
    UserStatus,
    ConversationMemberRole,
    ConversationType,
    ConversationMemberStatus,
)

from app.validators import ConversationMemberValidator
from app.results import ServiceResult, Result, ResultCode, FailureResult

from typing import Sequence
import logging

logger = logging.getLogger(__name__)


class ConversationMemberService(BaseService):
    """Provides relationships between conversations and users."""

    def add_member(
        self,
        user_id: int | None,
        conversation_id: int | None,
        role: str | None,
        actor_id: int | None,
    ) -> Result[ConversationMember]:
        """
        Add a member to conversation and Add the membership into the database.
        Returns:
            ServiceResult containing the added membership or validation errors.
        """

        if error := ConversationMemberValidator.role(role):
            return ServiceResult.fail({"role": error})

        assert role is not None

        clean_role = ConversationMemberRole(role.strip())

        result = self._require_user(user_id)

        if isinstance(result, FailureResult):
            return result

        assert user_id is not None

        result = self._require_conversation(conversation_id)

        if isinstance(result, FailureResult):
            return result

        assert conversation_id is not None

        conversation = result.data

        if conversation.conversation_type == ConversationType.PRIVATE:
            return ServiceResult.fail(
                {"permission": "Members cannot be added to private conversations."},
                code=ResultCode.FORBIDDEN,
            )

        actor_membership_result = self._require_membership(actor_id, conversation_id)

        if isinstance(actor_membership_result, FailureResult):
            return actor_membership_result

        actor_membership = actor_membership_result.data

        if actor_membership.role != ConversationMemberRole.ADMIN:
            return ServiceResult.fail(
                {"permission": "Only administrators can add members."},
                code=ResultCode.FORBIDDEN,
            )

        membership = self.conversation_member_repository.get_membership(
            user_id, conversation_id, removed=True
        )

        if (
            membership is not None
            and membership.status == ConversationMemberStatus.ACTIVE
        ):
            return ServiceResult.fail(
                {"membership": "User is already a member of this conversation."},
                code=ResultCode.CONFLICT,
            )

        if membership is not None:
            membership.status = ConversationMemberStatus.ACTIVE
            membership.role = clean_role
            membership.is_archived = False
            membership.is_hidden = False

            logger.info(
                "User restored a conversation member. %s %s %s",
                actor_membership.user,
                membership.user,
                membership.conversation,
            )
            return ServiceResult.ok(membership)

        membership = ConversationMember(
            user_id=user_id, conversation_id=conversation_id, role=clean_role
        )

        membership = self.conversation_member_repository.create(
            conversation_member=membership
        )

        logger.info(
            "User added a member to conversation. %s %s %s",
            actor_membership.user,
            membership.user,
            membership.conversation,
        )
        return ServiceResult.ok(membership, code=ResultCode.CREATED)

    def get_membership(
        self,
        user_id: int | None,
        conversation_id: int | None,
    ) -> Result[ConversationMember]:
        """Return the membership for the given user ID and conversation ID."""

        return self._require_membership(user_id, conversation_id)

    def get_member(
        self,
        user_id: int | None,
        conversation_id: int | None,
        actor_id: int | None,
    ) -> Result[User]:
        """Return a conversation member's user if the actor is also a member."""

        result = self._require_membership(user_id, conversation_id)

        if isinstance(result, FailureResult):
            return result

        result = self._require_membership(actor_id, conversation_id)

        if isinstance(result, FailureResult):
            return result

        return ServiceResult.ok(result.data.user)

    def get_conversation_members(
        self,
        conversation_id: int | None,
        actor_id: int | None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Result[Sequence[User]]:
        """Return the members for the given conversation ID."""

        result = self._require_membership(actor_id, conversation_id)

        if isinstance(result, FailureResult):
            return result

        assert conversation_id is not None

        memberships = self.conversation_member_repository.get_conversation_members(
            conversation_id, limit, offset
        )

        members = [
            membership.user
            for membership in memberships
            if membership.user.status != UserStatus.DELETED
        ]

        return ServiceResult.ok(members)

    def remove_member(
        self, actor_id: int | None, user_id: int | None, conversation_id: int | None
    ) -> Result[ConversationMember]:
        """Soft-delete the membership of the given ID's by marking it's status as REMOVED."""

        actor_membership_result = self._require_membership(actor_id, conversation_id)

        if isinstance(actor_membership_result, FailureResult):
            return actor_membership_result

        actor_membership = actor_membership_result.data

        if actor_membership.role != ConversationMemberRole.ADMIN:
            return ServiceResult.fail(
                {"permission": "Only administrators can remove members."},
                code=ResultCode.FORBIDDEN,
            )

        result = self._require_membership(user_id, conversation_id)

        if isinstance(result, FailureResult):
            return result

        membership = result.data

        if membership.role == ConversationMemberRole.ADMIN:
            return ServiceResult.fail(
                {"permission": "You cannot remove administrators."},
                code=ResultCode.FORBIDDEN,
            )

        membership.status = ConversationMemberStatus.REMOVED
        membership.is_hidden = True

        logger.info(
            "User removed a member from conversation. %s %s %s",
            actor_membership.user,
            membership.user,
            membership.conversation,
        )
        return ServiceResult.ok(membership)

    def leave(
        self, user_id: int | None, conversation_id: int | None
    ) -> Result[ConversationMember]:
        """Soft-delete the membership of the given ID's by marking it's status as REMOVED."""

        result = self._require_membership(user_id, conversation_id)

        if isinstance(result, FailureResult):
            return result

        membership = result.data

        membership.status = ConversationMemberStatus.LEFT
        membership.is_hidden = True

        logger.info(
            "User left conversation. %s %s",
            membership.user,
            membership.conversation,
        )
        return ServiceResult.ok(membership)
