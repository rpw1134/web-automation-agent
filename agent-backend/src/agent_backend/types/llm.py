from dataclasses import dataclass
from typing import Any, List

@dataclass
class PlanResponse:
    plan: str
    function_calls: list[str]
    done: bool

@dataclass
class PlanResponseError:
    error: str
    
@dataclass
class ParsedFunction:
    name: str
    arguments: List[Any]