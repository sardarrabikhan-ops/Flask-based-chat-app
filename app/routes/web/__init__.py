# app/routes/web/__init__.py

from flask import Blueprint

web = Blueprint("web", __name__)

from app.routes.web.main_routes import main
from app.routes.web.authentication_routes import web_auth
from app.routes.web.users_routes import web_users
from app.routes.web.conversations_routes import web_chats
from app.routes.web.profile_routes import web_profile
from app.routes.web.friends_routes import web_friends
from app.routes.web.friend_requests_routes import web_friend_requests

web.register_blueprint(main)
web.register_blueprint(web_auth)
web.register_blueprint(web_users)
web.register_blueprint(web_chats)
web.register_blueprint(web_profile)
web.register_blueprint(web_friends)
web.register_blueprint(web_friend_requests)
