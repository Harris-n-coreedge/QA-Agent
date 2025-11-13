"""
Minimal backend for testing - starts immediately without full dependencies
"""
from datetime import datetime
from typing import Dict, List, Optional
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

app = FastAPI(title="QA Agent API - Minimal")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/qa-tests/health")
async def health():
    return {
        "status": "healthy",
        "active_sessions": 0,
        "total_test_results": 0,
        "timestamp": "2024-01-01T00:00:00",
        "message": "Minimal backend running - install full dependencies for complete functionality"
    }

@app.get("/api/v1/qa-tests/sessions")
async def list_sessions():
    return {
        "sessions": [],
        "total": 0,
        "message": "No sessions - install full dependencies to create sessions"
    }

@app.get("/api/v1/qa-tests/test-results")
async def list_results():
    return {
        "results": [],
        "total": 0,
        "filtered_by_session": None
    }

@app.get("/")
async def root():
    return {
        "message": "QA Agent Minimal Backend",
        "status": "running",
        "docs": "/docs",
        "note": "This is a minimal backend. Install full dependencies for complete functionality."
    }


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = Field(default=None, description="Existing conversation identifier")
    message: str = Field(..., description="User message to send to the QA assistant")
    history: List[ChatMessage] = Field(default_factory=list, description="Optional prior history")
    persona: Optional[str] = Field(default=None, description="Optional persona label")


class ChatReply(BaseModel):
    id: str
    role: str
    content: str
    timestamp: str


class ChatResponse(BaseModel):
    conversation_id: str
    reply: ChatReply
    usage: Optional[Dict[str, Optional[int]]] = None
    suggestions: Optional[List[str]] = None


@app.post("/api/v1/qa-tests/chat", response_model=ChatResponse)
async def chat_stub(request: ChatRequest):
    """
    Minimal stub for the QA chat endpoint.
    Returns a canned response to keep the frontend functional when the full backend isn't available.
    """
    conversation_id = request.conversation_id or str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    reply_text = (
        "This is the minimal backend stub. Configure and run the full standalone backend to get "
        "Gemini-powered QA insights. In the meantime, document your goals and I'll flag that the "
        "real assistant is offline."
    )

    reply = ChatReply(
        id=str(uuid.uuid4()),
        role="assistant",
        content=reply_text,
        timestamp=timestamp,
    )

    suggestions = [
        "Launch the full standalone backend for live QA analytics",
        "Verify GOOGLE_API_KEY is set in your environment",
        "Re-run the chat once the main service is online",
    ]

    return ChatResponse(
        conversation_id=conversation_id,
        reply=reply,
        usage=None,
        suggestions=suggestions,
    )

if __name__ == "__main__":
    print("=" * 50)
    print("Starting Minimal Backend...")
    print("This will let the frontend connect while you fix dependencies")
    print("=" * 50)
    print("API: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("=" * 50)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
