# app/error_handlers.py

from flask import Flask, render_template, request, jsonify
from flask.typing import ResponseReturnValue

from app.results import ServiceResult, ResultCode
from app.schemas import ResponseBuilder

import logging

logger = logging.getLogger(__name__)


def _is_api_request() -> bool:

    return request.path.startswith("/api/")


def register_error_handlers(app: Flask) -> None:

    @app.errorhandler(404)
    def handle_not_found(_error) -> ResponseReturnValue:

        if _is_api_request():
            body, status = ResponseBuilder.build(
                ServiceResult.fail(
                    {"general": "The requested endpoint was not found."},
                    code=ResultCode.NOT_FOUND,
                )
            )

            return jsonify(body), status

        return render_template("404.html"), ResultCode.NOT_FOUND.http_status

    @app.errorhandler(405)
    def handle_method_not_allowed(_error) -> ResponseReturnValue:

        if _is_api_request():
            body, status = ResponseBuilder.build(
                ServiceResult.fail(
                    {"general": "The requested HTTP method is not allowed."},
                    code=ResultCode.METHOD_NOT_ALLOWED,
                )
            )

            return jsonify(body), status

        return render_template("405.html"), ResultCode.METHOD_NOT_ALLOWED.http_status

    @app.errorhandler(Exception)
    def handle_unexpected(_error) -> ResponseReturnValue:

        logger.exception("Unhandled exception.")

        if _is_api_request():
            body, status = ResponseBuilder.build(
                ServiceResult.fail(
                    {
                        "general": "An unexpected error occurred. Please try again later."
                    },
                    code=ResultCode.INTERNAL_SERVER_ERROR,
                )
            )

            return jsonify(body), status

        return render_template("500.html"), ResultCode.INTERNAL_SERVER_ERROR.http_status
