# app/routes/web/friend_requests_routes.py

from app.utils.decorators import login_required

from flask import Blueprint, render_template

web_friend_requests = Blueprint("web_friend_requests", __name__, url_prefix="/friend-requests")


@web_friend_requests.get("/")
@login_required
def friend_requests() -> str:
    return render_template("index.html")
