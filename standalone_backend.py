"""
Standalone QA Agent Backend - Works independently of existing qa_agent package
This provides the full functionality for the frontend without dependencies on other routes
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
import asyncio
import json
from datetime import datetime
import uuid
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="QA Agent API",
    description="Backend service for multi-AI QA automation",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active agent sessions
active_sessions: Dict[str, Any] = {}
test_results: Dict[str, Dict] = {}


class AIProvider(str, Enum):
    """Supported AI providers"""
    openai = "openai"
    anthropic = "anthropic"
    google = "google"


class TestStatus(str, Enum):
    """Test execution status"""
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class SessionCreateRequest(BaseModel):
    """Request to create a new QA agent session"""
    website_url: str = Field(default="https://www.w3schools.com/", description="Website URL to test")
    ai_provider: AIProvider = Field(default=AIProvider.openai, description="AI provider to use")
    auto_check: bool = Field(default=True, description="Run automatic checks on page load")
    session_name: Optional[str] = Field(default=None, description="Custom session name")


class CommandRequest(BaseModel):
    """Request to execute a command in a session"""
    session_id: str = Field(..., description="Session ID")
    command: str = Field(..., description="Natural language command to execute")


class BrowserUseRequest(BaseModel):
    """Request for browser-use simple automation"""
    task: str = Field(..., description="Task description for browser automation")
    ai_provider: AIProvider = Field(default=AIProvider.google, description="AI provider (default: google)")


class SessionResponse(BaseModel):
    """Response after creating a session"""
    session_id: str
    website_url: str
    ai_provider: str
    status: str
    created_at: str
    message: str


class CommandResponse(BaseModel):
    """Response after executing a command"""
    session_id: str
    command: str
    result: str
    status: TestStatus
    executed_at: str
    duration_ms: Optional[float] = None


class TestResultResponse(BaseModel):
    """Test result details"""
    test_id: str
    session_id: str
    command: str
    status: TestStatus
    result: str
    started_at: str
    completed_at: Optional[str] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "QA Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/qa-tests/health"
    }


@app.get("/api/v1/qa-tests/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_sessions": len(active_sessions),
        "total_test_results": len(test_results),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/qa-tests/sessions", response_model=SessionResponse)
async def create_session(request: SessionCreateRequest, background_tasks: BackgroundTasks):
    """
    Create a new QA agent session with browser automation.
    """
    try:
        # Try to import MultiAIQAAgent
        try:
            from multi_ai_qa_agent import MultiAIQAAgent
        except ImportError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to import MultiAIQAAgent. Make sure multi_ai_qa_agent.py exists in the project root. Error: {str(e)}"
            )

        # Generate session ID
        session_id = str(uuid.uuid4())
        session_name = request.session_name or f"Session-{session_id[:8]}"

        # Get API key from environment
        from dotenv import load_dotenv
        load_dotenv()

        api_key = None
        if request.ai_provider == AIProvider.openai:
            api_key = os.getenv("OPENAI_API_KEY")
        elif request.ai_provider == AIProvider.anthropic:
            api_key = os.getenv("ANTHROPIC_API_KEY")
        elif request.ai_provider == AIProvider.google:
            api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise HTTPException(
                status_code=400,
                detail=f"API key for {request.ai_provider} not found in environment variables. Please add it to your .env file."
            )

        # Initialize the agent
        agent = MultiAIQAAgent(
            ai_provider=request.ai_provider.value,
            api_key=api_key
        )

        # Store session info
        session_info = {
            "session_id": session_id,
            "session_name": session_name,
            "agent": agent,
            "website_url": request.website_url,
            "ai_provider": request.ai_provider.value,
            "status": "initializing",
            "created_at": datetime.utcnow().isoformat(),
            "commands_executed": 0
        }
        active_sessions[session_id] = session_info

        # Start session in background
        async def start_agent_session():
            try:
                await agent.start_session(
                    website_url=request.website_url,
                    auto_check=request.auto_check
                )
                active_sessions[session_id]["status"] = "active"
            except Exception as e:
                active_sessions[session_id]["status"] = "failed"
                active_sessions[session_id]["error"] = str(e)

        background_tasks.add_task(start_agent_session)

        return SessionResponse(
            session_id=session_id,
            website_url=request.website_url,
            ai_provider=request.ai_provider.value,
            status="initializing",
            created_at=session_info["created_at"],
            message=f"Session '{session_name}' created successfully. Initializing browser..."
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@app.get("/api/v1/qa-tests/sessions/{session_id}")
async def get_session(session_id: str):
    """Get details about a specific session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    session = active_sessions[session_id]
    return {
        "session_id": session["session_id"],
        "session_name": session["session_name"],
        "website_url": session["website_url"],
        "ai_provider": session["ai_provider"],
        "status": session["status"],
        "created_at": session["created_at"],
        "commands_executed": session["commands_executed"],
        "error": session.get("error")
    }


@app.get("/api/v1/qa-tests/sessions")
async def list_sessions():
    """List all active sessions"""
    return {
        "sessions": [
            {
                "session_id": s["session_id"],
                "session_name": s["session_name"],
                "website_url": s["website_url"],
                "ai_provider": s["ai_provider"],
                "status": s["status"],
                "created_at": s["created_at"],
                "commands_executed": s["commands_executed"]
            }
            for s in active_sessions.values()
        ],
        "total": len(active_sessions)
    }


@app.post("/api/v1/qa-tests/sessions/{session_id}/commands", response_model=CommandResponse)
async def execute_command(session_id: str, request: CommandRequest):
    """Execute a natural language command in an active session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    session = active_sessions[session_id]

    if session["status"] != "active":
        raise HTTPException(
            status_code=400,
            detail=f"Session is not active. Current status: {session['status']}"
        )

    try:
        agent = session["agent"]
        start_time = datetime.utcnow()

        # Execute the command
        result = await agent.process_command(request.command)

        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000

        # Update session stats
        session["commands_executed"] += 1

        # Store test result
        test_id = str(uuid.uuid4())
        test_results[test_id] = {
            "test_id": test_id,
            "session_id": session_id,
            "command": request.command,
            "result": result,
            "status": TestStatus.completed,
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat(),
            "duration_ms": duration_ms
        }

        return CommandResponse(
            session_id=session_id,
            command=request.command,
            result=result,
            status=TestStatus.completed,
            executed_at=end_time.isoformat(),
            duration_ms=duration_ms
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {str(e)}")


@app.delete("/api/v1/qa-tests/sessions/{session_id}")
async def close_session(session_id: str):
    """Close and cleanup a session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    session = active_sessions[session_id]

    try:
        # Close the agent's browser
        agent = session["agent"]
        if hasattr(agent, 'browser') and agent.browser:
            await agent.browser.close()
        if hasattr(agent, 'playwright') and agent.playwright:
            await agent.playwright.stop()

        # Remove from active sessions
        del active_sessions[session_id]

        return {
            "message": f"Session {session_id} closed successfully",
            "session_id": session_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to close session: {str(e)}")


@app.post("/api/v1/qa-tests/browser-use/execute")
async def execute_browser_use(request: BrowserUseRequest):
    """
    Execute a simple browser automation task using browser-use library.
    """
    try:
        # Import browser_use components
        try:
            from browser_use import Agent as BrowserAgent, ChatGoogle
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="browser-use library not installed. Install with: pip install browser-use"
            )

        # Import appropriate chat model
        if request.ai_provider == AIProvider.google:
            # Get API key from environment
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise HTTPException(
                    status_code=400,
                    detail="Google API key not found in environment variables. Please add GOOGLE_API_KEY to your .env file."
                )
            llm = ChatGoogle(model="gemini-flash-latest", api_key=api_key)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Browser-use currently only supports Google AI provider"
            )

        # Create agent and execute task
        agent = BrowserAgent(task=request.task, llm=llm)

        # Run the task
        result = await agent.run()

        return {
            "task": request.task,
            "status": "completed",
            "result": str(result),
            "executed_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Browser automation failed: {str(e)}")


@app.get("/api/v1/qa-tests/test-results/{test_id}", response_model=TestResultResponse)
async def get_test_result(test_id: str):
    """Get details of a specific test result"""
    if test_id not in test_results:
        raise HTTPException(status_code=404, detail=f"Test result {test_id} not found")

    return test_results[test_id]


@app.get("/api/v1/qa-tests/test-results")
async def list_test_results(session_id: Optional[str] = None, limit: int = 50):
    """List test results, optionally filtered by session"""
    results = list(test_results.values())

    if session_id:
        results = [r for r in results if r["session_id"] == session_id]

    # Sort by most recent first
    results.sort(key=lambda x: x["started_at"], reverse=True)

    return {
        "results": results[:limit],
        "total": len(results),
        "filtered_by_session": session_id
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("QA Agent Backend - Standalone Version")
    print("=" * 60)
    print(f"API: http://localhost:8000")
    print(f"Docs: http://localhost:8000/docs")
    print(f"Frontend: http://localhost:3000")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
