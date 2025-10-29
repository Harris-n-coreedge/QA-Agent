"""
Event persistence and storage.
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
import json

from qa_agent.core.logging import get_logger

logger = get_logger(__name__)


class SessionEvent:
    """Represents a session event."""
    
    def __init__(
        self,
        run_id: UUID,
        event_type: str,
        timestamp: float,
        payload: Dict[str, Any],
        step_id: Optional[UUID] = None
    ):
        self.id = UUID()  # Generate unique ID
        self.run_id = run_id
        self.step_id = step_id
        self.event_type = event_type
        self.timestamp = timestamp
        self.payload = payload
        self.created_at = datetime.utcnow()


class EventStorage:
    """Handles event persistence and retrieval."""
    
    def __init__(self):
        self.events: Dict[UUID, List[SessionEvent]] = {}
    
    async def store_event(self, event: SessionEvent) -> None:
        """Store a session event."""
        if event.run_id not in self.events:
            self.events[event.run_id] = []
        
        self.events[event.run_id].append(event)
        
        logger.debug(
            "Event stored",
            run_id=str(event.run_id),
            event_type=event.event_type,
            timestamp=event.timestamp
        )
    
    async def store_events(self, events: List[SessionEvent]) -> None:
        """Store multiple events."""
        for event in events:
            await self.store_event(event)
    
    async def get_events_for_run(
        self,
        run_id: UUID,
        event_type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[SessionEvent]:
        """Get events for a specific run."""
        run_events = self.events.get(run_id, [])
        
        # Filter by event type if specified
        if event_type:
            run_events = [e for e in run_events if e.event_type == event_type]
        
        # Sort by timestamp
        run_events.sort(key=lambda x: x.timestamp)
        
        # Apply pagination
        if offset:
            run_events = run_events[offset:]
        
        if limit:
            run_events = run_events[:limit]
        
        return run_events
    
    async def get_events_by_type(
        self,
        event_type: str,
        limit: Optional[int] = None
    ) -> List[SessionEvent]:
        """Get events by type across all runs."""
        all_events = []
        
        for run_events in self.events.values():
            type_events = [e for e in run_events if e.event_type == event_type]
            all_events.extend(type_events)
        
        # Sort by timestamp
        all_events.sort(key=lambda x: x.timestamp)
        
        if limit:
            all_events = all_events[:limit]
        
        return all_events
    
    async def get_event_timeline(self, run_id: UUID) -> List[Dict[str, Any]]:
        """Get chronological timeline of events for a run."""
        events = await self.get_events_for_run(run_id)
        
        timeline = []
        for event in events:
            timeline.append({
                "id": str(event.id),
                "type": event.event_type,
                "timestamp": event.timestamp,
                "step_id": str(event.step_id) if event.step_id else None,
                "payload": event.payload
            })
        
        return timeline
    
    async def get_event_summary(self, run_id: UUID) -> Dict[str, Any]:
        """Get summary statistics for events in a run."""
        events = await self.get_events_for_run(run_id)
        
        if not events:
            return {
                "total_events": 0,
                "event_types": {},
                "duration": 0,
                "first_event": None,
                "last_event": None
            }
        
        # Count by type
        event_types = {}
        for event in events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
        
        # Calculate duration
        timestamps = [e.timestamp for e in events]
        duration = max(timestamps) - min(timestamps) if timestamps else 0
        
        return {
            "total_events": len(events),
            "event_types": event_types,
            "duration": duration,
            "first_event": min(timestamps) if timestamps else None,
            "last_event": max(timestamps) if timestamps else None
        }
    
    async def cleanup_old_events(self, older_than_days: int = 30) -> int:
        """Cleanup events older than specified days."""
        cutoff_time = datetime.utcnow().timestamp() - (older_than_days * 24 * 60 * 60)
        
        removed_count = 0
        for run_id in list(self.events.keys()):
            original_count = len(self.events[run_id])
            self.events[run_id] = [
                e for e in self.events[run_id]
                if e.timestamp > cutoff_time
            ]
            
            removed_count += original_count - len(self.events[run_id])
            
            # Remove empty run entries
            if not self.events[run_id]:
                del self.events[run_id]
        
        logger.info("Cleaned up old events", removed_count=removed_count, older_than_days=older_than_days)
        return removed_count


class SnapshotManager:
    """Manages page snapshots."""
    
    def __init__(self):
        self.snapshots: Dict[UUID, List[Dict[str, Any]]] = {}
    
    async def capture_snapshot(
        self,
        run_id: UUID,
        page,
        step_id: Optional[UUID] = None,
        description: str = ""
    ) -> Dict[str, Any]:
        """Capture a page snapshot."""
        try:
            # Take screenshot
            screenshot = await page.screenshot(full_page=True)
            
            # Get page info
            url = page.url
            title = await page.title()
            
            snapshot = {
                "id": str(UUID()),
                "run_id": str(run_id),
                "step_id": str(step_id) if step_id else None,
                "timestamp": datetime.utcnow().timestamp(),
                "url": url,
                "title": title,
                "description": description,
                "screenshot": screenshot,  # Base64 encoded
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store snapshot
            if run_id not in self.snapshots:
                self.snapshots[run_id] = []
            
            self.snapshots[run_id].append(snapshot)
            
            logger.debug("Snapshot captured", run_id=str(run_id), url=url)
            
            return snapshot
            
        except Exception as e:
            logger.error("Failed to capture snapshot", run_id=str(run_id), error=str(e))
            raise
    
    async def get_snapshots_for_run(self, run_id: UUID) -> List[Dict[str, Any]]:
        """Get all snapshots for a run."""
        return self.snapshots.get(run_id, [])
    
    async def get_snapshot_timeline(self, run_id: UUID) -> List[Dict[str, Any]]:
        """Get chronological timeline of snapshots."""
        snapshots = await self.get_snapshots_for_run(run_id)
        
        # Sort by timestamp
        snapshots.sort(key=lambda x: x["timestamp"])
        
        return snapshots


# Global storage instances
event_storage = EventStorage()
snapshot_manager = SnapshotManager()
