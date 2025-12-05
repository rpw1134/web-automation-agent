from openai import AsyncClient
from openai.types.chat import ChatCompletionMessageParam 
from ..utils.prompts import REACT_PLANNING_SYSTEM_PROMPT
from typing import List

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
        while calls < 15:
            plan = (await self.client.chat.completions.create(
                model="gpt-4o",
                messages=context,
                max_tokens=1000,
                temperature=0.7
            )).choices[0].message
            
            
    def _parse_plan(self, plan: str):
        # Parse the plan into plan, function calls, and 'done' status
        pass