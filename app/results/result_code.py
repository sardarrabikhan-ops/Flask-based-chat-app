# app/results/result_code.py

from enum import Enum
from http import HTTPStatus


class ResultCode(Enum):

    OK = ("ok", HTTPStatus.OK)
    CREATED = ("created", HTTPStatus.CREATED)
    NO_CONTENT = ("no_content", HTTPStatus.NO_CONTENT)

    BAD_REQUEST = ("bad_request", HTTPStatus.BAD_REQUEST)
    UNAUTHORIZED = ("unauthorized", HTTPStatus.UNAUTHORIZED)
    FORBIDDEN = ("forbidden", HTTPStatus.FORBIDDEN)
    NOT_FOUND = ("not_found", HTTPStatus.NOT_FOUND)
    CONFLICT = ("conflict", HTTPStatus.CONFLICT)
    LOCKED = ("locked", HTTPStatus.LOCKED)
    INTERNAL_ERROR = (
        "internal_error",
        HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    def __init__(
        self,
        code: str,
        http_status: HTTPStatus,
    ) -> None:
        self._code = code
        self._http_status = http_status

    @property
    def code(self) -> str:
        return self._code

    @property
    def http_status(self) -> HTTPStatus:
        return self._http_status
