# app/routes/api/authentication_routes.py

from flask import Blueprint, request, jsonify, session
from flask.typing import ResponseReturnValue

from app.utils.decorators import api_login_required
from app.schemas import ResponseBuilder

from app.dependencies import Dependencies
from app.constants import SESSION_USER_ID

from app.results import SuccessResult, ServiceResult, ResultCode

deps = Dependencies()

api_auth = Blueprint("api_auth", __name__, url_prefix="/authentication")


@api_auth.post("/signin")
def signin() -> ResponseReturnValue:

    payload = request.get_json(silent=True) or {}

    result = deps.authentication_service.login(
        email=payload.get("email"), password=payload.get("password")
    )

    if isinstance(result, SuccessResult):
        session[SESSION_USER_ID] = result.data.id

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_auth.post("/signup")
def signup() -> ResponseReturnValue:

    payload = request.get_json(silent=True) or {}

    result = deps.authentication_service.register(
        firstname=payload.get("firstname"),
        lastname=payload.get("lastname"),
        email=payload.get("email"),
        phone_number=payload.get("phone_number"),
        password=payload.get("password"),
        confirm_password=payload.get("confirm_password"),
    )

    body, status = ResponseBuilder.build(result)
    return jsonify(body), status


@api_auth.post("/signout")
@api_login_required
def signout() -> ResponseReturnValue:
    session.clear()

    body, status = ResponseBuilder.build(ServiceResult.ok(None))
    return jsonify(body), status
