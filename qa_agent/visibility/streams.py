"""
WebSocket event streaming for real-time updates.
"""
from typing import Dict, Any, Callable, Set
from uuid import UUID
import asyncio
import json

from qa_agent.core.logging import get_logger

logger = get_logger(__name__)


class EventStreamManager:
    """Manages real-time event streaming via WebSocket."""
    
    def __init__(self):
        self.subscribers: Dict[UUID, Set[Callable]] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.is_running = False
    
    async def start(self) -> None:
        """Start the event streaming service."""
        if self.is_running:
            return
        
        self.is_running = True
        asyncio.create_task(self._process_events())
        
        logger.info("Event streaming service started")
    
    async def stop(self) -> None:
        """Stop the event streaming service."""
        self.is_running = False
        logger.info("Event streaming service stopped")
    
    async def subscribe_to_run(self, run_id: UUID, callback: Callable) -> None:
        """Subscribe to events for a specific run."""
        if run_id not in self.subscribers:
            self.subscribers[run_id] = set()
        
        self.subscribers[run_id].add(callback)
        
        logger.debug("Subscribed to run events", run_id=str(run_id))
    
    async def unsubscribe_from_run(self, run_id: UUID) -> None:
        """Unsubscribe from events for a specific run."""
        if run_id in self.subscribers:
            del self.subscribers[run_id]
        
        logger.debug("Unsubscribed from run events", run_id=str(run_id))
    
    async def emit_event(self, run_id: UUID, event: Dict[str, Any]) -> None:
        """Emit an event to subscribers."""
        if not self.is_running:
            return
        
        event_data = {
            "run_id": str(run_id),
            "event": event,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await self.event_queue.put(event_data)
    
    async def emit_run_status(self, run_id: UUID, status: str, details: Dict[str, Any] = None) -> None:
        """Emit run status update."""
        event = {
            "type": "run_status",
            "status": status,
            "details": details or {}
        }
        
        await self.emit_event(run_id, event)
    
    async def emit_step_start(self, run_id: UUID, step_index: int, step_info: Dict[str, Any]) -> None:
        """Emit step start event."""
        event = {
            "type": "step_start",
            "step_index": step_index,
            "step_info": step_info
        }
        
        await self.emit_event(run_id, event)
    
    async def emit_step_complete(self, run_id: UUID, step_index: int, result: Dict[str, Any]) -> None:
        """Emit step completion event."""
        event = {
            "type": "step_complete",
            "step_index": step_index,
            "result": result
        }
        
        await self.emit_event(run_id, event)
    
    async def emit_friction_detected(self, run_id: UUID, friction_info: Dict[str, Any]) -> None:
        """Emit friction detection event."""
        event = {
            "type": "friction_detected",
            "friction_info": friction_info
        }
        
        await self.emit_event(run_id, event)
    
    async def emit_milestone(self, run_id: UUID, milestone: str, details: Dict[str, Any] = None) -> None:
        """Emit milestone event."""
        event = {
            "type": "milestone",
            "milestone": milestone,
            "details": details or {}
        }
        
        await self.emit_event(run_id, event)
    
    async def _process_events(self) -> None:
        """Process events from the queue and distribute to subscribers."""
        while self.is_running:
            try:
                # Wait for events with timeout
                event_data = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                
                run_id = UUID(event_data["run_id"])
                event = event_data["event"]
                
                # Send to subscribers
                if run_id in self.subscribers:
                    subscribers = self.subscribers[run_id].copy()
                    
                    for callback in subscribers:
                        try:
                            await callback(event)
                        except Exception as e:
                            logger.error("Error in event callback", error=str(e))
                            # Remove faulty callback
                            self.subscribers[run_id].discard(callback)
                
            except asyncio.TimeoutError:
                # Timeout is expected, continue
                continue
            except Exception as e:
                logger.error("Error processing event", error=str(e))
    
    def get_subscriber_count(self, run_id: UUID) -> int:
        """Get number of subscribers for a run."""
        return len(self.subscribers.get(run_id, set()))
    
    def get_total_subscribers(self) -> int:
        """Get total number of subscribers across all runs."""
        return sum(len(subscribers) for subscribers in self.subscribers.values())
    
    async def broadcast_to_all(self, event: Dict[str, Any]) -> None:
        """Broadcast event to all subscribers."""
        for run_id in list(self.subscribers.keys()):
            await self.emit_event(run_id, event)
    
    async def get_run_event_history(self, run_id: UUID, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent event history for a run."""
        # This would typically query the database
        # For now, return empty list
        return []


class WebSocketConnection:
    """Represents a WebSocket connection."""
    
    def __init__(self, websocket, run_id: UUID):
        self.websocket = websocket
        self.run_id = run_id
        self.is_active = True
    
    async def send_event(self, event: Dict[str, Any]) -> None:
        """Send event to WebSocket client."""
        if not self.is_active:
            return
        
        try:
            message = json.dumps(event)
            await self.websocket.send_text(message)
        except Exception as e:
            logger.error("Error sending WebSocket message", error=str(e))
            self.is_active = False
    
    async def close(self) -> None:
        """Close the WebSocket connection."""
        self.is_active = False
        try:
            await self.websocket.close()
        except Exception:
            pass


# Global event stream manager
event_stream_manager = EventStreamManager()
