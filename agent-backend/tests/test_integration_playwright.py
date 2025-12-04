"""
INTEGRATION TEST FILE - REAL BROWSER AUTOMATION

This file contains integration tests that use REAL Playwright browsers
through YOUR custom wrapper functions (not mocking).

These tests actually:
- Use the BrowserManager singleton
- Create real browser contexts and pages
- Call YOUR functions from browser_functions and playwright_functions
- Navigate to real websites
- Click real buttons
- Fill real forms
- Take real screenshots

Unlike unit tests (which use mocks and run in milliseconds), these tests:
- Are SLOWER (take seconds to complete)
- Require Playwright browsers to be installed
- Actually interact with real web pages
- Test your full automation stack end-to-end

Run these separately from unit tests using:
    pytest tests/test_integration_playwright.py -v -s

Skip these during normal testing:
    pytest -m "not integration"
"""

import pytest
from pathlib import Path
from uuid import UUID

# Import YOUR functions (not Playwright directly!)
from agent_backend.utils.browser_functions import (
    create_browser_context,
    delete_browser_context_by_id,
    create_page,
    delete_page_by_page_id,
    get_page_by_id
)

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

from agent_backend.main import browser_manager


# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
async def initialize_browser():
    """
    Module-scoped fixture that initializes the BrowserManager.

    This ensures the browser_manager singleton is initialized once
    for all tests in this file.
    """
    # Always initialize the browser manager for tests
    print("\n🔧 Initializing BrowserManager...")
    await browser_manager.initialize()
    print("✅ BrowserManager initialized")

    yield browser_manager

    # Cleanup: Terminate browser after all tests
    print("\n🔧 Terminating BrowserManager...")
    await browser_manager.terminate()
    print("✅ BrowserManager terminated")


@pytest.fixture
async def test_context(initialize_browser):
    """
    Function-scoped fixture that creates a browser context for each test.

    Uses YOUR create_browser_context function!

    Returns:
        UUID: The context ID for use in the test.
    """
    # Create context using YOUR function
    context_id, context = await create_browser_context()
    print(f"\n📂 Created browser context: {context_id}")

    yield context_id

    # Cleanup: Delete context after test
    await delete_browser_context_by_id(context_id)
    print(f"🗑️  Deleted browser context: {context_id}")


@pytest.fixture(scope="session")
def screenshots_dir():
    """
    Session-scoped fixture that ensures the screenshots directory exists.

    Returns:
        Path: Path object pointing to the screenshots directory.
    """
    project_root = Path(__file__).parent.parent
    screenshots_path = project_root / "screenshots"
    screenshots_path.mkdir(exist_ok=True)
    return screenshots_path


class TestGitHubNavigationWithCustomFunctions:
    """
    Integration tests for GitHub navigation using YOUR custom functions.

    This tests the complete stack:
    - BrowserManager
    - browser_functions utilities
    - playwright_functions automation tools
    """

    @pytest.mark.asyncio
    async def test_browser_initialization(self, initialize_browser):
        """
        Simple test to verify the browser manager is initialized correctly.

        This test should run first to ensure fixtures are working.
        """
        print("\n🧪 Testing browser initialization...")
        assert initialize_browser is not None
        assert initialize_browser.browser is not None
        print("✅ Browser is initialized and accessible")

    @pytest.mark.asyncio
    async def test_context_creation(self, test_context: UUID):
        """
        Test that we can create a browser context.

        This verifies the test_context fixture works.
        """
        print("\n🧪 Testing context creation...")
        assert test_context is not None
        print(f"✅ Context created with ID: {test_context}")

    @pytest.mark.asyncio
    async def test_github_complete_workflow(self, test_context: UUID, screenshots_dir: Path):
        """
        Complete workflow test using YOUR functions:
        1. Navigate to GitHub
        2. Click login button
        3. Fill username field
        4. Take screenshot

        This tests YOUR entire automation stack end-to-end!

        Args:
            test_context: Browser context ID (from fixture).
            screenshots_dir: Path to screenshots directory (from fixture).
        """
        print("\n" + "="*70)
        print("🚀 STARTING GITHUB AUTOMATION WORKFLOW (Using Custom Functions)")
        print("="*70)

        context_id = test_context

        # Action 1: Navigate to GitHub using YOUR go_to_url function
        print("\n[1/6] 🌐 Navigating to github.com using go_to_url()...")
        page_id, page = await go_to_url(context_id, "https://github.com")
        print(f"      ✅ Page created with ID: {page_id}")
        print(f"      ✅ Navigated to: {page.url}")

        # Verify we're on GitHub
        assert "github.com" in page.url.lower()

        # Take screenshot of homepage using YOUR screenshot_page function
        print("\n[2/6] 📸 Taking homepage screenshot using screenshot_page()...")
        homepage_screenshot = str(screenshots_dir / "integration_01_homepage.png")
        result = await screenshot_page(context_id, page_id, homepage_screenshot)
        print(f"      {result}")

        # Action 2: Click "Sign in" button using YOUR click function
        print("\n[3/6] 🖱️  Clicking 'Sign in' button using click()...")
        sign_in_selector = 'a[href="/login"]'

        # Wait for the button using YOUR wait_for_selector function
        wait_result = await wait_for_selector(context_id, page_id, sign_in_selector, timeout=10000)
        print(f"      {wait_result}")

        # Click using YOUR click function
        click_result = await click(context_id, page_id, sign_in_selector)
        print(f"      {click_result}")

        # Wait for navigation to login page
        import asyncio
        await asyncio.sleep(2)  # Give page time to load

        # Verify we're on login page
        page = await get_page_by_id(context_id, page_id)
        assert "/login" in page.url
        print(f"      ✅ Navigated to login page: {page.url}")

        # Take screenshot of login page using YOUR function
        print("\n[4/6] 📸 Taking login page screenshot using screenshot_page()...")
        login_screenshot = str(screenshots_dir / "integration_02_login_page.png")
        result = await screenshot_page(context_id, page_id, login_screenshot)
        print(f"      {result}")

        # Action 3: Fill username field using YOUR type_text function
        print("\n[5/6] ✍️  Filling username field using type_text()...")
        username_selector = "#login_field"
        test_username = "web_automation_agent_test"

        # Wait for username field
        wait_result = await wait_for_selector(context_id, page_id, username_selector, timeout=10000)
        print(f"      {wait_result}")

        # Type username using YOUR function
        type_result = await type_text(context_id, page_id, username_selector, test_username)
        print(f"      {type_result}")

        # Action 4: Take final screenshot using YOUR function
        print("\n[6/6] 📸 Taking final screenshot using screenshot_page()...")
        final_screenshot = str(screenshots_dir / "integration_03_username_filled.png")
        result = await screenshot_page(context_id, page_id, final_screenshot)
        print(f"      {result}")

        # Verify the screenshot exists
        assert Path(final_screenshot).exists()
        assert Path(final_screenshot).stat().st_size > 0

        print("\n" + "="*70)
        print("🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📁 Screenshots saved in: {screenshots_dir}")
        print(f"   ✅ integration_01_homepage.png")
        print(f"   ✅ integration_02_login_page.png")
        print(f"   ✅ integration_03_username_filled.png")

        # Cleanup: Delete the page
        await delete_page_by_page_id(context_id, page_id)
        print(f"\n🗑️  Deleted page: {page_id}")

    @pytest.mark.asyncio
    async def test_extract_text_from_github(self, test_context: UUID):
        """
        Test extracting text from GitHub page using YOUR extract_text function.

        Demonstrates:
        - Navigation using go_to_url
        - Text extraction using extract_text
        - Multiple pages in same context
        """
        print("\n📝 Testing text extraction from GitHub...")
        context_id = test_context

        # Navigate to GitHub
        page_id, page = await go_to_url(context_id, "https://github.com")
        print(f"✅ Navigated to GitHub")

        # Try to extract text from a heading
        # GitHub's main heading selector (may change if GitHub updates their site)
        heading_selector = "h1, h2"  # Get first h1 or h2

        # Wait for heading
        await wait_for_selector(context_id, page_id, heading_selector, timeout=5000)

        # Extract text using YOUR function
        text = await extract_text(context_id, page_id, heading_selector)
        print(f"📄 Extracted text: '{text}'")

        # Verify we got some text back
        assert len(text) > 0
        print("✅ Text extraction successful")

        # Cleanup
        await delete_page_by_page_id(context_id, page_id)

    @pytest.mark.asyncio
    async def test_multiple_pages_in_context(self, test_context: UUID, screenshots_dir: Path):
        """
        Test managing multiple pages in the same context using YOUR functions.

        Demonstrates:
        - Creating multiple pages
        - Getting open pages
        - Managing page lifecycle
        """
        print("\n📑 Testing multiple pages in one context...")
        context_id = test_context

        # Create first page and navigate to GitHub
        print("\n📄 Creating page 1...")
        page1_id, page1 = await go_to_url(context_id, "https://github.com")
        print(f"✅ Page 1 created: {page1_id}")

        # Create second page and navigate to GitHub Explore
        print("\n📄 Creating page 2...")
        page2_id, page2 = await go_to_url(context_id, "https://github.com/explore")
        print(f"✅ Page 2 created: {page2_id}")

        # Get all open pages using YOUR function
        print("\n📋 Getting all open pages...")
        open_pages = await get_open_pages(context_id)
        print(f"✅ Found {len(open_pages)} open pages")

        # Verify we have at least 2 pages
        assert len(open_pages) >= 2
        print("✅ Multiple pages verified")

        # Take screenshots of both pages
        screenshot1 = str(screenshots_dir / "integration_multi_page1.png")
        screenshot2 = str(screenshots_dir / "integration_multi_page2.png")

        await screenshot_page(context_id, page1_id, screenshot1)
        print(f"📸 Screenshot of page 1 saved")

        await screenshot_page(context_id, page2_id, screenshot2)
        print(f"📸 Screenshot of page 2 saved")

        # Cleanup pages
        await delete_page_by_page_id(context_id, page1_id)
        await delete_page_by_page_id(context_id, page2_id)
        print("🗑️  Cleaned up both pages")

    @pytest.mark.asyncio
    async def test_scroll_and_reload(self, test_context: UUID, screenshots_dir: Path):
        """
        Test scrolling and reloading using YOUR functions.

        Demonstrates:
        - Scrolling using scroll()
        - Reloading using reload_page()
        - Taking screenshots at different states
        """
        print("\n📜 Testing scroll and reload functions...")
        context_id = test_context

        # Navigate to GitHub Explore (has scrollable content)
        page_id, page = await go_to_url(context_id, "https://github.com/explore")
        print("✅ Navigated to GitHub Explore")

        # Take screenshot at top
        top_screenshot = str(screenshots_dir / "integration_scroll_01_top.png")
        await screenshot_page(context_id, page_id, top_screenshot)
        print("📸 Screenshot at top")

        # Scroll down using YOUR scroll function
        print("\n⬇️  Scrolling down...")
        scroll_result = await scroll(context_id, page_id, 0, 500)
        print(f"   {scroll_result}")

        # Take screenshot after scroll
        import asyncio
        await asyncio.sleep(1)  # Wait for scroll animation
        scrolled_screenshot = str(screenshots_dir / "integration_scroll_02_scrolled.png")
        await screenshot_page(context_id, page_id, scrolled_screenshot)
        print("📸 Screenshot after scroll")

        # Reload page using YOUR reload_page function
        print("\n🔄 Reloading page...")
        reload_result = await reload_page(context_id, page_id)
        print(f"   {reload_result}")

        await asyncio.sleep(1)  # Wait for reload
        print("✅ Page reloaded")

        # Cleanup
        await delete_page_by_page_id(context_id, page_id)


# Pytest configuration for this file
def pytest_configure(config):
    """Register the 'integration' marker."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test (uses real browser)"
    )
