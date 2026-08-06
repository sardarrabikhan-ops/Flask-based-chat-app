# app/routes/api/friends_routes.py

from flask import Blueprint, request, jsonify
from flask.typing import ResponseReturnValue

from app.utils.decorators import api_login_required
from app.schemas import ResponseBuilder, PaginationSchema

from app.dependencies import Dependencies
from app.results import FailureResult, ServiceResult

deps = Dependencies()

api_friends = Blueprint("api_friends", __name__, url_prefix="/friends")


@api_friends.get("/")
@api_login_required
def get_friends() -> ResponseReturnValue:

    pagination_result = PaginationSchema.load(request.args)

    if isinstance(pagination_result, FailureResult):
        body, status = ResponseBuilder.build(pagination_result)
        return jsonify(body), status

    pagination = pagination_result.data

    result = deps.friend_service.get_friends(
        user_id=deps.required_user.id,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_friends.get("/<int:friend_id>")
@api_login_required
def get_friend(friend_id: int) -> ResponseReturnValue:

    result = deps.friend_service.get(
        user_id=deps.required_user.id,
        friend_id=friend_id,
    )

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_friends.delete("/<int:friend_id>")
@api_login_required
def delete_friend(friend_id: int) -> ResponseReturnValue:

    result = deps.friend_service.delete(
        user_id=deps.required_user.id,
        friend_id=friend_id,
    )

    if isinstance(result, FailureResult):
        body, status = ResponseBuilder.build(result)
        return jsonify(body), status

    body, status = ResponseBuilder.build(ServiceResult.ok(None))
    return jsonify(body), status
