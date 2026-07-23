# app/models/conversations.py

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, text, CheckConstraint, ForeignKey

from app.database import Base
from app.constants import ConversationType, ConversationStatus
from app.utils import get_enum_values

if TYPE_CHECKING:
    from app.models.conversation_members import ConversationMember
    from app.models.messages import Message


class Conversation(Base):

    __tablename__ = "conversations"

    allowed_status = get_enum_values(ConversationStatus)
    allowed_type = get_enum_values(ConversationType)

    __table_args__ = (
        CheckConstraint(
            f"conversation_type IN ({allowed_type})",
            name="ck_conversations_conversation_type_valid",
        ),
        CheckConstraint(
            f"status IN ({allowed_status})",
            name="ck_conversations_status_valid",
        ),
        CheckConstraint(
            "conversation_type = 'private' OR name IS NOT NULL",
            name="ck_conversations_group_requires_name",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str | None] = mapped_column(String(30), nullable=True)

    conversation_type: Mapped["ConversationType"] = mapped_column(
        String(15), default=ConversationType.PRIVATE.value, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    status: Mapped["ConversationStatus"] = mapped_column(
        String(15), default=ConversationStatus.ACTIVE.value, nullable=False
    )

    members: Mapped[list["ConversationMember"]] = relationship(
        "ConversationMember",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
