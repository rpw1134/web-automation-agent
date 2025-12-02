from typing import Dict
from playwright.async_api import BrowserContext, Browser, Playwright, async_playwright

class BrowserManager:
    
    def __init__(self):
        # 1 per agent sessions. ID --> BrowserContext
        self._playwright : Playwright | None = None
        self._browser: Browser | None = None
        self._contexts: Dict[int, BrowserContext]  = {}
    
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
    