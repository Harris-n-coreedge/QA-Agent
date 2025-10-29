"""
Browser lifecycle management for Kernel browsers.

Connects Playwright over CDP to remote Kernel browsers.
Implements defensive cleanup of Kernel browsers when runs finish or time out.
"""
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Tuple, Optional, Dict, Any
import asyncio
from uuid import UUID

from qa_agent.kernel.client import kernel_client
from qa_agent.core.logging import get_logger

logger = get_logger(__name__)


class BrowserManager:
    """Manages browser lifecycle and connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, Any]] = {}
    
    async def create_browser_session(
        self,
        run_id: UUID,
        stealth: bool = None,
        profile: Optional[str] = None,
        standby: bool = False,
        headless: bool = True
    ) -> Tuple[Browser, BrowserContext, Page, Dict[str, Any]]:
        """
        Create a complete browser session with Kernel integration.
        
        Uses Kernel's advanced features:
        - Stealth mode for anti-detection
        - Profile persistence for session reuse
        - Standby mode for fast next-run
        - Headless mode for automation
        """
        try:
            # Create or reuse Kernel browser
            browser_response = await kernel_client.create_or_reuse_browser(
                stealth=stealth,
                profile=profile,
                standby=standby,
                headless=headless,
            )
            
            browser_id = browser_response.get("id")
            cdp_url = kernel_client.get_cdp_url(browser_response)
            
            if not cdp_url:
                raise ValueError("No CDP URL received from Kernel")
            
            logger.info(
                "Connecting to browser via CDP", 
                run_id=str(run_id), 
                browser_id=browser_id,
                cdp_url=cdp_url
            )
            
            # Connect via Playwright CDP
            playwright = await async_playwright().start()
            browser = await playwright.chromium.connect_over_cdp(cdp_url)
            
            # Get or create context
            contexts = browser.contexts
            if contexts:
                context = contexts[0]
                logger.info("Reusing existing browser context", run_id=str(run_id))
            else:
                context = await browser.new_context()
                logger.info("Created new browser context", run_id=str(run_id))
            
            # Create new page
            page = await context.new_page()

            # If headful requested, try to ensure window is visible/maximized when possible
            try:
                if not headless:
                    await page.bring_to_front()
            except Exception:
                pass
            
            # Store connection info with all URLs
            self.active_connections[str(run_id)] = {
                "browser_id": browser_id,
                "browser_response": browser_response,
                "playwright": playwright,
                "browser": browser,
                "context": context,
                "page": page,
                "urls": kernel_client.get_browser_urls(browser_response)
            }
            
            logger.info(
                "Browser session created successfully", 
                run_id=str(run_id), 
                browser_id=browser_id,
                live_view_url=kernel_client.get_live_view_url(browser_response)
            )
            
            return browser, context, page, browser_response
            
        except Exception as e:
            logger.error("Failed to create browser session", run_id=str(run_id), error=str(e))
            raise
    
    async def terminate_browser_session(self, run_id: UUID) -> None:
        """Terminate a browser session."""
        run_id_str = str(run_id)
        
        if run_id_str not in self.active_connections:
            logger.warning("No active browser session found", run_id=run_id_str)
            return
        
        try:
            connection_info = self.active_connections[run_id_str]
            browser_id = connection_info["browser_id"]
            playwright = connection_info["playwright"]
            
            # Close Playwright connections
            try:
                await connection_info["page"].close()
                await connection_info["context"].close()
                await connection_info["browser"].close()
                await playwright.stop()
            except Exception as e:
                logger.warning("Error closing Playwright connections", run_id=run_id_str, error=str(e))
            
            # Terminate Kernel browser
            try:
                await kernel_client.terminate_browser(browser_id)
            except Exception as e:
                logger.warning("Error terminating Kernel browser", run_id=run_id_str, browser_id=browser_id, error=str(e))
            
            # Remove from active connections
            del self.active_connections[run_id_str]
            
            logger.info("Browser session terminated", run_id=run_id_str, browser_id=browser_id)
            
        except Exception as e:
            logger.error("Failed to terminate browser session", run_id=run_id_str, error=str(e))
            raise
    
    def get_session_info(self, run_id: UUID) -> Optional[Dict[str, Any]]:
        """Get comprehensive session information including all URLs."""
        run_id_str = str(run_id)
        if run_id_str in self.active_connections:
            connection_info = self.active_connections[run_id_str]
            return {
                "browser_id": connection_info["browser_id"],
                "urls": connection_info.get("urls", {}),
                "live_view_url": kernel_client.get_live_view_url(connection_info["browser_response"]),
                "replay_url": kernel_client.get_replay_url(connection_info["browser_response"]),
                "cdp_url": kernel_client.get_cdp_url(connection_info["browser_response"])
            }
        return None
    
    async def cleanup_all_sessions(self) -> None:
        """Cleanup all active sessions."""
        for run_id in list(self.active_connections.keys()):
            try:
                await self.terminate_browser_session(UUID(run_id))
            except Exception as e:
                logger.error("Failed to cleanup session", run_id=run_id, error=str(e))


# Global browser manager
browser_manager = BrowserManager()


async def connect_kernel_browser(
    run_id: UUID,
    stealth: bool = None,
    profile: Optional[str] = None,
    standby: bool = False,
    headless: bool = True
) -> Tuple[Browser, BrowserContext, Page, Dict[str, Any]]:
    """
    Connect to a Kernel browser via CDP.
    
    This is the main entry point for connecting to Kernel browsers.
    """
    return await browser_manager.create_browser_session(
        run_id=run_id,
        stealth=stealth,
        profile=profile,
        standby=standby,
        headless=headless
    )


async def disconnect_kernel_browser(run_id: UUID) -> None:
    """Disconnect from a Kernel browser."""
    await browser_manager.terminate_browser_session(run_id)


# Example function as specified in the plan
async def example_run():
    """
    Example: Connect to Kernel & Navigate (Sketch)
    
    This demonstrates the basic pattern for using Kernel browsers
    as described in the plan.
    """
    run_id = UUID()  # Generate a temporary run ID
    
    browser, context, page, browser_response = await connect_kernel_browser(
        run_id=run_id,
        stealth=True,
        profile="example_profile",
        standby=True
    )
    
    try:
        # Navigate to example site
        await page.goto("https://example.com", wait_until="domcontentloaded")
        
        # Perform actions
        await page.click("text=Sign up")
        
        # Get URLs for debugging/review
        live_view_url = kernel_client.get_live_view_url(browser_response)
        replay_url = kernel_client.get_replay_url(browser_response)
        
        logger.info("Example run completed", live_view_url=live_view_url, replay_url=replay_url)
        
    finally:
        # Ensure termination via Kernel SDK per docs
        await disconnect_kernel_browser(run_id)
