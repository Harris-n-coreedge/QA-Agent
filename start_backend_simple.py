"""
Simple backend starter script - runs standalone backend
"""
import uvicorn
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("=" * 50)
    print("Starting QA Agent Backend...")
    print("=" * 50)
    print(f"API: http://localhost:8000")
    print(f"Docs: http://localhost:8000/docs")
    print(f"Frontend: http://localhost:3000")
    print("=" * 50)

    # Use standalone backend (no dependencies on existing qa_agent routes)
    uvicorn.run(
        "standalone_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
