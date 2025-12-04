from ..main import browser_manager
from playwright.async_api import Browser
from uuid import UUID
from playwright.async_api import BrowserContext

async def get_browser_context_by_id(context_id: UUID) -> BrowserContext:
    """Retrieve a browser context by its ID."""
    return browser_manager.get_browser_context_by_id(context_id)

async def go_to_url(context_id: UUID, url: str):
    """Navigate to a page using the global browser instance."""
    #TODO: store page metadata if needed
    browser_context = await get_browser_context_by_id(context_id)
    page = await browser_context.new_page()
    await page.goto(url)
    return page

async def get_open_pages(context_id: UUID):
    """Retrieve all open pages in a given browser context."""
    browser_context = await get_browser_context_by_id(context_id)
    return browser_context.pages


