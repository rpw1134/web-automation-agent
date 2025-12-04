from typing import Dict, Tuple
from playwright.async_api import BrowserContext, Browser, Playwright, async_playwright, Page
from uuid import uuid4, UUID

class BrowserManager:
    """
    Manages browser instances and contexts for web automation agents.

    This class provides a centralized interface for managing Playwright browser
    instances and multiple browser contexts. Each context is identified by a UUID
    and can be used by different agent sessions.

    Attributes:
        _playwright: Playwright instance instantiated upon startup. Singleton.
        _browser: Browser instance instantiated upon startup. Singleton.
        _contexts: Mapping of browser context IDs to their instances. One created per agent session.
        _pages: Nested mapping of context IDs to their pages by page IDs.
    """
    
    def __init__(self):
        self._playwright : Playwright | None = None
        self._browser: Browser | None = None
        self._contexts: Dict[UUID, BrowserContext]  = {}
        self._pages: Dict[UUID, Dict[UUID, Page]] = {}
    
    @property
    def playwright(self) -> Playwright:
        """
        Get the Playwright instance.

        Returns:
            Playwright: The initialized Playwright instance.

        Raises:
            RuntimeError: If the Playwright instance is not initialized.
        """
        if self._playwright is None:
            raise RuntimeError("Playwright instance is not initialized.")
        return self._playwright
    
    @property
    def browser(self) -> Browser:
        """
        Get the Browser instance.

        Returns:
            Browser: The initialized Chromium browser instance.

        Raises:
            RuntimeError: If the browser instance is not initialized.
        """
        if self._browser is None:
            raise RuntimeError("Browser instance is not initialized.")
        return self._browser
    
    @property
    def contexts(self) -> Dict[UUID, BrowserContext]:
        """
        Get all browser contexts.

        Returns:
            Dict[UUID, BrowserContext]: Mapping of context IDs to BrowserContext instances.
        """
        return self._contexts

    @property
    def pages(self) -> Dict[UUID, Dict[UUID, Page]]:
        """
        Get all pages organized by context.

        Returns:
            Dict[UUID, Dict[UUID, Page]]: Nested mapping where first UUID is context ID
                and second UUID is page ID, mapping to Page instances.
        """
        return self._pages
    
    async def initialize(self):
        """
        Initialize the Playwright and Browser instances.

        Starts the Playwright instance and launches a Chromium browser in non-headless mode.
        This method should be called once during application startup.
        """
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=False)
        
    async def terminate(self):
        """
        Terminate the browser and Playwright instances.

        Safely closes the browser and stops the Playwright instance, suppressing any errors
        that occur during shutdown. This method should be called during application shutdown.
        """
        try:
            if self._browser:
                await self._browser.close()
        except Exception:
            pass
        finally:
            if self._playwright:
                await self._playwright.stop()
            print("Browser instance closed")
    
    def get_page_by_id(self, context_id: UUID, page_id: UUID) -> Page:
        """
        Retrieve a page by its ID within a specific context.

        Args:
            context_id: The UUID of the browser context containing the page.
            page_id: The UUID of the page to retrieve.

        Returns:
            Page: The requested Playwright Page instance.

        Raises:
            KeyError: If no page is found with the given IDs.
            RuntimeError: If the page exists but is no longer valid (closed).
        """
        context_pages = self._pages.get(context_id, {})
        page = context_pages.get(page_id, None)
        if page is None:
            raise KeyError(f"No page found for ID: {page_id} in context ID: {context_id}")
        try:
            _ = page.url
        except Exception:
            raise RuntimeError(f"Page with ID: {page_id} in context ID: {context_id} is no longer valid.")
        return page
    
    async def create_page(self, context_id: UUID) -> Tuple[UUID, Page]:
        """
        Create a new page within a browser context.

        Args:
            context_id: The UUID of the browser context where the page will be created.

        Returns:
            Tuple[UUID, Page]: A tuple containing the new page's UUID and the Page instance.

        Raises:
            KeyError: If no browser context is found with the given ID.
            RuntimeError: If the browser context is no longer valid.
        """
        context: BrowserContext = self.get_browser_context_by_id(context_id)
        page = await context.new_page()
        page_id = uuid4()
        if context_id not in self._pages:
            self._pages[context_id] = {}
        self._pages[context_id][page_id] = page
        return page_id, page
    
    async def delete_page_by_page_id(self, context_id: UUID, page_id: UUID):
        """
        Close and remove a page from tracking.

        Args:
            context_id: The UUID of the browser context containing the page.
            page_id: The UUID of the page to delete.

        Note:
            If the page doesn't exist, this method silently succeeds without error.
        """
        context_pages = self._pages.get(context_id, {})
        page = context_pages.get(page_id, None)
        if page:
            await page.close()
            del context_pages[page_id]
    
    def get_browser_context_by_id(self, context_id: UUID) -> BrowserContext:
        """
        Retrieve a browser context by its ID.

        Args:
            context_id: The UUID of the browser context to retrieve.

        Returns:
            BrowserContext: The requested Playwright BrowserContext instance.

        Raises:
            KeyError: If no browser context is found with the given ID.
            RuntimeError: If the browser context exists but is no longer valid (closed).
        """
        browser_context = self._contexts.get(context_id, None)
        if browser_context is None:
            raise KeyError(f"No browser context found for ID: {context_id}")
        try:
            _ = browser_context.pages
        except Exception:
            raise RuntimeError(f"Browser context for ID: {context_id} is no longer valid.")
        return browser_context
    
    async def create_browser_context(self) -> Tuple[UUID, BrowserContext]:
        """
        Create a new browser context.

        Creates a new isolated browser context with its own cookies, cache, and storage.
        Each agent session should have its own context.

        Returns:
            Tuple[UUID, BrowserContext]: A tuple containing the new context's UUID and the
                BrowserContext instance.

        Raises:
            RuntimeError: If the browser instance is not initialized.
        """
        context_id = uuid4()
        browser_context = await self.browser.new_context()
        self._contexts[context_id] = browser_context
        return (context_id, browser_context)
    
    async def delete_browser_context_by_id(self, context_id: UUID):
        """
        Close and remove a browser context from tracking.

        Closes the browser context and removes it along with all associated pages
        from the tracking dictionaries.

        Args:
            context_id: The UUID of the browser context to delete.

        Note:
            If the context doesn't exist, this method silently succeeds without error.
            All pages within the context are automatically removed from tracking.
        """
        browser_context = self._contexts.get(context_id, None)
        if browser_context:
            await browser_context.close()
            del self._contexts[context_id]
            if context_id in self._pages:
                del self._pages[context_id]