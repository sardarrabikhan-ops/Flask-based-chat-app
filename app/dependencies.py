# app/dependencies

from flask import g
from sqlalchemy.orm import Session

from functools import cached_property

from app.models import User
from app.services import (
    AuthenticationService,
    UserService,
    ConversationService,
    ConversationMemberService,
    MessageService,
    FriendService,
    FriendRequestService,
)

from typing import cast


class Dependencies:

    @cached_property
    def authentication_service(self) -> AuthenticationService:
        return AuthenticationService(g.db)

    @cached_property
    def user_service(self) -> UserService:
        return UserService(g.db)

    @cached_property
    def conversation_service(self) -> ConversationService:
        return ConversationService(g.db)

    @cached_property
    def conversation_member_service(self) -> ConversationMemberService:
        return ConversationMemberService(g.db)

    @cached_property
    def message_service(self) -> MessageService:
        return MessageService(g.db)

    @cached_property
    def friend_service(self) -> FriendService:
        return FriendService(g.db)

    @cached_property
    def friend_request_service(self) -> FriendRequestService:
        return FriendRequestService(g.db)

    @property
    def db(self) -> Session:
        return cast(Session, g.db)

    @property
    def current_user(self) -> User | None:
        return cast(User | None, g.user)

    @property
    def required_user(self) -> User:
        user = self.current_user
        assert user is not None
        return user
