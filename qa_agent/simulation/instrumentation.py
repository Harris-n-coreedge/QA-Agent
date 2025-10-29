"""
Comprehensive instrumentation for browser interactions.

Instrumentation for:
- Navigation lifecycle (load, DOMContentLoaded)
- Network (requests/responses/errors)
- Console messages, JS errors
- DOM events (click, input, change, focus, blur)
- Custom injected script for cursor movements, throttled scrolls, layout stability, long tasks
- Emit SessionEvent objects with timestamps, run/step correlation, and payload
- Periodically flush buffered events to the API/DB to avoid loss
"""
from playwright.async_api import Page
from typing import Dict, Any, List, Callable, Optional
from uuid import UUID
import json
import asyncio
import time

from qa_agent.core.logging import get_logger

logger = get_logger(__name__)


class InstrumentationManager:
    """
    Manages comprehensive browser instrumentation and event capture.
    
    Implements instrumentation for:
    - Navigation lifecycle (load, DOMContentLoaded)
    - Network (requests/responses/errors)
    - Console messages, JS errors
    - DOM events (click, input, change, focus, blur)
    - Custom injected script for cursor movements, throttled scrolls, layout stability, long tasks
    """
    
    def __init__(self):
        self.event_handlers: List[Callable] = []
        self.buffered_events: List[Dict[str, Any]] = []
        self.flush_interval = 1.0  # Flush events every second
        self.is_collecting = False
    
    async def setup_instrumentation(self, page: Page, run_id: UUID) -> None:
        """Setup comprehensive instrumentation on a page."""
        logger.info("Setting up comprehensive instrumentation", run_id=str(run_id))
        
        # Navigation lifecycle instrumentation
        await self._setup_navigation_instrumentation(page, run_id)
        
        # Network instrumentation
        await self._setup_network_instrumentation(page, run_id)
        
        # Console instrumentation
        await self._setup_console_instrumentation(page, run_id)
        
        # DOM event instrumentation
        await self._setup_dom_instrumentation(page, run_id)
        
        # Performance instrumentation
        await self._setup_performance_instrumentation(page, run_id)
        
        # Custom injected script for advanced monitoring
        await self._setup_custom_instrumentation(page, run_id)
        
        # Start periodic event flushing
        self.is_collecting = True
        asyncio.create_task(self._periodic_flush())
        
        logger.info("Comprehensive instrumentation setup complete", run_id=str(run_id))
    
    async def _setup_navigation_instrumentation(self, page: Page, run_id: UUID) -> None:
        """Setup navigation lifecycle monitoring."""
        
        async def handle_load():
            await self._emit_event({
                "type": "page_load",
                "run_id": str(run_id),
                "timestamp": time.time(),
                "payload": {
                    "url": page.url,
                    "title": await page.title()
                }
            })
        
        async def handle_dom_content_loaded():
            await self._emit_event({
                "type": "dom_content_loaded",
                "run_id": str(run_id),
                "timestamp": time.time(),
                "payload": {
                    "url": page.url
                }
            })
        
        page.on("load", handle_load)
        page.on("domcontentloaded", handle_dom_content_loaded)
    
    async def _setup_network_instrumentation(self, page: Page, run_id: UUID) -> None:
        """Setup comprehensive network monitoring including errors."""
        
        async def handle_request(request):
            await self._emit_event({
                "type": "network_request",
                "run_id": str(run_id),
                "timestamp": time.time(),
                "payload": {
                    "url": request.url,
                    "method": request.method,
                    "headers": dict(request.headers),
                    "post_data": request.post_data,
                    "resource_type": request.resource_type
                }
            })
        
        async def handle_response(response):
            await self._emit_event({
                "type": "network_response",
                "run_id": str(run_id),
                "timestamp": time.time(),
                "payload": {
                    "url": response.url,
                    "status": response.status,
                    "headers": dict(response.headers),
                    "size": response.headers.get("content-length"),
                    "timing": await response.timing() if hasattr(response, 'timing') else None
                }
            })
        
        async def handle_request_failed(request):
            await self._emit_event({
                "type": "network_error",
                "run_id": str(run_id),
                "timestamp": time.time(),
                "payload": {
                    "url": request.url,
                    "method": request.method,
                    "error": request.failure.get("errorText") if request.failure else "Unknown error"
                }
            })
        
        page.on("request", handle_request)
        page.on("response", handle_response)
        page.on("requestfailed", handle_request_failed)
    
    async def _setup_console_instrumentation(self, page: Page, run_id: UUID) -> None:
        """Setup console message and JS error monitoring."""
        
        async def handle_console(msg):
            await self._emit_event({
                "type": "console_message",
                "run_id": str(run_id),
                "timestamp": time.time(),
                "payload": {
                    "type": msg.type,
                    "text": msg.text,
                    "location": str(msg.location) if msg.location else None,
                    "args": [str(arg) for arg in msg.args] if hasattr(msg, 'args') else []
                }
            })
        
        async def handle_page_error(error):
            await self._emit_event({
                "type": "js_error",
                "run_id": str(run_id),
                "timestamp": time.time(),
                "payload": {
                    "error": str(error),
                    "stack": error.stack if hasattr(error, 'stack') else None
                }
            })
        
        page.on("console", handle_console)
        page.on("pageerror", handle_page_error)
    
    async def _setup_dom_instrumentation(self, page: Page, run_id: UUID) -> None:
        """Setup DOM event monitoring."""
        
        # Inject custom script for DOM events
        await page.add_init_script("""
            window.__qa_events = [];
            
            function emitEvent(type, data) {
                window.__qa_events.push({
                    type: type,
                    timestamp: Date.now(),
                    data: data
                });
            }
            
            // Monitor clicks
            document.addEventListener('click', (e) => {
                emitEvent('click', {
                    x: e.clientX,
                    y: e.clientY,
                    target: e.target.tagName,
                    text: e.target.textContent?.slice(0, 100)
                });
            });
            
            // Monitor input changes
            document.addEventListener('input', (e) => {
                emitEvent('input', {
                    target: e.target.tagName,
                    name: e.target.name,
                    value: e.target.value?.slice(0, 100)
                });
            });
            
            // Monitor focus/blur
            document.addEventListener('focus', (e) => {
                emitEvent('focus', {
                    target: e.target.tagName,
                    name: e.target.name
                });
            });
            
            document.addEventListener('blur', (e) => {
                emitEvent('blur', {
                    target: e.target.tagName,
                    name: e.target.name
                });
            });
        """)
        
        # Periodically collect DOM events
        async def collect_dom_events():
            while True:
                try:
                    events = await page.evaluate("window.__qa_events.splice(0)")
                    for event in events:
                        await self._emit_event({
                            "type": f"dom_{event['type']}",
                            "run_id": str(run_id),
                            "timestamp": event["timestamp"] / 1000,  # Convert to seconds
                            "payload": event["data"]
                        })
                except Exception as e:
                    logger.warning("Error collecting DOM events", error=str(e))
                
                await asyncio.sleep(0.1)  # Collect every 100ms
        
        # Start DOM event collection
        asyncio.create_task(collect_dom_events())
    
    async def _setup_performance_instrumentation(self, page: Page, run_id: UUID) -> None:
        """Setup performance monitoring."""
        
        await page.add_init_script("""
            // Monitor long tasks
            if ('PerformanceObserver' in window) {
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (entry.duration > 50) {  // Tasks longer than 50ms
                            window.__qa_events.push({
                                type: 'long_task',
                                timestamp: Date.now(),
                                data: {
                                    duration: entry.duration,
                                    startTime: entry.startTime
                                }
                            });
                        }
                    }
                });
                observer.observe({entryTypes: ['longtask']});
            }
            
            // Monitor layout shifts
            if ('PerformanceObserver' in window) {
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        window.__qa_events.push({
                            type: 'layout_shift',
                            timestamp: Date.now(),
                            data: {
                                value: entry.value,
                                hadRecentInput: entry.hadRecentInput
                            }
                        });
                    }
                });
                observer.observe({entryTypes: ['layout-shift']});
            }
    async def _setup_custom_instrumentation(self, page: Page, run_id: UUID) -> None:
        """
        Setup custom injected script for advanced monitoring.
        
        Implements cursor movements, throttled scrolls, layout stability, long tasks
        as specified in the plan.
        """
        await page.add_init_script("""
            // Enhanced QA Agent instrumentation
            window.__qa_agent_events = [];
            window.__qa_agent_config = {
                throttleScroll: true,
                trackCursor: true,
                trackLongTasks: true,
                trackLayoutShifts: true
            };
            
            function emitQAEvent(type, data) {
                window.__qa_agent_events.push({
                    type: type,
                    timestamp: Date.now(),
                    data: data
                });
            }
            
            // Cursor movement tracking
            if (window.__qa_agent_config.trackCursor) {
                let lastCursorTime = 0;
                document.addEventListener('mousemove', (e) => {
                    const now = Date.now();
                    if (now - lastCursorTime > 100) { // Throttle to 10fps
                        emitQAEvent('cursor_move', {
                            x: e.clientX,
                            y: e.clientY,
                            movementX: e.movementX,
                            movementY: e.movementY
                        });
                        lastCursorTime = now;
                    }
                });
            }
            
            // Throttled scroll tracking
            if (window.__qa_agent_config.throttleScroll) {
                let scrollTimeout;
                window.addEventListener('scroll', () => {
                    clearTimeout(scrollTimeout);
                    scrollTimeout = setTimeout(() => {
                        emitQAEvent('scroll', {
                            scrollX: window.scrollX,
                            scrollY: window.scrollY,
                            scrollHeight: document.documentElement.scrollHeight,
                            scrollWidth: document.documentElement.scrollWidth
                        });
                    }, 150); // Throttle scroll events
                });
            }
            
            // Enhanced DOM event tracking
            ['click', 'dblclick', 'mousedown', 'mouseup', 'mouseover', 'mouseout'].forEach(eventType => {
                document.addEventListener(eventType, (e) => {
                    emitQAEvent(eventType, {
                        x: e.clientX,
                        y: e.clientY,
                        target: e.target.tagName,
                        id: e.target.id,
                        className: e.target.className,
                        text: e.target.textContent?.slice(0, 100)
                    });
                });
            });
            
            // Form interaction tracking
            ['input', 'change', 'focus', 'blur', 'submit'].forEach(eventType => {
                document.addEventListener(eventType, (e) => {
                    emitQAEvent(eventType, {
                        target: e.target.tagName,
                        name: e.target.name,
                        type: e.target.type,
                        value: e.target.value?.slice(0, 100),
                        id: e.target.id
                    });
                });
            });
            
            // Keyboard tracking
            document.addEventListener('keydown', (e) => {
                emitQAEvent('keydown', {
                    key: e.key,
                    code: e.code,
                    ctrlKey: e.ctrlKey,
                    shiftKey: e.shiftKey,
                    altKey: e.altKey,
                    target: e.target.tagName
                });
            });
            
            // Performance monitoring
            if (window.__qa_agent_config.trackLongTasks && 'PerformanceObserver' in window) {
                const longTaskObserver = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        emitQAEvent('long_task', {
                            duration: entry.duration,
                            startTime: entry.startTime,
                            name: entry.name
                        });
                    }
                });
                longTaskObserver.observe({entryTypes: ['longtask']});
            }
            
            // Layout shift monitoring
            if (window.__qa_agent_config.trackLayoutShifts && 'PerformanceObserver' in window) {
                const layoutShiftObserver = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        emitQAEvent('layout_shift', {
                            value: entry.value,
                            hadRecentInput: entry.hadRecentInput,
                            lastInputTime: entry.lastInputTime,
                            sources: entry.sources?.map(source => ({
                                node: source.node?.tagName,
                                previousRect: source.previousRect,
                                currentRect: source.currentRect
                            }))
                        });
                    }
                });
                layoutShiftObserver.observe({entryTypes: ['layout-shift']});
            }
            
            // Memory usage tracking
            if ('memory' in performance) {
                setInterval(() => {
                    emitQAEvent('memory_usage', {
                        usedJSHeapSize: performance.memory.usedJSHeapSize,
                        totalJSHeapSize: performance.memory.totalJSHeapSize,
                        jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
                    });
                }, 5000); // Every 5 seconds
            }
            
            // Connection quality tracking
            if ('connection' in navigator) {
                emitQAEvent('connection_info', {
                    effectiveType: navigator.connection.effectiveType,
                    downlink: navigator.connection.downlink,
                    rtt: navigator.connection.rtt
                });
            }
        """)
        
        # Collect custom events periodically
        async def collect_custom_events():
            while self.is_collecting:
                try:
                    events = await page.evaluate("window.__qa_agent_events.splice(0)")
                    for event in events:
                        await self._emit_event({
                            "type": f"custom_{event['type']}",
                            "run_id": str(run_id),
                            "timestamp": event["timestamp"] / 1000,
                            "payload": event["data"]
                        })
                except Exception as e:
                    logger.warning("Error collecting custom events", error=str(e))
                
                await asyncio.sleep(0.1)  # Collect every 100ms
        
        asyncio.create_task(collect_custom_events())
    
    async def _periodic_flush(self) -> None:
        """Periodically flush buffered events to avoid loss."""
        while self.is_collecting:
            try:
                if self.buffered_events:
                    # Flush events to handlers
                    events_to_flush = self.buffered_events.copy()
                    self.buffered_events.clear()
                    
                    for handler in self.event_handlers:
                        try:
                            await handler(events_to_flush)
                        except Exception as e:
                            logger.error("Error flushing events to handler", error=str(e))
                    
                    logger.debug("Flushed events", count=len(events_to_flush))
                
            except Exception as e:
                logger.error("Error in periodic flush", error=str(e))
            
            await asyncio.sleep(self.flush_interval)
    
    def stop_collection(self) -> None:
        """Stop event collection and flush remaining events."""
        self.is_collecting = False
    
    async def _emit_event(self, event: Dict[str, Any]) -> None:
        """Emit an event to all registered handlers."""
        self.buffered_events.append(event)
        
        # Call registered handlers
        for handler in self.event_handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error("Error in event handler", error=str(e))
    
    def add_event_handler(self, handler: Callable) -> None:
        """Add an event handler."""
        self.event_handlers.append(handler)
    
    def get_buffered_events(self) -> List[Dict[str, Any]]:
        """Get and clear buffered events."""
        events = self.buffered_events.copy()
        self.buffered_events.clear()
        return events
