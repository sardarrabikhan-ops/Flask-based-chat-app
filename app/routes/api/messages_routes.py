# app/routes/api/messages_routes.py

from flask import Blueprint, request, jsonify
from flask.typing import ResponseReturnValue

from app.utils.decorators import api_login_required
from app.schemas import ResponseBuilder, PaginationSchema

from app.dependencies import Dependencies
from app.results import FailureResult, ServiceResult

deps = Dependencies()

api_messages = Blueprint("api_messages", __name__)


@api_messages.get("/conversations/<int:conversation_id>/messages")
@api_login_required
def get_messages(conversation_id: int) -> ResponseReturnValue:

    pagination_result = PaginationSchema.load(request.args)

    if isinstance(pagination_result, FailureResult):
        body, status = ResponseBuilder.build(pagination_result)
        return jsonify(body), status

    pagination = pagination_result.data

    result = deps.message_service.get_conversation_messages(
        user_id=deps.required_user.id,
        conversation_id=conversation_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_messages.post("/conversations/<int:conversation_id>/messages")
@api_login_required
def send_in_conversation(conversation_id: int) -> ResponseReturnValue:

    payload = request.get_json(silent=True) or {}

    result = deps.message_service.send_in_conversation(
        sender_id=deps.required_user.id,
        conversation_id=conversation_id,
        content=payload.get("content"),
    )

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_messages.post("/messages/private")
@api_login_required
def send_private() -> ResponseReturnValue:

    payload = request.get_json(silent=True) or {}

    result = deps.message_service.send_private(
        sender_id=deps.required_user.id,
        receiver_id=payload.get("receiver_id"),
        content=payload.get("content"),
    )

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_messages.patch("/messages/<int:message_id>")
@api_login_required
def edit_message(message_id: int) -> ResponseReturnValue:

    payload = request.get_json(silent=True) or {}

    result = deps.message_service.edit(
        user_id=deps.required_user.id,
        message_id=message_id,
        content=payload.get("content"),
    )

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_messages.delete("/messages/<int:message_id>")
@api_login_required
def delete_message(message_id: int) -> ResponseReturnValue:

    result = deps.message_service.delete(
        user_id=deps.required_user.id,
        message_id=message_id,
    )

    if isinstance(result, FailureResult):
        body, status = ResponseBuilder.build(result)
        return jsonify(body), status

    body, status = ResponseBuilder.build(ServiceResult.ok(None))
    return jsonify(body), status
