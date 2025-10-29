"""
Flow DSL Execution Engine

Integrates with the DSL compiler to execute flows with comprehensive step processing,
fallback selectors, and robust error handling.
"""
from typing import Dict, Any, List, Optional, Union
from uuid import UUID
import asyncio
import time
import json

from playwright.async_api import Page, Locator
from qa_agent.generation.dsl import FlowDSL, FlowStep, StepType, flow_compiler
from qa_agent.simulation.selectors import SelectorManager
from qa_agent.simulation.policies import PolicyManager
from qa_agent.core.logging import get_logger

logger = get_logger(__name__)


class FlowExecutor:
    """
    Executes compiled Flow DSL with comprehensive step processing.
    
    Features:
    - Robust selector handling with fallbacks
    - Pre/post condition validation
    - Comprehensive error handling and retries
    - Step-by-step instrumentation
    - Policy enforcement (delays, realistic typing, randomization)
    """
    
    def __init__(self):
        self.selector_manager = SelectorManager()
        self.policy_manager = PolicyManager()
        self.compiled_flows: Dict[str, FlowDSL] = {}
    
    async def execute_flow(
        self,
        page: Page,
        flow_dsl: FlowDSL,
        run_id: UUID,
        step_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Execute a compiled Flow DSL with comprehensive instrumentation.
        
        Args:
            page: Playwright page instance
            flow_dsl: Compiled Flow DSL
            run_id: Unique run identifier
            step_callback: Optional callback for step events
        
        Returns:
            Execution results with step outcomes and metrics
        """
        logger.info("Starting flow execution", flow_name=flow_dsl.name, run_id=str(run_id))
        
        start_time = time.time()
        results = {
            "flow_name": flow_dsl.name,
            "flow_version": flow_dsl.version,
            "start_time": start_time,
            "steps": [],
            "status": "running",
            "error": None
        }
        
        try:
            # Navigate to start URL if provided
            if flow_dsl.start_url:
                await self._navigate_to_start_url(page, flow_dsl.start_url, run_id)
            
            # Execute each step with comprehensive handling
            for i, step in enumerate(flow_dsl.steps):
                step_result = await self._execute_step(
                    page, step, i, run_id, flow_dsl.policies, step_callback
                )
                results["steps"].append(step_result)
                
                # Check if step failed critically
                if step_result["status"] == "failed" and not step_result.get("retryable", True):
                    results["status"] = "failed"
                    results["error"] = step_result["error"]
                    break
            
            # Mark as completed if all steps succeeded
            if results["status"] == "running":
                results["status"] = "completed"
            
        except Exception as e:
            logger.error("Flow execution failed", error=str(e), run_id=str(run_id))
            results["status"] = "failed"
            results["error"] = str(e)
        
        results["end_time"] = time.time()
        results["duration"] = results["end_time"] - results["start_time"]
        
        logger.info("Flow execution completed", 
                   flow_name=flow_dsl.name, 
                   status=results["status"],
                   duration=results["duration"],
                   run_id=str(run_id))
        
        return results
    
    async def _navigate_to_start_url(self, page: Page, url: str, run_id: UUID) -> None:
        """Navigate to the flow's start URL."""
        logger.info("Navigating to start URL", url=url, run_id=str(run_id))
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            logger.info("Navigation completed", url=url, run_id=str(run_id))
        except Exception as e:
            logger.error("Navigation failed", url=url, error=str(e), run_id=str(run_id))
            raise
    
    async def _execute_step(
        self,
        page: Page,
        step: FlowStep,
        step_index: int,
        run_id: UUID,
        policies: Any,
        step_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Execute a single step with comprehensive error handling and retries.
        
        Features:
        - Pre/post condition validation
        - Fallback selector handling
        - Retry logic with exponential backoff
        - Policy enforcement
        - Comprehensive instrumentation
        """
        step_start_time = time.time()
        
        step_result = {
            "step_index": step_index,
            "step_type": step.type.value,
            "status": "pending",
            "start_time": step_start_time,
            "attempts": 0,
            "error": None,
            "retryable": True,
            "fallback_used": None,
            "pre_conditions_passed": True,
            "post_conditions_passed": True
        }
        
        # Validate pre-conditions
        if step.pre_conditions:
            pre_condition_result = await self._validate_conditions(
                page, step.pre_conditions, "pre", step_index, run_id
            )
            step_result["pre_conditions_passed"] = pre_condition_result["passed"]
            
            if not pre_condition_result["passed"]:
                step_result["status"] = "failed"
                step_result["error"] = f"Pre-conditions failed: {pre_condition_result['error']}"
                step_result["retryable"] = False
                return step_result
        
        # Execute step with retries
        retry_attempts = step.retry_attempts or policies.retry_attempts
        last_error = None
        
        for attempt in range(retry_attempts):
            step_result["attempts"] = attempt + 1
            
            try:
                # Execute the step
                await self._execute_step_action(page, step, step_index, run_id, step_result)
                
                # Validate post-conditions
                if step.post_conditions:
                    post_condition_result = await self._validate_conditions(
                        page, step.post_conditions, "post", step_index, run_id
                    )
                    step_result["post_conditions_passed"] = post_condition_result["passed"]
                    
                    if not post_condition_result["passed"]:
                        raise Exception(f"Post-conditions failed: {post_condition_result['error']}")
                
                # Step completed successfully
                step_result["status"] = "completed"
                step_result["end_time"] = time.time()
                step_result["duration"] = step_result["end_time"] - step_result["start_time"]
                
                # Apply policies (delays, realistic typing, randomization)
                await self.policy_manager.apply_step_policies(step)
                
                # Call step callback if provided
                if step_callback:
                    await step_callback(step_result)
                
                logger.info("Step completed successfully", 
                           step_index=step_index, 
                           step_type=step.type.value,
                           attempts=attempt + 1,
                           run_id=str(run_id))
                
                return step_result
                
            except Exception as e:
                last_error = e
                step_result["error"] = str(e)
                
                logger.warning("Step attempt failed", 
                              step_index=step_index, 
                              step_type=step.type.value,
                              attempt=attempt + 1,
                              error=str(e),
                              run_id=str(run_id))
                
                # Wait before retry (exponential backoff)
                if attempt < retry_attempts - 1:
                    wait_time = min(2 ** attempt, 10)  # Cap at 10 seconds
                    await asyncio.sleep(wait_time)
        
        # All retries exhausted
        step_result["status"] = "failed"
        step_result["end_time"] = time.time()
        step_result["duration"] = step_result["end_time"] - step_result["start_time"]
        
        logger.error("Step failed after all retries", 
                    step_index=step_index, 
                    step_type=step.type.value,
                    attempts=retry_attempts,
                    error=str(last_error),
                    run_id=str(run_id))
        
        return step_result
    
    async def _execute_step_action(
        self,
        page: Page,
        step: FlowStep,
        step_index: int,
        run_id: UUID,
        step_result: Dict[str, Any]
    ) -> None:
        """Execute the actual step action based on step type."""
        
        if step.type == StepType.CLICK:
            await self._execute_click(page, step, step_result)
            
        elif step.type == StepType.TYPE:
            await self._execute_type(page, step, step_result)
            
        elif step.type == StepType.WAIT:
            await self._execute_wait(page, step, step_result)
            
        elif step.type == StepType.NAVIGATE:
            await self._execute_navigate(page, step, step_result)
            
        elif step.type == StepType.ASSERT:
            await self._execute_assert(page, step, step_result)
            
        elif step.type == StepType.SCROLL:
            await self._execute_scroll(page, step, step_result)
            
        elif step.type == StepType.HOVER:
            await self._execute_hover(page, step, step_result)
            
        elif step.type == StepType.SELECT:
            await self._execute_select(page, step, step_result)
            
        elif step.type == StepType.UPLOAD:
            await self._execute_upload(page, step, step_result)
            
        elif step.type == StepType.DOWNLOAD:
            await self._execute_download(page, step, step_result)
            
        elif step.type == StepType.SWITCH_TAB:
            await self._execute_switch_tab(page, step, step_result)
            
        elif step.type == StepType.CLOSE_TAB:
            await self._execute_close_tab(page, step, step_result)
            
        elif step.type == StepType.EXECUTE_SCRIPT:
            await self._execute_script(page, step, step_result)
            
        else:
            raise ValueError(f"Unsupported step type: {step.type}")
    
    async def _execute_click(self, page: Page, step: FlowStep, step_result: Dict[str, Any]) -> None:
        """Execute click step with fallback selectors."""
        element = await self._find_element_with_fallbacks(page, step, step_result)
        await element.click()
        
        logger.debug("Element clicked", selector=step.selector, run_id=str(step_result.get("run_id")))
    
    async def _execute_type(self, page: Page, step: FlowStep, step_result: Dict[str, Any]) -> None:
        """Execute type step with realistic typing."""
        element = await self._find_element_with_fallbacks(page, step, step_result)
        
        # Apply realistic typing policy
        text = step.text or ""
        await self.policy_manager.apply_typing_policy(text)
        await element.fill(text)
        
        logger.debug("Text typed", 
                    selector=step.selector, 
                    text_length=len(text),
                    run_id=str(step_result.get("run_id")))
    
    async def _execute_wait(self, page: Page, step: FlowStep, step_result: Dict[str, Any]) -> None:
        """Execute wait step."""
        timeout = step.timeout or 5000
        await page.wait_for_timeout(timeout)
        
        logger.debug("Wait completed", timeout=timeout, run_id=str(step_result.get("run_id")))
    
    async def _execute_navigate(self, page: Page, step: FlowStep, step_result: Dict[str, Any]) -> None:
        """Execute navigate step."""
        url = step.url
        if not url:
            raise ValueError("Navigate step requires URL")
        
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        
        logger.debug("Navigation completed", url=url, run_id=str(step_result.get("run_id")))
    
    async def _execute_assert(self, page: Page, step: FlowStep, step_result: Dict[str, Any]) -> None:
        """Execute assertion step."""
        expect = step.expect or {}
        
        if "url_contains" in expect:
            expected_url = expect["url_contains"]
            current_url = page.url
            
            if expected_url not in current_url:
                raise AssertionError(f"URL assertion failed: expected '{expected_url}' in '{current_url}'")
        
        elif "text_present" in expect:
            expected_text = expect["text_present"]
            page_text = await page.text_content("body")
            
            if expected_text not in page_text:
                raise AssertionError(f"Text assertion failed: expected '{expected_text}' not found")
        
        elif "element_visible" in expect:
            selector = expect["element_visible"]
            is_visible = await self.selector_manager.is_element_visible(page, selector)
            
            if not is_visible:
                raise AssertionError(f"Element visibility assertion failed: '{selector}' not visible")
        
        else:
            raise ValueError("Assert step requires valid expect conditions")
        
        logger.debug("Assertion passed", expect=expect, run_id=str(step_result.get("run_id")))
    
    async def _execute_scroll(self, page: Page, step: FlowStep, step_result: Dict[str, Any]) -> None:
        """Execute scroll step."""
        direction = step.direction or "down"
        amount = step.amount or 500
        
        if direction == "down":
            await page.evaluate(f"window.scrollBy(0, {amount})")
        elif direction == "up":
            await page.evaluate(f"window.scrollBy(0, -{amount})")
        elif direction == "left":
            await page.evaluate(f"window.scrollBy(-{amount}, 0)")
        elif direction == "right":
            await page.evaluate(f"window.scrollBy({amount}, 0)")
        
        logger.debug("Page scrolled", direction=direction, amount=amount, run_id=str(step_result.get("run_id")))
    
    async def _execute_hover(self, page: Page, step: FlowStep, step_result: Dict[str, Any]) -> None:
        """Execute hover step."""
        element = await self._find_element_with_fallbacks(page, step, step_result)
        await element.hover()
        
        logger.debug("Element hovered", selector=step.selector, run_id=str(step_result.get("run_id")))
    
    async def _execute_select(self, page: Page, step: FlowStep, step_result: Dict[str, Any]) -> None:
        """Execute select step."""
        element = await self._find_element_with_fallbacks(page, step, step_result)
        value = step.value
        
        if not value:
            raise ValueError("Select step requires value")
        
        await element.select_option(value)
        
        logger.debug("Option selected", selector=step.selector, value=value, run_id=str(step_result.get("run_id")))
    
    async def _execute_upload(self, page: Page, step: FlowStep, step_result: Dict[str, Any]) -> None:
        """Execute upload step."""
        element = await self._find_element_with_fallbacks(page, step, step_result)
        file_path = step.file_path
        
        if not file_path:
            raise ValueError("Upload step requires file_path")
        
        await element.set_input_files(file_path)
        
        logger.debug("File uploaded", selector=step.selector, file_path=file_path, run_id=str(step_result.get("run_id")))
    
    async def _execute_download(self, page: Page, step: FlowStep, step_result: Dict[str, Any]) -> None:
        """Execute download step."""
        # Download handling would be implemented here
        # This is a placeholder for future implementation
        logger.debug("Download step executed", run_id=str(step_result.get("run_id")))
    
    async def _execute_switch_tab(self, page: Page, step: FlowStep, step_result: Dict[str, Any]) -> None:
        """Execute switch tab step."""
        tab_index = step.tab_index or 0
        context = page.context
        
        if tab_index < len(context.pages):
            await context.pages[tab_index].bring_to_front()
        
        logger.debug("Tab switched", tab_index=tab_index, run_id=str(step_result.get("run_id")))
    
    async def _execute_close_tab(self, page: Page, step: FlowStep, step_result: Dict[str, Any]) -> None:
        """Execute close tab step."""
        await page.close()
        
        logger.debug("Tab closed", run_id=str(step_result.get("run_id")))
    
    async def _execute_script(self, page: Page, step: FlowStep, step_result: Dict[str, Any]) -> None:
        """Execute JavaScript step."""
        script = step.script
        
        if not script:
            raise ValueError("Execute script step requires script")
        
        result = await page.evaluate(script)
        
        logger.debug("Script executed", script_preview=script[:100], run_id=str(step_result.get("run_id")))
    
    async def _find_element_with_fallbacks(
        self,
        page: Page,
        step: FlowStep,
        step_result: Dict[str, Any]
    ) -> Locator:
        """Find element using primary selector and fallbacks."""
        selectors_to_try = [step.selector]
        
        # Add fallback selectors if available
        if step.fallback_selectors:
            selectors_to_try.extend(step.fallback_selectors)
        
        last_error = None
        
        for i, selector in enumerate(selectors_to_try):
            try:
                element = await self.selector_manager.find_element(page, selector)
                
                # Mark which selector was used
                if i > 0:
                    step_result["fallback_used"] = selector
                
                return element
                
            except Exception as e:
                last_error = e
                logger.debug("Selector failed", selector=selector, error=str(e))
                continue
        
        # All selectors failed
        raise ValueError(f"Could not find element with any selector. Last error: {last_error}")
    
    async def _validate_conditions(
        self,
        page: Page,
        conditions: List[Dict[str, Any]],
        condition_type: str,
        step_index: int,
        run_id: UUID
    ) -> Dict[str, Any]:
        """Validate pre/post conditions."""
        for i, condition in enumerate(conditions):
            try:
                condition_type_field = condition.get("type")
                condition_value = condition.get("value")
                
                if condition_type_field == "element_visible":
                    is_visible = await self.selector_manager.is_element_visible(page, condition_value)
                    if not is_visible:
                        return {
                            "passed": False,
                            "error": f"Element '{condition_value}' not visible"
                        }
                
                elif condition_type_field == "text_present":
                    page_text = await page.text_content("body")
                    if condition_value not in page_text:
                        return {
                            "passed": False,
                            "error": f"Text '{condition_value}' not present"
                        }
                
                elif condition_type_field == "url_contains":
                    if condition_value not in page.url:
                        return {
                            "passed": False,
                            "error": f"URL does not contain '{condition_value}'"
                        }
                
                else:
                    return {
                        "passed": False,
                        "error": f"Unknown condition type: {condition_type_field}"
                    }
                
            except Exception as e:
                return {
                    "passed": False,
                    "error": f"Condition validation failed: {str(e)}"
                }
        
        return {"passed": True, "error": None}


# Global flow executor
flow_executor = FlowExecutor()
