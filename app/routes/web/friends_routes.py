# app/routes/web/friends_routes.py

from app.utils.decorators import login_required

from flask import Blueprint, render_template

web_friends = Blueprint("web_friends", __name__, url_prefix="/friends")


@web_friends.get("/")
@login_required
def friends() -> str:
    return render_template("friends.html")
