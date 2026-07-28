# app/repositories/messages_repo.py


from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.models import Message
from app.constants import MessageStatus

from typing import Sequence


class MessageRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, message_id: int) -> Message | None:
        return self.session.get(Message, message_id)

    def get_by_conversation_id(
        self,
        conversation_id: int,
        status: MessageStatus | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[Message]:

        statement = select(Message).where(Message.conversation_id == conversation_id)

        if status is not None:
            statement = statement.where(Message.status == MessageStatus.ACTIVE)

        if limit is not None:
            statement = statement.limit(limit)

        if offset is not None:
            statement = statement.offset(offset)

        statement = statement.order_by(Message.created_at)

        return self.session.scalars(statement).all()

    def create(self, message: Message) -> Message:
        self.session.add(message)
        return message
