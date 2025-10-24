"""
Event management routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID

from qa_agent.schemas import SessionEventResponse
from qa_agent.storage.repo import EventRepository

router = APIRouter()


@router.get("/events", response_model=List[SessionEventResponse])
async def list_events(
    run_id: UUID = None,
    event_type: str = None,
    limit: int = 100,
    offset: int = 0,
    repo: EventRepository = Depends()
):
    """List events with optional filtering."""
    # TODO: Implement event listing
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/events/{event_id}", response_model=SessionEventResponse)
async def get_event(
    event_id: UUID,
    repo: EventRepository = Depends()
):
    """Get a specific event."""
    # TODO: Implement event retrieval
    raise HTTPException(status_code=501, detail="Not implemented")
