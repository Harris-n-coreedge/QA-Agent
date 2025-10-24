"""
Kernel client wrapper for browsers-as-a-service integration.

Uses Kernel's Python SDK to create browsers quickly and at scale. 
Kernel returns a cdp_ws_url to connect Playwright over CDP.

Relevant Kernel features:
- Headless mode, Stealth mode
- Standby mode (fast next-run), Persistence (reuse sessions, cookies)
- Live View (debug, human-in-the-loop), Replays (video review)
"""
from kernel import Kernel
from typing import Dict, Any, Optional, List
import asyncio
from uuid import UUID
import inspect

from qa_agent.core.config import settings
from qa_agent.core.logging import get_logger

logger = get_logger(__name__)


class KernelClient:
    """Wrapper for Kernel API client with advanced browser management."""
    
    def __init__(self):
        self.client = Kernel(api_key=settings.KERNEL_API_KEY)
        self.active_browsers: Dict[str, Dict[str, Any]] = {}
        self.browser_profiles: Dict[str, Dict[str, Any]] = {}
    
    async def create_browser(
        self,
        stealth: bool = None,
        profile: Optional[str] = None,
        standby: bool = False,
        headless: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new browser instance with Kernel's advanced features.
        
        Args:
            stealth: Enable stealth mode (anti-detection)
            profile: Persistable profile name for session reuse
            standby: Enable standby mode for fast next-run
            headless: Run in headless mode
            **kwargs: Additional Kernel browser options
        """
        if stealth is None:
            stealth = settings.DEFAULT_STEALTH
        
        browser_config = {
            "stealth": stealth,
            "standby": standby,
            "headless": headless,
            **kwargs
        }
        
        if profile:
            browser_config["profile"] = profile
            logger.info("Using persistent profile", profile=profile)
        
        try:
            logger.info("Creating Kernel browser", config=browser_config)
            response = await self._create_browser_via_compat(browser_config)
            
            browser_id = response.get("id")
            if browser_id:
                self.active_browsers[browser_id] = response
                
                # Store profile info if provided
                if profile:
                    self.browser_profiles[profile] = {
                        "browser_id": browser_id,
                        "last_used": asyncio.get_event_loop().time(),
                        "config": browser_config
                    }
                
                logger.info(
                    "Browser created successfully", 
                    browser_id=browser_id,
                    cdp_url=self.get_cdp_url(response),
                    live_view_url=self.get_live_view_url(response)
                )
            
            return response
            
        except Exception as e:
            logger.error("Failed to create browser", error=str(e))
            raise
    
    async def terminate_browser(self, browser_id: str) -> None:
        """
        Terminate a browser instance with defensive cleanup.
        
        Implements defensive cleanup of Kernel browsers when runs finish or time out.
        """
        try:
            logger.info("Terminating browser", browser_id=browser_id)
            await self._terminate_browser_via_compat(browser_id)
            
            # Remove from active browsers
            if browser_id in self.active_browsers:
                del self.active_browsers[browser_id]
            
            # Clean up profile references
            for profile_name, profile_info in list(self.browser_profiles.items()):
                if profile_info.get("browser_id") == browser_id:
                    del self.browser_profiles[profile_name]
            
            logger.info("Browser terminated successfully", browser_id=browser_id)
            
        except Exception as e:
            logger.error("Failed to terminate browser", browser_id=browser_id, error=str(e))
            raise
    
    async def create_or_reuse_browser(
        self,
        profile: Optional[str] = None,
        stealth: bool = None,
        standby: bool = True,
        headless: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a new browser or reuse existing one with profile persistence.
        
        Args:
            profile: Profile name for session persistence
            stealth: Enable stealth mode
            standby: Enable standby mode for fast reuse
        """
        if profile and profile in self.browser_profiles:
            # Try to reuse existing browser
            profile_info = self.browser_profiles[profile]
            browser_id = profile_info["browser_id"]
            
            if browser_id in self.active_browsers:
                logger.info("Reusing existing browser", browser_id=browser_id, profile=profile)
                return self.active_browsers[browser_id]
        
        # Create new browser
        return await self.create_browser(
            stealth=stealth,
            profile=profile,
            standby=standby,
            headless=headless,
        )
    
    def get_profile_info(self, profile: str) -> Optional[Dict[str, Any]]:
        """Get information about a browser profile."""
        return self.browser_profiles.get(profile)
    
    def list_profiles(self) -> List[str]:
        """List all available browser profiles."""
        return list(self.browser_profiles.keys())
    
    async def get_browser_info(self, browser_id: str) -> Optional[Dict[str, Any]]:
        """Get browser information."""
        try:
            return await self.client.browsers.get(browser_id)
        except Exception as e:
            logger.error("Failed to get browser info", browser_id=browser_id, error=str(e))
            return None
    
    async def list_browsers(self) -> list:
        """List all browsers."""
        try:
            response = await self.client.browsers.list()
            return response.get("browsers", [])
        except Exception as e:
            logger.error("Failed to list browsers", error=str(e))
            return []
    
    def get_cdp_url(self, browser_response: Dict[str, Any]) -> str:
        """
        Extract CDP WebSocket URL from browser response.
        
        This is the key URL for Playwright to connect over CDP to remote Kernel browsers.
        """
        # Try common keys for CDP WebSocket endpoint across SDKs/vendors
        for key in (
            "cdp_ws_url",
            "cdpUrl",
            "cdp_url",
            "webSocketDebuggerUrl",
            "websocketDebuggerUrl",
            "ws_url",
            "wsEndpoint",
            "cdp",
        ):
            url = browser_response.get(key)
            if url:
                return url
        return ""
    
    def get_live_view_url(self, browser_response: Dict[str, Any]) -> str:
        """
        Extract Live View URL from browser response.
        
        Provides debug, human-in-the-loop capabilities during runs.
        """
        # Try multiple common keys across SDK variants
        for key in (
            "browser_live_view_url",  # Official Kernel SDK field
            "live_view_url",
            "liveview_url",
            "live_url",
            "liveViewUrl",
            "liveViewURL",
            "browserLiveViewUrl",
        ):
            url = browser_response.get(key)
            if url:
                return url
        return ""
    
    def get_replay_url(self, browser_response: Dict[str, Any]) -> str:
        """
        Extract replay URL from browser response.
        
        Provides video review capabilities after runs complete.
        """
        for key in ("replay_url", "replayUrl", "recording_url", "recordingUrl", "video_url"):
            url = browser_response.get(key)
            if url:
                return url
        return ""
    
    def get_browser_urls(self, browser_response: Dict[str, Any]) -> Dict[str, str]:
        """Get all URLs from browser response."""
        return {
            "cdp_ws_url": self.get_cdp_url(browser_response),
            "live_view_url": self.get_live_view_url(browser_response),
            "replay_url": self.get_replay_url(browser_response)
        }
    
    async def cleanup_all_browsers(self) -> None:
        """Cleanup all active browsers."""
        for browser_id in list(self.active_browsers.keys()):
            try:
                await self.terminate_browser(browser_id)
            except Exception as e:
                logger.error("Failed to cleanup browser", browser_id=browser_id, error=str(e))

    async def _maybe_await(self, value):
        """Await value if it's awaitable; otherwise return it."""
        if inspect.isawaitable(value):
            return await value
        return value

    async def _create_browser_via_compat(self, browser_config: Dict[str, Any]) -> Dict[str, Any]:
        """Call Kernel browsers.create with compatible signatures across SDK versions."""
        attempts = [
            lambda: self.client.browsers.create(config=browser_config),
            lambda: self.client.browsers.create(json=browser_config),
            lambda: self.client.browsers.create(data=browser_config),
            lambda: self.client.browsers.create(**browser_config),
            lambda: self.client.browsers.create(),
        ]
        last_error: Optional[Exception] = None
        for fn in attempts:
            try:
                result = fn()
                result = await self._maybe_await(result)
                if isinstance(result, dict) and result:
                    return result
                # Some SDKs may return objects; try to coerce to dict
                if hasattr(result, "__dict__"):
                    return dict(result.__dict__)
                if result:
                    return result
            except TypeError as e:
                last_error = e
                continue
            except Exception as e:
                last_error = e
                continue
        if last_error:
            raise last_error
        raise RuntimeError("Kernel browsers.create returned no result")

    async def _terminate_browser_via_compat(self, browser_id: str) -> None:
        """Call Kernel to terminate/delete/close a browser across SDK variants."""
        attempts = [
            lambda: self.client.browsers.terminate(browser_id),
            lambda: self.client.browsers.terminate(id=browser_id),
            lambda: self.client.browsers.delete(browser_id),
            lambda: self.client.browsers.delete(id=browser_id),
            lambda: self.client.browsers.close(browser_id),
            lambda: self.client.browsers.close(id=browser_id),
        ]
        last_error: Optional[Exception] = None
        for fn in attempts:
            try:
                result = fn()
                await self._maybe_await(result)
                return
            except AttributeError as e:
                last_error = e
                continue
            except TypeError as e:
                last_error = e
                continue
            except Exception as e:
                last_error = e
                continue
        if last_error:
            raise last_error


# Global kernel client instance
kernel_client = KernelClient()
