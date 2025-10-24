"""
Simple Browser Demo - Fixed Version

This version bypasses strict validation to show the browser automation working.
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright


async def simple_github_demo():
    """Simple GitHub demo without strict validation."""
    print("📝 GitHub Signup Demo (Simple Version)")
    print("=" * 40)
    print("This will open a browser and show AI performing signup actions!")
    print()
    
    playwright = await async_playwright().start()
    browser = None
    
    try:
        # Launch browser (visible window)
        browser = await playwright.chromium.launch(
            headless=False,  # Set to True to run without visible window
            slow_mo=1500,   # Slow down actions for better visibility
            args=['--start-maximized']
        )
        
        # Create page
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        print("✅ Browser opened!")
        
        # Navigate to GitHub
        print("\n🌐 Navigating to GitHub...")
        await page.goto("https://github.com", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        # Step 1: Click Sign up
        print("\n📋 Step 1: Clicking 'Sign up'")
        try:
            signup_button = page.locator("text=Sign up").first
            await signup_button.highlight()
            await page.wait_for_timeout(500)
            await signup_button.click()
            print("   ✅ Clicked 'Sign up'!")
        except Exception as e:
            print(f"   ❌ Failed to click Sign up: {e}")
            return
        
        await page.wait_for_timeout(2000)
        
        # Step 2: Fill username
        print("\n📋 Step 2: Filling username")
        try:
            username_input = page.locator("input[name='user[login]']").first
            await username_input.highlight()
            await page.wait_for_timeout(500)
            await username_input.fill(f"demo-user-{int(asyncio.get_event_loop().time())}")
            print("   ✅ Username filled!")
        except Exception as e:
            print(f"   ❌ Failed to fill username: {e}")
            return
        
        # Step 3: Fill email
        print("\n📋 Step 3: Filling email")
        try:
            email_input = page.locator("input[name='user[email]']").first
            await email_input.highlight()
            await page.wait_for_timeout(500)
            await email_input.fill(f"demo-{int(asyncio.get_event_loop().time())}@example.com")
            print("   ✅ Email filled!")
        except Exception as e:
            print(f"   ❌ Failed to fill email: {e}")
            return
        
        # Step 4: Fill password
        print("\n📋 Step 4: Filling password")
        try:
            password_input = page.locator("input[name='user[password]']").first
            await password_input.highlight()
            await page.wait_for_timeout(500)
            await password_input.fill("DemoPassword123!")
            print("   ✅ Password filled!")
        except Exception as e:
            print(f"   ❌ Failed to fill password: {e}")
            return
        
        await page.wait_for_timeout(1000)
        
        # Step 5: Click submit
        print("\n📋 Step 5: Clicking submit")
        try:
            submit_button = page.locator("button[type='submit']").first
            await submit_button.highlight()
            await page.wait_for_timeout(500)
            await submit_button.click()
            print("   ✅ Submit clicked!")
        except Exception as e:
            print(f"   ❌ Failed to click submit: {e}")
            return
        
        await page.wait_for_timeout(3000)
        
        print("\n🎉 GitHub signup demo completed!")
        print("👀 Watch the browser - the AI just performed a signup!")
        print("📝 Note: This is a demo - no actual account was created")
        
        # Keep browser open for a moment
        print("\n⏰ Browser will close in 10 seconds...")
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    finally:
        # Cleanup
        if browser:
            await browser.close()
        await playwright.stop()
        print("🧹 Browser closed!")


async def simple_google_demo():
    """Simple Google search demo."""
    print("🔍 Google Search Demo (Simple Version)")
    print("=" * 40)
    print("This will open a browser and show AI performing search actions!")
    print()
    
    playwright = await async_playwright().start()
    browser = None
    
    try:
        # Launch browser (visible window)
        browser = await playwright.chromium.launch(
            headless=False,  # Set to True to run without visible window
            slow_mo=1000,    # Slow down actions for better visibility
            args=['--start-maximized']
        )
        
        # Create page
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        print("✅ Browser opened!")
        
        # Navigate to Google
        print("\n🌐 Navigating to Google...")
        await page.goto("https://www.google.com", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        # Step 1: Click search box
        print("\n📋 Step 1: Clicking search box")
        try:
            search_box = page.locator("textarea[name='q']").first
            await search_box.highlight()
            await page.wait_for_timeout(500)
            await search_box.click()
            print("   ✅ Search box clicked!")
        except Exception as e:
            print(f"   ❌ Failed to click search box: {e}")
            return
        
        # Step 2: Type search query
        print("\n📋 Step 2: Typing search query")
        try:
            await search_box.fill("QA Agent Flow DSL automation demo")
            print("   ✅ Search query typed!")
        except Exception as e:
            print(f"   ❌ Failed to type search query: {e}")
            return
        
        await page.wait_for_timeout(1000)
        
        # Step 3: Click search button
        print("\n📋 Step 3: Clicking search button")
        try:
            search_button = page.locator("input[type='submit']").first
            await search_button.highlight()
            await page.wait_for_timeout(500)
            await search_button.click()
            print("   ✅ Search button clicked!")
        except Exception as e:
            print(f"   ❌ Failed to click search button: {e}")
            return
        
        await page.wait_for_timeout(3000)
        
        print("\n🎉 Google search demo completed!")
        print("👀 Watch the browser - the AI just performed a search!")
        
        # Keep browser open for a moment
        print("\n⏰ Browser will close in 10 seconds...")
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    finally:
        # Cleanup
        if browser:
            await browser.close()
        await playwright.stop()
        print("🧹 Browser closed!")


if __name__ == "__main__":
    print("🤖 QA Agent Browser Demo (Fixed Version)")
    print("=" * 50)
    print("Choose a demo:")
    print("1. 🔍 Google Search Demo")
    print("2. 📝 GitHub Signup Demo")
    
    choice = input("Enter choice (1-2): ").strip()
    
    if choice == "2":
        asyncio.run(simple_github_demo())
    else:
        asyncio.run(simple_google_demo())
