"""
Browser Demo - Visual Flow DSL Execution

This demo shows the Flow DSL in action with real browser automation.
You can watch the AI perform actions like sign up, login, and navigation
in a real browser window.
"""
import asyncio
import time
from uuid import uuid4
from typing import Dict, Any

from playwright.async_api import async_playwright
from qa_agent.generation.dsl import flow_compiler
from qa_agent.generation.executor import flow_executor
from qa_agent.core.logging import get_logger

logger = get_logger(__name__)


class BrowserDemo:
    """
    Visual demonstration of Flow DSL execution with real browser automation.
    
    Features:
    - Real browser window opens
    - AI performs actions step by step
    - Visual feedback and logging
    - Interactive demonstration
    """
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
    
    async def setup_browser(self, headless: bool = False):
        """Setup Playwright browser for demonstration."""
        print("🚀 Setting up browser for demo...")
        
        playwright = await async_playwright().start()
        
        # Use Chromium for better compatibility
        self.browser = await playwright.chromium.launch(
            headless=headless,
            slow_mo=1000,  # Slow down actions for better visibility
            args=[
                '--start-maximized',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # Create context with realistic settings
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = await self.context.new_page()
        
        # Add visual indicators
        await self.page.add_init_script("""
            // Add visual indicators for demo
            const style = document.createElement('style');
            style.textContent = `
                .qa-agent-demo {
                    position: fixed;
                    top: 10px;
                    right: 10px;
                    background: #4CAF50;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    z-index: 9999;
                    font-family: Arial, sans-serif;
                    font-size: 14px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                }
            `;
            document.head.appendChild(style);
            
            // Show demo indicator
            const indicator = document.createElement('div');
            indicator.className = 'qa-agent-demo';
            indicator.textContent = '🤖 QA Agent Demo Running';
            document.body.appendChild(indicator);
        """)
        
        print("✅ Browser setup complete!")
    
    async def cleanup(self):
        """Cleanup browser resources."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        print("🧹 Browser cleanup complete!")
    
    async def run_signup_demo(self):
        """Run a visual signup flow demonstration."""
        print("\n🎯 Starting Signup Flow Demo")
        print("=" * 50)
        
        # Create signup flow
        signup_flow = {
            "name": "demo_signup",
            "version": 1,
            "description": "Visual signup demonstration",
            "start_url": "https://www.github.com",
            "steps": [
                {
                    "type": "click",
                    "selector": "text=Sign up",
                    "timeout": 10000,
                    "retry_attempts": 3
                },
                {
                    "type": "wait",
                    "timeout": 2000
                },
                {
                    "type": "type",
                    "selector": "input[name='user[login]']",
                    "text": f"demo-user-{int(time.time())}",
                    "timeout": 5000
                },
                {
                    "type": "type",
                    "selector": "input[name='user[email]']",
                    "text": f"demo-{int(time.time())}@example.com",
                    "timeout": 5000
                },
                {
                    "type": "type",
                    "selector": "input[name='user[password]']",
                    "text": "DemoPassword123!",
                    "timeout": 5000
                },
                {
                    "type": "wait",
                    "timeout": 1000
                },
                {
                    "type": "click",
                    "selector": "button[type='submit']",
                    "timeout": 10000
                },
                {
                    "type": "wait",
                    "timeout": 3000
                },
                {
                    "type": "assert",
                    "expect": {
                        "text_present": "Welcome"
                    }
                }
            ],
            "policies": {
                "human_like": True,
                "max_step_timeout_ms": 15000,
                "min_delay_ms": 500,
                "max_delay_ms": 2000,
                "retry_attempts": 3
            }
        }
        
        # Compile and execute flow
        try:
            compiled_flow = flow_compiler.compile_flow(signup_flow)
            print(f"📝 Compiled flow: {compiled_flow.name}")
            print(f"📊 Steps: {len(compiled_flow.steps)}")
            
            # Execute with visual feedback
            run_id = uuid4()
            print(f"🚀 Starting execution (Run ID: {run_id})")
            
            # Navigate to start URL
            print(f"🌐 Navigating to: {compiled_flow.start_url}")
            await self.page.goto(compiled_flow.start_url, wait_until="domcontentloaded")
            await self.page.wait_for_timeout(2000)
            
            # Execute each step with visual feedback
            for i, step in enumerate(compiled_flow.steps, 1):
                print(f"\n📋 Step {i}/{len(compiled_flow.steps)}: {step.type.value}")
                
                if step.selector:
                    print(f"   🎯 Selector: {step.selector}")
                
                if step.text:
                    print(f"   ✍️  Text: {step.text}")
                
                # Execute step
                await self._execute_step_with_feedback(step, i)
                
                # Wait between steps for visibility
                await self.page.wait_for_timeout(1000)
            
            print("\n✅ Signup flow completed successfully!")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            # Take screenshot for debugging
            await self.page.screenshot(path="demo_error.png")
            print("📸 Screenshot saved as demo_error.png")
    
    async def run_login_demo(self):
        """Run a visual login flow demonstration."""
        print("\n🔐 Starting Login Flow Demo")
        print("=" * 50)
        
        # Create login flow
        login_flow = {
            "name": "demo_login",
            "version": 1,
            "description": "Visual login demonstration",
            "start_url": "https://www.github.com/login",
            "steps": [
                {
                    "type": "wait",
                    "timeout": 2000
                },
                {
                    "type": "type",
                    "selector": "input[name='login']",
                    "text": "demo-user",
                    "timeout": 5000
                },
                {
                    "type": "type",
                    "selector": "input[name='password']",
                    "text": "demo-password",
                    "timeout": 5000
                },
                {
                    "type": "wait",
                    "timeout": 1000
                },
                {
                    "type": "click",
                    "selector": "input[type='submit']",
                    "timeout": 10000
                },
                {
                    "type": "wait",
                    "timeout": 3000
                }
            ],
            "policies": {
                "human_like": True,
                "max_step_timeout_ms": 15000,
                "min_delay_ms": 500,
                "max_delay_ms": 2000,
                "retry_attempts": 3
            }
        }
        
        try:
            compiled_flow = flow_compiler.compile_flow(login_flow)
            print(f"📝 Compiled flow: {compiled_flow.name}")
            
            # Navigate to start URL
            print(f"🌐 Navigating to: {compiled_flow.start_url}")
            await self.page.goto(compiled_flow.start_url, wait_until="domcontentloaded")
            await self.page.wait_for_timeout(2000)
            
            # Execute steps
            for i, step in enumerate(compiled_flow.steps, 1):
                print(f"\n📋 Step {i}/{len(compiled_flow.steps)}: {step.type.value}")
                await self._execute_step_with_feedback(step, i)
                await self.page.wait_for_timeout(1000)
            
            print("\n✅ Login flow completed!")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
    
    async def run_search_demo(self):
        """Run a visual search flow demonstration."""
        print("\n🔍 Starting Search Flow Demo")
        print("=" * 50)
        
        # Create search flow
        search_flow = {
            "name": "demo_search",
            "version": 1,
            "description": "Visual search demonstration",
            "start_url": "https://www.google.com",
            "steps": [
                {
                    "type": "wait",
                    "timeout": 2000
                },
                {
                    "type": "click",
                    "selector": "textarea[name='q']",
                    "timeout": 5000
                },
                {
                    "type": "type",
                    "selector": "textarea[name='q']",
                    "text": "QA Agent Flow DSL automation",
                    "timeout": 5000
                },
                {
                    "type": "wait",
                    "timeout": 1000
                },
                {
                    "type": "click",
                    "selector": "input[type='submit']",
                    "timeout": 5000
                },
                {
                    "type": "wait",
                    "timeout": 3000
                },
                {
                    "type": "scroll",
                    "direction": "down",
                    "amount": 500
                },
                {
                    "type": "wait",
                    "timeout": 2000
                }
            ],
            "policies": {
                "human_like": True,
                "max_step_timeout_ms": 15000,
                "min_delay_ms": 500,
                "max_delay_ms": 2000,
                "retry_attempts": 3
            }
        }
        
        try:
            compiled_flow = flow_compiler.compile_flow(search_flow)
            print(f"📝 Compiled flow: {compiled_flow.name}")
            
            # Navigate to start URL
            print(f"🌐 Navigating to: {compiled_flow.start_url}")
            await self.page.goto(compiled_flow.start_url, wait_until="domcontentloaded")
            await self.page.wait_for_timeout(2000)
            
            # Execute steps
            for i, step in enumerate(compiled_flow.steps, 1):
                print(f"\n📋 Step {i}/{len(compiled_flow.steps)}: {step.type.value}")
                await self._execute_step_with_feedback(step, i)
                await self.page.wait_for_timeout(1000)
            
            print("\n✅ Search flow completed!")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
    
    async def _execute_step_with_feedback(self, step, step_number):
        """Execute a step with visual feedback."""
        try:
            if step.type.value == "click":
                element = await self.page.locator(step.selector).first
                await element.highlight()
                await self.page.wait_for_timeout(500)
                await element.click()
                print(f"   ✅ Clicked element")
                
            elif step.type.value == "type":
                element = await self.page.locator(step.selector).first
                await element.highlight()
                await self.page.wait_for_timeout(500)
                await element.fill(step.text)
                print(f"   ✅ Typed: {step.text}")
                
            elif step.type.value == "wait":
                print(f"   ⏳ Waiting {step.timeout}ms")
                await self.page.wait_for_timeout(step.timeout)
                
            elif step.type.value == "scroll":
                print(f"   📜 Scrolling {step.direction} by {step.amount}px")
                if step.direction == "down":
                    await self.page.evaluate(f"window.scrollBy(0, {step.amount})")
                elif step.direction == "up":
                    await self.page.evaluate(f"window.scrollBy(0, -{step.amount})")
                
            elif step.type.value == "assert":
                print(f"   🔍 Checking assertion: {step.expect}")
                # Simple assertion check
                if "text_present" in step.expect:
                    text = step.expect["text_present"]
                    content = await self.page.text_content("body")
                    if text in content:
                        print(f"   ✅ Assertion passed: '{text}' found")
                    else:
                        print(f"   ❌ Assertion failed: '{text}' not found")
                
        except Exception as e:
            print(f"   ❌ Step failed: {e}")
            raise


async def run_interactive_demo():
    """Run an interactive demo with user choice."""
    print("🎭 QA Agent Flow DSL Browser Demo")
    print("=" * 50)
    print("This demo will open a real browser and show the AI performing actions!")
    print()
    
    demo = BrowserDemo()
    
    try:
        # Ask user for demo type
        print("Choose a demo to run:")
        print("1. 🔐 Login Flow (GitHub)")
        print("2. 📝 Signup Flow (GitHub)")
        print("3. 🔍 Search Flow (Google)")
        print("4. 🎬 All Demos")
        print()
        
        choice = input("Enter your choice (1-4): ").strip()
        
        # Setup browser (non-headless for visual demo)
        await demo.setup_browser(headless=False)
        
        if choice == "1":
            await demo.run_login_demo()
        elif choice == "2":
            await demo.run_signup_demo()
        elif choice == "3":
            await demo.run_search_demo()
        elif choice == "4":
            print("🎬 Running all demos...")
            await demo.run_login_demo()
            await asyncio.sleep(3)
            await demo.run_search_demo()
            await asyncio.sleep(3)
            await demo.run_signup_demo()
        else:
            print("❌ Invalid choice. Running default demo...")
            await demo.run_search_demo()
        
        # Keep browser open for a moment
        print("\n🎉 Demo completed! Browser will close in 5 seconds...")
        await asyncio.sleep(5)
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    finally:
        await demo.cleanup()


async def run_quick_demo():
    """Run a quick demo without user interaction."""
    print("🚀 Quick Flow DSL Demo")
    print("=" * 30)
    
    demo = BrowserDemo()
    
    try:
        await demo.setup_browser(headless=False)
        await demo.run_search_demo()
        
        print("\n✅ Quick demo completed!")
        await asyncio.sleep(3)
        
    except Exception as e:
        print(f"❌ Quick demo failed: {e}")
    finally:
        await demo.cleanup()


if __name__ == "__main__":
    print("Choose demo mode:")
    print("1. Interactive demo (choose what to see)")
    print("2. Quick demo (automatic)")
    
    mode = input("Enter mode (1-2): ").strip()
    
    if mode == "1":
        asyncio.run(run_interactive_demo())
    else:
        asyncio.run(run_quick_demo())
