# app/routes/web/authentication_routes.py

from flask import Blueprint, render_template

web_auth = Blueprint("web_auth", __name__)


@web_auth.get("/signin")
def signin() -> str:
    return render_template("index.html")


@web_auth.get("/signup")
def signup() -> str:
    return render_template("index.html")
