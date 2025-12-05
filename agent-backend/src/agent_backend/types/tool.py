from dataclasses import dataclass
from typing import Any

@dataclass
class Parameters:
    type: str
    properties: dict[str, Any]
    required: list[str]
    additionalProperties: bool = False

@dataclass
class Tool:
    type: str
    name: str
    description: str
    parameters: Parameters
    strict: bool = True

@dataclass
class ToolResponse:
    success: bool
    content: str


