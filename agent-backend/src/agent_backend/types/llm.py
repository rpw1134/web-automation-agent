from dataclasses import dataclass

@dataclass
class PlanResponse:
    plan: str
    function_calls: list[str]
    done: bool

@dataclass
class PlanResponseError:
    error: str