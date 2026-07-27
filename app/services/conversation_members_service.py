# app/services/conversation_members_service.py

# add_member()
# leave()
# get_member()
# get_members()
# get_conversations()
# is_member()
# change_role()

from sqlalchemy.orm import Session

from app.models import ConversationMember
from app.repositories import (
    ConversationMemberRepository,
    ConversationRepository,
    UserRepository,
)
from app.schemas import ServiceResult


class ConversationMemberService:
    """Provides relationships between conversations and users."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ConversationMemberRepository(session)
        self.conversation_repository = ConversationRepository(session)
        self.user_repository = UserRepository(session)

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

        if user is None:
            return ServiceResult.fail({"user_id": "User not found."})

        conversation = self.conversation_repository.get_by_id(conversation_id)

        if conversation is None:
            return ServiceResult.fail({"conversation_id": "Conversation not found."})

        membership = self.repository.get(user_id, conversation_id)

        if membership is not None:
            return ServiceResult.fail(
                {"membership": "User is already a member of this conversation."}
            )

        membership = ConversationMember(
            user_id=user_id, conversation_id=conversation_id
        )

        membership = self.repository.create(conversation_member=membership)

        return ServiceResult.ok(membership)

    def leave(
        self, user_id: int | None, conversation_id: int | None
    ) -> ServiceResult[ConversationMember]:
        """
        Remove a member from conversation and delete the membership from database.
        User leaves a group.
        Returns:
            ServiceResult containing the deleted membership or validation errors.
        """

        if user_id is None:
            return ServiceResult.fail({"user_id": "User ID is required."})

        if conversation_id is None:
            return ServiceResult.fail(
                {"conversation_id": "Conversation ID is required."}
            )

        membership = self.repository.get(user_id, conversation_id)

        if membership is None:
            return ServiceResult.fail({"membership": "Membership not found."})

        self.repository.delete(membership)

        return ServiceResult.ok(membership)

    def get_member(
        self, user_id: int | None, conversation_id: int | None
    ) -> ServiceResult[ConversationMember]:
        """Return the membership for the given user and conversation."""

        if user_id is None:
            return ServiceResult.fail({"user_id": "User ID is required."})

        if conversation_id is None:
            return ServiceResult.fail(
                {"conversation_id": "Conversation ID is required."}
            )

        membership = self.repository.get(user_id, conversation_id)

        if membership is None:
            return ServiceResult.fail({"membership": "Membership not found."})

        return ServiceResult.ok(membership)
