from openai import AsyncClient
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionMessage
from ..utils.prompts import REACT_PLANNING_SYSTEM_PROMPT
from typing import List, Union
from ..types.llm import PlanResponse, PlanResponseError
from ..types.tool import ToolResponse
import json
from dataclasses import asdict

# Import executor lazily to avoid circular import
def get_executor():
    from ..instances import executor
    return executor

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
            
            # Execute desired functions and get response
            execution_response: List[ToolResponse] = await get_executor().execute_request(plan_response.function_calls)
            
            # Add as context
            context.append({"role":"system", "content": f"Action Response: {json.dumps([asdict(response) for response in execution_response])}"})
            
            #TODO: Add observation logic, most likely with a seperate prompt
            
    def _parse_plan(self, plan_response: str|None)->Union[PlanResponse, PlanResponseError]:
        """
        Parse the plan response into plan text, raw function calls, and 'done' status.

        Function calls are left as raw strings to be parsed by the Executor.

        Args:
            plan_response: JSON string response from LLM

        Returns:
            PlanResponse with raw function call strings, or PlanResponseError if parsing fails
        """
        plan_dict: dict
        plan_error: PlanResponseError
        try:
            plan_dict = json.loads(str(plan_response))
            plan: str = plan_dict.get("plan", "")
            
            # Pass raw function call strings - Executor will parse them
            function_calls: list[str] = plan_dict.get("function_calls", [])
            return PlanResponse(
                plan=plan,
                function_calls=function_calls,
                done=True if plan_dict.get("plan", "").lower() == "done" else False
            )
        except json.JSONDecodeError:
            plan_error: PlanResponseError = PlanResponseError(
                error="Failed to parse plan JSON. Please carefully construct your plan and action."
            )
            return plan_error