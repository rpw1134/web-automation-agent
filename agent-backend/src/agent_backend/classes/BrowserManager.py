from typing import Dict
from playwright.async_api import BrowserContext, Browser, Playwright, async_playwright, Page
from uuid import uuid4, UUID

class BrowserManager:
    '''
        :attribute _playwright: Playwright instance instantiated upon startup. Singleton
        :attribute _browser: Browser instance instantiated upon startup. Singleton
        :attribute  _contexts: Dict[UUID, BrowserContext] - Mapping of browser context IDs to their instances. One created per agent session
        :attribute _pages: Dict[UUID, Dict[UUID, Page]] - Nested mapping of context IDs to their pages by page IDs.
        '''
    
    def __init__(self):
        self._playwright : Playwright | None = None
        self._browser: Browser | None = None
        self._contexts: Dict[UUID, BrowserContext]  = {}
        self._pages: Dict[UUID, Dict[UUID, Page]] = {}
    
    async def initialize(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=False)
        
    async def terminate(self):
        try:
            if self._browser:
                await self._browser.close()
        except Exception:
            pass
        finally:
            if self._playwright:
                await self._playwright.stop()
            print("Browser instance closed")
    
    @property
    def playwright(self) -> Playwright:
        if self._playwright is None:
            raise RuntimeError("Playwright instance is not initialized.")
        return self._playwright
    
    @property
    def browser(self) -> Browser:
        if self._browser is None:
            raise RuntimeError("Browser instance is not initialized.")
        return self._browser
    
    def get_page_by_id(self, context_id: UUID, page_id: UUID) -> Page:
        context_pages = self._pages.get(context_id, {})
        page = context_pages.get(page_id, None)
        if page is None:
            raise KeyError(f"No page found for ID: {page_id} in context ID: {context_id}")
        try:
            _ = page.url
        except Exception:
            raise RuntimeError(f"Page with ID: {page_id} in context ID: {context_id} is no longer valid.")
        return page
    
    def create_page(self, context_id: UUID, page: Page) -> UUID:
        page_id = uuid4()
        if context_id not in self._pages:
            self._pages[context_id] = {}
        self._pages[context_id][page_id] = page
        return page_id
    
    async def delete_page_by_page_id(self, context_id: UUID, page_id: UUID):
        context_pages = self._pages.get(context_id, {})
        page = context_pages.get(page_id, None)
        if page:
            await page.close()
            del context_pages[page_id]
    
    def get_browser_context_by_id(self, context_id: UUID) -> BrowserContext:
        browser_context = self._contexts.get(context_id, None)
        if browser_context is None:
            raise KeyError(f"No browser context found for ID: {context_id}")
        try:
            _ = browser_context.pages
        except Exception:
            raise RuntimeError(f"Browser context for ID: {context_id} is no longer valid.")
        return browser_context
    
    async def create_browser_context(self) -> UUID:
        context_id = uuid4()
        browser_context = await self.browser.new_context()
        self._contexts[context_id] = browser_context
        return context_id
    
    async def delete_browser_context_by_id(self, context_id: UUID):
        browser_context = self._contexts.get(context_id, None)
        if browser_context:
            await browser_context.close()
            del self._contexts[context_id]
            if context_id in self._pages:
                del self._pages[context_id]