"""
Main application entrypoint.
"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from qa_agent.api.main import create_app
from qa_agent.core.config import settings
from qa_agent.core.db import create_db_and_tables, close_db_connections
from qa_agent.core.queues import close_queue_connections
from qa_agent.core.logging import configure_logging
from qa_agent.core.telemetry import setup_telemetry
from qa_agent.visibility.streams import event_stream_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    configure_logging()
    setup_telemetry()
    
    # Create database tables
    await create_db_and_tables()
    
    # Start event streaming
    await event_stream_manager.start()
    
    yield
    
    # Shutdown
    await event_stream_manager.stop()
    await close_queue_connections()
    await close_db_connections()


# Create FastAPI app with lifespan
app = create_app()
app.router.lifespan_context = lifespan


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "qa_agent.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.ENV == "local",
        log_level=settings.LOG_LEVEL.lower()
    )
