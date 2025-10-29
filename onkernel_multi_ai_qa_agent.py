import asyncio
import os
import sys
import json
import base64
from uuid import uuid4

# Ensure project root on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Optional: best-effort .env loading without hard dependency
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from qa_agent.kernel.browser import connect_kernel_browser, disconnect_kernel_browser
from qa_agent.kernel.client import kernel_client
import webbrowser
import subprocess
import platform

# Reuse the full feature set from the original agent
from multi_ai_qa_agent import MultiAIQAAgent


class OnKernelMultiAIQAAgent(MultiAIQAAgent):
    """
    Drop-in replacement for MultiAIQAAgent that runs on Kernel browsers.
    It preserves all features and handlers, swapping only the session lifecycle
    to use Kernel's browsers-as-a-service via CDP.
    """

    def __init__(self, ai_provider: str = "openai", api_key: str = None):
        super().__init__(ai_provider=ai_provider, api_key=api_key)
        self.kernel_run_id = None
        self.kernel_browser_response = None

    async def start_session(self, website_url: str = "https://www.w3schools.com/", auto_check: bool = True):
        """Start a Kernel-powered browser session on a specific website."""
        print("🤖 Multi-AI QA Agent (Kernel)")
        print("=" * 40)
        print(f"🌐 Opening: {website_url}")
        print(f"🧠 AI Provider: {self.ai_provider.upper()}")
        print("🧩 Browser Backend: Kernel (Playwright over CDP)")
        print("👁️ Browser Mode: VISIBLE (headful)")

        # Kernel connection options can be customized via env
        stealth = os.getenv("KERNEL_STEALTH", "true").lower() in ("1", "true", "yes")
        standby = os.getenv("KERNEL_STANDBY", "true").lower() in ("1", "true", "yes")
        profile = os.getenv("KERNEL_PROFILE", None)
        headless_env = os.getenv("KERNEL_HEADLESS", "false").lower() in ("1", "true", "yes")

        # Connect to Kernel browser
        self.kernel_run_id = uuid4()
        browser, context, page, browser_response = await connect_kernel_browser(
            run_id=self.kernel_run_id,
            stealth=stealth,
            profile=profile,
            standby=standby,
            headless=headless_env,
        )

        self.kernel_browser_response = browser_response
        self.browser = browser
        self.context = context
        self.current_page = page

        # Optional: configure sensible default timeouts
        try:
            self.current_page.set_default_timeout(60000)
            self.current_page.set_default_navigation_timeout(90000)
        except Exception:
            pass

        # Navigate to the website with robust fallbacks
        try:
            await self.current_page.goto(website_url, wait_until="domcontentloaded", timeout=45000)
        except Exception as e1:
            print(f"⚠️ DOMContentLoaded timed out: {e1}. Retrying with 'load'...")
            try:
                await self.current_page.goto(website_url, wait_until="load", timeout=60000)
            except Exception as e2:
                print(f"⚠️ Load timed out: {e2}. Retrying with 'commit'...")
                try:
                    await self.current_page.goto(website_url, wait_until="commit", timeout=30000)
                except Exception as e3:
                    print(f"⚠️ Navigation still timing out: {e3}. Continuing best-effort.")

        try:
            await self.current_page.wait_for_selector("body", timeout=10000)
        except Exception:
            pass
        await self.current_page.wait_for_timeout(2000)

        # Advanced analysis and optional baseline checks
        try:
            await self._analyze_page_characteristics()
        except Exception as e:
            print(f"⚠️ Page analysis failed: {e}")

        if auto_check:
            try:
                summary = await self._run_auto_checks()
                print(summary)
            except Exception as e:
                print(f"⚠️ Auto-checks failed: {e}")

        # Show Kernel live URLs for convenience
        try:
            # First try the official browser_live_view_url field
            live_view_url = kernel_client.get_live_view_url(browser_response)
            
            # If not found, construct authenticated URL from CDP JWT
            if not live_view_url:
                cdp_url = kernel_client.get_cdp_url(browser_response)
                if cdp_url and "jwt=" in cdp_url:
                    try:
                        # Extract the full JWT token from CDP URL
                        jwt_token = cdp_url.split("jwt=")[-1]
                        
                        # Decode to get session info
                        payload = jwt_token.split(".")[1]
                        padding = 4 - len(payload) % 4
                        if padding != 4:
                            payload += "=" * padding
                        decoded = base64.urlsafe_b64decode(payload)
                        session_data = json.loads(decoded).get("session", {})
                        
                        # Get session ID and construct Live View URL
                        session_id = session_data.get("id")
                        if session_id:
                            # Use the official Live View URL pattern from docs
                            live_view_url = f"https://live.onkernel.app/session/{session_id}"
                            print(f"🔴 Live View (session): {live_view_url}")
                    except Exception as e:
                        print(f"⚠️ Could not construct Live View URL: {e}")
            
            if live_view_url:
                print(f"🔴 Live View: {live_view_url}")
                # Save URL for manual access
                try:
                    with open("kernel_live_view_url.txt", "w", encoding="utf-8") as f:
                        f.write(live_view_url + "\n")
                    print("📝 Live View URL saved to kernel_live_view_url.txt")
                except Exception:
                    pass
                # Auto-open Live View so the run is visible in a browser immediately
                opened = False
                try:
                    opened = webbrowser.open(live_view_url, new=2)
                except Exception:
                    opened = False
                if not opened:
                    # Fallbacks per OS
                    try:
                        system = platform.system().lower()
                        if "windows" in system:
                            subprocess.Popen(["start", "", live_view_url], shell=True)
                            opened = True
                        elif "darwin" in system:
                            subprocess.Popen(["open", live_view_url])
                            opened = True
                        else:
                            subprocess.Popen(["xdg-open", live_view_url])
                            opened = True
                    except Exception:
                        pass
                if opened:
                    print("✅ Live View opened in browser!")
                    print("🔐 If you see a login page, use your Kernel account credentials:")
                    print("   📧 Email: Your Kernel dashboard email")
                    print("   🔑 Password: Your Kernel dashboard password")
                    print("   🌐 Same credentials you use at https://www.onkernel.com/")
                    print("   💡 This is required to access the Live View stream")
                else:
                    print("🔗 Could not auto-open Live View. URL saved to kernel_live_view_url.txt")
            else:
                print("⚠️ No Live View URL found - check Kernel API response")
            
            replay_url = kernel_client.get_replay_url(browser_response)
            if replay_url:
                print(f"🎞️ Replay: {replay_url}")
        except Exception as e:
            print(f"⚠️ Error extracting Kernel URLs: {e}")

        self.current_url = website_url
        print("✅ Agent ready on Kernel! I can understand natural language commands.")
        print()
        print("💬 Try commands like: log in, sign up, search for python, auto check, report")
        return True

    async def close_session(self):
        """Close the Kernel browser session cleanly."""
        try:
            if self.kernel_run_id is not None:
                await disconnect_kernel_browser(self.kernel_run_id)
        except Exception as e:
            print(f"⚠️ Kernel session cleanup error: {e}")
        finally:
            self.kernel_run_id = None
            self.kernel_browser_response = None
            self.current_page = None
            self.context = None
            self.browser = None
            print("🧹 Kernel session closed!")


async def main():
    """Main interactive loop using Kernel backend."""
    print("🤖 Multi-AI QA Agent (Kernel)")
    print("=" * 25)
    print("Choose AI provider:")
    print("1. OpenAI (GPT-3.5)")
    print("2. Anthropic (Claude)")
    print("3. Google (Gemini)")
    print("4. No AI (Basic processing)")

    # Auto-select Google Gemini for testing parity with original script
    choice = "3"
    print(f"Auto-selecting: {choice} (Google Gemini)")

    ai_provider = "openai"
    api_key = None

    if choice == "1":
        ai_provider = "openai"
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            api_key = input("Enter your OpenAI API key: ").strip()
    elif choice == "2":
        ai_provider = "anthropic"
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            api_key = input("Enter your Anthropic API key: ").strip()
    elif choice == "3":
        ai_provider = "google"
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            api_key = input("Enter your Google API key: ").strip()
    else:
        ai_provider = "none"

    agent = OnKernelMultiAIQAAgent(ai_provider, api_key)

    try:
        start_url = sys.argv[1] if len(sys.argv) > 1 else os.getenv("START_URL", "https://www.youtube.com/")
        await agent.start_session(start_url)

        print("💬 Enter your commands (type 'quit' to exit):")
        while True:
            user_input = input("\n🤖 You: ").strip()
            if user_input.lower() in ["quit", "exit", "bye", "goodbye"]:
                print("👋 Goodbye!")
                break
            if not user_input:
                continue
            result = await agent.process_command(user_input)
            print(f"🤖 Agent: {result}")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await agent.close_session()


if __name__ == "__main__":
    asyncio.run(main())


