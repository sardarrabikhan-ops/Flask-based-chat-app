# app/repositories/messages_repo.py

from sqlalchemy import select

from app.repositories import BaseRepository
from app.models import Message
from app.constants import MessageStatus

from typing import Sequence


class MessageRepository(BaseRepository):

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
            statement = statement.where(Message.status == status)

        statement = self._paginate(statement, limit, offset).order_by(
            Message.created_at, Message.id
        )

        return self.session.scalars(statement).all()

    def create(self, message: Message) -> Message:
        self.session.add(message)
        return message
