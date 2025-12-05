from dataclasses import dataclass
from typing import Any, List

@dataclass
class ParsedFunction:
    name: str
    arguments: List[Any]

@dataclass
class PlanResponse:
    plan: str
    function_calls: list[str]  # Raw function call strings, will be parsed by Executor
    done: bool

@dataclass
class PlanResponseError:
    error: str
    