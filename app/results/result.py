# app/results/result.py

from dataclasses import dataclass
from abc import ABC

from app.results import ResultCode


@dataclass(slots=True)
class BaseResult(ABC):

    success: bool
    code: ResultCode
