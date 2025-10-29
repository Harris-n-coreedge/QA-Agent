"""
Simple test to verify backend can start
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing backend imports...")
print("=" * 50)

# Test 1: Import FastAPI
try:
    from fastapi import FastAPI
    print("✅ FastAPI imported successfully")
except ImportError as e:
    print(f"❌ FastAPI import failed: {e}")
    print("   Run: pip install fastapi")

# Test 2: Import uvicorn
try:
    import uvicorn
    print("✅ uvicorn imported successfully")
except ImportError as e:
    print(f"❌ uvicorn import failed: {e}")
    print("   Run: pip install uvicorn")

# Test 3: Import qa_agent.api.main
try:
    from qa_agent.api.main import app
    print("✅ QA Agent API imported successfully")
except Exception as e:
    print(f"❌ QA Agent API import failed: {e}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

# Test 4: Check if multi_ai_qa_agent.py exists
multi_ai_path = os.path.join(os.path.dirname(__file__), "multi_ai_qa_agent.py")
if os.path.exists(multi_ai_path):
    print(f"✅ multi_ai_qa_agent.py found at {multi_ai_path}")
else:
    print(f"❌ multi_ai_qa_agent.py not found at {multi_ai_path}")

# Test 5: Check if broswer_use.py exists
browser_use_path = os.path.join(os.path.dirname(__file__), "broswer_use.py")
if os.path.exists(browser_use_path):
    print(f"✅ broswer_use.py found at {browser_use_path}")
else:
    print(f"❌ broswer_use.py not found at {browser_use_path}")

# Test 6: Check .env file
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    print(f"✅ .env file found")

    # Check for API keys
    from dotenv import load_dotenv
    load_dotenv()

    has_key = False
    if os.getenv("OPENAI_API_KEY"):
        print("   ✅ OPENAI_API_KEY found")
        has_key = True
    if os.getenv("ANTHROPIC_API_KEY"):
        print("   ✅ ANTHROPIC_API_KEY found")
        has_key = True
    if os.getenv("GOOGLE_API_KEY"):
        print("   ✅ GOOGLE_API_KEY found")
        has_key = True

    if not has_key:
        print("   ⚠️ No AI provider API keys found in .env")
else:
    print(f"❌ .env file not found at {env_path}")

print("=" * 50)
print("\nIf all tests pass, you can start the backend with:")
print("  python start_backend_simple.py")
print("\nOr:")
print("  uvicorn qa_agent.api.main:app --reload --host 0.0.0.0 --port 8000")
