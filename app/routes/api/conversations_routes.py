# app/routes/api/conversations_routes.py

from flask import Blueprint, request, jsonify
from flask.typing import ResponseReturnValue

from app.utils.decorators import api_login_required
from app.schemas import ResponseBuilder, PaginationSchema, SearchSchema

from app.dependencies import Dependencies
from app.results import FailureResult, ServiceResult

deps = Dependencies()

api_conversations = Blueprint(
    "api_conversations",
    __name__,
    url_prefix="/conversations",
)


@api_conversations.get("/")
@api_login_required
def get_conversations() -> ResponseReturnValue:

    pagination_result = PaginationSchema.load(request.args)

    if isinstance(pagination_result, FailureResult):
        body, status = ResponseBuilder.build(pagination_result)
        return jsonify(body), status

    search_result = SearchSchema.load(request.args)

    if isinstance(search_result, FailureResult):
        body, status = ResponseBuilder.build(search_result)
        return jsonify(body), status

    pagination = pagination_result.data
    search = search_result.data

    if search.name is not None:
        result = deps.conversation_service.search_by_name(
            user_id=deps.required_user.id,
            conversation_name=search.name,
            limit=pagination.limit,
            offset=pagination.offset,
        )

    else:
        result = deps.conversation_service.get_user_conversations(
            user_id=deps.required_user.id,
            limit=pagination.limit,
            offset=pagination.offset,
        )

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_conversations.get("/<int:conversation_id>")
@api_login_required
def get_conversation(conversation_id: int) -> ResponseReturnValue:

    result = deps.conversation_member_service.get_member(
        user_id=deps.required_user.id,
        conversation_id=conversation_id,
    )

    if isinstance(result, FailureResult):
        body, status = ResponseBuilder.build(result)
        return jsonify(body), status

    body, status = ResponseBuilder.build(ServiceResult.ok(result.data.conversation))
    return jsonify(body), status


@api_conversations.post("/groups")
@api_login_required
def create_group() -> ResponseReturnValue:

    payload = request.get_json(silent=True) or {}

    result = deps.conversation_service.create_group(
        actor_id=deps.required_user.id,
        name=payload.get("name"),
    )

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_conversations.patch("/<int:conversation_id>")
@api_login_required
def rename_group(conversation_id: int) -> ResponseReturnValue:

    payload = request.get_json(silent=True) or {}

    result = deps.conversation_service.rename(
        actor_id=deps.required_user.id,
        conversation_id=conversation_id,
        new_name=payload.get("new_name"),
    )

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_conversations.patch("/<int:conversation_id>/archive")
@api_login_required
def archive_conversation(conversation_id: int) -> ResponseReturnValue:

    result = deps.conversation_service.archive(
        conversation_id=conversation_id,
        user_id=deps.required_user.id,
    )

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_conversations.delete("/<int:conversation_id>")
@api_login_required
def delete_conversation(conversation_id: int) -> ResponseReturnValue:

    result = deps.conversation_service.delete(
        conversation_id=conversation_id,
        user_id=deps.required_user.id,
    )

    if isinstance(result, FailureResult):
        body, status = ResponseBuilder.build(result)
        return jsonify(body), status

    body, status = ResponseBuilder.build(ServiceResult.ok(None))
    return jsonify(body), status
