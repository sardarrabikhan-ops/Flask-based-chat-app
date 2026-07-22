# app/models/messages.py

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, text, CheckConstraint, ForeignKey

from app.database import Base
from app.constants import MessageStatus

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.conversations import Conversation


class Message(Base):

    __tablename__ = "messages"

    allowed_status = ", ".join(f"'{status.value}'" for status in MessageStatus)

    __table_args__ = (
        CheckConstraint(
            f"status IN ({allowed_status})",
            name="ck_messages_status_valid",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"), nullable=False
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    status: Mapped[str] = mapped_column(
        String(15), default=MessageStatus.ACTIVE.value, nullable=False
    )

    sender: Mapped["User"] = relationship("User", back_populates="messages")

    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )
