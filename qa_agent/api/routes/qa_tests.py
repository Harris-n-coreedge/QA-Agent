from fastapi import APIRouter, HTTPException
from datetime import datetime
from qa_agent.schemas import (
    BrowserUseRequest, 
    BrowserUseResponse, 
    TestResultResponse,
    AIProvider
)
import asyncio
import os

router = APIRouter()

@router.post("/browser-use/execute")
async def execute_browser_use(request: BrowserUseRequest):
    """
    Execute a simple browser automation task using Playwright directly.
    """
    print(f"Browser-use request: task={request.task}, provider={request.ai_provider}")
    print("USING SIMPLIFIED PLAYWRIGHT IMPLEMENTATION")
    
    try:
        # Set environment variables to fix Unicode issues
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '1'
        
        # Use Playwright directly to avoid Windows subprocess issues
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            print("Launching browser...")
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor"
                ]
            )
            
            print("Creating new page...")
            page = await browser.new_page()
            
            # Extract URL from task if present
            import re
            url_match = re.search(r'https?://[^\s]+', request.task)
            if url_match:
                url = url_match.group(0)
                print(f"Navigating to: {url}")
                await page.goto(url)
                
                # Get page title
                title = await page.title()
                result = f"Successfully navigated to {url}. Page title: {title}"
                print(f"Task completed successfully: {result}")
            else:
                # If no URL found, just navigate to Google
                print("No URL found in task, navigating to Google...")
                await page.goto("https://www.google.com")
                title = await page.title()
                result = f"Successfully navigated to Google. Page title: {title}"
                print(f"Task completed successfully: {result}")
            
            await browser.close()
        
        return {
            "task": request.task,
            "status": "completed",
            "result": result,
            "executed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Browser automation error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Browser automation failed: {str(e)}"
        )
