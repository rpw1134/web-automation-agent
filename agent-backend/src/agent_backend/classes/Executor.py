from openai import AsyncClient
from typing import List, Tuple
from uuid import UUID
from ..types.llm import ParsedFunction
from ..types.tool import ToolResponse
from ..tools.playwright_functions import playwright_function_names_to_tools, playwright_function_names_to_functions
from collections.abc import Callable

class Executor:
    def __init__(self, env_key: str):
        self.client = AsyncClient(api_key=env_key)

    def _parse_functions(self, function_calls: list[str]) -> Tuple[List[ParsedFunction], List[Tuple[str, str]]]:
        """
        Parse raw function call strings into ParsedFunction objects.

        Example: "go_to_url(https://github.com)" -> ParsedFunction(function=go_to_url, arguments=["https://github.com"])

        Args:
            function_calls: List of function call strings in format "func_name(arg1, arg2, ...)"

        Returns:
            List of ParsedFunction objects with parsed function reference and arguments

        Raises:
            ValueError: If function not found in tool definitions or unsupported parameter type
        """
        functions: List[ParsedFunction] = []
        errors: List[Tuple[str, str]] = []

        for j, func_call in enumerate(function_calls):
            func_name = func_call.split("(")[0]
            try:
                # Split function name and arguments
                function: Callable | None = playwright_function_names_to_functions.get(func_name, None)
                if not function:
                    raise ValueError(f"Function {func_name} not found in function mappings.")
                func_args = func_call[len(func_name)+1:-1].split(",")
                func_arg_names = [func_arg.split("=", 1)[0].strip() for func_arg in func_args]
                func_arg_values = [func_arg.split("=", 1)[1].strip().strip("'\"") for func_arg in func_args]
                func_args_parsed = {}

                # Get tool definition to understand parameter types
                tool_def = playwright_function_names_to_tools.get(func_name, None)
                if not tool_def:
                    raise ValueError(f"Function {func_name} not found in tool definitions.")

                # Parse each argument according to its type from tool definition
                for i, property in enumerate(func_arg_names):
                    property = tool_def.parameters.properties.get(func_arg_names[i], None)
                    if not property:
                        raise ValueError(f"Parameter {func_arg_names[i]} not found in tool definition for function {func_name}.")
                    match property.get("type"):
                        case "string":
                            func_args_parsed[func_arg_names[i]] = str(func_arg_values[i])
                        case "integer":
                            func_args_parsed[func_arg_names[i]] = int(func_arg_values[i])
                        case "boolean":
                            func_args_parsed[func_arg_names[i]] = bool(func_arg_values[i])
                        case "float":
                            func_args_parsed[func_arg_names[i]] = float(func_arg_values[i])
                        case "UUID":
                            func_args_parsed[func_arg_names[i]] = UUID(func_arg_values[i])
                        case _:
                            raise ValueError(f"Unsupported parameter type: {property.get('type')}")
            # If there is an error in function argument parsing, log and skip remaining arguments
            except ValueError as ve:
                errors.append((func_name, str(ve)))
                j+=1
                while j<len(function_calls):
                    errors.append((func_name, "This call was skipped due to previous error."))
                    j+=1
                break
            if len(errors)>0:
                break
            functions.append(ParsedFunction(function=function, arguments=func_args_parsed))
        print(f"[Executor._parse_functions] Parsed functions: {functions}, Errors: {errors}")
        return functions, errors
    
    async def _execute_function(self, parsed_function: ParsedFunction, context_id: UUID)->ToolResponse:
        function = parsed_function.function
        try:
            res = await function(**parsed_function.arguments, context_id=context_id)
        except Exception as e:
            return ToolResponse(
                success=False,
                content=f"Error executing function {function.__name__}: {str(e)}"
            )
        return res
    
    async def execute_request(self, function_calls: List[str], context_id: UUID) -> List[ToolResponse]:
        """
        Execute a list of raw function call strings.

        Args:
            function_calls: List of function call strings in format "func_name(arg1, arg2, ...)"

        Returns:
            List of results from each function execution
        """
        results = []
        parsed_functions, errors = self._parse_functions(function_calls)

        for parsed_function in parsed_functions:
            result: ToolResponse = await self._execute_function(parsed_function, context_id=context_id)
            results.append(result)
            if not result.success:
                break  # Stop execution if any function fails
        for func_name, error_msg in errors:
            results.append(ToolResponse(
                success=False,
                content=f"Error executing {func_name}: {error_msg}"
            ))
        
        return results