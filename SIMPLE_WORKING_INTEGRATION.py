"""
SIMPLE WORKING INTEGRATION
==========================

This is the ACTUAL working code to add to standalone_backend.py
It analyzes tasks BEFORE execution and prompts for approval if needed.

This approach WORKS because it checks the task description before running
browser-use, rather than trying to intercept individual actions.
"""

# ============================================================================
# ADD THIS CODE TO standalone_backend.py
# ============================================================================

# 1. ADD THESE IMPORTS AT THE TOP
"""
from qa_agent.task_confidence_checker import task_confidence_checker
from qa_agent.api.routes.approvals import (
    approval_manager,
    ApprovalRequest,
    broadcast_approval_update
)
"""

# 2. ADD THIS NEW ENDPOINT (or replace your existing browser-use endpoint)
"""
from fastapi import HTTPException
from pydantic import BaseModel
import os

class BrowserUseRequest(BaseModel):
    task: str
    ai_provider: str = "google"


@app.post("/api/v1/qa-tests/browser-use/execute")
async def execute_browser_use(request: BrowserUseRequest):
    '''Execute browser-use task with pre-execution confidence checking.'''

    # STEP 1: Analyze the task BEFORE execution
    should_prompt, analysis = task_confidence_checker.should_prompt_for_approval(request.task)

    # STEP 2: If risky, create approval request and wait
    if should_prompt:
        logger.info(
            f"Task requires approval - Risk: {analysis.risk_level.value}, "
            f"Confidence: {analysis.confidence_score:.0f}%"
        )

        # Create approval request
        approval_request = ApprovalRequest(
            action_description=request.task,
            current_url=None,
            element_text=None,
            confidence_score=analysis.confidence_score / 100,
            confidence_level=analysis.risk_level.value,
            reasoning=analysis.recommendation,
            risk_factors=analysis.risk_factors,
            timeout_seconds=60
        )

        # Store approval request
        request_id = approval_manager.create_approval_request(approval_request)

        # Broadcast to frontend
        await broadcast_approval_update({
            'type': 'new_request',
            'request_id': request_id,
            'action': request.task,
            'confidence_level': analysis.risk_level.value
        })

        # Wait for user response (60 seconds timeout)
        approved = await approval_manager.wait_for_response(request_id, timeout=60)

        if not approved:
            logger.warning("Task execution denied by user or timeout")
            return {
                "terminal_output": "❌ Task execution denied by user or timed out.",
                "status": "denied",
                "analysis": {
                    "risk_level": analysis.risk_level.value,
                    "confidence": analysis.confidence_score,
                    "operations": analysis.detected_operations
                }
            }

        logger.info("Task execution approved by user")

    # STEP 3: Execute the task (only if approved or safe)
    try:
        from browser_use import Agent as BrowserAgent, ChatGoogle

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not configured")

        llm = ChatGoogle(model="gemini-flash-latest", api_key=api_key)
        agent = BrowserAgent(task=request.task, llm=llm)

        # Run the agent
        history = await agent.run()

        # Format output
        from qa_agent.utils.browser_use_parser import format_terminal_output_simple
        terminal_output = format_terminal_output_simple(history, request.task)

        return {
            "terminal_output": terminal_output,
            "status": "completed",
            "analysis": {
                "risk_level": analysis.risk_level.value,
                "confidence": analysis.confidence_score,
                "operations": analysis.detected_operations,
                "required_approval": should_prompt
            }
        }

    except Exception as e:
        logger.error(f"Error executing browser-use task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
"""

# 3. REGISTER THE APPROVALS ROUTER (add near other app.include_router calls)
"""
from qa_agent.api.routes.approvals import router as approvals_router
app.include_router(approvals_router, prefix="/api/v1")
"""

# ============================================================================
# THAT'S IT! Just those 3 sections above.
# ============================================================================

# ============================================================================
# COMPLETE EXAMPLE FOR COPY-PASTE
# ============================================================================

COMPLETE_WORKING_CODE = '''
# At the TOP of standalone_backend.py, add these imports:
from qa_agent.task_confidence_checker import task_confidence_checker
from qa_agent.api.routes.approvals import (
    router as approvals_router,
    approval_manager,
    ApprovalRequest,
    broadcast_approval_update
)

# After creating your FastAPI app, add:
app.include_router(approvals_router, prefix="/api/v1")

# Find your browser-use endpoint (around line 672) and REPLACE with:
@app.post("/api/v1/qa-tests/browser-use/execute")
async def execute_browser_use(request: BrowserUseRequest):
    """Execute browser-use with confidence checking."""

    # Analyze task first
    should_prompt, analysis = task_confidence_checker.should_prompt_for_approval(request.task)

    # If risky, wait for approval
    if should_prompt:
        approval_request = ApprovalRequest(
            action_description=request.task,
            current_url=None,
            element_text=None,
            confidence_score=analysis.confidence_score / 100,
            confidence_level=analysis.risk_level.value,
            reasoning=analysis.recommendation,
            risk_factors=analysis.risk_factors,
            timeout_seconds=60
        )

        request_id = approval_manager.create_approval_request(approval_request)

        await broadcast_approval_update({
            'type': 'new_request',
            'request_id': request_id,
            'action': request.task,
            'confidence_level': analysis.risk_level.value
        })

        approved = await approval_manager.wait_for_response(request_id, timeout=60)

        if not approved:
            return {
                "terminal_output": "❌ Task execution denied by user or timed out.",
                "status": "denied"
            }

    # Execute the task
    from browser_use import Agent as BrowserAgent, ChatGoogle
    import os

    api_key = os.getenv("GOOGLE_API_KEY")
    llm = ChatGoogle(model="gemini-flash-latest", api_key=api_key)
    agent = BrowserAgent(task=request.task, llm=llm)
    history = await agent.run()

    from qa_agent.utils.browser_use_parser import format_terminal_output_simple
    terminal_output = format_terminal_output_simple(history, request.task)

    return {"terminal_output": terminal_output, "status": "completed"}
'''

print(COMPLETE_WORKING_CODE)
print("\n" + "="*70)
print("TESTING:")
print("="*70)
print("""
1. Add the code above to standalone_backend.py
2. Add <ApprovalPrompt /> to QuickTest.jsx
3. Test with: "Go to wisemarket.com.pk and complete checkout"
4. You should see approval prompt BEFORE the browser even opens!
""")
