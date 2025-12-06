"""
Integration tests for browser automation using Playwright.

Run with: poetry run pytest tests/test_integration_playwright.py -v -s
"""

import pytest
import asyncio
import re
from pathlib import Path
from uuid import UUID

from agent_backend.instances import browser_manager
from agent_backend.utils.browser_functions import (
    create_browser_context,
    delete_browser_context_by_id,
    delete_page_by_page_id,
    get_page_by_id
)
from agent_backend.tools.playwright_functions import (
    go_to_url,
    type_text,
    extract_text,
    wait_for_selector,
    screenshot_page,
    scroll
)

# Mark all tests as integration tests
pytestmark = pytest.mark.integration

# Screenshots directory
SCREENSHOTS_DIR = Path(__file__).parent.parent / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)


def extract_page_id_from_response(response_content: str) -> UUID:
    """Extract page_id UUID from go_to_url response content."""
    match = re.search(r'Page ID: ([0-9a-f-]+)', response_content)
    if match:
        return UUID(match.group(1))
    raise ValueError(f"Could not extract page_id from: {response_content}")


class TestGitHubNavigation:
    """Integration tests for GitHub navigation."""

    @pytest.mark.asyncio
    async def test_browser_initialization(self):
        """Test that the browser manager initializes correctly."""
        await browser_manager.initialize()
        
        assert browser_manager.browser is not None
        print("✅ Browser initialized")
        
        await browser_manager.terminate()

    @pytest.mark.asyncio
    async def test_create_context_and_navigate(self):
        """Test creating a context and navigating to a page."""
        await browser_manager.initialize()

        try:
            # Create context
            context_id, _ = await create_browser_context()
            print(f"✅ Context created: {context_id}")

            # Navigate to GitHub
            response = await go_to_url(context_id, "https://github.com")
            assert response.success, f"Navigation failed: {response.content}"
            print(f"✅ {response.content}")

            # Verify we're on GitHub (need to get page to check URL)
            # Note: In real usage, you'd track page_id from response.content or use a different approach

            # Cleanup
            await delete_browser_context_by_id(context_id)
            print("✅ Cleanup complete")

        finally:
            await browser_manager.terminate()

    @pytest.mark.asyncio
    async def test_extract_text(self):
        """Test extracting text from a page."""
        await browser_manager.initialize()

        try:
            context_id, _ = await create_browser_context()

            response = await go_to_url(context_id, "https://github.com")
            assert response.success, f"Navigation failed: {response.content}"
            page_id = extract_page_id_from_response(response.content)

            # Extract heading text
            response = await wait_for_selector(context_id, page_id, "h1, h2", timeout=5000)
            assert response.success, f"Wait failed: {response.content}"

            response = await extract_text(context_id, page_id, "h1, h2")
            assert response.success, f"Extract failed: {response.content}"

            print(f"✅ Extracted text: '{response.content}'")
            assert len(response.content) > 0

            await delete_page_by_page_id(context_id, page_id)
            await delete_browser_context_by_id(context_id)

        finally:
            await browser_manager.terminate()

    @pytest.mark.asyncio
    async def test_scroll(self):
        """Test scrolling on a page."""
        await browser_manager.initialize()

        try:
            context_id, _ = await create_browser_context()

            response = await go_to_url(context_id, "https://github.com/explore")
            assert response.success, f"Navigation failed: {response.content}"
            page_id = extract_page_id_from_response(response.content)

            # Scroll down
            response = await scroll(context_id, page_id, 0, 500)
            assert response.success, f"Scroll failed: {response.content}"
            print(f"✅ {response.content}")

            await asyncio.sleep(1)

            # Screenshot after scroll
            screenshot_path = str(SCREENSHOTS_DIR / "03_scrolled.png")
            response = await screenshot_page(context_id, page_id, screenshot_path)
            assert response.success, f"Screenshot failed: {response.content}"
            print(f"✅ {response.content}")

            await delete_page_by_page_id(context_id, page_id)
            await delete_browser_context_by_id(context_id)

        finally:
            await browser_manager.terminate()
