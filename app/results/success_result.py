# app/results/success_result.py

from dataclasses import dataclass, field
from typing import Generic, TypeVar, Literal

from app.results import BaseResult

T = TypeVar("T")


@dataclass(slots=True)
class SuccessResult(BaseResult, Generic[T]):

    data: T
    success: Literal[True] = field(init=False, default=True)
