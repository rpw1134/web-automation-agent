from dataclasses import dataclass
from typing import Any, Awaitable, Dict
from collections.abc import Callable
from ..types.tool import ToolResponse

@dataclass
class ParsedFunction:
    function: Callable[..., Awaitable[ToolResponse]]
    arguments: Dict[str, Any]

@dataclass
class PlanResponse:
    observation: str
    plan: str
    function_calls: list[str]  # Raw function call strings, will be parsed by Executor
    done: bool

@dataclass
class PlanResponseError:
    error: str
    