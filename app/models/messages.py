# app/models/messages.py

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, text, CheckConstraint, ForeignKey

from datetime import datetime
from app.database import Base
from app.constants import MessageStatus


class Message(Base):

    __tablename__ = "messages"

    allowed = ", ".join(f"'{status.value}'" for status in MessageStatus)

    __table_args__ = (
            CheckConstraint(
                f"status IN ({allowed})",
                name="ck_messages_status_valid",
            )
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

    status: Mapped[str] = mapped_column(String(15), default=MessageStatus.ACTIVE.value, nullable=False)