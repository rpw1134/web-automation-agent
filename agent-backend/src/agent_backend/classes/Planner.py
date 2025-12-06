from openai import AsyncClient
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionMessage
from ..utils.prompts import REACT_PLANNING_SYSTEM_PROMPT
from ..utils.llm_utils import parse_delimited_response
from typing import List, Union, TYPE_CHECKING
from ..types.llm import PlanResponse, PlanResponseError
from ..types.tool import ToolResponse
import json
from dataclasses import asdict

if TYPE_CHECKING:
    from .Executor import Executor
    from .BrowserManager import BrowserManager

class Planner:
    def __init__(self, api_key: str, executor: "Executor | None" = None, browser_manager: "BrowserManager | None" = None):
        self.client = AsyncClient(api_key=api_key)
        self._executor: "Executor | None" = executor
        self._browser_manager: "BrowserManager | None" = browser_manager
    
    def set_executor(self, executor: "Executor") -> None:
        """Set the executor instance (for dependency injection after construction)."""
        self._executor = executor
        
    def set_browser_manager(self, browser_manager: "BrowserManager") -> None:
        """Set the browser manager instance (for dependency injection after construction)."""
        self._browser_manager = browser_manager
    
    @property
    def executor(self) -> "Executor":
        """Get the executor instance."""
        if self._executor is None:
            raise RuntimeError("Executor not set. Call set_executor() first.")
        return self._executor
    
    @property
    def browser_manager(self) -> "BrowserManager":
        """Get the browser manager instance."""
        if self._browser_manager is None:
            raise RuntimeError("BrowserManager not set. Call set_browser_manager() first.")
        return self._browser_manager
    
    async def react_loop(self, user_request: str):
        # Send a PLAN request to OpenAI
        # Take plan and function request, return plan to user and send function request to executor
        # Executor parses function request, interacts with browser, synthesizes raw results
        # Returns to planner who takes next steps
        # If at any point, planner sends 'done' or calls exceeds 15, break loop
        
        # Create new context for this user request
        browser_context_id, _ = await self.browser_manager.create_browser_context()
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
            
            # Get observation, plan, and proposed action(s)
            plan: str|None = (await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[*context, {"role": "assistant", "content": "I must remember to respond using the delimiter-based format with proper sections."}],
                max_tokens=1000,
                temperature=0.7
            )).choices[0].message.content
            print(f"[Planner.react_loop] Raw Plan: {plan}")
            plan_response = self._parse_plan(plan)
            print(f"[Planner.react_loop] Plan Response: {plan_response}")
            
            # Check for decode error or invalid llm response
            if isinstance(plan_response, PlanResponseError):
                context.append({"role":"system", "content": f"Error parsing plan: {plan_response.error}. Please try again."})
                continue
            # Check if action is to finish the loop
            if plan_response.done:
                return plan_response
            
            # Append messages for context in future loops
            context.append({"role":"assistant", "content": f"Observation: {plan_response.observation}"})
            print(f"[Planner.react_loop] Observation: {plan_response.observation}")
            context.append({"role":"assistant", "content": "Thought: "+plan_response.plan})
            print(f"[Planner.react_loop] Thought: {plan_response.plan}")
            context.append({"role":"assistant", "content": f"Action{"s" if len(plan_response.function_calls)>1 else ""}: {json.dumps(plan_response.function_calls)}"})
            print(f"[Planner.react_loop] Action(s): {json.dumps(plan_response.function_calls)}")

            # Execute desired functions and get response
            execution_response: List[ToolResponse] = await self.executor.execute_request(plan_response.function_calls, context_id=browser_context_id)
            print(f"[Planner.react_loop] Execution Response: {json.dumps([asdict(response) for response in execution_response])}")
            
            # Add as context
            context.append({"role":"system", "content": f"Action Response: {json.dumps([asdict(response) for response in execution_response])}"})
        self.browser_manager.get_browser_context_by_id(browser_context_id)
            
            
    def _parse_plan(self, plan_response: str|None)->Union[PlanResponse, PlanResponseError]:
        """
        Parse the plan response into plan text, raw function calls, and 'done' status.

        Function calls are left as raw strings to be parsed by the Executor.

        Args:
            plan_response: Delimiter-based string response from LLM

        Returns:
            PlanResponse with raw function call strings, or PlanResponseError if parsing fails
        """
        return parse_delimited_response(plan_response)