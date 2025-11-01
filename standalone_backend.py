"""
Standalone QA Agent Backend - Works independently of existing qa_agent package
This provides the full functionality for the frontend without dependencies on other routes
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from contextlib import asynccontextmanager
import asyncio
import json
from datetime import datetime
import uuid
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Store global agent and test results
global_agent: Optional[Any] = None
agent_status: str = "uninitialized"  # uninitialized, initializing, active, failed
agent_error: Optional[str] = None
commands_executed: int = 0
test_results: Dict[str, Dict] = {}
# Store external browsers to keep them alive
external_browsers: Dict[str, Any] = {}  # Store playwright and browser instances


class AIProvider(str, Enum):
    """Supported AI providers"""
    openai = "openai"
    anthropic = "anthropic"
    google = "google"


class TestStatus(str, Enum):
    """Test execution status"""
    pending = "pending"
    running = "running"
    completed = "completed"
    passed = "passed"
    failed = "failed"
    cancelled = "cancelled"


class CommandRequest(BaseModel):
    """Request to execute a command"""
    command: str = Field(..., description="Natural language command to execute")


class NavigateRequest(BaseModel):
    """Request to navigate to a website URL"""
    website_url: str = Field(..., description="Website URL to navigate to")


class CrossBrowserTestRequest(BaseModel):
    """Request for cross-browser testing"""
    website_url: Optional[str] = Field(default=None, description="Website URL to test (uses current URL if not provided)")
    browser_type: Optional[str] = Field(default=None, description="Specific browser to test (chromium, firefox, webkit). If not provided, tests all.")


class BrowserUseRequest(BaseModel):
    """Request for browser-use simple automation"""
    task: str = Field(..., description="Task description for browser automation")
    ai_provider: AIProvider = Field(default=AIProvider.google, description="AI provider (default: google)")


class CommandResponse(BaseModel):
    """Response after executing a command"""
    command: str
    result: str
    status: TestStatus
    executed_at: str
    duration_ms: Optional[float] = None

# Internal helpers for global agent management
async def _ensure_global_agent() -> bool:
    """Ensure the global agent exists and is active. Returns True if agent is ready."""
    global global_agent, agent_status, agent_error
    
    try:
        # If already active or initializing, return status
        if agent_status in {"active", "initializing"}:
            return agent_status == "active"
        
        # If failed, don't retry automatically
        if agent_status == "failed":
            return False

        # Lazy import to reuse existing logic
        from dotenv import load_dotenv
        load_dotenv()
        # Prefer provider from env; fallback to google from qa_config.yaml if any
        preferred_provider = os.getenv("QA_AGENT_AI_PROVIDER")
        if not preferred_provider:
            try:
                import yaml
                cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qa_config.yaml")
                if os.path.exists(cfg_path):
                    with open(cfg_path, "r", encoding="utf-8") as f:
                        cfg = yaml.safe_load(f) or {}
                        preferred_provider = (cfg.get("ai") or {}).get("provider")
            except Exception:
                preferred_provider = None
        preferred_provider = (preferred_provider or AIProvider.google.value).lower()

        # Map to enum safely
        provider_enum = AIProvider(preferred_provider) if preferred_provider in {p.value for p in AIProvider} else AIProvider.google

        # Read API key for chosen provider
        if provider_enum == AIProvider.openai:
            api_key = os.getenv("OPENAI_API_KEY")
        elif provider_enum == AIProvider.anthropic:
            api_key = os.getenv("ANTHROPIC_API_KEY")
        else:
            api_key = os.getenv("GOOGLE_API_KEY")

        # If missing API key, mark as failed
        if not api_key:
            agent_status = "failed"
            agent_error = f"API key for {provider_enum.value} not found in environment variables. Please add it to your .env file."
            return False

        # Import and construct agent (lazy initialization - don't start browser session yet)
        from multi_ai_qa_agent import MultiAIQAAgent
        agent_status = "uninitialized"  # Changed from "initializing" - browser not started yet
        global_agent = MultiAIQAAgent(ai_provider=provider_enum.value, api_key=api_key)

        # Browser session will be initialized on-demand when first test runs
        # Do NOT start browser session here - it will be started lazily when needed

        return False  # Agent object created but browser session not started
    except Exception as e:
        agent_status = "failed"
        agent_error = str(e)
        return False

async def _start_browser_session(website_url: str = "https://www.w3schools.com/", auto_check: bool = False):
    """Start browser session lazily when needed (on-demand initialization)"""
    global global_agent, agent_status, agent_error
    
    # If already active, return
    if agent_status == "active":
        return True
    
    # If already initializing, wait for it
    if agent_status == "initializing":
        # Wait up to 60 seconds for initialization
        for _ in range(60):
            await asyncio.sleep(1)
            if agent_status == "active":
                return True
            if agent_status == "failed":
                return False
        return False
    
    # Ensure agent object exists
    if global_agent is None:
        await _ensure_global_agent()
    
    if global_agent is None:
        return False
    
    # Start browser session
    # IMPORTANT: We'll modify start_session to accept headless parameter
    try:
        agent_status = "initializing"
        
        # Start browser session in headless mode for embedding
        # We need to directly initialize browser instead of using start_session
        # because start_session has headless=False hardcoded
        from playwright.async_api import async_playwright
        print("🤖 Multi-AI QA Agent Starting (Headless for Embedding)...")
        print("=" * 40)
        print(f"🌐 Opening: {website_url}")
        print(f"🧠 AI Provider: {global_agent.ai_provider.upper()}")
        print("👁️ Browser Mode: HEADLESS (embedded)")
        
        global_agent.playwright = await async_playwright().start()
        global_agent.browser = await global_agent.playwright.chromium.launch(
            headless=True,  # Run headless - no external window
            slow_mo=500,    # Slower interactions for stability
            args=[
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        global_agent.context = await global_agent.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        global_agent.current_page = await global_agent.context.new_page()
        
        try:
            global_agent.current_page.set_default_timeout(60000)
            global_agent.current_page.set_default_navigation_timeout(90000)
        except Exception:
            pass
        
        # Navigate to the website
        try:
            await global_agent.current_page.goto(website_url, wait_until="domcontentloaded", timeout=45000)
        except Exception as e1:
            try:
                await global_agent.current_page.goto(website_url, wait_until="load", timeout=60000)
            except Exception as e2:
                try:
                    await global_agent.current_page.goto(website_url, wait_until="commit", timeout=30000)
                except Exception as e3:
                    print(f"⚠️ Navigation still timing out: {e3}. Continuing best-effort.")
        
        try:
            await global_agent.current_page.wait_for_selector("body", timeout=10000)
        except Exception:
            pass
        await global_agent.current_page.wait_for_timeout(2000)
        
        # Analyze page characteristics
        try:
            await global_agent._analyze_page_characteristics()
        except Exception as e:
            print(f"⚠️ Page analysis failed: {e}")
        
        # Auto-check if requested
        if auto_check:
            try:
                summary = await global_agent._run_auto_checks()
                print(summary)
            except Exception as e:
                print(f"⚠️ Auto-checks failed: {e}")
        
        global_agent.current_url = website_url
        print("✅ Agent ready (Headless)! I can understand natural language commands.")
        agent_status = "active"
        agent_error = None
        return True
    except Exception as e:
        agent_status = "failed"
        agent_error = str(e)
        return False

def _get_agent_status():
    """Get current agent status"""
    return {
        "status": agent_status,
        "commands_executed": commands_executed,
        "error": agent_error,
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup - DO NOT auto-initialize browser (lazy initialization)
    # Agent object will be created on first request, browser session starts on first test
    yield
    # Shutdown - cleanup browser if it was started
    global global_agent, external_browsers
    try:
        if global_agent:
            if hasattr(global_agent, 'browser') and global_agent.browser:
                await global_agent.browser.close()
            if hasattr(global_agent, 'playwright') and global_agent.playwright:
                await global_agent.playwright.stop()
        # Close all external browsers
        for browser_key, browser_info in external_browsers.items():
            try:
                if 'browser' in browser_info:
                    await browser_info['browser'].close()
                if 'playwright' in browser_info:
                    await browser_info['playwright'].stop()
            except Exception:
                pass
        external_browsers.clear()
    except Exception:
        pass


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="QA Agent API",
    description="Backend service for multi-AI QA automation",
    version="1.0.0",
    lifespan=lifespan,
)

# Ensure screenshots directory exists and mount static serving
SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mobile_test_screenshots")
try:
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
except Exception:
    pass

app.mount("/static/mobile", StaticFiles(directory=SCREENSHOTS_DIR), name="mobile_screenshots")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MobileTestRequest(BaseModel):
    """Request to run a mobile responsiveness test"""
    deviceName: Optional[str] = Field(default="iPhone 17 Pro Max", description="Device name to emulate")
    custom: Optional[Dict[str, Any]] = Field(default=None, description="Custom dimensions { width, height, deviceScaleFactor? }")
    overlapPercent: Optional[float] = Field(default=0.12, description="Fractional overlap between successive screenshots (e.g., 0.1 for 10%)")

class MobileTestResponse(BaseModel):
    """Response for mobile test run"""
    device_name: str
    device: Dict[str, Any]
    screenshots: list
    served_base_url: str
    message: str



class TestResultResponse(BaseModel):
    """Test result details"""
    test_id: str
    command: str
    status: TestStatus
    result: str
    started_at: str
    completed_at: Optional[str] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "QA Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/qa-tests/health"
    }


@app.get("/api/v1/qa-tests/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_status": agent_status,
        "commands_executed": commands_executed,
        "total_test_results": len(test_results),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/qa-tests/agent-status")
async def get_agent_status():
    """Get current agent status"""
    await _ensure_global_agent()
    return _get_agent_status()


@app.get("/api/v1/qa-tests/browser-view")
async def get_browser_view():
    """Get browser view - returns screenshot for embedding in frontend"""
    global global_agent, agent_status
    
    # Check if browser is active
    if agent_status != "active":
        return {
            "active": False,
            "message": f"Browser is not active. Status: {agent_status}",
            "status": agent_status
        }
    
    try:
        browser = getattr(global_agent, "browser", None)
        page = getattr(global_agent, "current_page", None)
        
        if browser is None or page is None:
            return {
                "active": False,
                "message": "Browser page not available",
                "status": agent_status
            }
        
        # Capture screenshot and return as base64
        try:
            screenshot_bytes = await page.screenshot(full_page=False)
            import base64
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            current_url = page.url
            
            return {
                "active": True,
                "page_url": current_url,
                "screenshot": screenshot_b64,
                "screenshot_data_url": f"data:image/png;base64,{screenshot_b64}",
                "message": "Browser is active and ready",
                "status": agent_status,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as screenshot_error:
            return {
                "active": True,
                "page_url": page.url if page else None,
                "screenshot": None,
                "message": f"Screenshot failed: {str(screenshot_error)}",
                "status": agent_status
            }
    except Exception as e:
        return {
            "active": False,
            "message": f"Error getting browser view: {str(e)}",
            "status": agent_status
        }


@app.post("/api/v1/qa-tests/navigate")
async def navigate_to_url(request: NavigateRequest):
    """Navigate to a website URL"""
    # Ensure agent object exists (may be uninitialized)
    await _ensure_global_agent()
    
    # Lazy initialize browser session if not already active
    if agent_status not in {"active", "initializing"}:
        # Start browser session with the requested URL (no auto_check)
        if not await _start_browser_session(website_url=request.website_url.strip(), auto_check=False):
            if agent_status == "failed":
                raise HTTPException(
                    status_code=400,
                    detail=f"Browser initialization failed. Status: {agent_status}. Error: {agent_error or 'Unknown error'}"
                )
            raise HTTPException(
                status_code=400,
                detail=f"Browser is not ready. Status: {agent_status}. Please wait for initialization."
            )
    
    # If still initializing, wait for it
    if agent_status == "initializing":
        for _ in range(60):
            await asyncio.sleep(1)
            if agent_status == "active":
                break
            if agent_status == "failed":
                raise HTTPException(
                    status_code=400,
                    detail=f"Browser initialization failed. Error: {agent_error or 'Unknown error'}"
                )
    
    if agent_status != "active":
        raise HTTPException(
            status_code=400,
            detail=f"Browser is not ready. Status: {agent_status}. Please wait for initialization."
        )

    try:
        # Get the current page from the agent
        page = getattr(global_agent, "current_page", None)
        if page is None:
            raise HTTPException(status_code=400, detail="No active page available")

        # Navigate to the new URL
        website_url = request.website_url.strip()
        if not website_url.startswith(('http://', 'https://')):
            website_url = f'https://{website_url}'

        try:
            await page.goto(website_url, wait_until="domcontentloaded", timeout=45000)
        except Exception as e1:
            try:
                await page.goto(website_url, wait_until="load", timeout=60000)
            except Exception as e2:
                try:
                    await page.goto(website_url, wait_until="commit", timeout=30000)
                except Exception as e3:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to navigate to {website_url}: {str(e3)}"
                    )

        # Wait for page to be ready
        try:
            await page.wait_for_selector("body", timeout=10000)
        except Exception:
            pass
        await page.wait_for_timeout(2000)

        # Verify navigation succeeded by checking actual page URL
        actual_url = page.url
        if not actual_url.startswith(website_url.split('?')[0]) and not actual_url.startswith(website_url.replace('https://', 'http://').split('?')[0]):
            # Check if it's a redirect - normalize both URLs for comparison
            normalized_target = website_url.rstrip('/').split('?')[0].split('#')[0]
            normalized_actual = actual_url.rstrip('/').split('?')[0].split('#')[0]
            if normalized_actual != normalized_target and not normalized_actual.startswith(normalized_target):
                raise HTTPException(
                    status_code=500,
                    detail=f"Navigation verification failed: expected {website_url} but page is at {actual_url}"
                )

        # Update agent's current URL
        global_agent.current_url = website_url

        # Run page analysis after navigation (similar to start_session)
        # This helps the agent understand the new page
        try:
            if hasattr(global_agent, '_analyze_page_characteristics'):
                await global_agent._analyze_page_characteristics()
        except Exception as e:
            # Log but don't fail - page analysis is optional
            print(f"⚠️ Page analysis after navigation failed: {e}")

        return {
            "message": f"Successfully navigated to {website_url}",
            "website_url": website_url,
            "actual_url": actual_url,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Navigation failed: {str(e)}")


@app.post("/api/v1/qa-tests/commands", response_model=CommandResponse)
async def execute_command(request: CommandRequest):
    """Execute a natural language command"""
    global commands_executed
    
    # Ensure agent object exists (may be uninitialized)
    await _ensure_global_agent()
    
    # Lazy initialize browser session if not already active
    if agent_status not in {"active", "initializing"}:
        # Start browser session with default URL (will navigate to user's URL later)
        if not await _start_browser_session(website_url="https://www.w3schools.com/", auto_check=False):
            if agent_status == "failed":
                raise HTTPException(
                    status_code=400,
                    detail=f"Browser initialization failed. Status: {agent_status}. Error: {agent_error or 'Unknown error'}"
                )
            raise HTTPException(
                status_code=400,
                detail=f"Browser is not ready. Status: {agent_status}. Please wait for initialization."
            )
    
    # If still initializing, wait for it
    if agent_status == "initializing":
        # Wait up to 60 seconds for initialization
        for _ in range(60):
            await asyncio.sleep(1)
            if agent_status == "active":
                break
            if agent_status == "failed":
                raise HTTPException(
                    status_code=400,
                    detail=f"Browser initialization failed. Error: {agent_error or 'Unknown error'}"
                )
    
    # Final check
    if agent_status != "active":
        raise HTTPException(
            status_code=400,
            detail=f"Browser is not ready. Status: {agent_status}. Please wait for initialization."
        )

    try:
        start_time = datetime.utcnow()

        # For auto check and auto audit commands, add scrolling behavior before execution
        command_lower = request.command.lower().strip()
        if command_lower == 'auto check' or command_lower == 'auto audit':
            try:
                page = getattr(global_agent, "current_page", None)
                if page:
                    # Scroll to top first
                    await page.evaluate("window.scrollTo(0, 0)")
                    await asyncio.sleep(0.5)
                    
                    # Get page height
                    page_height = await page.evaluate("document.body.scrollHeight || document.documentElement.scrollHeight")
                    viewport_height = await page.evaluate("window.innerHeight")
                    
                    # Scroll from top to bottom smoothly
                    scroll_step = viewport_height // 2
                    scroll_position = 0
                    
                    while scroll_position < page_height:
                        await page.evaluate(f"window.scrollTo(0, {scroll_position})")
                        await asyncio.sleep(0.2)  # Smooth scrolling
                        scroll_position += scroll_step
                    
                    # Scroll to bottom and stay there
                    await page.evaluate(f"window.scrollTo(0, {page_height})")
                    await asyncio.sleep(1)
                    
                    # Keep at bottom for a moment before executing command
                    await asyncio.sleep(0.5)
            except Exception as scroll_error:
                print(f"⚠️ Scrolling during {command_lower} failed: {scroll_error}")

        # Execute the command
        result = await global_agent.process_command(request.command)

        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000

        # Update stats
        commands_executed += 1

        # Store test result
        test_id = str(uuid.uuid4())
        test_results[test_id] = {
            "test_id": test_id,
            "command": request.command,
            "result": result,
            "status": TestStatus.completed,
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat(),
            "duration_ms": duration_ms
        }

        return CommandResponse(
            command=request.command,
            result=result,
            status=TestStatus.completed,
            executed_at=end_time.isoformat(),
            duration_ms=duration_ms
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {str(e)}")


@app.post("/api/v1/qa-tests/open-browser-external")
async def open_browser_external(request: CrossBrowserTestRequest):
    """Open a browser externally in headful mode with full UI"""
    global global_agent, external_browsers
    
    # Ensure agent object exists
    await _ensure_global_agent()
    
    # Use the provided URL or current URL from agent
    test_url = request.website_url or getattr(global_agent, "current_url", None) or "https://www.w3schools.com/"
    
    # Get browser type from request
    browser_type = getattr(request, 'browser_type', 'chromium')
    
    if browser_type not in ['chromium', 'firefox', 'webkit']:
        raise HTTPException(status_code=400, detail="Invalid browser type. Use: chromium, firefox, or webkit")
    
    try:
        from playwright.async_api import async_playwright
        
        # Close existing browser of this type if it exists
        browser_key = f"{browser_type}_external"
        if browser_key in external_browsers:
            try:
                existing = external_browsers[browser_key]
                if 'browser' in existing:
                    await existing['browser'].close()
                if 'playwright' in existing:
                    await existing['playwright'].stop()
            except Exception:
                pass  # Ignore errors closing old browser
            del external_browsers[browser_key]
        
        # Launch browser in headful mode (visible, with full UI)
        playwright = await async_playwright().start()
        
        if browser_type == 'chromium':
            browser = await playwright.chromium.launch(
                headless=False,  # Show full browser UI
                slow_mo=500,
                args=['--start-maximized']  # Maximize window
            )
        elif browser_type == 'firefox':
            browser = await playwright.firefox.launch(
                headless=False,  # Show full browser UI
                slow_mo=500
            )
        elif browser_type == 'webkit':
            browser = await playwright.webkit.launch(
                headless=False,  # Show full browser UI
                slow_mo=500
            )
        
        # Create context and page
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        # Navigate to URL
        try:
            await page.goto(test_url, wait_until="domcontentloaded", timeout=45000)
        except Exception as e1:
            try:
                await page.goto(test_url, wait_until="load", timeout=60000)
            except Exception as e2:
                await page.goto(test_url, wait_until="commit", timeout=30000)
        
        await page.wait_for_timeout(1000)
        
        # Store browser instances to keep them alive
        external_browsers[browser_key] = {
            'playwright': playwright,
            'browser': browser,
            'context': context,
            'page': page,
            'browser_type': browser_type,
            'url': test_url,
            'opened_at': datetime.utcnow().isoformat()
        }
        
        return {
            "message": f"Opened {browser_type} externally",
            "browser_type": browser_type,
            "url": test_url,
            "status": "opened",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to open browser externally: {str(e)}")


@app.post("/api/v1/qa-tests/cross-browser-test")
async def run_cross_browser_test(request: CrossBrowserTestRequest):
    """Run cross-browser test - can test all browsers or a specific one"""
    global global_agent, agent_status, commands_executed, test_results
    
    # Ensure agent object exists (may be uninitialized)
    await _ensure_global_agent()
    
    # Use the provided URL or current URL from agent
    test_url = request.website_url or getattr(global_agent, "current_url", None) or "https://www.w3schools.com/"
    
    # Get browser type from request if provided
    browser_type = getattr(request, 'browser_type', None)
    
    start_time = datetime.utcnow()
    
    try:
        from playwright.async_api import async_playwright
        
        # If specific browser requested, test only that one
        if browser_type and browser_type in ['chromium', 'firefox', 'webkit']:
            browsers_to_test = [browser_type]
        else:
            browsers_to_test = ['chromium', 'firefox', 'webkit']
        
        results = {}
        
        for browser_type in browsers_to_test:
            try:
                print(f"🌐 Testing on {browser_type}...")
                
                # Launch browser in headless mode (for embedding)
                playwright = await async_playwright().start()
                
                if browser_type == 'chromium':
                    browser = await playwright.chromium.launch(headless=True, slow_mo=500)
                elif browser_type == 'firefox':
                    browser = await playwright.firefox.launch(headless=True, slow_mo=500)
                elif browser_type == 'webkit':
                    browser = await playwright.webkit.launch(headless=True, slow_mo=500)
                else:
                    results[browser_type] = {"status": "failed", "error": f"Unknown browser: {browser_type}"}
                    continue
                
                # Create context and page
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    ignore_https_errors=True
                )
                page = await context.new_page()
                
                # Navigate to URL
                try:
                    await page.goto(test_url, wait_until="domcontentloaded", timeout=45000)
                except Exception as e1:
                    try:
                        await page.goto(test_url, wait_until="load", timeout=60000)
                    except Exception as e2:
                        await page.goto(test_url, wait_until="commit", timeout=30000)
                
                await page.wait_for_timeout(2000)
                
                # Get page info
                title = await page.title()
                url = page.url
                
                # Take screenshot
                screenshot_bytes = await page.screenshot(full_page=False)
                import base64
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                
                # Close browser
                await browser.close()
                await playwright.stop()
                
                results[browser_type] = {
                    "status": "success",
                    "title": title,
                    "url": url,
                    "screenshot": f"data:image/png;base64,{screenshot_b64}"
                }
                
            except Exception as e:
                results[browser_type] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Determine overall test status
        success_count = len([r for r in results.values() if r.get("status") == "success"])
        total_count = len(browsers_to_test)
        
        if success_count == total_count:
            overall_status = TestStatus.passed
        elif success_count > 0:
            overall_status = TestStatus.completed
        else:
            overall_status = TestStatus.failed
        
        # Update stats
        commands_executed += 1
        
        # Store test result for dashboard
        test_id = str(uuid.uuid4())
        
        # Format result text
        result_lines = [f"🌐 Cross-Browser Test Results for {test_url}:"]
        for browser_name, browser_result in results.items():
            if browser_result.get("status") == "success":
                result_lines.append(f"   ✅ {browser_name.capitalize()}: Success - {browser_result.get('title', 'N/A')}")
            else:
                result_lines.append(f"   ❌ {browser_name.capitalize()}: Failed - {browser_result.get('error', 'Unknown error')}")
        
        result_text = "\n".join(result_lines)
        
        test_results[test_id] = {
            "test_id": test_id,
            "command": f"cross-browser test ({', '.join(browsers_to_test)})",
            "result": result_text,
            "status": overall_status,
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat(),
            "duration_ms": duration_ms,
            "executed_at": end_time.isoformat()
        }
        
        return {
            "test_url": test_url,
            "browsers": results,
            "total_browsers": len(browsers_to_test),
            "completed": success_count,
            "test_id": test_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        # Still record the test as failed
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        commands_executed += 1
        
        test_id = str(uuid.uuid4())
        test_results[test_id] = {
            "test_id": test_id,
            "command": f"cross-browser test ({', '.join(browsers_to_test) if 'browsers_to_test' in locals() else 'all browsers'})",
            "result": f"Cross-browser test failed: {str(e)}",
            "status": TestStatus.failed,
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat(),
            "duration_ms": duration_ms,
            "executed_at": end_time.isoformat(),
            "error": str(e)
        }
        
        raise HTTPException(status_code=500, detail=f"Cross-browser test failed: {str(e)}")


@app.post("/api/v1/qa-tests/mobile-test", response_model=MobileTestResponse)
async def run_mobile_test(request: MobileTestRequest, http_request: Request):
    """Run a non-interactive mobile test and return screenshot URLs."""
    # Ensure agent object exists (may be uninitialized)
    await _ensure_global_agent()
    
    # Lazy initialize browser session if not already active
    if agent_status not in {"active", "initializing"}:
        # Start browser session with default URL (will navigate to user's URL later)
        if not await _start_browser_session(website_url="https://www.w3schools.com/", auto_check=False):
            if agent_status == "failed":
                raise HTTPException(
                    status_code=400,
                    detail=f"Browser initialization failed. Status: {agent_status}. Error: {agent_error or 'Unknown error'}"
                )
            raise HTTPException(
                status_code=400,
                detail=f"Browser is not ready. Status: {agent_status}. Please wait for initialization."
            )
    
    # If still initializing, wait for it
    if agent_status == "initializing":
        for _ in range(60):
            await asyncio.sleep(1)
            if agent_status == "active":
                break
            if agent_status == "failed":
                raise HTTPException(
                    status_code=400,
                    detail=f"Browser initialization failed. Error: {agent_error or 'Unknown error'}"
                )
    
    if agent_status != "active":
        raise HTTPException(
            status_code=400,
            detail=f"Browser is not ready. Status: {agent_status}. Please wait for initialization."
        )

    try:
        started_at = datetime.utcnow()
        test_id = str(uuid.uuid4())
        page = getattr(global_agent, "current_page", None)
        if page is None:
            raise HTTPException(status_code=400, detail="No active page available. Wait for initialization to complete.")

        # Resolve device config from agent's MobileDeviceManager or custom
        device_name = request.deviceName or "iPhone 17 Pro Max"
        device_cfg: Dict[str, Any]
        if request.custom and isinstance(request.custom, dict):
            # Validate custom dimensions
            width = int(request.custom.get("width", 0))
            height = int(request.custom.get("height", 0))
            scale = int(request.custom.get("deviceScaleFactor", 1) or 1)
            if width <= 0 or height <= 0:
                raise HTTPException(status_code=400, detail="Custom width and height must be positive integers")
            device_cfg = {"width": width, "height": height, "deviceScaleFactor": scale}
            device_name = request.custom.get("name") or f"Custom {width}x{height}"
        else:
            devices = getattr(global_agent.mobile_device_manager, "devices", {})
            device_cfg = devices.get(device_name)
            if not device_cfg:
                raise HTTPException(status_code=400, detail=f"Unknown device: {device_name}")

        # Store original viewport
        original_viewport = page.viewport_size

        # Set viewport to device
        await page.set_viewport_size({
            "width": device_cfg["width"],
            "height": device_cfg["height"],
        })

        # Allow layout to stabilize
        await page.wait_for_timeout(500)

        # Measure page height and scroll, capturing screenshots
        try:
            page_height = await page.evaluate("document.body.scrollHeight")
        except Exception:
            page_height = device_cfg["height"]

        viewport_h = device_cfg["height"]
        scroll_position = 0
        count = 0
        screenshot_urls = []

        # Calculate overlap: default 12% (10-15% requested)
        try:
            overlap_fraction = float(request.overlapPercent if request.overlapPercent is not None else 0.12)
        except Exception:
            overlap_fraction = 0.12
        # Clamp reasonable bounds [0, 0.3]
        overlap_fraction = max(0.0, min(0.3, overlap_fraction))
        step = max(1, int(viewport_h * (1.0 - overlap_fraction)))

        # Namespace files in a per-test directory
        test_dir = os.path.join(SCREENSHOTS_DIR, test_id)
        try:
            os.makedirs(test_dir, exist_ok=True)
        except Exception:
            pass

        while scroll_position < page_height and count < 40:
            # Scroll and wait
            await page.evaluate(f"window.scrollTo(0, {scroll_position})")
            await page.wait_for_timeout(400)

            count += 1
            filename = f"{device_name.replace(' ', '_')}_{count}.png"
            filepath = os.path.join(test_dir, filename)
            try:
                await page.screenshot(path=filepath)
                rel = f"/static/mobile/{test_id}/{filename}"
                base = str(http_request.base_url).rstrip('/')
                screenshot_urls.append(f"{base}{rel}")
            except Exception:
                # Skip failures but continue
                pass

            scroll_position += step

        # Scroll back to top and reset viewport
        try:
            await page.evaluate("window.scrollTo(0, 0)")
        except Exception:
            pass
        try:
            await page.set_viewport_size(original_viewport)
        except Exception:
            pass

        # Persist test result for Test Results page
        try:
            completed_at = datetime.utcnow()
            duration_ms = (completed_at - started_at).total_seconds() * 1000
            test_results[test_id] = {
                "test_id": test_id,
                "command": "mobile test",
                "status": TestStatus.completed,
                "result": f"Captured {len(screenshot_urls)} screenshots on {device_name} ({device_cfg.get('width')}x{device_cfg.get('height')})",
                "started_at": started_at.isoformat(),
                "completed_at": completed_at.isoformat(),
                "duration_ms": duration_ms,
                "device": {
                    "name": device_name,
                    "width": device_cfg.get("width"),
                    "height": device_cfg.get("height"),
                    "deviceScaleFactor": device_cfg.get("deviceScaleFactor", 1),
                },
                "screenshots": screenshot_urls,
            }
        except Exception:
            pass

        return MobileTestResponse(
            device_name=device_name,
            device={
                "name": device_name,
                "width": device_cfg.get("width"),
                "height": device_cfg.get("height"),
                "deviceScaleFactor": device_cfg.get("deviceScaleFactor", 1),
            },
            screenshots=screenshot_urls,
            served_base_url=str(http_request.base_url).rstrip('/') + "/static/mobile/",
            message=f"Captured {len(screenshot_urls)} screenshots"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mobile test failed: {str(e)}")


@app.post("/api/v1/qa-tests/browser-use/execute")
async def execute_browser_use(request: BrowserUseRequest):
    """
    Execute a simple browser automation task using browser-use library.
    Returns structured output of agent execution history.
    """
    started_at = datetime.utcnow()
    test_id = str(uuid.uuid4())
    
    try:
        # Import browser_use components
        try:
            from browser_use import Agent as BrowserAgent, ChatGoogle
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="browser-use library not installed. Install with: pip install browser-use"
            )

        # Import parser utility - use only the simple formatter to avoid schema dependencies
        from qa_agent.utils.browser_use_parser import format_terminal_output_simple

        # Import appropriate chat model
        if request.ai_provider == AIProvider.google:
            # Get API key from environment
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise HTTPException(
                    status_code=400,
                    detail="Google API key not found in environment variables. Please add GOOGLE_API_KEY to your .env file."
                )
            llm = ChatGoogle(model="gemini-flash-latest", api_key=api_key)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Browser-use currently only supports Google AI provider"
            )

        # Create agent and execute task
        agent = BrowserAgent(task=request.task, llm=llm)

        # Run the task and get history
        history = await agent.run()
        
        # Create terminal-style output (simple version that doesn't need schemas)
        terminal_output = format_terminal_output_simple(history, request.task)

        # Determine test status by parsing terminal output
        # Use regex patterns similar to frontend logic for more robust matching
        import re
        terminal_text = terminal_output
        
        # Check for explicit PASSED/FAILED markers using regex (case-insensitive)
        passed_patterns = [
            r'(?:\n|^)\s*✓\s*TEST\s+CASE\s+STATUS:\s*PASSED',
            r'(?:\n|^)\s*TEST\s+CASE:\s*PASSED',
            r'test\s+case\s+is\s*\*\*passed\*\*',
            r'Test\s+case\s+is\s+PASSED',
            r'test\s+case\s+status:\s*passed',
            r'test\s+case:\s*passed',
        ]
        failed_patterns = [
            r'(?:\n|^)\s*✗\s*TEST\s+CASE\s+STATUS:\s*FAILED',
            r'(?:\n|^)\s*TEST\s+CASE:\s*FAILED',
            r'test\s+case\s+is\s*\*\*failed\*\*',
            r'Test\s+case\s+is\s+FAILED',
            r'test\s+case\s+status:\s*failed',
            r'test\s+case:\s*failed',
            r'Conclusion:\s*Test\s+case\s+failed',  # Catch conclusion patterns
            r'Conclusion:.*[Tt]est\s+case\s+failed',  # Catch variations
        ]
        
        passed_marker = any(re.search(pattern, terminal_text, re.IGNORECASE | re.MULTILINE) for pattern in passed_patterns)
        failed_marker = any(re.search(pattern, terminal_text, re.IGNORECASE | re.MULTILINE) for pattern in failed_patterns)
        
        # Determine status
        if passed_marker and not failed_marker:
            test_status = TestStatus.passed
        elif failed_marker:
            test_status = TestStatus.failed
        else:
            test_status = TestStatus.completed

        completed_at = datetime.utcnow()
        duration_ms = (completed_at - started_at).total_seconds() * 1000

        # Store test result
        test_results[test_id] = {
            "test_id": test_id,
            "command": request.task,
            "status": test_status.value,
            "result": terminal_output,
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "duration_ms": duration_ms
        }

        return {
            "task": request.task,
            "status": test_status.value,
            "terminal_output": terminal_output,  # Terminal-style formatted output
            "executed_at": completed_at.isoformat(),
            "test_id": test_id
        }

    except HTTPException:
        raise
    except Exception as e:
        # Store failed test result
        completed_at = datetime.utcnow()
        duration_ms = (completed_at - started_at).total_seconds() * 1000
        test_results[test_id] = {
            "test_id": test_id,
            "command": request.task,
            "status": TestStatus.failed.value,
            "result": f"Browser automation failed: {str(e)}",
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "duration_ms": duration_ms,
            "error": str(e)
        }
        raise HTTPException(status_code=500, detail=f"Browser automation failed: {str(e)}")


@app.get("/api/v1/qa-tests/test-results/{test_id}", response_model=TestResultResponse)
async def get_test_result(test_id: str):
    """Get details of a specific test result"""
    if test_id not in test_results:
        raise HTTPException(status_code=404, detail=f"Test result {test_id} not found")

    return test_results[test_id]


@app.get("/api/v1/qa-tests/test-results")
async def list_test_results(limit: int = 50):
    """List test results"""
    results = list(test_results.values())

    # Sort by most recent first
    results.sort(key=lambda x: x["started_at"], reverse=True)

    return {
        "results": results[:limit],
        "total": len(results)
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("QA Agent Backend - Standalone Version")
    print("=" * 60)
    print(f"API: http://localhost:8000")
    print(f"Docs: http://localhost:8000/docs")
    print(f"Frontend: http://localhost:3000")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
