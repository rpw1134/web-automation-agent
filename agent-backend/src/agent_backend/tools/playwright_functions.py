from playwright.async_api import Browser, Locator, Page
from uuid import UUID
from typing import Tuple, Any
from ..types.tool import Tool, Parameters, ToolResponse
from ..utils.browser_functions import get_browser_context_by_id, create_browser_context, delete_browser_context_by_id, get_page_by_id, create_page, delete_page_by_page_id, create_new_locators_for_page, get_locator_by_id
from typing import Dict, List, Callable, Awaitable


async def go_to_url(context_id: UUID, url: str) -> ToolResponse:
    """Navigate to a page using the global browser instance.
    Args:
        context_id: The UUID of the browser context where the page will be created.
        url: The URL to navigate to.
    Returns:
        ToolResponse: A dict with success status and page_id or error message."""
    try:
        page_id, page = await create_page(context_id)
        await page.goto(url, timeout=30000)  # 30 second timeout
        return ToolResponse(success=True, content=f"Successfully navigated to '{url}'. Page ID: {str(page_id)}")
    except Exception as e:
        return ToolResponse(success=False, content=f"ERROR: Failed to navigate to '{url}': {str(e)}")

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
    

# async def click(context_id: UUID, page_id: UUID, selector: str) -> ToolResponse:
#     """Click an element on a page.
#     Args:
#         context_id: The UUID of the browser context containing the page.
#         page_id: The UUID of the page where the click will occur.
#         selector: The selector of the element to click.
#     Returns:
#         ToolResponse: A dict with success status and message.
#     """
#     try:
#         page: Page = await get_page_by_id(context_id, page_id)
#         await page.click(selector=selector, timeout=5000)
#         return ToolResponse(success=True, content=f"Successfully clicked element with selector '{selector}'.")
#     except TimeoutError:
#         return ToolResponse(success=False, content=f"ERROR: Request timed out or element with selector '{selector}' not found for clicking. This generally implies either the element is not loaded or there are multiple elements matching your selector. Adding a :visible to your selector may help.")
#     except Exception as e:
#         return ToolResponse(success=False, content=f"ERROR: Unexpected error clicking element with selector '{selector}': {str(e)}")

# click_tool = Tool(
#     type="function",
#     name="click",
#     description="Click an element on a page using a CSS selector",
#     parameters=Parameters(
#         type="object",
#         properties={
#             "page_id": {"type": "UUID", "description": "The UUID of the page where the click will occur."},
#             "selector": {"type": "string", "description": "The selector of the element to click."}
#         },
#         required=["page_id", "selector"]
#     ),
#     strict=True
# )

async def type_text(context_id: UUID, page_id: UUID, selector: str, text: str) -> ToolResponse:
    """Type text into an input field on a page.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page where the typing will occur.
        selector: The selector of the input field.
        text: The text to type into the input field.
    Returns:
        ToolResponse: A dict with success status and message.
    """
    try:
        page: Page = await get_page_by_id(context_id, page_id)
        await page.fill(selector=selector, value=text, timeout=5000)
        return ToolResponse(success=True, content=f"Successfully typed text '{text}' into element with selector '{selector}'.")
    except TimeoutError:
        return ToolResponse(success=False, content=f"ERROR: Request timed out or input field with selector '{selector}' not found for typing.")
    except Exception as e:
        return ToolResponse(success=False, content=f"ERROR: Unexpected error typing into element with selector '{selector}': {str(e)}")

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

async def extract_text(context_id: UUID, page_id: UUID, selector: str) -> ToolResponse:
    """Extract text content from an element on a page.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page where the extraction will occur.
        selector: The selector of the element to extract text from.
    Returns:
        ToolResponse: A dict with success status and extracted text or error message.
    """
    try:
        page: Page = await get_page_by_id(context_id, page_id)
        text_content = await page.text_content(selector=selector, timeout=5000)
        if text_content is None:
            return ToolResponse(success=False, content=f"ERROR: No text content found in element with selector '{selector}'.")
        return ToolResponse(success=True, content=text_content.strip())
    except TimeoutError:
        return ToolResponse(success=False, content=f"ERROR: Request timed out or element with selector '{selector}' not found for text extraction.")
    except Exception as e:
        return ToolResponse(success=False, content=f"ERROR: Unexpected error extracting text from element with selector '{selector}': {str(e)}")

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

async def wait_for_selector(context_id: UUID, page_id: UUID, selector: str, timeout: int = 5000) -> ToolResponse:
    """Wait for an element to appear on a page.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page to wait on.
        selector: The selector of the element to wait for.
        timeout: Maximum time to wait in milliseconds. Default is 5000ms.
    Returns:
        ToolResponse: A dict with success status and message.
    """
    try:
        page: Page = await get_page_by_id(context_id, page_id)
        await page.wait_for_selector(selector=selector, timeout=timeout)
        return ToolResponse(success=True, content=f"Element with selector '{selector}' is now present on the page.")
    except TimeoutError:
        return ToolResponse(success=False, content=f"ERROR: Request timed out or element with selector '{selector}' not found within {timeout}ms.")
    except Exception as e:
        return ToolResponse(success=False, content=f"ERROR: Unexpected error waiting for element with selector '{selector}': {str(e)}")

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

async def evaluate_script(context_id: UUID, page_id: UUID, script: str, arg: Any | None = None) -> ToolResponse:
    """Evaluate a JavaScript script on a page. Allows access to DOM and page context.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page where the script will be evaluated.
        script: The JavaScript code to evaluate.
    Returns:
        ToolResponse: A dict with success status and script result or error message.
    """
    try:
        page: Page = await get_page_by_id(context_id, page_id)
        result = await page.evaluate(expression=script, arg=arg)
        if result is None:
            return ToolResponse(success=True, content="Script evaluation completed with no return value.")
        return ToolResponse(success=True, content=str(result))
    except Exception as e:
        return ToolResponse(success=False, content=f"ERROR: Unexpected error evaluating script: {str(e)}")

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

async def scroll(context_id: UUID, page_id: UUID, x: int, y: int) -> ToolResponse:
    """Scroll to a specific position on a page.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page to scroll.
        x: The horizontal pixel value to scroll to.
        y: The vertical pixel value to scroll to.
    Returns:
        ToolResponse: A dict with success status and message.
    """
    try:
        page: Page = await get_page_by_id(context_id, page_id)
        await page.evaluate(f"window.scrollTo({x}, {y});")
        return ToolResponse(success=True, content=f"Successfully scrolled to position ({x}, {y}).")
    except Exception as e:
        return ToolResponse(success=False, content=f"ERROR: Unexpected error scrolling to position ({x}, {y}): {str(e)}")

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

async def set_viewport_size(context_id: UUID, page_id: UUID, width: int, height: int) -> ToolResponse:
    """Set the viewport size of a page.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page to set the viewport size.
        width: The desired viewport width in pixels.
        height: The desired viewport height in pixels.
    Returns:
        ToolResponse: A dict with success status and message.
    """
    try:
        page: Page = await get_page_by_id(context_id, page_id)
        await page.set_viewport_size({"width": width, "height": height})
        return ToolResponse(success=True, content=f"Successfully set viewport size to ({width}, {height}).")
    except Exception as e:
        return ToolResponse(success=False, content=f"ERROR: Unexpected error setting viewport size to ({width}, {height}): {str(e)}")

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

async def reload_page(context_id: UUID, page_id: UUID) -> ToolResponse:
    """Reload a page.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page to reload.
    Returns:
        ToolResponse: A dict with success status and message.
    """
    try:
        page: Page = await get_page_by_id(context_id, page_id)
        await page.reload()
        return ToolResponse(success=True, content="Successfully reloaded the page.")
    except Exception as e:
        return ToolResponse(success=False, content=f"ERROR: Unexpected error reloading page: {str(e)}")

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

async def screenshot_page(context_id: UUID, page_id: UUID, path: str) -> ToolResponse:
    """Take a screenshot of a page.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page to screenshot.
    Returns:
        ToolResponse: A dict with success status and message.
    """
    try:
        page: Page = await get_page_by_id(context_id, page_id)
        await page.screenshot(path=path)
        return ToolResponse(success=True, content=f"Successfully took screenshot and saved to '{path}'.")
    except Exception as e:
        return ToolResponse(success=False, content=f"ERROR: Unexpected error taking screenshot: {str(e)}")

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

async def get_open_pages(context_id: UUID) -> ToolResponse:
    """Retrieve all open pages in a given browser context."""
    try:
        browser_context = await get_browser_context_by_id(context_id)
        pages = browser_context.pages
        page_info = [f"Page {i}: {page.url}" for i, page in enumerate(pages)]
        return ToolResponse(success=True, content="\n".join(page_info) if page_info else "No open pages.")
    except Exception as e:
        return ToolResponse(success=False, content=f"ERROR: Failed to retrieve open pages: {str(e)}")

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

async def get_visible_elements_by(context_id: UUID, page_id: UUID, query: str, query_by: str) -> ToolResponse:
    """Get an element on a page by various query methods.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page to query.
        query: The query string to search for (e.g., CSS selector, label text, or text content).
        query_by: The method to use for querying. Must be one of: "css", "label", "text".
    Returns:
        ToolResponse: A dict with success status and message about element found or error.
    """
    # Validate query_by parameter
    valid_query_types = ["css", "label", "text"]
    if query_by not in valid_query_types:
        return ToolResponse(
            success=False,
            content=f"ERROR: Invalid query_by value '{query_by}'. Must be one of {valid_query_types}."
        )

    try:
        page: Page = await get_page_by_id(context_id, page_id)

        # Use appropriate locator method based on query_by
        if query_by == "css":
            locator = page.locator(query)
        elif query_by == "label":
            locator = page.get_by_label(query)
        else:
            locator = page.get_by_text(query)
        
        # Filter by visible elements
        visible_locators = [locator for locator in await locator.all() if await locator.is_visible()]

        # Check if element exists and is visible
        count = len(visible_locators)
        if count == 0:
            return ToolResponse(
                success=False,
                content=f"ERROR: No element found with {query_by}='{query}'."
            )
        
        # Create locators in BrowserManager
        new_ids = await create_new_locators_for_page(page_id, visible_locators)
        
        return ToolResponse(
            success=True,
            content=f"Found {count} element(s) with {query_by}='{query}'. Locator IDs: {new_ids}"
        )
    except TimeoutError:
        return ToolResponse(
            success=False,
            content=f"ERROR: Request timed out while searching for element with {query_by}='{query}'."
        )
    except Exception as e:
        return ToolResponse(
            success=False,
            content=f"ERROR: Unexpected error while searching for element with {query_by}='{query}': {str(e)}"
        )

get_visible_elements_by_tool = Tool(
    type="function",
    name="get_visible_elements_by",
    description="Get visible elements on a page using different query methods (CSS selector, label, or text)",
    parameters=Parameters(
        type="object",
        properties={
            "page_id": {"type": "UUID", "description": "The UUID of the page to query."},
            "query": {"type": "string", "description": "The query string to search for (e.g., CSS selector, label text, or text content)."},
            "query_by": {"type": "string", "description": "The method to use for querying. Must be one of: 'css', 'label', 'text'."}
        },
        required=["page_id", "query", "query_by"]
    ),
    strict=True
)

# NEED CONTEXT ID FOR GENERALIZED FUNCTION CALLING IN EXECUTOR
async def click_by_locator(context_id, page_id: UUID, locator_id: UUID) -> ToolResponse:
    """Click an element on a page using a stored locator ID.
    Args:
        page_id: The UUID of the page where the click will occur.
        locator_id: The UUID of the stored locator to click.
    Returns:
        ToolResponse: A dict with success status and message.
    """
    try:
        locator: Locator = get_locator_by_id(page_id, locator_id)
        await locator.click(timeout=5000)
        return ToolResponse(success=True, content=f"Successfully clicked element with locator ID '{locator_id}'.")
    except TimeoutError:
        return ToolResponse(success=False, content=f"ERROR: Request timed out or element with locator ID '{locator_id}' not found for clicking.")
    except Exception as e:
        return ToolResponse(success=False, content=f"ERROR: Unexpected error clicking element with locator ID '{locator_id}': {str(e)}")
    
    
click_by_locator_tool = Tool(
    type="function",
    name="click_by_locator",
    description="Click on an element by its locator id",
    parameters=Parameters(
        type="object",
        properties={
            "page_id": {"type": "UUID", "description": "The UUID of the page to query."},
            "locator_id": {"type": "UUID", "description": "The UUID of the stored locator to click."}
        },
        required=["page_id", "locator_id"]
    ),
    strict=True
)    

# NEED CONTEXT ID FOR GENERALIZED FUNCTION CALLING IN EXECUTOR
async def fill_field_by_locator(context_id, page_id: UUID, locator_id: UUID, text: str) -> ToolResponse:
    """Fill an input field on a page using a stored locator ID.
    Args:
        context_id: The UUID of the browser context containing the page.
        page_id: The UUID of the page where the filling will occur.
        locator_id: The UUID of the stored locator to fill.
        text: The text to fill into the input field.
    Returns:
        ToolResponse: A dict with success status and message.
    """
    try:
        locator: Locator = get_locator_by_id(page_id, locator_id)
        await locator.fill(value=text, timeout=5000)
        return ToolResponse(success=True, content=f"Successfully filled text '{text}' into element with locator ID '{locator_id}'.")
    except TimeoutError:
        return ToolResponse(success=False, content=f"ERROR: Request timed out or input field with locator ID '{locator_id}' not found for filling.")
    except Exception as e:
        return ToolResponse(success=False, content=f"ERROR: Unexpected error filling element with locator ID '{locator_id}': {str(e)}")

fill_field_by_locator_tool = Tool(
    type="function",
    name="fill_field_by_locator",
    description="Fill a field of an element by its locator id",
    parameters=Parameters(
        type="object",
        properties={
            "page_id": {"type": "UUID", "description": "The UUID of the page to query."},
            "locator_id": {"type": "UUID", "description": "The UUID of the stored locator to fill."}
        },
        required=["page_id", "locator_id"]
    ),
    strict=True
)    

playwright_function_names_to_functions: Dict[str, Callable[..., Awaitable[ToolResponse]]] = {
    "go_to_url": go_to_url,
    # "click": click,
    "type_text": type_text,
    "extract_text": extract_text,
    "wait_for_selector": wait_for_selector,
    "evaluate_script": evaluate_script,
    "scroll": scroll,
    "set_viewport_size": set_viewport_size,
    "reload_page": reload_page,
    "screenshot_page": screenshot_page,
    "get_open_pages": get_open_pages,
    "get_visible_elements_by": get_visible_elements_by,
    "click_by_locator": click_by_locator,
    "fill_field_by_locator": fill_field_by_locator
}
playwright_function_names_to_tools: Dict[str, Tool] = {
    "go_to_url": go_to_url_tool,
    # "click": click_tool,
    "type_text": type_text_tool,
    "extract_text": extract_text_tool,
    "wait_for_selector": wait_for_selector_tool,
    "evaluate_script": evaluate_script_tool,
    "scroll": scroll_tool,
    "set_viewport_size": set_viewport_size_tool,
    "reload_page": reload_page_tool,
    "screenshot_page": screenshot_page_tool,
    "get_open_pages": get_open_pages_tool,
    "get_visible_elements_by": get_visible_elements_by_tool,
    "click_by_locator": click_by_locator_tool,
    "fill_field_by_locator": fill_field_by_locator_tool
}

all_playwright_tools: List[Tool] = list(playwright_function_names_to_tools.values())
