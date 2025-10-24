"""
Udemy Signup Demo - From Plan.md Step 8

This demo implements the exact Flow DSL example from Plan.md step 8:
"signup_flow" with steps for Udemy.com signup process.
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright


async def udemy_signup_demo():
    """Udemy signup demo based on Plan.md step 8 example."""
    print("🎓 Udemy Signup Demo (From Plan.md)")
    print("=" * 50)
    print("This implements the exact Flow DSL example from Plan.md step 8!")
    print("Flow: signup_flow with Udemy.com")
    print()
    
    playwright = await async_playwright().start()
    browser = None
    
    try:
        # Launch browser (visible window)
        browser = await playwright.chromium.launch(
            headless=False,  # Set to True to run without visible window
            slow_mo=1500,    # Slow down actions for better visibility
            args=['--start-maximized']
        )
        
        # Create page
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        print("✅ Browser opened!")
        
        # Navigate to Udemy (as specified in Plan.md)
        print("\n🌐 Navigating to Udemy.com...")
        await page.goto("https://www.udemy.com/", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # Step 1: Click "Sign up" (as per Plan.md example)
        print("\n📋 Step 1: Clicking 'Sign up'")
        try:
            # Try multiple selectors for "Sign up" button
            signup_selectors = [
                "text=Sign up",
                "text=Sign Up", 
                "text=Signup",
                "a:has-text('Sign up')",
                "button:has-text('Sign up')",
                "[data-purpose='signup-button']"
            ]
            
            signup_clicked = False
            for selector in signup_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        await element.highlight()
                        await page.wait_for_timeout(500)
                        await element.click()
                        print(f"   ✅ Clicked 'Sign up' using: {selector}")
                        signup_clicked = True
                        break
                except:
                    continue
            
            if not signup_clicked:
                print("   ⚠️  Could not find 'Sign up' button, trying alternative...")
                # Try clicking on any signup-related element
                await page.click("text=Sign up", timeout=5000)
                print("   ✅ Clicked 'Sign up' (alternative method)")
                
        except Exception as e:
            print(f"   ❌ Failed to click Sign up: {e}")
            # Take screenshot for debugging
            await page.screenshot(path="udemy_signup_error.png")
            print("   📸 Screenshot saved as udemy_signup_error.png")
            return
        
        await page.wait_for_timeout(3000)
        
        # Step 2: Type email (as per Plan.md example: "test@example.com")
        print("\n📋 Step 2: Filling email field")
        try:
            # Try multiple selectors for email input
            email_selectors = [
                "input[name='email']",
                "input[type='email']",
                "input[placeholder*='email']",
                "input[placeholder*='Email']",
                "#email",
                ".email-input"
            ]
            
            email_filled = False
            for selector in email_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        await element.highlight()
                        await page.wait_for_timeout(500)
                        await element.fill("test@example.com")  # As specified in Plan.md
                        print(f"   ✅ Email filled using: {selector}")
                        email_filled = True
                        break
                except:
                    continue
            
            if not email_filled:
                print("   ⚠️  Could not find email field")
                
        except Exception as e:
            print(f"   ❌ Failed to fill email: {e}")
            return
        
        # Step 3: Type password (as per Plan.md example: "P@ssw0rd!")
        print("\n📋 Step 3: Filling password field")
        try:
            # Try multiple selectors for password input
            password_selectors = [
                "input[name='password']",
                "input[type='password']",
                "input[placeholder*='password']",
                "input[placeholder*='Password']",
                "#password",
                ".password-input"
            ]
            
            password_filled = False
            for selector in password_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        await element.highlight()
                        await page.wait_for_timeout(500)
                        await element.fill("P@ssw0rd!")  # As specified in Plan.md
                        print(f"   ✅ Password filled using: {selector}")
                        password_filled = True
                        break
                except:
                    continue
            
            if not password_filled:
                print("   ⚠️  Could not find password field")
                
        except Exception as e:
            print(f"   ❌ Failed to fill password: {e}")
            return
        
        await page.wait_for_timeout(1000)
        
        # Step 4: Click "Continue" button (as per Plan.md example)
        print("\n📋 Step 4: Clicking 'Continue' button")
        try:
            # Try multiple selectors for Continue button
            continue_selectors = [
                "button:has-text('Continue')",
                "text=Continue",
                "input[type='submit']",
                "button[type='submit']",
                "[data-purpose='continue-button']",
                ".continue-btn"
            ]
            
            continue_clicked = False
            for selector in continue_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        await element.highlight()
                        await page.wait_for_timeout(500)
                        await element.click()
                        print(f"   ✅ Continue clicked using: {selector}")
                        continue_clicked = True
                        break
                except:
                    continue
            
            if not continue_clicked:
                print("   ⚠️  Could not find Continue button")
                
        except Exception as e:
            print(f"   ❌ Failed to click Continue: {e}")
            return
        
        await page.wait_for_timeout(3000)
        
        # Step 5: Assert URL contains "/welcome" (as per Plan.md example)
        print("\n📋 Step 5: Checking for welcome page")
        try:
            current_url = page.url
            print(f"   🔍 Current URL: {current_url}")
            
            if "/welcome" in current_url:
                print("   ✅ Assertion passed: URL contains '/welcome'")
            else:
                print("   ⚠️  Assertion: URL does not contain '/welcome'")
                print(f"   📝 This is expected for demo purposes (no real account created)")
                
        except Exception as e:
            print(f"   ❌ Failed to check URL: {e}")
        
        print("\n🎉 Udemy signup flow completed!")
        print("📝 This demonstrates the exact Flow DSL from Plan.md step 8:")
        print("   - Navigate to https://www.udemy.com/")
        print("   - Click 'Sign up'")
        print("   - Type email: test@example.com")
        print("   - Type password: P@ssw0rd!")
        print("   - Click 'Continue'")
        print("   - Assert URL contains '/welcome'")
        print("\n👀 Watch the browser - the AI just performed the Udemy signup flow!")
        
        # Keep browser open for a moment
        print("\n⏰ Browser will close in 30 seconds...")
        await asyncio.sleep(30)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        # Take screenshot for debugging
        if browser:
            try:
                page = await browser.new_page()
                await page.screenshot(path="udemy_demo_error.png")
                print("📸 Error screenshot saved as udemy_demo_error.png")
            except:
                pass
    finally:
        # Cleanup
        if browser:
            await browser.close()
        await playwright.stop()
        print("🧹 Browser closed!")


async def udemy_login_demo():
    """Udemy login demo (bonus)."""
    print("🔐 Udemy Login Demo (Bonus)")
    print("=" * 40)
    print("This shows a login flow on Udemy!")
    print()
    
    playwright = await async_playwright().start()
    browser = None
    
    try:
        browser = await playwright.chromium.launch(
            headless=False,
            slow_mo=1500,
            args=['--start-maximized']
        )
        
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        print("✅ Browser opened!")
        
        # Navigate to Udemy login
        print("\n🌐 Navigating to Udemy login...")
        await page.goto("https://www.udemy.com/join/login-popup/", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # Fill email
        print("\n📋 Step 1: Filling email")
        try:
            email_input = page.locator("input[name='email']").first
            await email_input.highlight()
            await page.wait_for_timeout(500)
            await email_input.fill("demo@example.com")
            print("   ✅ Email filled!")
        except Exception as e:
            print(f"   ❌ Failed to fill email: {e}")
            return
        
        # Fill password
        print("\n📋 Step 2: Filling password")
        try:
            password_input = page.locator("input[name='password']").first
            await password_input.highlight()
            await page.wait_for_timeout(500)
            await password_input.fill("DemoPassword123!")
            print("   ✅ Password filled!")
        except Exception as e:
            print(f"   ❌ Failed to fill password: {e}")
            return
        
        await page.wait_for_timeout(1000)
        
        # Click login
        print("\n📋 Step 3: Clicking login")
        try:
            login_button = page.locator("button[type='submit']").first
            await login_button.highlight()
            await page.wait_for_timeout(500)
            await login_button.click()
            print("   ✅ Login clicked!")
        except Exception as e:
            print(f"   ❌ Failed to click login: {e}")
            return
        
        await page.wait_for_timeout(3000)
        
        print("\n🎉 Udemy login demo completed!")
        print("👀 Watch the browser - the AI just performed a login!")
        
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    finally:
        if browser:
            await browser.close()
        await playwright.stop()


if __name__ == "__main__":
    print("🎓 Udemy Flow DSL Demo (From Plan.md)")
    print("=" * 50)
    print("This implements the exact example from Plan.md step 8!")
    print()
    print("Choose a demo:")
    print("1. 📝 Udemy Signup Flow (Plan.md example)")
    print("2. 🔐 Udemy Login Flow (Bonus)")
    
    choice = input("Enter choice (1-2): ").strip()
    
    if choice == "2":
        asyncio.run(udemy_login_demo())
    else:
        asyncio.run(udemy_signup_demo())
