"""
Metrics and health routes.
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any

from qa_agent.storage.repo import MetricsRepository

router = APIRouter()


@router.get("/metrics")
async def get_metrics(
    project_id: str = None,
    repo: MetricsRepository = Depends()
) -> Dict[str, Any]:
    """Get basic health and performance metrics."""
    # TODO: Implement metrics collection
    return {
        "status": "healthy",
        "message": "Metrics endpoint not yet implemented"
    }


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "healthy"}
