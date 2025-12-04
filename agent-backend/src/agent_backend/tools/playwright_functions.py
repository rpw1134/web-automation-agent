from ..main import browser_manager
from playwright.async_api import Browser
from uuid import UUID
from playwright.async_api import BrowserContext, Page
from typing import Tuple
from ..utils.browser_functions import get_browser_context_by_id, create_browser_context, delete_browser_context_by_id, get_page_by_id, create_page, delete_page_by_page_id


async def go_to_url(context_id: UUID, url: str) -> Tuple[UUID, Page]:
    """Navigate to a page using the global browser instance.
    Args:
        context_id: The UUID of the browser context where the page will be created.
        url: The URL to navigate to.
    Returns:
        Tuple[UUID,Page]: A tuple containing the new page's UUID and the Page instance."""
    page_id, page = await create_page(context_id)
    await page.goto(url)
    return (page_id, page)

async def click(context_id: UUID, page_id: UUID, selector: str) -> str:
    """Click an element on a page.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page where the click will occur.
        selector: The selector of the element to click.
    """
    page: Page = await get_page_by_id(context_id, page_id)
    try:
        await page.click(selector=selector, timeout=5000)
    except TimeoutError:
        return f"Request timed out or element with selector '{selector}' not found for clicking."
    except Exception as e:
        return f"Unexpected error clicking element with selector '{selector}': {str(e)}"
    return f"Successfully licked element with selector '{selector}'."

async def type_text(context_id: UUID, page_id: UUID, selector: str, text: str) -> str:
    """Type text into an input field on a page.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page where the typing will occur.
        selector: The selector of the input field.
        text: The text to type into the input field.
    """
    page: Page = await get_page_by_id(context_id, page_id)
    try:
        await page.fill(selector=selector, value=text, timeout=5000)
    except TimeoutError:
        return f"Request timed out or input field with selector '{selector}' not found for typing."
    except Exception as e:
        return f"Unexpected error typing into element with selector '{selector}': {str(e)}"
    return f"Successfully yped text '{text}' into element with selector '{selector}'."

async def extract_text(context_id: UUID, page_id: UUID, selector: str) -> str:
    """Extract text content from an element on a page.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page where the extraction will occur.
        selector: The selector of the element to extract text from.
    Returns:
        str: The extracted text content or an error message.
    """
    page: Page = await get_page_by_id(context_id, page_id)
    try:
        text_content = await page.text_content(selector=selector, timeout=5000)
        if text_content is None:
            return f"No text content found in element with selector '{selector}'."
        return text_content.strip()
    except TimeoutError:
        return f"Request timed out or element with selector '{selector}' not found for text extraction."
    except Exception as e:
        return f"Unexpected error extracting text from element with selector '{selector}': {str(e)}"

async def get_open_pages(context_id: UUID):
    """Retrieve all open pages in a given browser context."""
    browser_context = await get_browser_context_by_id(context_id)
    return browser_context.pages


