"""
Shared instances for browser_manager, planner, and executor.
This module prevents circular imports by using lazy initialization.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Lazy initialization to avoid circular imports
_browser_manager = None
_planner = None
_executor = None


def get_browser_manager():
    """Get or create the browser manager instance."""
    global _browser_manager
    if _browser_manager is None:
        from .classes.BrowserManager import BrowserManager
        _browser_manager = BrowserManager()
    return _browser_manager


def get_planner():
    """Get or create the planner instance."""
    global _planner
    if _planner is None:
        from .classes.Planner import Planner
        _planner = Planner(api_key=os.getenv("OPENAI_API_KEY", ""))
    return _planner


def get_executor():
    """Get or create the executor instance."""
    global _executor
    if _executor is None:
        from .classes.Executor import Executor
        _executor = Executor(env_key=os.getenv("OPENAI_API_KEY", ""))
    return _executor


# Convenience exports
browser_manager = get_browser_manager()
planner = get_planner()
executor = get_executor()
