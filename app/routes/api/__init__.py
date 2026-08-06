# app/routes/api/__init__.py

from flask import Blueprint

api = Blueprint("api", __name__, url_prefix="/api")

from app.routes.api.authentication_routes import api_auth
from app.routes.api.users_routes import api_users
from app.routes.api.conversations_routes import api_conversations
from app.routes.api.conversation_members_routes import api_conversation_members
from app.routes.api.messages_routes import api_messages
from app.routes.api.friends_routes import api_friends
from app.routes.api.friend_requests_routes import api_friend_requests

api.register_blueprint(api_auth)
api.register_blueprint(api_users)
api.register_blueprint(api_conversations)
api.register_blueprint(api_conversation_members)
api.register_blueprint(api_messages)
api.register_blueprint(api_friends)
api.register_blueprint(api_friend_requests)
