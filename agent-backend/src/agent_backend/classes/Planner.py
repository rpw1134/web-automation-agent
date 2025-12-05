from openai import AsyncClient
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionMessage
from ..utils.prompts import REACT_PLANNING_SYSTEM_PROMPT
from ..tools.playwright_functions import playwright_function_names_to_tools
from typing import List, Union
from ..types.llm import PlanResponse, PlanResponseError, ParsedFunction
import json
from uuid import UUID

class Planner:
    def __init__(self, api_key: str):
        self.client = AsyncClient(api_key=api_key)
    
    async def react_loop(self, user_request: str):
        # Send a PLAN request to OpenAI
        # Take plan and function request, return plan to user and send function request to executor
        # Executor parses function request, interacts with browser, synthesizes raw results
        # Returns to planner who takes next steps
        # If at any point, planner sends 'done' or calls exceeds 15, break loop
        calls = 0
        context: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": REACT_PLANNING_SYSTEM_PROMPT},
            {"role" : "user" , "content": user_request}]
        # call loop
        while calls < 15:
            calls+=1
            
            # Check call number
            if calls == 15:
                return "Maximum Number of Calls Exceeded"
            
            # Get plan
            plan: str|None = (await self.client.chat.completions.create(
                model="gpt-4o",
                messages=context,
                max_tokens=1000,
                temperature=0.7
            )).choices[0].message.content
            plan_response = self._parse_plan(plan)
            
            # Check for decode error or invalid llm response
            if isinstance(plan_response, PlanResponseError):
                context.append({"role":"system", "content": f"Error parsing plan: {plan_response.error}. Please try again."})
                continue
            # Check if action is to finish the loop
            if plan_response.done:
                return plan_response
            
            # Append messages for context in future loops
            context.append({"role":"assistant", "content": "Thought: "+plan_response.plan})
            context.append({"role":"assistant", "content": f"Action{"s" if len(plan_response.function_calls)>1 else ""}: {json.dumps(plan_response.function_calls)}"})
            
    def _parse_plan(self, plan: str|None)->Union[PlanResponse, PlanResponseError]:
        # Parse the plan into plan, function calls, and 'done' status, or return error in parsing
        # TODO: Create function to properly parse actions. Actions should: parse the name of the method, use this to lookup tool definition, parse parameters according to tool definition types, populate a json object and send to executor. This should reduce num tokens produced and in turn possible mistakes. Example response: go_to_url(https://github.com) -> {"url": "https://github.com"}
        plan_dict: dict
        plan_error: PlanResponseError
        try:
            plan_dict = json.loads(str(plan))
            return PlanResponse(**plan_dict, done=True if plan_dict.get("plan", "").lower() == "done" else False)
        except json.JSONDecodeError:
            plan_error: PlanResponseError = PlanResponseError(error="Failed to parse plan JSON. Please carefully construct your plan and action.")
            return plan_error
    
    def _parse_functions(self, function_calls: list[str]):
        functions: List[ParsedFunction] = []
        for func_call in function_calls:
            func_name = func_call.split("(")[0]
            func_args = func_call[len(func_name)+1:-1].split(",")
            func_args_parsed = []
            tool_def = playwright_function_names_to_tools.get(func_name, None)
            if not tool_def:
                raise ValueError(f"Function {func_name} not found in tool definitions.")
            for i, property in enumerate(tool_def.parameters.properties.values()):
                match property.type:
                    case "string":
                        func_args_parsed[i] = str(func_args[i].strip())
                    case "int":
                        func_args_parsed[i] = int(func_args[i].strip())
                    case "boolean":
                        func_args_parsed[i] = bool(func_args[i].strip())
                    case "float":
                        func_args_parsed[i] = float(func_args[i].strip())
                    case "UUID":
                        func_args_parsed[i] = UUID(func_args[i].strip())
                    case _:
                        raise ValueError(f"Unsupported parameter type: {property.type}")
            functions.append(ParsedFunction(name=func_name, arguments=func_args_parsed))
        return functions