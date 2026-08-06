# app/results/__init__.py

from typing import TypeVar, TypeAlias

from app.results.result_code import ResultCode
from app.results.result import BaseResult
from app.results.success_result import SuccessResult
from app.results.failure_result import FailureResult
from app.results.service_result import ServiceResult

T = TypeVar("T")

Result: TypeAlias = SuccessResult[T] | FailureResult
