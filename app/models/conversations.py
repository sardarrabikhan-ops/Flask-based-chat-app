# app/models/conversations.py

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, text, CheckConstraint

from datetime import datetime
from app.database import Base
from app.constants import ConversationType, ConversationStatus


class Conversation(Base):

    __tablename__ = "conversations"

    allowed_status = ", ".join(f"'{status.value}'" for status in ConversationStatus)
    allowed_type = ", ".join(
        f"'{conversation_type .value}'" for conversation_type in ConversationType
    )

    __table_args__ = (
        CheckConstraint(
            f"conversation_type IN ({allowed_type})",
            name="ck_conversations_conversation_type_valid",
        ),
        CheckConstraint(
            f"status IN ({allowed_status})",
            name="ck_conversations_status_valid",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str | None] = mapped_column(String(30), default=None, nullable=True)

    conversation_type: Mapped[str] = mapped_column(
        String(15), default=ConversationType.PRIVATE.value, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(15), default=ConversationStatus.ACTIVE.value, nullable=False
    )
