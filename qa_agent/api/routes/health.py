"""
Health check endpoint for monitoring API status.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health")
async def health_check():
    """Check API health status."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "message": "QA Agent API is running",
            "version": "1.0.0"
        }
    )

