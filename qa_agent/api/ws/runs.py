"""
WebSocket routes for real-time event streaming.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
import asyncio
from uuid import UUID

from qa_agent.visibility.streams import EventStreamManager

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, run_id: UUID):
        await websocket.accept()
        if run_id not in self.active_connections:
            self.active_connections[run_id] = set()
        self.active_connections[run_id].add(websocket)

    def disconnect(self, websocket: WebSocket, run_id: UUID):
        if run_id in self.active_connections:
            self.active_connections[run_id].discard(websocket)
            if not self.active_connections[run_id]:
                del self.active_connections[run_id]

    async def send_to_run(self, run_id: UUID, message: dict):
        if run_id in self.active_connections:
            disconnected = set()
            for websocket in self.active_connections[run_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except:
                    disconnected.add(websocket)
            
            # Clean up disconnected websockets
            for ws in disconnected:
                self.active_connections[run_id].discard(ws)


manager = ConnectionManager()


@router.websocket("/runs/{run_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    run_id: UUID,
    stream_manager: EventStreamManager = Depends()
):
    """WebSocket endpoint for real-time run event streaming."""
    await manager.connect(websocket, run_id)
    
    try:
        # Subscribe to events for this run
        await stream_manager.subscribe_to_run(run_id, manager.send_to_run)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (ping/pong, etc.)
                data = await websocket.receive_text()
                # Echo back for now
                await websocket.send_text(f"Echo: {data}")
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, run_id)
        await stream_manager.unsubscribe_from_run(run_id)
