# app/routes/__init__.py

from app.routes.web import web
from app.routes.api import api


from flask import Flask


def register_blueprints(app: Flask) -> None:

    app.register_blueprint(web)
    app.register_blueprint(api)