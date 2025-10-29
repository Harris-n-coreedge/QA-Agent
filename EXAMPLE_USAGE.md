# Structured Output Example Usage

This document shows how to use the structured output feature with browser-use agent history.

## Quick Start

### 1. Backend Endpoint Call

```python
# In your FastAPI endpoint
from qa_agent.utils.browser_use_parser import parse_agent_history, format_history_for_display
from browser_use import Agent, ChatGoogle

@app.post("/api/v1/qa-tests/browser-use/execute")
async def execute_browser_use(request: BrowserUseRequest):
    llm = ChatGoogle(model="gemini-flash-latest", api_key=os.getenv("GOOGLE_API_KEY"))
    agent = Agent(task=request.task, llm=llm)
    
    # Run and get history
    history = await agent.run()
    
    # Parse into structured format
    structured_history = parse_agent_history(history, request.task)
    
    # Format for display
    formatted_history = format_history_for_display(structured_history)
    
    return {
        "task": request.task,
        "status": "completed",
        "structured_history": structured_history.model_dump(),
        "formatted_summary": formatted_history,
        "executed_at": datetime.utcnow().isoformat()
    }
```

### 2. Response Structure

The endpoint returns two data formats:

#### A. Full Structured History (`structured_history`)
Contains complete Pydantic models with all action details:

```python
{
    "task": "Your task",
    "status": "completed",
    "total_steps": 5,
    "actions": [
        {
            "step_number": 1,
            "action_result": {
                "is_done": False,
                "success": None,
                "extracted_content": "Navigated to https://example.com",
                "long_term_memory": "...",
                "metadata": {...}
            },
            "model_action": {
                "action_type": "navigate",
                "navigate": {
                    "url": "https://example.com",
                    "new_tab": False
                }
            }
        },
        # ... more actions
    ],
    "visited_urls": ["https://example.com", ...],
    "extracted_content": [...],
    "errors": [],
    "final_result": "...",
    "is_done": True,
    "is_successful": True,
    "has_errors": False
}
```

#### B. Formatted Summary (`formatted_summary`)
Simplified format for easy display:

```python
{
    "task": "Your task",
    "status": "completed",
    "summary": {
        "total_steps": 5,
        "visited_urls_count": 3,
        "has_errors": False,
        "is_successful": True,
        "is_done": True
    },
    "visited_urls": ["https://example.com"],
    "final_result": "...",
    "actions_summary": [
        {
            "step": 1,
            "action_type": "navigate",
            "extracted_content": "Navigated to...",
            "error": None,
            "success": True
        },
        # ... more actions
    ]
}
```

## 3. Frontend Usage

The frontend automatically displays both formats:

```jsx
// Display structured data
{result.formatted_summary && (
  <div>
    <h3>Execution Summary</h3>
    
    {/* Summary Stats */}
    <div>
      <p>Total Steps: {result.formatted_summary.summary.total_steps}</p>
      <p>Visited URLs: {result.formatted_summary.summary.visited_urls_count}</p>
      <p>Status: {result.formatted_summary.summary.is_successful ? 'Success' : 'Failed'}</p>
    </div>
    
    {/* Visited URLs */}
    <div>
      {result.formatted_summary.visited_urls.map(url => (
        <a href={url}>{url}</a>
      ))}
    </div>
    
    {/* Actions Timeline */}
    <div>
      {result.formatted_summary.actions_summary.map(action => (
        <div key={action.step}>
          Step {action.step}: {action.action_type}
          {action.extracted_content && <p>{action.extracted_content}</p>}
          {action.error && <p style={{color: 'red'}}>{action.error}</p>}
        </div>
      ))}
    </div>
    
    {/* Final Result */}
    <pre>{result.formatted_summary.final_result}</pre>
  </div>
)}
```

## 4. Direct Python Usage

You can also use the parser directly in Python code:

```python
from qa_agent.utils.browser_use_parser import parse_agent_history, format_history_for_display
from browser_use import Agent, ChatGoogle

# Setup and run agent
llm = ChatGoogle(model="gemini-flash-latest", api_key="your-key")
agent = Agent(task="Your task", llm=llm)
history = await agent.run()

# Parse structured data
structured = parse_agent_history(history, "Your task")

# Access specific fields
print(f"Total steps: {structured.total_steps}")
print(f"Visited URLs: {structured.visited_urls}")
print(f"Final result: {structured.final_result}")
print(f"Is successful: {structured.is_successful}")

# Iterate through actions
for action in structured.actions:
    print(f"Step {action.step_number}")
    if action.model_action:
        print(f"  Action type: {action.model_action.action_type}")
    
    if action.action_result.extracted_content:
        print(f"  Extracted: {action.action_result.extracted_content}")
    
    if action.action_result.error:
        print(f"  Error: {action.action_result.error}")

# Get formatted summary for display
formatted = format_history_for_display(structured)
print(f"Summary stats: {formatted['summary']}")
```

## 5. Data Models

### AgentAction Models

- **NavigateAction**: URL navigation
- **ClickAction**: Element clicking
- **InputAction**: Text input
- **ExtractAction**: Content extraction
- **DoneAction**: Task completion

### Element Information

- **DOMInteractedElement**: Full DOM element details
- **DOMRect**: Element bounding box
- **ActionResult**: Action execution results

### Complete History

- **ActionHistory**: Single action with result and model action
- **StructuredAgentHistory**: Complete execution history

## 6. Benefits

1. ✅ **Type-Safe**: Pydantic models ensure data integrity
2. ✅ **Structured**: Organized action history
3. ✅ **Error Tracking**: Separate error lists
4. ✅ **Element Details**: Full DOM interaction info
5. ✅ **Display Ready**: Pre-formatted summary included
6. ✅ **API Integration**: Ready for frontend consumption

## Next Steps

See `STRUCTURED_OUTPUT_GUIDE.md` for detailed documentation.


