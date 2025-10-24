"""
Simulation Engine

Orchestrates a run with a flow using Kernel browsers via CDP.
Implements comprehensive instrumentation for event capture, DOM hooks, network, console.
Emits SessionEvent objects with timestamps, run/step correlation, and payload.
Respects safety & anti-detection policies (delays, realistic typing, randomization).
"""
from typing import Dict, Any, List, Optional, Callable
from uuid import UUID
import asyncio
import time

from qa_agent.kernel.browser import connect_kernel_browser, disconnect_kernel_browser
from qa_agent.simulation.instrumentation import InstrumentationManager
from qa_agent.simulation.policies import PolicyManager
from qa_agent.simulation.selectors import SelectorManager
from qa_agent.visibility.events import SessionEvent, event_storage
from qa_agent.core.logging import get_logger

logger = get_logger(__name__)


class SimulationEngine:
    """
    Orchestrates simulation runs with flows.
    
    Responsibilities:
    - Connect to Kernel browser via Playwright CDP
    - Navigate through steps in a flow (compiled from DSL) with robust selectors and retries
    - Instrumentation for navigation lifecycle, network, console, DOM events, custom injected script
    - Emit SessionEvent objects with timestamps, run/step correlation, and payload
    - Respect safety & anti-detection policies (delays, realistic typing, randomization)
    """
    
    def __init__(self):
        self.instrumentation = InstrumentationManager()
        self.policies = PolicyManager()
        self.selectors = SelectorManager()
        self.event_handlers: List[Callable] = []
    
    def add_event_handler(self, handler: Callable) -> None:
        """Add an event handler for SessionEvent emission."""
        self.event_handlers.append(handler)
    
    async def emit_session_event(
        self,
        run_id: UUID,
        event_type: str,
        payload: Dict[str, Any],
        step_id: Optional[UUID] = None
    ) -> None:
        """Emit a SessionEvent and notify handlers."""
        event = SessionEvent(
            run_id=run_id,
            event_type=event_type,
            timestamp=time.time(),
            payload=payload,
            step_id=step_id
        )
        
        # Store event
        await event_storage.store_event(event)
        
        # Notify handlers
        for handler in self.event_handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error("Error in event handler", error=str(e))
    
    async def execute_run(
        self,
        run_id: UUID,
        flow_dsl: Dict[str, Any],
        target_url: str,
        profile: str = None,
        stealth: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a complete simulation run with comprehensive instrumentation.
        
        Key data flows:
        - API schedules runs → Worker spins up Kernel browser → Playwright connects over CDP
        - Simulation executes + instrumentation → events streamed to API (WS) and persisted
        - Friction analysis computed → results exposed via API
        """
        browser = None
        context = None
        page = None
        browser_response = None
        
        try:
            logger.info("Starting simulation run", run_id=str(run_id))
            
            # Emit run start event
            await self.emit_session_event(
                run_id=run_id,
                event_type="run_start",
                payload={
                    "flow_name": flow_dsl.get("name", "unknown"),
                    "target_url": target_url,
                    "profile": profile,
                    "stealth": stealth
                }
            )
            
            # Connect to Kernel browser via CDP
            browser, context, page, browser_response = await connect_kernel_browser(
                run_id=run_id,
                profile=profile,
                stealth=stealth,
                standby=True
            )
            
            # Emit browser connection event
            await self.emit_session_event(
                run_id=run_id,
                event_type="browser_connected",
                payload={
                    "browser_id": browser_response.get("id"),
                    "cdp_url": browser_response.get("cdp_ws_url"),
                    "live_view_url": browser_response.get("live_view_url")
                }
            )
            
            # Setup comprehensive instrumentation
            await self.instrumentation.setup_instrumentation(page, run_id)
            
            # Navigate to target with lifecycle events
            await self._navigate_with_events(page, target_url, run_id)
            
            # Execute flow steps with instrumentation
            results = await self._execute_flow_steps(page, flow_dsl, run_id)
            
            # Emit run completion event
            await self.emit_session_event(
                run_id=run_id,
                event_type="run_completed",
                payload={
                    "total_steps": len(results),
                    "successful_steps": len([r for r in results if r.get("status") == "completed"]),
                    "failed_steps": len([r for r in results if r.get("status") == "failed"])
                }
            )
            
            logger.info("Simulation run completed", run_id=str(run_id))
            
            return {
                "status": "completed",
                "results": results,
                "browser_info": browser_response,
                "total_events": len(await event_storage.get_events_for_run(run_id))
            }
            
        except Exception as e:
            logger.error("Simulation run failed", run_id=str(run_id), error=str(e))
            
            # Emit run failure event
            await self.emit_session_event(
                run_id=run_id,
                event_type="run_failed",
                payload={
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            
            return {
                "status": "failed",
                "error": str(e),
                "browser_info": browser_response
            }
            
        finally:
            # Cleanup with defensive termination
            if run_id:
                await disconnect_kernel_browser(run_id)
                
                # Emit cleanup event
                await self.emit_session_event(
                    run_id=run_id,
                    event_type="browser_disconnected",
                    payload={"cleanup_completed": True}
                )
    
    async def _navigate_with_events(self, page, url: str, run_id: UUID) -> None:
        """Navigate to URL with comprehensive lifecycle event tracking."""
        await self.emit_session_event(
            run_id=run_id,
            event_type="navigation_start",
            payload={"url": url}
        )
        
        try:
            await page.goto(url, wait_until="domcontentloaded")
            
            await self.emit_session_event(
                run_id=run_id,
                event_type="navigation_complete",
                payload={
                    "url": url,
                    "final_url": page.url,
                    "title": await page.title()
                }
            )
            
        except Exception as e:
            await self.emit_session_event(
                run_id=run_id,
                event_type="navigation_error",
                payload={
                    "url": url,
                    "error": str(e)
                }
            )
            raise
    
    async def _execute_flow_steps(
        self,
        page,
        flow_dsl: Dict[str, Any],
        run_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Execute individual flow steps with comprehensive instrumentation.
        
        Each step includes:
        - Step start/complete events
        - Robust selectors with retries
        - Policy application (delays, realistic typing, randomization)
        - Error handling and recovery
        """
        steps = flow_dsl.get("steps", [])
        results = []
        
        for i, step in enumerate(steps):
            step_id = UUID()  # Generate unique step ID
            
            try:
                logger.info("Executing step", run_id=str(run_id), step_index=i, step_type=step.get("type"))
                
                # Emit step start event
                await self.emit_session_event(
                    run_id=run_id,
                    event_type="step_start",
                    payload={
                        "step_index": i,
                        "step_type": step.get("type"),
                        "selector": step.get("selector"),
                        "text": step.get("text"),
                        "url": step.get("url")
                    },
                    step_id=step_id
                )
                
                # Execute step with retries
                result = await self._execute_step_with_retries(page, step, run_id, i, step_id)
                results.append(result)
                
                # Emit step completion event
                await self.emit_session_event(
                    run_id=run_id,
                    event_type="step_complete",
                    payload={
                        "step_index": i,
                        "status": result.get("status"),
                        "duration": result.get("duration", 0)
                    },
                    step_id=step_id
                )
                
                # Apply policies (delays, realistic typing, randomization)
                await self.policies.apply_step_policies(step)
                
            except Exception as e:
                logger.error("Step execution failed", run_id=str(run_id), step_index=i, error=str(e))
                
                # Emit step failure event
                await self.emit_session_event(
                    run_id=run_id,
                    event_type="step_failed",
                    payload={
                        "step_index": i,
                        "error": str(e),
                        "error_type": type(e).__name__
                    },
                    step_id=step_id
                )
                
                results.append({
                    "step_index": i,
                    "status": "failed",
                    "error": str(e),
                    "step_id": str(step_id)
                })
        
        return results
    
    async def _execute_step_with_retries(
        self,
        page,
        step: Dict[str, Any],
        run_id: UUID,
        step_index: int,
        step_id: UUID
    ) -> Dict[str, Any]:
        """
        Execute a single step with retries and comprehensive instrumentation.
        
        Implements robust selectors and retries as specified in the plan.
        """
        start_time = time.time()
        step_type = step.get("type")
        retry_attempts = self.policies.get_retry_attempts(step)
        
        for attempt in range(retry_attempts):
            try:
                result = await self._execute_step(page, step, run_id, step_index, step_id)
                result["duration"] = time.time() - start_time
                result["attempts"] = attempt + 1
                result["step_id"] = str(step_id)
                return result
                
            except Exception as e:
                if attempt < retry_attempts - 1:
                    logger.warning(
                        "Step attempt failed, retrying",
                        run_id=str(run_id),
                        step_index=step_index,
                        attempt=attempt + 1,
                        error=str(e)
                    )
                    
                    # Wait before retry
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                else:
                    raise
    
    async def _execute_step(
        self,
        page,
        step: Dict[str, Any],
        run_id: UUID,
        step_index: int,
        step_id: UUID
    ) -> Dict[str, Any]:
        """
        Execute a single step with comprehensive instrumentation.
        
        Supports all step types with proper event emission and error handling.
        """
        step_type = step.get("type")
        selector = step.get("selector")
        
        # Emit step action event
        await self.emit_session_event(
            run_id=run_id,
            event_type="step_action",
            payload={
                "step_type": step_type,
                "selector": selector,
                "text": step.get("text"),
                "url": step.get("url")
            },
            step_id=step_id
        )
        
        if step_type == "click":
            element = await self.selectors.find_element(page, selector)
            await element.click()
            
            # Emit click event
            await self.emit_session_event(
                run_id=run_id,
                event_type="element_clicked",
                payload={
                    "selector": selector,
                    "element_info": await self.selectors.get_element_info(page, selector)
                },
                step_id=step_id
            )
            
        elif step_type == "type":
            element = await self.selectors.find_element(page, selector)
            text = step.get("text", "")
            
            # Apply realistic typing policy
            await self.policies.apply_typing_policy(text)
            await element.fill(text)
            
            # Emit typing event
            await self.emit_session_event(
                run_id=run_id,
                event_type="text_typed",
                payload={
                    "selector": selector,
                    "text_length": len(text),
                    "text_preview": text[:50] + "..." if len(text) > 50 else text
                },
                step_id=step_id
            )
            
        elif step_type == "wait":
            timeout = step.get("timeout", 5000)
            await page.wait_for_timeout(timeout)
            
            # Emit wait event
            await self.emit_session_event(
                run_id=run_id,
                event_type="wait_completed",
                payload={"timeout": timeout},
                step_id=step_id
            )
            
        elif step_type == "navigate":
            url = step.get("url")
            await self._navigate_with_events(page, url, run_id)
            
        elif step_type == "assert":
            # Implement assertions with event emission
            await self._execute_assertion(page, step, run_id, step_id)
            
        elif step_type == "scroll":
            # Implement scrolling
            direction = step.get("direction", "down")
            amount = step.get("amount", 500)
            
            if direction == "down":
                await page.evaluate(f"window.scrollBy(0, {amount})")
            elif direction == "up":
                await page.evaluate(f"window.scrollBy(0, -{amount})")
            
            # Emit scroll event
            await self.emit_session_event(
                run_id=run_id,
                event_type="page_scrolled",
                payload={
                    "direction": direction,
                    "amount": amount
                },
                step_id=step_id
            )
        
        return {
            "step_index": step_index,
            "step_type": step_type,
            "status": "completed",
            "step_id": str(step_id)
        }
    
    async def _execute_assertion(
        self,
        page,
        step: Dict[str, Any],
        run_id: UUID,
        step_id: UUID
    ) -> None:
        """Execute assertion step with comprehensive validation."""
        expect = step.get("expect", {})
        
        if "url_contains" in expect:
            expected_url = expect["url_contains"]
            current_url = page.url
            
            if expected_url not in current_url:
                raise AssertionError(f"URL assertion failed: expected '{expected_url}' in '{current_url}'")
            
            # Emit assertion success event
            await self.emit_session_event(
                run_id=run_id,
                event_type="assertion_passed",
                payload={
                    "assertion_type": "url_contains",
                    "expected": expected_url,
                    "actual": current_url
                },
                step_id=step_id
            )
        
        elif "text_present" in expect:
            expected_text = expect["text_present"]
            page_text = await page.text_content("body")
            
            if expected_text not in page_text:
                raise AssertionError(f"Text assertion failed: expected '{expected_text}' not found")
            
            # Emit assertion success event
            await self.emit_session_event(
                run_id=run_id,
                event_type="assertion_passed",
                payload={
                    "assertion_type": "text_present",
                    "expected": expected_text
                },
                step_id=step_id
            )
        
        elif "element_visible" in expect:
            selector = expect["element_visible"]
            is_visible = await self.selectors.is_element_visible(page, selector)
            
            if not is_visible:
                raise AssertionError(f"Element visibility assertion failed: '{selector}' not visible")
            
            # Emit assertion success event
            await self.emit_session_event(
                run_id=run_id,
                event_type="assertion_passed",
                payload={
                    "assertion_type": "element_visible",
                    "selector": selector
                },
                step_id=step_id
            )


# Global simulation engine
simulation_engine = SimulationEngine()
