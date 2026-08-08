# app/routes/web/profile_routes.py

from app.utils.decorators import login_required

from flask import Blueprint, render_template

web_profile = Blueprint("web_profile", __name__, url_prefix="/profile")


@web_profile.get("/")
@login_required
def profile() -> str:
    return render_template("index.html")
