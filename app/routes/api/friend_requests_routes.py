# app/routes/api/friend_requests_routes.py

from flask import Blueprint, request, jsonify
from flask.typing import ResponseReturnValue

from app.utils.decorators import api_login_required
from app.schemas import ResponseBuilder, PaginationSchema

from app.dependencies import Dependencies
from app.results import FailureResult

deps = Dependencies()

api_friend_requests = Blueprint(
    "api_friend_requests", __name__, url_prefix="/friend-requests"
)


@api_friend_requests.get("/sent")
@api_login_required
def get_sent_friend_requests() -> ResponseReturnValue:

    pagination_result = PaginationSchema.load(request.args)

    if isinstance(pagination_result, FailureResult):
        body, status = ResponseBuilder.build(pagination_result)
        return jsonify(body), status

    pagination = pagination_result.data

    result = deps.friend_request_service.get_sent_requests(
        sender_id=deps.required_user.id,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_friend_requests.get("/received")
@api_login_required
def get_received_friend_requests() -> ResponseReturnValue:

    pagination_result = PaginationSchema.load(request.args)

    if isinstance(pagination_result, FailureResult):
        body, status = ResponseBuilder.build(pagination_result)
        return jsonify(body), status

    pagination = pagination_result.data

    result = deps.friend_request_service.get_received_requests(
        receiver_id=deps.required_user.id,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_friend_requests.post("/")
@api_login_required
def send_friend_request() -> ResponseReturnValue:

    payload = request.get_json(silent=True) or {}

    result = deps.friend_request_service.send(
        sender_id=deps.required_user.id,
        receiver_id=payload.get("receiver_id"),
    )

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_friend_requests.patch("/<int:friend_request_id>/accept")
@api_login_required
def accept_friend_request(friend_request_id: int) -> ResponseReturnValue:

    result = deps.friend_request_service.accept(
        friend_request_id=friend_request_id,
        actor_id=deps.required_user.id,
    )

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_friend_requests.patch("/<int:friend_request_id>/reject")
@api_login_required
def reject_friend_request(friend_request_id: int) -> ResponseReturnValue:

    result = deps.friend_request_service.reject(
        friend_request_id=friend_request_id,
        actor_id=deps.required_user.id,
    )

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_friend_requests.delete("/<int:friend_request_id>/cancel")
@api_login_required
def delete_friend_request(friend_request_id: int) -> ResponseReturnValue:

    result = deps.friend_request_service.cancel(
        friend_request_id=friend_request_id,
        actor_id=deps.required_user.id,
    )

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status
