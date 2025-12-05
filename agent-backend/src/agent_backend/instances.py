"""
Shared instances for browser_manager, planner, and executor.
This module creates singleton instances and wires up dependencies.
"""
import os
from dotenv import load_dotenv

from .classes.BrowserManager import BrowserManager
from .classes.Planner import Planner
from .classes.Executor import Executor
from .utils.browser_functions import init_browser_functions

load_dotenv()

# Create instances
browser_manager = BrowserManager()
executor = Executor(env_key=os.getenv("OPENAI_API_KEY", ""))
planner = Planner(api_key=os.getenv("OPENAI_API_KEY", ""), executor=executor)

# Wire up browser_functions module with the browser_manager
init_browser_functions(browser_manager)
