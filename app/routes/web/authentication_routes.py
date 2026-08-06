# app/routes/web/authentication_routes.py

from app.utils.decorators import login_required

from flask import Blueprint, render_template

web_auth = Blueprint("web_auth", __name__)


@web_auth.get("/signin")
def signin() -> str:
    return render_template("signin.html")


@web_auth.get("/signup")
def signup() -> str:
    return render_template("signup.html")
