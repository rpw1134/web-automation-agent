"""Utility functions for parsing LLM responses."""

from typing import Union
from ..types.llm import PlanResponse, PlanResponseError


def parse_delimited_response(response: str | None) -> Union[PlanResponse, PlanResponseError]:
    """
    Parse a delimiter-based LLM response into a PlanResponse object.

    Expected format:
    #/OBSERVATION/#
    <observation text>

    #/PLAN/#
    <plan text>

    #/FUNCTION_CALLS/#
    function1(arg1=val1,arg2=val2)
    function2(arg1=val1)
    function3(arg1=val1)

    #/DONE/#
    false

    Args:
        response: The raw response string from the LLM

    Returns:
        PlanResponse object with parsed fields, or PlanResponseError if parsing fails
    """
    if response is None:
        return PlanResponseError(error="Response is None")

    try:
        # Define the delimiters
        obs_delimiter = "#/OBSERVATION/#"
        plan_delimiter = "#/PLAN/#"
        func_delimiter = "#/FUNCTION_CALLS/#"
        done_delimiter = "#/DONE/#"

        # Initialize values
        observation = ""
        plan = ""
        function_calls = []
        done = False

        # Find delimiter positions
        obs_pos = response.find(obs_delimiter)
        plan_pos = response.find(plan_delimiter)
        func_pos = response.find(func_delimiter)
        done_pos = response.find(done_delimiter)

        # Extract observation
        if obs_pos != -1 and plan_pos != -1:
            observation = response[obs_pos + len(obs_delimiter):plan_pos].strip()
        elif obs_pos != -1:
            # If there's no plan delimiter, extract until the next delimiter
            next_delim = min([p for p in [plan_pos, func_pos, done_pos] if p > obs_pos], default=len(response))
            observation = response[obs_pos + len(obs_delimiter):next_delim].strip()

        # Extract plan
        if plan_pos != -1 and func_pos != -1:
            plan = response[plan_pos + len(plan_delimiter):func_pos].strip()
        elif plan_pos != -1:
            # If there's no function delimiter, extract until the next delimiter
            next_delim = min([p for p in [func_pos, done_pos] if p > plan_pos], default=len(response))
            plan = response[plan_pos + len(plan_delimiter):next_delim].strip()

        # Extract function calls
        if func_pos != -1 and done_pos != -1:
            func_text = response[func_pos + len(func_delimiter):done_pos].strip()
            # Split by newlines and filter out empty lines
            function_calls = [line.strip() for line in func_text.split('\n') if line.strip()]
        elif func_pos != -1:
            func_text = response[func_pos + len(func_delimiter):].strip()
            function_calls = [line.strip() for line in func_text.split('\n') if line.strip()]

        # Extract done status
        if done_pos != -1:
            done_text = response[done_pos + len(done_delimiter):].strip().lower()
            # Check if the text contains 'true' (case insensitive)
            done = 'true' in done_text

        return PlanResponse(
            observation=observation,
            plan=plan,
            function_calls=function_calls,
            done=done
        )

    except Exception as e:
        return PlanResponseError(
            error=f"Failed to parse delimited response: {str(e)}"
        )
