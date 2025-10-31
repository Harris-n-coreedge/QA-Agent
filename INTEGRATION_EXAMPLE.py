"""
INTEGRATION EXAMPLE
===================

This file shows exactly how to integrate the confidence scoring system
into your existing standalone_backend.py file.

STEPS TO INTEGRATE:
"""

# ============================================================================
# STEP 1: Add these imports at the top of standalone_backend.py
# ============================================================================

from qa_agent.api.routes.approvals import router as approvals_router
from qa_agent.integration import ConfidenceIntegration

# ============================================================================
# STEP 2: Register the approvals router with your FastAPI app
# ============================================================================

# Find where you have other app.include_router() calls and add:
# app.include_router(approvals_router, prefix="/api/v1")

# ============================================================================
# STEP 3: Update your browser-use execute endpoint
# ============================================================================

# ORIGINAL CODE (around line 672 in standalone_backend.py):
# -------------
"""
@app.post("/api/v1/qa-tests/browser-use/execute")
async def execute_browser_use(request: BrowserUseRequest):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not configured")

    llm = ChatGoogle(model="gemini-flash-latest", api_key=api_key)
    agent = BrowserAgent(task=request.task, llm=llm)
    history = await agent.run()

    terminal_output = format_terminal_output_simple(history, request.task)
    return {"terminal_output": terminal_output}
"""

# NEW CODE WITH CONFIDENCE SCORING:
# ----------------------------------
"""
@app.post("/api/v1/qa-tests/browser-use/execute")
async def execute_browser_use(request: BrowserUseRequest):
    '''Execute browser-use task WITH confidence scoring for critical actions.'''

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not configured")

    # Use the confident agent instead of regular agent
    result = await ConfidenceIntegration.execute_task_with_confidence_scoring(
        task=request.task,
        ai_provider=request.ai_provider if hasattr(request, 'ai_provider') else "google",
        api_key=api_key
    )

    if result['success']:
        # Format the output as before
        from qa_agent.utils.browser_use_parser import format_terminal_output_simple
        terminal_output = format_terminal_output_simple(result['result'], request.task)

        return {
            "terminal_output": terminal_output,
            "statistics": result['statistics'],  # New: action statistics
            "action_history": result['action_history']  # New: detailed action log
        }
    else:
        raise HTTPException(status_code=500, detail=result['error'])
"""

# ============================================================================
# STEP 4: Add the frontend component to QuickTest.jsx
# ============================================================================

# Add to frontend/src/pages/QuickTest.jsx:
"""
import ApprovalPrompt from '../components/ApprovalPrompt';

// Inside your component's return statement, add:
<ApprovalPrompt apiBaseUrl="http://localhost:8000" />
"""

# ============================================================================
# COMPLETE EXAMPLE: Minimal Changes to standalone_backend.py
# ============================================================================

COMPLETE_EXAMPLE = """
# At the top of standalone_backend.py, add these two lines:
from qa_agent.api.routes.approvals import router as approvals_router
from qa_agent.integration import ConfidenceIntegration

# After creating your FastAPI app, add this line:
app.include_router(approvals_router, prefix="/api/v1")

# Replace your browser-use execute endpoint with:
@app.post("/api/v1/qa-tests/browser-use/execute")
async def execute_browser_use(request: BrowserUseRequest):
    '''Execute browser-use task WITH confidence scoring.'''
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not configured")

    # Execute with confidence scoring
    result = await ConfidenceIntegration.execute_task_with_confidence_scoring(
        task=request.task,
        ai_provider="google",
        api_key=api_key
    )

    if result['success']:
        from qa_agent.utils.browser_use_parser import format_terminal_output_simple
        terminal_output = format_terminal_output_simple(result['result'], request.task)
        return {
            "terminal_output": terminal_output,
            "statistics": result['statistics']
        }
    else:
        raise HTTPException(status_code=500, detail=result['error'])

# That's it! Only 3 lines of imports and replacing one endpoint.
"""

# ============================================================================
# ALTERNATIVE: Keep Original Endpoint, Add New One
# ============================================================================

# If you want to keep the original endpoint unchanged, add a NEW endpoint:
NEW_ENDPOINT_EXAMPLE = """
# Add this as a NEW endpoint (keep your original one unchanged)
@app.post("/api/v1/qa-tests/browser-use/execute-with-confidence")
async def execute_browser_use_with_confidence(request: BrowserUseRequest):
    '''Execute browser-use task WITH confidence scoring.'''
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not configured")

    result = await ConfidenceIntegration.execute_task_with_confidence_scoring(
        task=request.task,
        ai_provider="google",
        api_key=api_key
    )

    if result['success']:
        from qa_agent.utils.browser_use_parser import format_terminal_output_simple
        terminal_output = format_terminal_output_simple(result['result'], request.task)
        return {
            "terminal_output": terminal_output,
            "statistics": result['statistics']
        }
    else:
        raise HTTPException(status_code=500, detail=result['error'])

# Then update frontend to use the new endpoint when you want confidence scoring
"""

# ============================================================================
# TESTING YOUR INTEGRATION
# ============================================================================

TESTING_STEPS = """
1. Start your backend:
   python standalone_backend.py

2. Start your frontend:
   cd frontend && npm run dev

3. Open QuickTest page

4. Enter a test prompt with a critical action:
   "Go to wisemarket.com.pk, add iPhone to cart, and proceed to checkout"

5. Watch for the approval prompt when it reaches checkout!

6. Test different scenarios:
   - Safe action: "Go to example.com" → Auto-executes
   - Critical action: "Complete the purchase" → Prompts for approval
   - Medium risk: "Click on login" → Auto-executes with logging
"""

print(COMPLETE_EXAMPLE)
print("\n" + "="*70)
print("TESTING STEPS:")
print("="*70)
print(TESTING_STEPS)
