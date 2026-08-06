"""add performance indexes

Revision ID: 6d38363372d6
Revises: 1cc84e21d876
Create Date: 2026-08-06 09:58:18.446132

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "6d38363372d6"
down_revision: Union[str, Sequence[str], None] = "1cc84e21d876"
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
