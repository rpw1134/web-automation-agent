from fastapi import APIRouter
from ..schemas.request import UserRequest
from ..instances import planner
from ..utils.prompts import REACT_PLANNING_SYSTEM_PROMPT

router = APIRouter(prefix="/agent", tags=["agent"])

@router.get("/status")
async def get_agent_status():
    return {"status": "Agent is running"}

@router.get("/system-prompt")
async def get_system_prompt():
    print(REACT_PLANNING_SYSTEM_PROMPT)
    return {"prompt": REACT_PLANNING_SYSTEM_PROMPT}

@router.post("/task-completion")
async def post_new_task(request: UserRequest):
    await planner.react_loop(request.request)
    return {"status": "Task processing initiated"}