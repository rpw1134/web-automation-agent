from ..main import browser_manager
from playwright.async_api import Browser
from uuid import UUID
from playwright.async_api import BrowserContext, Page
from typing import Tuple, Any
from ..types.tool import Tool, Parameters
from ..utils.browser_functions import get_browser_context_by_id, create_browser_context, delete_browser_context_by_id, get_page_by_id, create_page, delete_page_by_page_id


async def go_to_url(context_id: UUID, url: str) -> Tuple[UUID, Page]:
    """Navigate to a page using the global browser instance.
    Args:
        context_id: The UUID of the browser context where the page will be created.
        url: The URL to navigate to.
    Returns:
        Tuple[UUID,Page]: A tuple containing the new page's UUID and the Page instance."""
    page_id, page = await create_page(context_id)
    await page.goto(url, timeout=30000)  # 30 second timeout
    return (page_id, page)

go_to_url_tool = Tool(
    type="function",
    name="go_to_url",
    description="Navigate to a URL",
    parameters = Parameters(
        type="object",
        properties={
            "url": {"type": "string", "description": "The URL to navigate to."}
        },
        required=["url"]
    ),
    strict=True
)
    

async def click(context_id: UUID, page_id: UUID, selector: str) -> str:
    """Click an element on a page.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page where the click will occur.
        selector: The selector of the element to click.
    Returns:
        str: A message indicating success or failure.
    """
    page: Page = await get_page_by_id(context_id, page_id)
    try:
        await page.click(selector=selector, timeout=5000)
    except TimeoutError:
        return f"Request timed out or element with selector '{selector}' not found for clicking."
    except Exception as e:
        return f"Unexpected error clicking element with selector '{selector}': {str(e)}"
    return f"Successfully licked element with selector '{selector}'."

click_tool = Tool(
    type="function",
    name="click",
    description="Click an element on a page using a CSS selector",
    parameters=Parameters(
        type="object",
        properties={
            "page_id": {"type": "UUID", "description": "The UUID of the page where the click will occur."},
            "selector": {"type": "string", "description": "The CSS selector of the element to click."}
        },
        required=["page_id", "selector"]
    ),
    strict=True
)

async def type_text(context_id: UUID, page_id: UUID, selector: str, text: str) -> str:
    """Type text into an input field on a page.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page where the typing will occur.
        selector: The selector of the input field.
        text: The text to type into the input field.
    Returns:
        str: A message indicating success or failure.
    """
    page: Page = await get_page_by_id(context_id, page_id)
    try:
        await page.fill(selector=selector, value=text, timeout=5000)
    except TimeoutError:
        return f"Request timed out or input field with selector '{selector}' not found for typing."
    except Exception as e:
        return f"Unexpected error typing into element with selector '{selector}': {str(e)}"
    return f"Successfully yped text '{text}' into element with selector '{selector}'."

type_text_tool = Tool(
    type="function",
    name="type_text",
    description="Type text into an input field on a page",
    parameters=Parameters(
        type="object",
        properties={
            "page_id": {"type": "UUID", "description": "The UUID of the page where the typing will occur."},
            "selector": {"type": "string", "description": "The CSS selector of the input field."},
            "text": {"type": "string", "description": "The text to type into the input field."}
        },
        required=["page_id", "selector", "text"]
    ),
    strict=True
)

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

extract_text_tool = Tool(
    type="function",
    name="extract_text",
    description="Extract text content from an element on a page",
    parameters=Parameters(
        type="object",
        properties={
            "page_id": {"type": "UUID", "description": "The UUID of the page where the extraction will occur."},
            "selector": {"type": "string", "description": "The CSS selector of the element to extract text from."}
        },
        required=["page_id", "selector"]
    ),
    strict=True
)

async def wait_for_selector(context_id: UUID, page_id: UUID, selector: str, timeout: int = 5000) -> str:
    """Wait for an element to appear on a page.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page to wait on.
        selector: The selector of the element to wait for.
        timeout: Maximum time to wait in milliseconds. Default is 5000ms.
    Returns:
        str: A message indicating success or timeout.
    """
    page: Page = await get_page_by_id(context_id, page_id)
    try:
        await page.wait_for_selector(selector=selector, timeout=timeout)
    except TimeoutError:
        return f"Request timed out or element with selector '{selector}' not found within {timeout}ms."
    except Exception as e:
        return f"Unexpected error waiting for element with selector '{selector}': {str(e)}"
    return f"Element with selector '{selector}' is now present on the page."

wait_for_selector_tool = Tool(
    type="function",
    name="wait_for_selector",
    description="Wait for an element to appear on a page",
    parameters=Parameters(
        type="object",
        properties={
            "page_id": {"type": "UUID", "description": "The UUID of the page to wait on."},
            "selector": {"type": "string", "description": "The CSS selector of the element to wait for."},
            "timeout": {"type": "integer", "description": "Maximum time to wait in milliseconds. Default is 5000ms."}
        },
        required=["page_id", "selector"]
    ),
    strict=True
)

async def evaluate_script(context_id: UUID, page_id: UUID, script: str, arg: Any | None = None):
    """Evaluate a JavaScript script on a page. Allows access to DOM and page context.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page where the script will be evaluated.
        script: The JavaScript code to evaluate.
    Returns:
        The result of the script evaluation or an error message.
    """
    page: Page = await get_page_by_id(context_id, page_id)
    try:
        result = await page.evaluate(expression=script, arg=arg)
        if not result:
            raise RuntimeError("Script evaluation returned no result.")
        return result
    except Exception as e:
        return f"Unexpected error evaluating script: {str(e)}"

evaluate_script_tool = Tool(
    type="function",
    name="evaluate_script",
    description="Evaluate a JavaScript script on a page with access to DOM and page context",
    parameters=Parameters(
        type="object",
        properties={
            "page_id": {"type": "UUID", "description": "The UUID of the page where the script will be evaluated."},
            "script": {"type": "string", "description": "The JavaScript code to evaluate."},
            "arg": {"description": "Optional argument to pass to the script."}
        },
        required=["page_id", "script"]
    ),
    strict=True
)

async def scroll(context_id: UUID, page_id: UUID, x: int, y: int) -> str:
    """Scroll to a specific position on a page.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page to scroll.
        x: The horizontal pixel value to scroll to.
        y: The vertical pixel value to scroll to.
    Returns:
        str: A message indicating success or failure.
    """
    page: Page = await get_page_by_id(context_id, page_id)
    try:
        await page.evaluate(f"window.scrollTo({x}, {y});")
    except Exception as e:
        return f"Unexpected error scrolling to position ({x}, {y}): {str(e)}"
    return f"Successfully scrolled to position ({x}, {y})."

scroll_tool = Tool(
    type="function",
    name="scroll",
    description="Scroll to a specific position on a page",
    parameters=Parameters(
        type="object",
        properties={
            "page_id": {"type": "UUID", "description": "The UUID of the page to scroll."},
            "x": {"type": "integer", "description": "The horizontal pixel value to scroll to."},
            "y": {"type": "integer", "description": "The vertical pixel value to scroll to."}
        },
        required=["page_id", "x", "y"]
    ),
    strict=True
)

async def set_viewport_size(context_id: UUID, page_id: UUID, width: int, height: int) -> str:
    """Set the viewport size of a page.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page to set the viewport size.
        width: The desired viewport width in pixels.
        height: The desired viewport height in pixels.
    Returns:
        str: A message indicating success or failure.
    """
    page: Page = await get_page_by_id(context_id, page_id)
    try:
        await page.set_viewport_size({"width": width, "height": height})
    except Exception as e:
        return f"Unexpected error setting viewport size to ({width}, {height}): {str(e)}"
    return f"Successfully set viewport size to ({width}, {height})."

set_viewport_size_tool = Tool(
    type="function",
    name="set_viewport_size",
    description="Set the viewport size of a page",
    parameters=Parameters(
        type="object",
        properties={
            "page_id": {"type": "UUID", "description": "The UUID of the page to set the viewport size."},
            "width": {"type": "integer", "description": "The desired viewport width in pixels."},
            "height": {"type": "integer", "description": "The desired viewport height in pixels."}
        },
        required=["page_id", "width", "height"]
    ),
    strict=True
)

async def reload_page(context_id: UUID, page_id: UUID) -> str:
    """Reload a page.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page to reload.
    Returns:
        str: A message indicating success or failure.
    """
    page: Page = await get_page_by_id(context_id, page_id)
    try:
        await page.reload()
    except Exception as e:
        return f"Unexpected error reloading page: {str(e)}"
    return "Successfully reloaded the page."

reload_page_tool = Tool(
    type="function",
    name="reload_page",
    description="Reload a page",
    parameters=Parameters(
        type="object",
        properties={
            "page_id": {"type": "UUID", "description": "The UUID of the page to reload."}
        },
        required=["page_id"]
    ),
    strict=True
)

async def screenshot_page(context_id: UUID, page_id: UUID, path: str) -> str:
    """Take a screenshot of a page.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page to screenshot.
    Returns:
        str: A message indicating success or failure.
    """
    page: Page = await get_page_by_id(context_id, page_id)
    try:
        await page.screenshot(path=path)
    except Exception as e:
        return f"Unexpected error taking screenshot: {str(e)}"
    return f"Successfully took screenshot and saved to '{path}'."

screenshot_page_tool = Tool(
    type="function",
    name="screenshot_page",
    description="Take a screenshot of a page and save it to a file",
    parameters=Parameters(
        type="object",
        properties={
            "page_id": {"type": "UUID", "description": "The UUID of the page to screenshot."},
            "path": {"type": "string", "description": "The file path where the screenshot will be saved."}
        },
        required=["page_id", "path"]
    ),
    strict=True
)

async def get_open_pages(context_id: UUID):
    """Retrieve all open pages in a given browser context."""
    browser_context = await get_browser_context_by_id(context_id)
    return browser_context.pages

get_open_pages_tool = Tool(
    type="function",
    name="get_open_pages",
    description="Retrieve all open pages in the current browser context",
    parameters=Parameters(
        type="object",
        properties={},
        required=[]
    ),
    strict=True
)

playwright_function_names_to_functions = {
    "go_to_url": go_to_url,
    "click": click,
    "type_text": type_text,
    "extract_text": extract_text,
    "wait_for_selector": wait_for_selector,
    "evaluate_script": evaluate_script,
    "scroll": scroll,
    "set_viewport_size": set_viewport_size,
    "reload_page": reload_page,
    "screenshot_page": screenshot_page,
    "get_open_pages": get_open_pages
}

playwright_function_names_to_tools = {
    "go_to_url": go_to_url_tool,
    "click": click_tool,
    "type_text": type_text_tool,
    "extract_text": extract_text_tool,
    "wait_for_selector": wait_for_selector_tool,
    "evaluate_script": evaluate_script_tool,
    "scroll": scroll_tool,
    "set_viewport_size": set_viewport_size_tool,
    "reload_page": reload_page_tool,
    "screenshot_page": screenshot_page_tool,
    "get_open_pages": get_open_pages_tool
}

all_playwright_tools = list(playwright_function_names_to_tools.values())
