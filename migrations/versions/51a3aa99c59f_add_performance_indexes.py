"""add performance indexes

Revision ID: 51a3aa99c59f
Revises: 7836ae2bb0b3
Create Date: 2026-08-06 19:55:42.694621

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "51a3aa99c59f"
down_revision: Union[str, Sequence[str], None] = "7836ae2bb0b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ==========================
    # Messages
    # ==========================

    op.create_index(
        "ix_messages_conversation_created",
        "messages",
        ["conversation_id", "created_at", "id"],
    )

    # ==========================
    # Conversation Members
    # ==========================

    op.create_index(
        "ix_conversation_members_conversation",
        "conversation_members",
        ["conversation_id"],
    )

    # ==========================
    # Friends
    # ==========================

    op.create_index(
        "ix_friends_friend",
        "friends",
        ["friend_id"],
    )

    # ==========================
    # Friend Requests
    # ==========================

    op.create_index(
        "ix_friend_requests_sender",
        "friend_requests",
        ["sender_id"],
    )

    op.create_index(
        "ix_friend_requests_receiver",
        "friend_requests",
        ["receiver_id"],
    )

    # Only one pending request between two users
    op.create_index(
        "uq_friend_requests_pending",
        "friend_requests",
        ["sender_id", "receiver_id"],
        unique=True,
        postgresql_where=sa.text("status = 'pending'"),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index("uq_friend_requests_pending")

    op.drop_index("ix_friend_requests_receiver")

    op.drop_index("ix_friend_requests_sender")

    op.drop_index("ix_friends_friend")

    op.drop_index("ix_conversation_members_conversation")

    op.drop_index("ix_messages_conversation_created")
