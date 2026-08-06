# app/results/failure_result.py

from dataclasses import dataclass, field
from typing import Literal

from app.results import BaseResult


@dataclass(slots=True)
class FailureResult(BaseResult):

    errors: dict[str, str]
    success: Literal[False] = field(init=False, default=False)
