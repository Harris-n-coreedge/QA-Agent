"""
Run management routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID

from qa_agent.schemas import RunCreate, RunResponse, RunUpdate
from qa_agent.storage.repo import RunRepository

router = APIRouter()


@router.post("/runs", response_model=RunResponse)
async def create_run(
    run: RunCreate,
    repo: RunRepository = Depends()
):
    """Start a new simulation run."""
    # TODO: Implement run creation
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/runs", response_model=List[RunResponse])
async def list_runs(
    project_id: UUID = None,
    flow_id: UUID = None,
    repo: RunRepository = Depends()
):
    """List runs, optionally filtered by project or flow."""
    # TODO: Implement run listing
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/runs/{run_id}", response_model=RunResponse)
async def get_run(
    run_id: UUID,
    repo: RunRepository = Depends()
):
    """Get a specific run with status and links."""
    # TODO: Implement run retrieval
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/runs/{run_id}", response_model=RunResponse)
async def update_run(
    run_id: UUID,
    run: RunUpdate,
    repo: RunRepository = Depends()
):
    """Update a run."""
    # TODO: Implement run update
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/runs/{run_id}")
async def cancel_run(
    run_id: UUID,
    repo: RunRepository = Depends()
):
    """Cancel a running simulation."""
    # TODO: Implement run cancellation
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/runs/{run_id}/events")
async def get_run_events(
    run_id: UUID,
    limit: int = 100,
    offset: int = 0,
    repo: RunRepository = Depends()
):
    """Get paginated events for a run."""
    # TODO: Implement event retrieval
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/runs/{run_id}/friction")
async def get_run_friction(
    run_id: UUID,
    repo: RunRepository = Depends()
):
    """Get friction issues and scores for a run."""
    # TODO: Implement friction analysis retrieval
    raise HTTPException(status_code=501, detail="Not implemented")
