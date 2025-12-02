from contextlib import asynccontextmanager
from fastapi import FastAPI
from playwright.async_api import async_playwright, Browser, Playwright

browser: Browser | None = None
playwright_instance: Playwright | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create browser instance
    global browser, playwright_instance
    playwright_instance = await async_playwright().start()
    browser = await playwright_instance.chromium.launch(headless=False)
    print("Browser instance created")
    
    yield
    
    # Close browser instance after shut down
    try:
        if browser:
            await browser.close()
    except Exception:
        pass
    finally:
        if playwright_instance:
            await playwright_instance.stop()
        print("Browser instance closed")

app = FastAPI(lifespan=lifespan)
