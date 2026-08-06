# app/utils/decorators.py

from functools import wraps
from typing import Callable, ParamSpec

from flask import redirect, url_for, jsonify, g
from flask.typing import ResponseReturnValue

from app.results import ServiceResult, ResultCode
from app.schemas import ResponseBuilder

P = ParamSpec("P")


def login_required(
    view: Callable[P, ResponseReturnValue],
) -> Callable[P, ResponseReturnValue]:

    @wraps(view)
    def wrapper(
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ResponseReturnValue:

        if g.user is None:
            return redirect(url_for("web.web_auth.signin"))

        return view(*args, **kwargs)

    return wrapper


def api_login_required(
    view: Callable[P, ResponseReturnValue],
) -> Callable[P, ResponseReturnValue]:

    @wraps(view)
    def wrapper(
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> ResponseReturnValue:

        if g.user is None:
            body, status = ResponseBuilder.build(
                ServiceResult.fail(
                    {"authentication": "Authentication required."},
                    code=ResultCode.UNAUTHORIZED,
                )
            )
            return jsonify(body), status

        return view(*args, **kwargs)

    return wrapper
