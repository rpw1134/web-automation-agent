from ..main import browser_manager
from playwright.async_api import Page, BrowserContext
from uuid import UUID
from typing import Tuple

# Abstraction layer for browser manager. Provides easier to use functions for other modules.

async def get_browser_context_by_id(context_id: UUID) -> BrowserContext:
    """Retrieve a browser context by its ID."""
    return browser_manager.get_browser_context_by_id(context_id)

async def create_browser_context() -> Tuple[UUID, BrowserContext]:
    """Create a new browser context using the global browser instance."""
    return await browser_manager.create_browser_context()

async def delete_browser_context_by_id(context_id: UUID):
    """Delete a browser context by its ID."""
    await browser_manager.delete_browser_context_by_id(context_id)
    
async def get_page_by_id(context_id: UUID, page_id: UUID)->Page:
    """Retrieve a page by its ID within a specific browser context."""
    return browser_manager.get_page_by_id(context_id, page_id)

async def create_page(context_id: UUID) -> Tuple[UUID, Page]:
    """Create a new page within a specific browser context."""
    return await browser_manager.create_page(context_id)

async def delete_page_by_page_id(context_id: UUID, page_id: UUID):
    """Delete a page by its ID within a specific browser context."""
    await browser_manager.delete_page_by_page_id(context_id, page_id)
