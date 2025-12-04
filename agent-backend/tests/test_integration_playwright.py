"""
Integration tests for browser automation using Playwright.

Run with: pytest tests/test_integration_playwright.py -v -s
"""

import sys
from pathlib import Path

# Add src to path so we can import agent_backend
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import asyncio
from uuid import UUID

from agent_backend.classes.BrowserManager import BrowserManager
from agent_backend.tools.playwright_functions import (
    go_to_url,
    click,
    type_text,
    extract_text,
    wait_for_selector,
    screenshot_page,
    scroll,
    reload_page,
    get_open_pages
)

# Mark all tests as integration tests
pytestmark = pytest.mark.integration

# Screenshots directory
SCREENSHOTS_DIR = Path(__file__).parent.parent / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)


class TestGitHubNavigation:
    """Integration tests for GitHub navigation."""

    @pytest.mark.asyncio
    async def test_browser_initialization(self):
        """Test that the browser manager initializes correctly."""
        from agent_backend.main import browser_manager
        
        await browser_manager.initialize()
        
        assert browser_manager.browser is not None
        print("✅ Browser initialized")
        
        await browser_manager.terminate()

    @pytest.mark.asyncio
    async def test_create_context_and_navigate(self):
        """Test creating a context and navigating to a page."""
        from agent_backend.main import browser_manager
        from agent_backend.utils.browser_functions import (
            create_browser_context,
            delete_browser_context_by_id,
            delete_page_by_page_id
        )
        
        # Initialize browser
        await browser_manager.initialize()
        
        try:
            # Create context
            context_id, context = await create_browser_context()
            print(f"✅ Context created: {context_id}")
            
            # Navigate to GitHub
            page_id, page = await go_to_url(context_id, "https://github.com")
            print(f"✅ Navigated to: {page.url}")
            
            assert "github.com" in page.url
            
            # Cleanup
            await delete_page_by_page_id(context_id, page_id)
            await delete_browser_context_by_id(context_id)
            print("✅ Cleanup complete")
            
        finally:
            await browser_manager.terminate()

    @pytest.mark.asyncio
    async def test_github_workflow(self):
        """
        Complete workflow test:
        1. Navigate to GitHub
        2. Click login button
        3. Fill username field
        4. Take screenshots
        """
        from agent_backend.main import browser_manager
        from agent_backend.utils.browser_functions import (
            create_browser_context,
            delete_browser_context_by_id,
            delete_page_by_page_id,
            get_page_by_id
        )
        
        await browser_manager.initialize()
        
        try:
            # Setup
            context_id, _ = await create_browser_context()
            
            # Step 1: Navigate to GitHub
            print("\n[1/5] Navigating to GitHub...")
            page_id, page = await go_to_url(context_id, "https://github.com")
            assert "github.com" in page.url
            print(f"✅ At: {page.url}")
            
            # Step 2: Screenshot homepage
            print("\n[2/5] Taking homepage screenshot...")
            screenshot_path = str(SCREENSHOTS_DIR / "01_homepage.png")
            await screenshot_page(context_id, page_id, screenshot_path)
            print(f"✅ Saved: {screenshot_path}")
            
            # Step 3: Click Sign In
            print("\n[3/5] Clicking Sign In...")
            await wait_for_selector(context_id, page_id, 'a[href="/login"]', timeout=10000)
            await click(context_id, page_id, 'a[href="/login"]')
            await asyncio.sleep(2)
            
            page = await get_page_by_id(context_id, page_id)
            assert "/login" in page.url
            print(f"✅ At login page: {page.url}")
            
            # Step 4: Fill username
            print("\n[4/5] Filling username...")
            await wait_for_selector(context_id, page_id, "#login_field", timeout=10000)
            await type_text(context_id, page_id, "#login_field", "test_user")
            print("✅ Username filled")
            
            # Step 5: Final screenshot
            print("\n[5/5] Taking final screenshot...")
            screenshot_path = str(SCREENSHOTS_DIR / "02_login_filled.png")
            await screenshot_page(context_id, page_id, screenshot_path)
            print(f"✅ Saved: {screenshot_path}")
            
            # Cleanup
            await delete_page_by_page_id(context_id, page_id)
            await delete_browser_context_by_id(context_id)
            
            print("\n🎉 Workflow complete!")
            
        finally:
            await browser_manager.terminate()

    @pytest.mark.asyncio
    async def test_extract_text(self):
        """Test extracting text from a page."""
        from agent_backend.main import browser_manager
        from agent_backend.utils.browser_functions import (
            create_browser_context,
            delete_browser_context_by_id,
            delete_page_by_page_id
        )
        
        await browser_manager.initialize()
        
        try:
            context_id, _ = await create_browser_context()
            page_id, _ = await go_to_url(context_id, "https://github.com")
            
            # Extract heading text
            await wait_for_selector(context_id, page_id, "h1, h2", timeout=5000)
            text = await extract_text(context_id, page_id, "h1, h2")
            
            print(f"✅ Extracted text: '{text}'")
            assert len(text) > 0
            
            await delete_page_by_page_id(context_id, page_id)
            await delete_browser_context_by_id(context_id)
            
        finally:
            await browser_manager.terminate()

    @pytest.mark.asyncio
    async def test_scroll(self):
        """Test scrolling on a page."""
        from agent_backend.main import browser_manager
        from agent_backend.utils.browser_functions import (
            create_browser_context,
            delete_browser_context_by_id,
            delete_page_by_page_id
        )
        
        await browser_manager.initialize()
        
        try:
            context_id, _ = await create_browser_context()
            page_id, _ = await go_to_url(context_id, "https://github.com/explore")
            
            # Scroll down
            result = await scroll(context_id, page_id, 0, 500)
            print(f"✅ {result}")
            
            await asyncio.sleep(1)
            
            # Screenshot after scroll
            screenshot_path = str(SCREENSHOTS_DIR / "03_scrolled.png")
            await screenshot_page(context_id, page_id, screenshot_path)
            print(f"✅ Saved: {screenshot_path}")
            
            await delete_page_by_page_id(context_id, page_id)
            await delete_browser_context_by_id(context_id)
            
        finally:
            await browser_manager.terminate()
