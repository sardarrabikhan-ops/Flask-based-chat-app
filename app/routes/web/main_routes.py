# app/routes/web/main_routes.py

from flask import Blueprint, redirect, url_for, g
from flask.typing import ResponseReturnValue

main = Blueprint("main", __name__)


@main.get("/")
def index() -> ResponseReturnValue:

    if g.user is None:
        return redirect(url_for("web.web_auth.signin"))

    return redirect(url_for("web.web_users.users"))
