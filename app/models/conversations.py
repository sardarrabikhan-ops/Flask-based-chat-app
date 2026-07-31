# app/models/conversations.py

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, text, CheckConstraint, Enum

from app.database import Base
from app.utils import get_enum_values
from app.constants import ConversationType, CONVERSATION_NAME_MAX_LENGTH

if TYPE_CHECKING:
    from app.models.conversation_members import ConversationMember
    from app.models.messages import Message


class Conversation(Base):

    __tablename__ = "conversations"

    allowed_type = get_enum_values(ConversationType)

    __table_args__ = (
        CheckConstraint(
            f"conversation_type IN ({allowed_type})",
            name="ck_conversations_conversation_type_valid",
        ),
        CheckConstraint(
            f"""
            (conversation_type = '{ConversationType.PRIVATE.value}' AND name IS NULL)
            OR
            (conversation_type = '{ConversationType.GROUP.value}' AND name IS NOT NULL)
            """,
            name="ck_conversation_name_matches_type",
        ),
    )

    def __repr__(self) -> str:
        return f"Conversation(id={self.id}, conversation_type={self.conversation_type}, created_at={self.created_at})"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str | None] = mapped_column(String(CONVERSATION_NAME_MAX_LENGTH), nullable=True)

    conversation_type: Mapped[ConversationType] = mapped_column(
        Enum(
            ConversationType,
            values_callable=lambda enum: [e.value for e in enum],
            name="conversationtype",
        ),
        nullable=False,
        default=ConversationType.PRIVATE,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    members: Mapped[list["ConversationMember"]] = relationship(
        "ConversationMember",
        back_populates="conversation",
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation"
    )
