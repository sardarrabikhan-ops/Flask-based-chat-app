# app/models/conversation_members.py

from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, text, CheckConstraint, ForeignKey

from app.database import Base
from app.constants import ConversationMemberRole

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.conversations import Conversation


class ConversationMember(Base):

    __tablename__ = "conversation_members"

    allowed_roles = ", ".join(f"'{role.value}'" for role in ConversationMemberRole)

    __table_args__ = (
        CheckConstraint(
            f"role IN ({allowed_roles})",
            name="ck_conversation_members_role_valid",
        ),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), primary_key=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    role: Mapped[str] = mapped_column(
        String(15), default=ConversationMemberRole.MEMBER.value, nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="conversation_members")

    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="members"
    )
