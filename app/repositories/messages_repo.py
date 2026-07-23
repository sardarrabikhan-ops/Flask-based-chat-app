# app/repositories/messages_repo.py


from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Message
from app.constants import MessageStatus

from typing import Sequence


class MessageRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, message_id: int) -> Message | None:
        return self.session.get(Message, message_id)

    def get_by_sender_id(self, sender_id: int) -> Sequence[Message]:
        statement = select(Message).where(Message.sender_id == sender_id)
        return self.session.scalars(statement).all()

    def get_active_by_sender_id(self, sender_id: int) -> Sequence[Message]:
        statement = select(Message).where(
            Message.sender_id == sender_id,
            Message.status != MessageStatus.DELETED.value,
        )
        return self.session.scalars(statement).all()

    def get_by_conversation_id(self, conversation_id: int) -> Sequence[Message]:
        statement = select(Message).where(Message.conversation_id == conversation_id)
        return self.session.scalars(statement).all()

    def get_active_by_conversation_id(self, conversation_id: int) -> Sequence[Message]:
        statement = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.status != MessageStatus.DELETED.value,
        )
        return self.session.scalars(statement).all()

    def create(self, message: Message) -> Message:
        self.session.add(message)
        return message
