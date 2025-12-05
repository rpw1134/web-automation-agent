from openai import AsyncClient
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionMessage
from ..utils.prompts import REACT_PLANNING_SYSTEM_PROMPT
from typing import List, Union
from ..types.llm import PlanResponse, PlanResponseError
import json

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
            plan: str|None = (await self.client.chat.completions.create(
                model="gpt-4o",
                messages=context,
                max_tokens=1000,
                temperature=0.7
            )).choices[0].message.content
            plan_response = self._parse_plan(plan)
            # error in decoding/invalid return?
            if isinstance(plan_response, PlanResponseError):
                context.append({"role":"system", "content": f"Error parsing plan: {plan_response.error}. Please try again."})
                continue
            # done?
            if plan_response.done:
                return plan_response
            context.append({"role":"assistant", "content": plan_response.plan})
            
    def _parse_plan(self, plan: str|None)->Union[PlanResponse, PlanResponseError]:
        # Parse the plan into plan, function calls, and 'done' status, or return error in parsing
        plan_dict: dict
        plan_error: PlanResponseError
        try:
            plan_dict = json.loads(str(plan))
            return PlanResponse(**plan_dict, done=True if plan_dict.get("plan", "").lower() == "done" else False)
        except json.JSONDecodeError:
            plan_error: PlanResponseError = PlanResponseError(error="Failed to parse plan JSON. Please carefully construct your plan and action.")
            return plan_error