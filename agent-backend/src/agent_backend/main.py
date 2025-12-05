from contextlib import asynccontextmanager
from fastapi import FastAPI
from playwright.async_api import async_playwright, Browser, Playwright
from .instances import browser_manager, planner, executor

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create browser instance
    await browser_manager.initialize()
    print("Browser instance created")
    
    yield
    
    # Close browser instance after shut down
    await browser_manager.terminate()

app = FastAPI(lifespan=lifespan)
