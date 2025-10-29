"""
WebSocket support for real-time QA test execution updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import json
from datetime import datetime

router = APIRouter()

# Store active WebSocket connections by session
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a WebSocket client to a session"""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str):
        """Disconnect a WebSocket client from a session"""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket client"""
        await websocket.send_json(message)

    async def broadcast_to_session(self, message: dict, session_id: str):
        """Broadcast a message to all clients connected to a session"""
        if session_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)

            # Clean up disconnected clients
            for connection in disconnected:
                self.active_connections[session_id].discard(connection)


manager = ConnectionManager()


@router.websocket("/qa-tests/sessions/{session_id}")
async def websocket_qa_session(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time QA test execution updates.

    Clients can connect to receive live updates about:
    - Command execution status
    - Test results
    - Browser events
    - Error messages
    """
    await manager.connect(websocket, session_id)

    try:
        # Send welcome message
        await manager.send_personal_message(
            {
                "type": "connection",
                "status": "connected",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"Connected to session {session_id}",
            },
            websocket,
        )

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Receive messages from client (for potential two-way communication)
                data = await websocket.receive_text()
                message = json.loads(data)

                # Echo back for now (can be extended for interactive features)
                await manager.send_personal_message(
                    {
                        "type": "echo",
                        "data": message,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    websocket,
                )

            except WebSocketDisconnect:
                break
            except Exception as e:
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    websocket,
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, session_id)


async def send_command_update(session_id: str, command: str, status: str, result: str = None):
    """
    Send command execution update to all connected clients.

    This function can be called from the API routes to push updates.
    """
    message = {
        "type": "command_update",
        "command": command,
        "status": status,
        "result": result,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await manager.broadcast_to_session(message, session_id)


async def send_test_result(session_id: str, test_id: str, status: str, result: dict):
    """
    Send test result update to all connected clients.
    """
    message = {
        "type": "test_result",
        "test_id": test_id,
        "status": status,
        "result": result,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await manager.broadcast_to_session(message, session_id)


async def send_browser_event(session_id: str, event_type: str, details: dict):
    """
    Send browser event update to all connected clients.
    """
    message = {
        "type": "browser_event",
        "event_type": event_type,
        "details": details,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await manager.broadcast_to_session(message, session_id)


# Export the manager for use in other modules
__all__ = ["router", "manager", "send_command_update", "send_test_result", "send_browser_event"]
