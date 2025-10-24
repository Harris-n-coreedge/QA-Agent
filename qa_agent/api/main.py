"""
FastAPI application factory and routing configuration.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from qa_agent.api.routes import qa_tests, health
# Temporarily disabled problematic routes
# from qa_agent.api.routes import projects, targets, flows, runs, events, metrics, settings
# Temporarily disabled WebSocket routes
# from qa_agent.api.ws import runs as ws_runs, qa_tests as ws_qa_tests
from qa_agent.core.config import settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="QA Agent API",
        description="Backend service for synthetic QA agents using Kernel browsers",
        version="0.1.0",
        docs_url="/docs" if settings.ENV != "prod" else None,
        redoc_url="/redoc" if settings.ENV != "prod" else None,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.ENV == "local" else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(qa_tests.router, prefix="/api/v1/qa-tests", tags=["qa-tests"])
    # Temporarily disabled problematic routes
    # app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
    # app.include_router(targets.router, prefix="/api/v1", tags=["targets"])
    # app.include_router(flows.router, prefix="/api/v1", tags=["flows"])
    # app.include_router(runs.router, prefix="/api/v1", tags=["runs"])
    # app.include_router(events.router, prefix="/api/v1", tags=["events"])
    # app.include_router(metrics.router, prefix="/api/v1", tags=["metrics"])
    # app.include_router(settings.router, prefix="/api/v1", tags=["settings"])

    # Include WebSocket routes - temporarily disabled
    # app.include_router(ws_runs.router, prefix="/ws", tags=["websockets"])
    # app.include_router(ws_qa_tests.router, prefix="/ws", tags=["websockets"])

    return app


# Create the app instance
app = create_app()
