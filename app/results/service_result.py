# app/results/service_result.py

from typing import TypeVar

from app.results import ResultCode, SuccessResult, FailureResult

T = TypeVar("T")


class ServiceResult:

    @staticmethod
    def ok(data: T, code: ResultCode = ResultCode.OK) -> SuccessResult[T]:
        return SuccessResult(code=code, data=data)

    @staticmethod
    def fail(
        errors: dict[str, str],
        code: ResultCode = ResultCode.BAD_REQUEST,
    ) -> FailureResult:
        return FailureResult(code=code, errors=errors)
