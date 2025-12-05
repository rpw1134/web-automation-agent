from dataclasses import dataclass
from typing import Any, List, Awaitable
from collections.abc import Callable
from ..types.tool import ToolResponse

@dataclass
class ParsedFunction:
    function: Callable[..., Awaitable[ToolResponse]]
    arguments: List[Any]

@dataclass
class PlanResponse:
    observation: str
    plan: str
    function_calls: list[str]  # Raw function call strings, will be parsed by Executor
    done: bool

@dataclass
class PlanResponseError:
    error: str
    