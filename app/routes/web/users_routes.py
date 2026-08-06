# app/routes/web/users_routes.py

from app.utils.decorators import login_required

from flask import Blueprint, render_template

web_users = Blueprint("web_users", __name__, url_prefix="/users")


@web_users.get("/")
@login_required
def users() -> str:
    return render_template("users.html")


@web_users.get("/<int:user_id>")
@login_required
def profile(user_id: int) -> str:
    return render_template("user_profile.html", user_id=user_id)
