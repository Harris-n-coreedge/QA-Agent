# Quick Start - Confidence Scoring (5 Minutes)

## What You Get

✅ Automatic detection of risky operations (purchases, deletions, payments)
✅ User approval prompt BEFORE executing critical tasks
✅ Beautiful modal UI showing risk level and reasoning
✅ Zero changes to main code - all in separate files

## How It Works

```
User enters: "Go to wisemarket.com.pk and complete checkout"
        ↓
Backend analyzes task BEFORE execution
        ↓
Detects: "checkout" = RISKY
        ↓
Shows approval modal to user:
  ⚠️ APPROVAL REQUIRED
  Risk: CRITICAL
  Detected: Checkout process
        ↓
User clicks "Approve" or "Deny"
        ↓
If approved → Opens browser and runs task
If denied → Stops immediately
```

## Installation (3 Steps)

### Step 1: Update Backend (standalone_backend.py)

**Add these imports at the top:**
```python
from qa_agent.task_confidence_checker import task_confidence_checker
from qa_agent.api.routes.approvals import (
    router as approvals_router,
    approval_manager,
    ApprovalRequest,
    broadcast_approval_update
)
```

**Register the approvals router (add near other app.include_router lines):**
```python
app.include_router(approvals_router, prefix="/api/v1")
```

**Find your browser-use endpoint (around line 672) and replace it with:**
```python
@app.post("/api/v1/qa-tests/browser-use/execute")
async def execute_browser_use(request: BrowserUseRequest):
    """Execute with confidence checking."""

    # Analyze task BEFORE execution
    should_prompt, analysis = task_confidence_checker.should_prompt_for_approval(request.task)

    # If risky, wait for user approval
    if should_prompt:
        approval_req = ApprovalRequest(
            action_description=request.task,
            current_url=None,
            element_text=None,
            confidence_score=analysis.confidence_score / 100,
            confidence_level=analysis.risk_level.value,
            reasoning=analysis.recommendation,
            risk_factors=analysis.risk_factors,
            timeout_seconds=60
        )

        request_id = approval_manager.create_approval_request(approval_req)

        await broadcast_approval_update({
            'type': 'new_request',
            'request_id': request_id,
            'action': request.task,
            'confidence_level': analysis.risk_level.value
        })

        approved = await approval_manager.wait_for_response(request_id, timeout=60)

        if not approved:
            return {
                "terminal_output": "❌ Task denied or timed out.",
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
```

### Step 2: Update Frontend (QuickTest.jsx)

**Add import at the top:**
```jsx
import ApprovalPrompt from '../components/ApprovalPrompt';
```

**Add component inside your component's return (anywhere in the JSX):**
```jsx
<ApprovalPrompt apiBaseUrl="http://localhost:8000" />
```

Example:
```jsx
function QuickTest() {
  return (
    <div>
      {/* Your existing UI */}
      <ApprovalPrompt apiBaseUrl="http://localhost:8000" />
    </div>
  );
}
```

### Step 3: Test It!

1. **Start backend:**
   ```bash
   python standalone_backend.py
   ```

2. **Start frontend:**
   ```bash
   cd frontend && npm run dev
   ```

3. **Test with risky task:**
   - Go to QuickTest page
   - Enter: `Go to wisemarket.com.pk, add product to cart, and complete the checkout`
   - Click Run
   - **You should see approval modal appear!**

4. **Test with safe task:**
   - Enter: `Go to example.com and click About`
   - Click Run
   - **Should execute immediately without prompt**

## Examples

### Safe Task (No Prompt)
```
"Go to google.com and search for iPhone"
```
→ Executes immediately ✅

### Risky Task (Shows Approval)
```
"Go to wisemarket.com.pk and complete checkout"
```
→ Shows modal: ⚠️ APPROVAL REQUIRED - Risk: CRITICAL

### Critical Task (Shows Strong Warning)
```
"Enter credit card details and submit payment"
```
→ Shows modal with all detected risks

## Customization

### Add Your Own Risk Keywords

Edit `qa_agent/task_confidence_checker.py`:

```python
self.critical_patterns = {
    'purchase': {
        'keywords': ['buy', 'purchase', 'your-keyword-here'],  # Add yours!
        'weight': 1.0,
        'description': 'Purchase operation'
    },
    'custom_operation': {  # Add new operation
        'keywords': ['dangerous', 'risky'],
        'weight': 0.9,
        'description': 'Custom risky operation'
    }
}
```

### Change Timeout

In the backend code, change:
```python
timeout_seconds=60  # Change to 120 for 2 minutes
```

## Troubleshooting

### Problem: No approval modal appears

**Check:**
1. Is `ApprovalPrompt` component added to QuickTest.jsx?
2. Is backend running?
3. Check browser console for errors (F12)
4. Check backend logs for "Task requires approval" message

**Fix:**
```bash
# Restart both servers
# Check browser console
# Verify imports are correct
```

### Problem: All tasks require approval

**Check:** Your task might have trigger words. Test with:
```
"Go to example.com"  # Should NOT prompt
```

### Problem: Approval modal stuck

**Fix:** Refresh the page. The modal polls every 2 seconds for pending approvals.

## What's Detected as Risky?

| Keywords | Risk Level |
|----------|------------|
| checkout, complete checkout | CRITICAL |
| purchase, buy, place order | CRITICAL |
| payment, credit card, cvv | CRITICAL |
| delete account, remove account | CRITICAL |
| transfer money, send money | CRITICAL |
| login, sign in | MODERATE |

## Files Created

- `qa_agent/task_confidence_checker.py` - Risk analysis
- `qa_agent/api/routes/approvals.py` - API endpoints
- `frontend/src/components/ApprovalPrompt.jsx` - UI modal
- Documentation files (this file, guides, examples)

## Next Steps

1. ✅ Test with various tasks
2. ✅ Customize risk keywords for your use case
3. ✅ Adjust timeout if needed
4. ✅ Add more trigger words

## Support

**Test the checker directly:**
```bash
python qa_agent/task_confidence_checker.py
```

This shows how different tasks are analyzed.

---

**That's it!** 🎉 Your QA automation now has intelligent risk detection and user approval for critical operations.
