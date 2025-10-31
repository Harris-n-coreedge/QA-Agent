# Confidence Scoring System - Integration Guide

## Overview

The Confidence Scoring System adds intelligent action validation to your QA automation. When the AI model feels uncertain about an action (especially critical operations like purchases or deletions), it automatically flags the action for user review before execution.

## Key Features

- **Automatic Risk Detection**: Identifies critical operations (purchases, payments, deletions, etc.)
- **Confidence Scoring**: Calculates 0-100% confidence score for each action
- **User Approval Workflow**: Prompts users for approval on uncertain or critical actions
- **Non-Intrusive**: Original functionality remains unchanged
- **Separate Files**: All code in separate modules - main files untouched

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser Automation Flow                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Confident Browser Agent Wrapper                 │
│          (qa_agent/confident_browser_agent.py)               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Confidence Scorer                           │
│              (qa_agent/confidence_scorer.py)                 │
│  • Analyzes action context                                   │
│  • Calculates confidence score                               │
│  • Identifies risk factors                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                  Requires Approval?
                   /              \
                  /                \
                YES                 NO
                 │                   │
                 ▼                   ▼
┌─────────────────────────┐   Execute
│  Approval API Endpoint   │   Automatically
│  (qa_agent/api/routes/   │
│   approvals.py)          │
└─────────────────────────┘
                 │
                 ▼
┌─────────────────────────┐
│  Frontend Approval UI    │
│  (frontend/src/          │
│   components/            │
│   ApprovalPrompt.jsx)    │
└─────────────────────────┘
                 │
                 ▼
          User Decision
          (Allow/Deny)
```

## Files Created

All new files - no modifications to existing code:

### Backend

1. **`qa_agent/confidence_scorer.py`**
   - Core confidence scoring logic
   - Risk pattern detection
   - Confidence level calculation

2. **`qa_agent/confident_browser_agent.py`**
   - Wrapper around browser-use Agent
   - Integrates confidence scoring with browser automation

3. **`qa_agent/api/routes/approvals.py`**
   - API endpoints for approval requests
   - WebSocket support for real-time updates
   - Approval state management

4. **`qa_agent/integration/confidence_integration.py`**
   - Integration helpers
   - Easy drop-in replacement functions

### Frontend

5. **`frontend/src/components/ApprovalPrompt.jsx`**
   - React component for approval UI
   - Real-time polling for pending approvals
   - Beautiful modal with action details

## Quick Start

### Step 1: Update Backend API Routes

Add the approvals router to your FastAPI app:

```python
# In your main FastAPI app file (e.g., standalone_backend.py)
from qa_agent.api.routes.approvals import router as approvals_router

# Add this line with your other router includes
app.include_router(approvals_router, prefix="/api/v1")
```

### Step 2: Update Browser-Use Endpoint

Replace the standard browser-use agent with the confident version:

```python
# In standalone_backend.py, find the browser-use execute endpoint
# and update it like this:

from qa_agent.integration import ConfidenceIntegration

@app.post("/api/v1/qa-tests/browser-use/execute")
async def execute_browser_use(request: BrowserUseRequest):
    """Execute browser-use task WITH confidence scoring."""

    # Use the confident agent instead of regular agent
    result = await ConfidenceIntegration.execute_task_with_confidence_scoring(
        task=request.task,
        ai_provider=request.ai_provider or "google"
    )

    if result['success']:
        return {
            "terminal_output": result['result'],
            "statistics": result['statistics'],
            "action_history": result['action_history']
        }
    else:
        raise HTTPException(status_code=500, detail=result['error'])
```

### Step 3: Add Frontend Component

Update your QuickTest page (or any page that runs browser automation):

```jsx
// In frontend/src/pages/QuickTest.jsx
import ApprovalPrompt from '../components/ApprovalPrompt';

function QuickTest() {
  // ... your existing code ...

  return (
    <div>
      {/* Your existing UI */}

      {/* Add the approval prompt component */}
      <ApprovalPrompt apiBaseUrl="http://localhost:8000" />
    </div>
  );
}
```

### Step 4: Test It!

1. Start your backend server
2. Start your frontend
3. Enter a task that includes a critical action, e.g.:
   ```
   Go to wisemarket.com.pk, add a product to cart, and proceed to checkout
   ```
4. Watch as the system prompts you for approval at the checkout step!

## Configuration

### Confidence Levels

The system uses 4 confidence levels:

| Level | Score Range | Behavior |
|-------|-------------|----------|
| **HIGH** | 0.8 - 1.0 | Auto-execute |
| **MEDIUM** | 0.6 - 0.79 | Auto-execute with logging |
| **LOW** | 0.4 - 0.59 | Flag for review (optional approval) |
| **CRITICAL** | 0.0 - 0.39 | Require user approval |

### Customizing Risk Detection

Edit `qa_agent/confidence_scorer.py` to customize risk patterns:

```python
# Add your own critical keywords
self.critical_keywords = {
    'purchase': ['buy', 'purchase', 'checkout', 'place order'],
    'payment': ['payment', 'credit card', 'billing'],
    'delete': ['delete', 'remove', 'cancel'],
    'custom': ['your', 'custom', 'keywords'],  # Add your own!
}

# Add URL patterns for critical pages
self.critical_url_patterns = [
    r'checkout', r'payment', r'billing',
    r'your-custom-pattern',  # Add your own!
]
```

### Auto-Approval Settings

Control which confidence levels require approval:

```python
agent = ConfidentBrowserAgent(
    task=task,
    llm=llm,
    auto_approve_high_confidence=True,   # Auto-execute high confidence
    auto_approve_medium_confidence=True, # Auto-execute medium confidence
    log_all_actions=True                 # Log everything
)
```

## Usage Examples

### Example 1: Safe Navigation (High Confidence)

```python
task = "Go to example.com and click on the About link"
```

**Result**: Executes automatically (high confidence, no risk)

---

### Example 2: Critical Purchase (Requires Approval)

```python
task = """
Go to wisemarket.com.pk, search for iPhone, add to cart,
proceed to checkout and complete the purchase
"""
```

**Result**:
- Navigation: Auto-executes ✓
- Add to cart: Auto-executes ✓
- Proceed to checkout: **Prompts for approval** ⚠️
- Complete purchase: **Prompts for approval** ⚠️

---

### Example 3: Using in Code

```python
from qa_agent.integration import execute_with_confidence

# Execute with confidence scoring
result = await execute_with_confidence(
    task="Your task here",
    ai_provider="google"
)

if result['success']:
    print(f"Completed with {result['statistics']['total_actions']} actions")
    print(f"Required {result['statistics']['total_approvals_requested']} approvals")
else:
    print(f"Failed: {result['error']}")
```

## API Reference

### Backend Endpoints

#### POST `/api/v1/approvals/request`
Create a new approval request (called by backend internally).

#### GET `/api/v1/approvals/pending`
Get all pending approval requests (polled by frontend).

#### POST `/api/v1/approvals/respond`
Respond to an approval request with approve/deny.

```json
{
  "request_id": "uuid",
  "approved": true,
  "user_notes": "Optional notes"
}
```

#### WebSocket `/api/v1/approvals/ws`
Real-time updates for new approval requests.

### Frontend Component Props

```jsx
<ApprovalPrompt
  apiBaseUrl="http://localhost:8000"  // Backend URL
/>
```

## Advanced Usage

### Global Enablement

Enable confidence scoring for all agents:

```python
from qa_agent.integration import enable_confidence_scoring_globally

# At app startup
enable_confidence_scoring_globally()
```

### Custom Approval Callback

Implement your own approval logic:

```python
async def my_approval_callback(confidence_score, context, timeout):
    """Custom approval logic."""
    # Your logic here
    # Return True to approve, False to deny
    return True

from qa_agent.confidence_scorer import confidence_scorer
confidence_scorer.set_approval_callback(my_approval_callback)
```

### Manual Action Evaluation

Evaluate a specific action before executing:

```python
from qa_agent.confidence_scorer import confidence_scorer, ActionContext

context = ActionContext(
    action_description="Click the delete button",
    current_url="https://example.com/settings",
    element_text="Delete Account"
)

score = confidence_scorer.calculate_confidence(context)
print(f"Confidence: {score.level.value} ({score.score:.2f})")
print(f"Reasoning: {score.reasoning}")
print(f"Requires approval: {score.requires_approval}")
```

## Testing

### Test the Confidence Scorer

```bash
python qa_agent/confidence_scorer.py
```

This runs example scenarios and shows confidence calculations.

### Test the Integration

```bash
python qa_agent/integration/confidence_integration.py
```

## Troubleshooting

### Issue: Approvals not showing in frontend

**Solution**: Check that:
1. Approval router is added to FastAPI app
2. ApprovalPrompt component is rendered on the page
3. Backend is running and accessible
4. No CORS issues (check browser console)

### Issue: All actions auto-execute without approval

**Solution**: Check confidence score calculation:
```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

Ensure critical keywords match your use case.

### Issue: Too many approval prompts

**Solution**: Adjust auto-approval settings:
```python
agent = ConfidentBrowserAgent(
    task=task,
    llm=llm,
    auto_approve_medium_confidence=True  # Set to True to reduce prompts
)
```

## Performance Impact

- **Minimal**: ~5-10ms per action for confidence calculation
- **Non-blocking**: Approval requests run async
- **Scalable**: Uses in-memory storage (can switch to Redis)

## Future Enhancements

Potential improvements you can add:

1. **Machine Learning**: Train on user approval patterns
2. **Context Awareness**: Consider previous actions in flow
3. **User Profiles**: Different risk tolerances per user
4. **Audit Log**: Track all approval decisions
5. **Batch Approvals**: Approve multiple actions at once
6. **Time-based Rules**: Different rules for different times

## Support

For issues or questions:
1. Check this guide first
2. Review example files
3. Enable debug logging
4. Check the console for errors

## License

Same as main QA-Agent project.

---

**Built with safety in mind** 🛡️

The confidence scoring system helps prevent unintended actions while maintaining the flexibility and power of automated testing.
