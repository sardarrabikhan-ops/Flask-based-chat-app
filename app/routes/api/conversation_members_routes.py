# app/routes/api/conversation_members_routes.py

from flask import Blueprint, request, jsonify
from flask.typing import ResponseReturnValue

from app.utils.decorators import api_login_required
from app.schemas import ResponseBuilder, PaginationSchema

from app.dependencies import Dependencies
from app.results import FailureResult, ServiceResult, ResultCode

deps = Dependencies()

api_conversation_members = Blueprint(
    "api_conversation_members",
    __name__,
    url_prefix="/conversations",
)


@api_conversation_members.get("/<int:conversation_id>/members")
@api_login_required
def get_members(conversation_id: int) -> ResponseReturnValue:

    pagination_result = PaginationSchema.load(request.args)

    if isinstance(pagination_result, FailureResult):
        body, status = ResponseBuilder.build(pagination_result)
        return jsonify(body), status

    pagination = pagination_result.data

    result = deps.conversation_member_service.get_conversation_members(
        conversation_id=conversation_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    body, status = ResponseBuilder.build(
        result, include={"id", "firstname", "lastname"}
    )
    return jsonify(body), status


@api_conversation_members.get("/<int:conversation_id>/members/<int:user_id>")
@api_login_required
def get_member(conversation_id: int, user_id: int) -> ResponseReturnValue:

    result = deps.conversation_member_service.get_member(
        user_id=user_id,
        conversation_id=conversation_id,
    )

    if isinstance(result, FailureResult):
        body, status = ResponseBuilder.build(result)
        return jsonify(body), status

    body, status = ResponseBuilder.build(ServiceResult.ok(result.data.user))
    return jsonify(body), status


@api_conversation_members.post("/<int:conversation_id>/members")
@api_login_required
def add_member(conversation_id: int) -> ResponseReturnValue:

    payload = request.get_json(silent=True) or {}

    result = deps.conversation_member_service.add_member(
        user_id=payload.get("user_id"),
        conversation_id=conversation_id,
        role=payload.get("role"),
        actor_id=deps.required_user.id,
    )

    if isinstance(result, FailureResult):
        body, status = ResponseBuilder.build(result)
        return jsonify(body), status

    body, status = ResponseBuilder.build(
        ServiceResult.ok(None, code=ResultCode.CREATED)
    )
    return jsonify(body), status


@api_conversation_members.delete("/<int:conversation_id>/members/<int:user_id>")
@api_login_required
def remove_member(conversation_id: int, user_id: int) -> ResponseReturnValue:

    result = deps.conversation_member_service.remove_member(
        actor_id=deps.required_user.id,
        user_id=user_id,
        conversation_id=conversation_id,
    )

    if isinstance(result, FailureResult):
        body, status = ResponseBuilder.build(result)
        return jsonify(body), status

    body, status = ResponseBuilder.build(
        ServiceResult.ok(None)
    )
    return jsonify(body), status


@api_conversation_members.post("/<int:conversation_id>/members/leave")
@api_login_required
def leave_conversation(conversation_id: int) -> ResponseReturnValue:

    result = deps.conversation_member_service.leave(
        user_id=deps.required_user.id,
        conversation_id=conversation_id,
    )

    if isinstance(result, FailureResult):
        body, status = ResponseBuilder.build(result)
        return jsonify(body), status

    body, status = ResponseBuilder.build(
        ServiceResult.ok(None)
    )
    return jsonify(body), status
