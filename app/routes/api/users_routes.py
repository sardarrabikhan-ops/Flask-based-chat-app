# app/routes/api/users_routes.py

from flask import Blueprint, request, jsonify, session
from flask.typing import ResponseReturnValue

from app.utils.decorators import api_login_required
from app.schemas import ResponseBuilder, PaginationSchema, SearchSchema

from app.dependencies import Dependencies
from app.results import FailureResult, ServiceResult

deps = Dependencies()

api_users = Blueprint("api_users", __name__, url_prefix="/users")


@api_users.get("/")
@api_login_required
def get_users() -> ResponseReturnValue:

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
        result = deps.user_service.search_by_name(
            name=search.name,
            limit=pagination.limit,
            offset=pagination.offset,
        )

    else:
        result = deps.user_service.get_all(
            limit=pagination.limit,
            offset=pagination.offset,
        )

    body, status = ResponseBuilder.build(
        result, include={"id", "firstname", "lastname"}
    )
    return jsonify(body), status


@api_users.get("/profile")
@api_login_required
def get_profile():

    result = deps.user_service.get_by_id(user_id=deps.required_user.id)

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_users.get("/<int:user_id>")
@api_login_required
def get_public_profile(user_id: int):

    result = deps.user_service.get_by_id(user_id=user_id)

    body, status = ResponseBuilder.build(
        result, include={"id", "firstname", "lastname"}
    )
    return jsonify(body), status


@api_users.patch("/profile")
@api_login_required
def update_profile() -> ResponseReturnValue:

    payload = request.get_json(silent=True) or {}

    result = deps.user_service.update_profile(
        user_id=deps.required_user.id,
        firstname=payload.get("firstname"),
        lastname=payload.get("lastname"),
        phone_number=payload.get("phone_number"),
    )

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_users.patch("/change-password")
@api_login_required
def change_password() -> ResponseReturnValue:

    payload = request.get_json(silent=True) or {}

    result = deps.user_service.change_password(
        user_id=deps.required_user.id,
        current_password=payload.get("current_password"),
        new_password=payload.get("new_password"),
        confirm_password=payload.get("confirm_password"),
    )

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_users.delete("/profile")
@api_login_required
def delete_profile() -> ResponseReturnValue:

    result = deps.user_service.delete(user_id=deps.required_user.id)

    if isinstance(result, FailureResult):
        body, status = ResponseBuilder.build(result)
        return jsonify(body), status

    session.clear()
    body, status = ResponseBuilder.build(ServiceResult.ok(None))
    return jsonify(body), status
