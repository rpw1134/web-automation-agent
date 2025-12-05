from openai import AsyncClient
from typing import List
from uuid import UUID
from ..types.llm import ParsedFunction
from ..tools.playwright_functions import playwright_function_names_to_tools

class Executor:
    def __init__(self, env_key: str):
        self.client = AsyncClient(api_key=env_key)

    def parse_functions(self, function_calls: list[str]) -> List[ParsedFunction]:
        """
        Parse raw function call strings into ParsedFunction objects.

        Example: "go_to_url(https://github.com)" -> ParsedFunction(name="go_to_url", arguments=["https://github.com"])

        Args:
            function_calls: List of function call strings in format "func_name(arg1, arg2, ...)"

        Returns:
            List of ParsedFunction objects with parsed names and arguments

        Raises:
            ValueError: If function not found in tool definitions or unsupported parameter type
        """
        functions: List[ParsedFunction] = []

        for func_call in function_calls:
            # Split function name and arguments
            func_name = func_call.split("(")[0]
            func_args = func_call[len(func_name)+1:-1].split(",")
            func_args_parsed = []

            # Get tool definition to understand parameter types
            tool_def = playwright_function_names_to_tools.get(func_name, None)
            if not tool_def:
                raise ValueError(f"Function {func_name} not found in tool definitions.")

            # Parse each argument according to its type from tool definition
            for i, property in enumerate(tool_def.parameters.properties.values()):
                match property.get("type"):
                    case "string":
                        func_args_parsed.append(str(func_args[i].strip()))
                    case "integer":
                        func_args_parsed.append(int(func_args[i].strip()))
                    case "boolean":
                        func_args_parsed.append(bool(func_args[i].strip()))
                    case "float":
                        func_args_parsed.append(float(func_args[i].strip()))
                    case "UUID":
                        func_args_parsed.append(UUID(func_args[i].strip()))
                    case _:
                        raise ValueError(f"Unsupported parameter type: {property.get('type')}")

            functions.append(ParsedFunction(name=func_name, arguments=func_args_parsed))

        return functions