from playwright.async_api import Page, BrowserContext, Locator
from uuid import UUID
from typing import Tuple, TYPE_CHECKING, List
from asyncio import gather

if TYPE_CHECKING:
    from ..classes.BrowserManager import BrowserManager

# Module-level browser manager reference - set via init_browser_functions()
_browser_manager: "BrowserManager | None" = None


def init_browser_functions(browser_manager: "BrowserManager") -> None:
    """Initialize the browser functions module with a BrowserManager instance."""
    global _browser_manager
    _browser_manager = browser_manager


def _get_browser_manager() -> "BrowserManager":
    """Get the browser manager instance."""
    if _browser_manager is None:
        raise RuntimeError("Browser functions not initialized. Call init_browser_functions() first.")
    return _browser_manager


async def get_browser_context_by_id(context_id: UUID) -> BrowserContext:
    """Retrieve a browser context by its ID."""
    return _get_browser_manager().get_browser_context_by_id(context_id)

async def create_browser_context() -> Tuple[UUID, BrowserContext]:
    """Create a new browser context using the global browser instance."""
    return await _get_browser_manager().create_browser_context()

async def delete_browser_context_by_id(context_id: UUID):
    """Delete a browser context by its ID."""
    await _get_browser_manager().delete_browser_context_by_id(context_id)
    
async def get_page_by_id(context_id: UUID, page_id: UUID)->Page:
    """Retrieve a page by its ID within a specific browser context."""
    return _get_browser_manager().get_page_by_id(context_id, page_id)

async def create_page(context_id: UUID) -> Tuple[UUID, Page]:
    """Create a new page within a specific browser context."""
    print(f"[create_page] Calling browser_manager.create_page({context_id})...")
    result = await _get_browser_manager().create_page(context_id)
    print(f"[create_page] Page created successfully")
    return result

async def delete_page_by_page_id(context_id: UUID, page_id: UUID):
    """Delete a page by its ID within a specific browser context."""
    await _get_browser_manager().delete_page_by_page_id(context_id, page_id)
    
async def create_new_locators_for_page(page_id: UUID, locators: List[Locator]):
    """Create a new locators dictionary for a specific page."""
    browser_manager = _get_browser_manager()
    returned_ids = await gather(*(browser_manager.store_locator(page_id, locator) for locator in locators))
    print(returned_ids)
    return returned_ids

async def get_locator_by_id(page_id: UUID, locator_id: UUID) -> Locator:
    """Retrieve a locator by its ID within a specific page."""
    return await _get_browser_manager().get_locator_by_id(page_id, locator_id)