"""
Kernel replay integration and local reconstruction.
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime

from qa_agent.kernel.client import kernel_client
from qa_agent.visibility.events import event_storage
from qa_agent.core.logging import get_logger

logger = get_logger(__name__)


class ReplayManager:
    """Manages Kernel replays and local reconstruction."""
    
    def __init__(self):
        self.replay_cache: Dict[str, Dict[str, Any]] = {}
    
    async def get_replay_url(self, browser_response: Dict[str, Any]) -> Optional[str]:
        """Get replay URL from browser response."""
        return kernel_client.get_replay_url(browser_response)
    
    async def get_live_view_url(self, browser_response: Dict[str, Any]) -> Optional[str]:
        """Get live view URL from browser response."""
        return kernel_client.get_live_view_url(browser_response)
    
    async def store_replay_info(
        self,
        run_id: UUID,
        browser_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store replay information for a run."""
        replay_url = await self.get_replay_url(browser_response)
        live_view_url = await self.get_live_view_url(browser_response)
        
        replay_info = {
            "run_id": str(run_id),
            "replay_url": replay_url,
            "live_view_url": live_view_url,
            "browser_id": browser_response.get("id"),
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Cache replay info
        self.replay_cache[str(run_id)] = replay_info
        
        logger.info("Replay info stored", run_id=str(run_id), replay_url=replay_url)
        
        return replay_info
    
    async def get_replay_info(self, run_id: UUID) -> Optional[Dict[str, Any]]:
        """Get replay information for a run."""
        return self.replay_cache.get(str(run_id))
    
    async def reconstruct_timeline(
        self,
        run_id: UUID,
        include_events: bool = True,
        include_snapshots: bool = True
    ) -> Dict[str, Any]:
        """Reconstruct timeline combining events and snapshots."""
        timeline = {
            "run_id": str(run_id),
            "replay_info": await self.get_replay_info(run_id),
            "events": [],
            "snapshots": [],
            "milestones": []
        }
        
        if include_events:
            # Get events timeline
            events = await event_storage.get_event_timeline(run_id)
            timeline["events"] = events
        
        if include_snapshots:
            # Get snapshots timeline
            from qa_agent.visibility.events import snapshot_manager
            snapshots = await snapshot_manager.get_snapshot_timeline(run_id)
            timeline["snapshots"] = snapshots
        
        # Generate milestones
        timeline["milestones"] = await self._generate_milestones(run_id)
        
        return timeline
    
    async def _generate_milestones(self, run_id: UUID) -> List[Dict[str, Any]]:
        """Generate key milestones from events."""
        events = await event_storage.get_events_for_run(run_id)
        
        milestones = []
        
        for event in events:
            if event.event_type in ["page_load", "form_submit", "navigation"]:
                milestone = {
                    "timestamp": event.timestamp,
                    "type": event.event_type,
                    "description": self._get_milestone_description(event),
                    "payload": event.payload
                }
                milestones.append(milestone)
        
        # Sort by timestamp
        milestones.sort(key=lambda x: x["timestamp"])
        
        return milestones
    
    def _get_milestone_description(self, event) -> str:
        """Get human-readable description for milestone."""
        descriptions = {
            "page_load": "Page loaded",
            "form_submit": "Form submitted",
            "navigation": "Navigation occurred"
        }
        
        base_description = descriptions.get(event.event_type, "Event occurred")
        
        # Add context from payload
        payload = event.payload
        if event.event_type == "page_load" and "url" in payload:
            return f"{base_description}: {payload['url']}"
        elif event.event_type == "form_submit" and "form_id" in payload:
            return f"{base_description}: {payload['form_id']}"
        
        return base_description
    
    async def export_timeline(
        self,
        run_id: UUID,
        format: str = "json"
    ) -> str:
        """Export timeline in specified format."""
        timeline = await self.reconstruct_timeline(run_id)
        
        if format == "json":
            import json
            return json.dumps(timeline, indent=2)
        elif format == "markdown":
            return self._timeline_to_markdown(timeline)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _timeline_to_markdown(self, timeline: Dict[str, Any]) -> str:
        """Convert timeline to markdown format."""
        md = f"# Run Timeline: {timeline['run_id']}\n\n"
        
        # Replay info
        replay_info = timeline.get("replay_info")
        if replay_info:
            md += "## Replay Information\n\n"
            if replay_info.get("replay_url"):
                md += f"- **Replay URL**: {replay_info['replay_url']}\n"
            if replay_info.get("live_view_url"):
                md += f"- **Live View URL**: {replay_info['live_view_url']}\n"
            md += "\n"
        
        # Milestones
        milestones = timeline.get("milestones", [])
        if milestones:
            md += "## Key Milestones\n\n"
            for milestone in milestones:
                timestamp = datetime.fromtimestamp(milestone["timestamp"]).strftime("%H:%M:%S")
                md += f"- **{timestamp}**: {milestone['description']}\n"
            md += "\n"
        
        # Events summary
        events = timeline.get("events", [])
        if events:
            md += f"## Events Summary\n\n"
            md += f"Total events: {len(events)}\n\n"
            
            # Group by type
            event_types = {}
            for event in events:
                event_type = event["type"]
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            md += "Event types:\n"
            for event_type, count in event_types.items():
                md += f"- {event_type}: {count}\n"
        
        return md
    
    async def cleanup_old_replays(self, older_than_days: int = 30) -> int:
        """Cleanup old replay information."""
        cutoff_time = datetime.utcnow().timestamp() - (older_than_days * 24 * 60 * 60)
        
        removed_count = 0
        for run_id in list(self.replay_cache.keys()):
            replay_info = self.replay_cache[run_id]
            created_at = datetime.fromisoformat(replay_info["created_at"]).timestamp()
            
            if created_at < cutoff_time:
                del self.replay_cache[run_id]
                removed_count += 1
        
        logger.info("Cleaned up old replays", removed_count=removed_count)
        return removed_count


# Global replay manager
replay_manager = ReplayManager()
