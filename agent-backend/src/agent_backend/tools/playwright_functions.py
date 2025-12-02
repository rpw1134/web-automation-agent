from ..main import browser_manager
from playwright.async_api import Browser

async def go_to_page(url: str):
    """Navigate to a page using the global browser instance."""
    browser: Browser = browser_manager.browser

