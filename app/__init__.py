# app/__init__.py

from flask import Flask

from app.config import Config
from app.routes import register_blueprints
from app.request_hooks import register_request_hooks
from app.error_handlers import register_error_handlers
from app.logging_config import configure_logging

def create_app() -> Flask:

    app = Flask(__name__)

    app.config.from_object(Config)

    configure_logging()

    register_blueprints(app)
    register_request_hooks(app)
    register_error_handlers(app)

    return app
