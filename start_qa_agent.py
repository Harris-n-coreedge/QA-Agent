"""
Startup script for the QA Agent with frontend.
This script starts both the FastAPI backend and the Next.js frontend.
"""
import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def start_backend():
    """Start the FastAPI backend."""
    print("🚀 Starting QA Agent Backend...")
    try:
        # Start the FastAPI backend
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "qa_agent.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8080", 
            "--reload"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start backend: {e}")
    except KeyboardInterrupt:
        print("🛑 Backend stopped by user")

def start_frontend():
    """Start the Next.js frontend."""
    print("🎨 Starting QA Agent Frontend...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found. Please run the setup first.")
        return
    
    try:
        # Change to frontend directory and start Next.js
        os.chdir(frontend_dir)
        subprocess.run(["npm", "run", "dev"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start frontend: {e}")
    except KeyboardInterrupt:
        print("🛑 Frontend stopped by user")

def main():
    """Main startup function."""
    print("🤖 QA Agent Dashboard Starting...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("qa_agent").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait a bit for backend to start
    print("⏳ Waiting for backend to start...")
    time.sleep(3)
    
    # Start frontend
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down QA Agent Dashboard...")
        print("✅ QA Agent Dashboard stopped")

if __name__ == "__main__":
    main()

