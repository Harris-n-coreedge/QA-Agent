"""
API endpoints for action approval management.

Handles approval requests from the confidence scoring system and
provides endpoints for frontend to respond to approval requests.
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from uuid import uuid4
import asyncio

from qa_agent.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/approvals", tags=["approvals"])


# Models
class ApprovalRequest(BaseModel):
    """Request for user approval of an action."""
    action_description: str
    current_url: Optional[str] = None
    element_text: Optional[str] = None
    confidence_score: float
    confidence_level: str
    reasoning: str
    risk_factors: List[str] = []
    timeout_seconds: int = 60


class ApprovalResponse(BaseModel):
    """User's response to an approval request."""
    request_id: str
    approved: bool
    user_notes: Optional[str] = None


class ApprovalStatus(BaseModel):
    """Status of an approval request."""
    request_id: str
    action_description: str
    confidence_score: float
    confidence_level: str
    reasoning: str
    risk_factors: List[str]
    current_url: Optional[str]
    element_text: Optional[str]
    status: str  # 'pending', 'approved', 'denied', 'timeout'
    created_at: str
    expires_at: str
    responded_at: Optional[str] = None


# In-memory storage for approval requests
# In production, use Redis or database
pending_approvals: Dict[str, Dict[str, Any]] = {}
approval_responses: Dict[str, Dict[str, Any]] = {}

# WebSocket connections for real-time updates
active_connections: List[WebSocket] = []


class ApprovalManager:
    """Manages approval requests and responses."""

    @staticmethod
    def create_approval_request(request: ApprovalRequest) -> str:
        """
        Create a new approval request.

        Returns:
            request_id: Unique identifier for the request
        """
        request_id = str(uuid4())
        created_at = datetime.now()
        expires_at = created_at + timedelta(seconds=request.timeout_seconds)

        pending_approvals[request_id] = {
            'request_id': request_id,
            'action_description': request.action_description,
            'current_url': request.current_url,
            'element_text': request.element_text,
            'confidence_score': request.confidence_score,
            'confidence_level': request.confidence_level,
            'reasoning': request.reasoning,
            'risk_factors': request.risk_factors,
            'status': 'pending',
            'created_at': created_at.isoformat(),
            'expires_at': expires_at.isoformat(),
            'responded_at': None,
            'timeout_seconds': request.timeout_seconds
        }

        logger.info(
            "Approval request created",
            request_id=request_id,
            action=request.action_description,
            confidence=request.confidence_level
        )

        return request_id

    @staticmethod
    async def wait_for_response(request_id: str, timeout: int = 60) -> bool:
        """
        Wait for user response to an approval request.

        Args:
            request_id: The approval request ID
            timeout: Maximum time to wait in seconds

        Returns:
            True if approved, False if denied or timeout
        """
        start_time = asyncio.get_event_loop().time()
        check_interval = 0.5  # Check every 500ms

        while True:
            # Check if response received
            if request_id in approval_responses:
                response = approval_responses[request_id]
                approved = response['approved']

                # Update status
                if request_id in pending_approvals:
                    pending_approvals[request_id]['status'] = 'approved' if approved else 'denied'
                    pending_approvals[request_id]['responded_at'] = datetime.now().isoformat()

                logger.info(
                    "Approval response received",
                    request_id=request_id,
                    approved=approved
                )

                return approved

            # Check for timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout:
                # Update status to timeout
                if request_id in pending_approvals:
                    pending_approvals[request_id]['status'] = 'timeout'
                    pending_approvals[request_id]['responded_at'] = datetime.now().isoformat()

                logger.warning("Approval request timed out", request_id=request_id)
                return False

            # Wait before checking again
            await asyncio.sleep(check_interval)

    @staticmethod
    def get_pending_requests() -> List[ApprovalStatus]:
        """Get all pending approval requests."""
        now = datetime.now()
        pending = []

        for request_id, request_data in list(pending_approvals.items()):
            if request_data['status'] == 'pending':
                # Check if expired
                expires_at = datetime.fromisoformat(request_data['expires_at'])
                if now > expires_at:
                    request_data['status'] = 'timeout'
                    request_data['responded_at'] = now.isoformat()
                else:
                    pending.append(ApprovalStatus(**request_data))

        return pending

    @staticmethod
    def respond_to_request(request_id: str, approved: bool, user_notes: Optional[str] = None):
        """Record a response to an approval request."""
        if request_id not in pending_approvals:
            raise HTTPException(status_code=404, detail="Approval request not found")

        request_data = pending_approvals[request_id]
        if request_data['status'] != 'pending':
            raise HTTPException(
                status_code=400,
                detail=f"Request already {request_data['status']}"
            )

        approval_responses[request_id] = {
            'request_id': request_id,
            'approved': approved,
            'user_notes': user_notes,
            'responded_at': datetime.now().isoformat()
        }

        logger.info(
            "Approval response recorded",
            request_id=request_id,
            approved=approved
        )

    @staticmethod
    def cleanup_old_requests(max_age_hours: int = 24):
        """Clean up old approval requests."""
        now = datetime.now()
        cutoff = now - timedelta(hours=max_age_hours)

        for request_id in list(pending_approvals.keys()):
            created_at = datetime.fromisoformat(pending_approvals[request_id]['created_at'])
            if created_at < cutoff:
                del pending_approvals[request_id]
                if request_id in approval_responses:
                    del approval_responses[request_id]

        logger.debug("Old approval requests cleaned up")


approval_manager = ApprovalManager()


# API Endpoints

@router.post("/request", response_model=Dict[str, str])
async def create_approval_request(request: ApprovalRequest):
    """
    Create a new approval request.

    This endpoint is called by the backend when an action requires approval.
    """
    request_id = approval_manager.create_approval_request(request)

    # Notify WebSocket clients
    await broadcast_approval_update({
        'type': 'new_request',
        'request_id': request_id,
        'action': request.action_description,
        'confidence_level': request.confidence_level
    })

    return {"request_id": request_id}


@router.get("/pending", response_model=List[ApprovalStatus])
async def get_pending_approvals():
    """
    Get all pending approval requests.

    Frontend polls this endpoint to check for new approval requests.
    """
    pending = approval_manager.get_pending_requests()
    return pending


@router.post("/respond")
async def respond_to_approval(response: ApprovalResponse):
    """
    Respond to an approval request.

    Called by frontend when user approves or denies an action.
    """
    try:
        approval_manager.respond_to_request(
            request_id=response.request_id,
            approved=response.approved,
            user_notes=response.user_notes
        )

        # Notify WebSocket clients
        await broadcast_approval_update({
            'type': 'response',
            'request_id': response.request_id,
            'approved': response.approved
        })

        return {"status": "success", "message": "Response recorded"}

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error recording approval response", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{request_id}", response_model=ApprovalStatus)
async def get_approval_status(request_id: str):
    """Get the status of a specific approval request."""
    if request_id not in pending_approvals:
        raise HTTPException(status_code=404, detail="Approval request not found")

    return ApprovalStatus(**pending_approvals[request_id])


@router.delete("/cleanup")
async def cleanup_old_approvals(max_age_hours: int = 24):
    """Clean up old approval requests (admin endpoint)."""
    approval_manager.cleanup_old_requests(max_age_hours)
    return {"status": "success", "message": "Old requests cleaned up"}


# WebSocket endpoint for real-time updates
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket connection for real-time approval updates.

    Frontend can connect to receive instant notifications of new approval requests.
    """
    await websocket.accept()
    active_connections.append(websocket)

    logger.info("WebSocket connection established")

    try:
        while True:
            # Keep connection alive and listen for pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("WebSocket connection closed")


async def broadcast_approval_update(message: Dict[str, Any]):
    """Broadcast update to all connected WebSocket clients."""
    disconnected = []

    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.warning("Error sending WebSocket message", error=str(e))
            disconnected.append(connection)

    # Remove disconnected clients
    for conn in disconnected:
        if conn in active_connections:
            active_connections.remove(conn)


# Helper function for backend to request approval
async def request_user_approval(
    action_description: str,
    confidence_score: float,
    confidence_level: str,
    reasoning: str,
    risk_factors: List[str],
    current_url: Optional[str] = None,
    element_text: Optional[str] = None,
    timeout_seconds: int = 60
) -> bool:
    """
    Request user approval for an action.

    This is the main function to be called by the confidence scorer.

    Args:
        action_description: Description of the action
        confidence_score: Confidence score (0.0 to 1.0)
        confidence_level: Confidence level string
        reasoning: Reasoning for the confidence score
        risk_factors: List of identified risk factors
        current_url: Current page URL
        element_text: Text of target element
        timeout_seconds: How long to wait for response

    Returns:
        True if approved, False if denied or timeout
    """
    # Create approval request
    request = ApprovalRequest(
        action_description=action_description,
        current_url=current_url,
        element_text=element_text,
        confidence_score=confidence_score,
        confidence_level=confidence_level,
        reasoning=reasoning,
        risk_factors=risk_factors,
        timeout_seconds=timeout_seconds
    )

    request_id = approval_manager.create_approval_request(request)

    # Notify connected clients
    await broadcast_approval_update({
        'type': 'new_request',
        'request_id': request_id,
        'action': action_description,
        'confidence_level': confidence_level
    })

    # Wait for response
    approved = await approval_manager.wait_for_response(
        request_id=request_id,
        timeout=timeout_seconds
    )

    return approved
