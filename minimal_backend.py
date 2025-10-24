"""
Minimal backend for testing - starts immediately without full dependencies
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

if __name__ == "__main__":
    print("=" * 50)
    print("Starting Minimal Backend...")
    print("This will let the frontend connect while you fix dependencies")
    print("=" * 50)
    print("API: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("=" * 50)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
