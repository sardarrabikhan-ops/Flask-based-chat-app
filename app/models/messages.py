# app/models/messages.py

from datetime import datetime, UTC
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, DateTime, text, CheckConstraint, ForeignKey, Enum

from app.database import Base
from app.constants import MessageStatus, MessageDeliveryStatus
from app.utils import get_enum_values

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.conversations import Conversation


class Message(Base):

    __tablename__ = "messages"

    allowed_status = get_enum_values(MessageStatus)
    allowed_delivery_status = get_enum_values(MessageDeliveryStatus)

    __table_args__ = (
        CheckConstraint(
            f"status IN ({allowed_status})",
            name="ck_messages_status_valid",
        ),
        CheckConstraint(
            f"delivery_status IN ({allowed_delivery_status})",
            name="ck_messages_delivery_status_valid",
        ),
    )

    def __repr__(self) -> str:
        preview = self.content[:20] + "..." if len(self.content) > 20 else self.content

        return f"Message(id={self.id}, sender_id={self.sender_id}, conversation_id={self.conversation_id}, content={preview}, status={self.status}, delivery_status={self.delivery_status}, created_at={self.created_at}, updated_at={self.updated_at})"

    id: Mapped[int] = mapped_column(primary_key=True)

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"), nullable=False
    )

    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    content: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[MessageStatus] = mapped_column(
        Enum(
            MessageStatus,
            values_callable=lambda enum: [e.value for e in enum],
            name="messagestatus",
        ),
        nullable=False,
        default=MessageStatus.ACTIVE,
    )

    delivery_status: Mapped[MessageDeliveryStatus] = mapped_column(
        Enum(
            MessageDeliveryStatus,
            values_callable=lambda enum: [e.value for e in enum],
            name="messagedeliverystatus",
        ),
        nullable=False,
        default=MessageDeliveryStatus.SENT,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=lambda: datetime.now(UTC),
    )

    sender: Mapped["User"] = relationship("User", back_populates="messages")

    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )
