"""
Project management routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID

from qa_agent.schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from qa_agent.storage.repo import ProjectRepository

router = APIRouter()


@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    repo: ProjectRepository = Depends()
):
    """Create a new project."""
    # TODO: Implement project creation
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    repo: ProjectRepository = Depends()
):
    """List all projects."""
    # TODO: Implement project listing
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    repo: ProjectRepository = Depends()
):
    """Get a specific project."""
    # TODO: Implement project retrieval
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project: ProjectUpdate,
    repo: ProjectRepository = Depends()
):
    """Update a project."""
    # TODO: Implement project update
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: UUID,
    repo: ProjectRepository = Depends()
):
    """Delete a project."""
    # TODO: Implement project deletion
    raise HTTPException(status_code=501, detail="Not implemented")
