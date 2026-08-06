# app/routes/web/main_routes.py

from flask import Blueprint, redirect, url_for
from flask.typing import ResponseReturnValue

main = Blueprint("main", __name__)


@main.get("/")
def index() -> ResponseReturnValue:
    return redirect(url_for("web.web_auth.signin"))
