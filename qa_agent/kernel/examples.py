"""
Kernel Integration Examples

This file demonstrates the complete Kernel integration as specified in the plan.
Shows how to use Kernel's browsers-as-a-service with all advanced features.
"""
import asyncio
from uuid import uuid4
from playwright.async_api import Page

from qa_agent.kernel.browser import connect_kernel_browser, disconnect_kernel_browser
from qa_agent.kernel.client import kernel_client
from qa_agent.core.logging import get_logger

logger = get_logger(__name__)


async def basic_kernel_example():
    """
    Basic example: Connect to Kernel & Navigate
    
    This matches the example sketch from the plan exactly.
    """
    run_id = uuid4()
    
    # Connect to Kernel browser with stealth mode
    browser, context, page, browser_response = await connect_kernel_browser(
        run_id=run_id,
        stealth=True,
        profile="demo_profile",
        standby=True
    )
    
    try:
        # Navigate to target site
        await page.goto("https://example.com", wait_until="domcontentloaded")
        
        # Perform user actions
        await page.click("text=Sign up")
        await page.fill("input[name='email']", "test@example.com")
        await page.fill("input[name='password']", "password123")
        await page.click("button:has-text('Create account')")
        
        # Get Kernel URLs for debugging
        live_view_url = kernel_client.get_live_view_url(browser_response)
        replay_url = kernel_client.get_replay_url(browser_response)
        
        logger.info("Basic example completed", 
                   live_view_url=live_view_url, 
                   replay_url=replay_url)
        
    finally:
        # Ensure termination via Kernel SDK per docs
        await disconnect_kernel_browser(run_id)


async def stealth_mode_example():
    """
    Demonstrate Kernel's stealth mode for anti-detection.
    """
    run_id = uuid4()
    
    browser, context, page, browser_response = await connect_kernel_browser(
        run_id=run_id,
        stealth=True,  # Enable anti-detection
        headless=True
    )
    
    try:
        # Navigate to a site that might detect automation
        await page.goto("https://bot.sannysoft.com/", wait_until="domcontentloaded")
        
        # Take screenshot to verify stealth mode
        await page.screenshot(path="stealth_test.png")
        
        logger.info("Stealth mode test completed", 
                   browser_id=browser_response.get("id"))
        
    finally:
        await disconnect_kernel_browser(run_id)


async def profile_persistence_example():
    """
    Demonstrate Kernel's profile persistence for session reuse.
    """
    profile_name = "persistent_demo_profile"
    
    # First session - create profile
    run_id_1 = uuid4()
    browser1, context1, page1, response1 = await connect_kernel_browser(
        run_id=run_id_1,
        profile=profile_name,
        stealth=True
    )
    
    try:
        # Login and set cookies
        await page1.goto("https://example.com/login", wait_until="domcontentloaded")
        await page1.fill("input[name='email']", "user@example.com")
        await page1.fill("input[name='password']", "password123")
        await page1.click("button[type='submit']")
        
        # Wait for login to complete
        await page1.wait_for_url("**/dashboard")
        
        logger.info("First session completed - profile created")
        
    finally:
        await disconnect_kernel_browser(run_id_1)
    
    # Second session - reuse profile
    run_id_2 = uuid4()
    browser2, context2, page2, response2 = await connect_kernel_browser(
        run_id=run_id_2,
        profile=profile_name,  # Same profile
        stealth=True
    )
    
    try:
        # Should be logged in automatically
        await page2.goto("https://example.com/dashboard", wait_until="domcontentloaded")
        
        # Verify we're still logged in
        user_element = await page2.query_selector(".user-info")
        if user_element:
            logger.info("Profile persistence working - user still logged in")
        else:
            logger.warning("Profile persistence failed - user not logged in")
        
    finally:
        await disconnect_kernel_browser(run_id_2)


async def standby_mode_example():
    """
    Demonstrate Kernel's standby mode for fast next-run.
    """
    run_id = uuid4()
    
    # Create browser with standby mode
    browser, context, page, browser_response = await connect_kernel_browser(
        run_id=run_id,
        standby=True,  # Enable standby mode
        stealth=True
    )
    
    try:
        # First run
        await page.goto("https://example.com", wait_until="domcontentloaded")
        await page.click("text=Products")
        
        logger.info("First run completed with standby mode")
        
        # Browser stays warm for next run
        # In a real scenario, you would reuse the same browser instance
        
    finally:
        await disconnect_kernel_browser(run_id)


async def live_view_debugging_example():
    """
    Demonstrate Kernel's Live View for human-in-the-loop debugging.
    """
    run_id = uuid4()
    
    browser, context, page, browser_response = await connect_kernel_browser(
        run_id=run_id,
        stealth=True
    )
    
    try:
        # Get Live View URL for debugging
        live_view_url = kernel_client.get_live_view_url(browser_response)
        
        logger.info("Live View URL available for debugging", 
                   live_view_url=live_view_url)
        
        # Perform actions while Live View is available
        await page.goto("https://example.com", wait_until="domcontentloaded")
        
        # Add delays to allow human observation via Live View
        await page.click("text=Sign up")
        await asyncio.sleep(2)  # Pause for human observation
        
        await page.fill("input[name='email']", "test@example.com")
        await asyncio.sleep(1)  # Pause for human observation
        
        await page.click("button:has-text('Create account')")
        
        logger.info("Live View debugging session completed")
        
    finally:
        await disconnect_kernel_browser(run_id)


async def replay_review_example():
    """
    Demonstrate Kernel's replay functionality for video review.
    """
    run_id = uuid4()
    
    browser, context, page, browser_response = await connect_kernel_browser(
        run_id=run_id,
        stealth=True
    )
    
    try:
        # Perform a complex flow
        await page.goto("https://example.com", wait_until="domcontentloaded")
        await page.click("text=Sign up")
        await page.fill("input[name='email']", "test@example.com")
        await page.fill("input[name='password']", "password123")
        await page.click("button:has-text('Create account')")
        
        # Wait for completion
        await page.wait_for_url("**/welcome")
        
        # Get replay URL for review
        replay_url = kernel_client.get_replay_url(browser_response)
        
        logger.info("Replay available for review", replay_url=replay_url)
        
    finally:
        await disconnect_kernel_browser(run_id)


async def comprehensive_kernel_demo():
    """
    Comprehensive demo showing all Kernel features together.
    """
    logger.info("Starting comprehensive Kernel integration demo")
    
    # Run all examples
    await basic_kernel_example()
    await stealth_mode_example()
    await profile_persistence_example()
    await standby_mode_example()
    await live_view_debugging_example()
    await replay_review_example()
    
    logger.info("Comprehensive Kernel integration demo completed")


if __name__ == "__main__":
    # Run the comprehensive demo
    asyncio.run(comprehensive_kernel_demo())
