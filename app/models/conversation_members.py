# app/models/conversation_members.py

from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, text, CheckConstraint, ForeignKey, Enum

from app.database import Base
from app.constants import ConversationMemberRole, ConversationMemberStatus
from app.utils import get_enum_values

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.conversations import Conversation


class ConversationMember(Base):

    __tablename__ = "conversation_members"

    allowed_roles = get_enum_values(ConversationMemberRole)
    allowed_status = get_enum_values(ConversationMemberStatus)

    __table_args__ = (
        CheckConstraint(
            f"role IN ({allowed_roles})",
            name="ck_conversation_members_role_valid",
        ),
        CheckConstraint(
            f"status IN ({allowed_status})",
            name="ck_conversation_members_status_valid",
        ),
    )

    def __repr__(self) -> str:
        return f"ConversationMember(user_id={self.user_id}, conversation_id={self.conversation_id}, role={self.role}, joined_at={self.joined_at})"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"), primary_key=True
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    status: Mapped[ConversationMemberStatus] = mapped_column(
        Enum(
            ConversationMemberStatus,
            values_callable=lambda enum: [e.value for e in enum],
            name="conversationmemberstatus",
        ),
        nullable=False,
        default=ConversationMemberStatus.ACTIVE,
    )

    is_archived: Mapped[bool] = mapped_column(nullable=False, default=False)

    is_hidden: Mapped[bool] = mapped_column(nullable=False, default=False)

    role: Mapped[ConversationMemberRole] = mapped_column(
        Enum(
            ConversationMemberRole,
            values_callable=lambda enum: [e.value for e in enum],
            name="conversationmemberrole",
        ),
        nullable=False,
        default=ConversationMemberRole.MEMBER,
    )

    user: Mapped["User"] = relationship("User", back_populates="conversation_members")

    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="members"
    )
