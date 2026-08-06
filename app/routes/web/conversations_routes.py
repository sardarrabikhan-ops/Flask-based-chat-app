# app/routes/web/chats_routes.py

from app.utils.decorators import login_required

from flask import Blueprint, render_template

web_chats = Blueprint("web_chats", __name__, url_prefix="/chats")


@web_chats.get("/")
@login_required
def chats() -> str:
    return render_template("chats.html")


@web_chats.get("/<int:conversation_id>")
@login_required
def chat(conversation_id: int) -> str:
    return render_template("chats.html", conversation_id=conversation_id)
