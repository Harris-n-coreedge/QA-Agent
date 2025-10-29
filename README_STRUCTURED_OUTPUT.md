# Browser-Use Structured Output - Complete Guide

This document explains how to get structured output from browser-use AgentHistoryList data, using documentation from Tavily MCP and Context7.

## 🎯 Problem

The browser-use library's `Agent.run()` returns an `AgentHistoryList` with raw data structures (`all_results` and `all_model_outputs`). This data needs to be parsed into structured, type-safe Pydantic models for easier consumption.

## ✨ Solution

We've created a complete solution that:

1. **Parses** AgentHistoryList into Pydantic models
2. **Returns** structured data from the backend API
3. **Displays** formatted results in the frontend

## 📁 Files Created

### Backend Files

1. **`qa_agent/schemas/__init__.py`** (Updated)
   - Added Pydantic models for structured output:
     - `DOMInteractedElement`: DOM element details
     - `ActionResult`: Action execution results
     - `ModelAction`: Action types (navigate, click, input, extract, done)
     - `StructuredAgentHistory`: Complete history structure

2. **`qa_agent/utils/browser_use_parser.py`** (New)
   - `parse_agent_history()`: Parse history into structured format
   - `format_history_for_display()`: Format for frontend display
   - `_parse_model_action()`: Parse individual model actions
   - `_parse_interacted_element()`: Parse DOM element data

3. **`standalone_backend.py`** (Updated)
   - Updated `/api/v1/qa-tests/browser-use/execute` endpoint
   - Returns both `structured_history` and `formatted_summary`
   - Uses the parser utility functions

### Frontend Files

4. **`frontend/src/pages/BrowserUse.jsx`** (Updated)
   - Enhanced UI to display structured data
   - Shows execution summary with stats
   - Displays visited URLs
   - Shows action timeline
   - Visual indicators for success/failure

### Documentation Files

5. **`STRUCTURED_OUTPUT_GUIDE.md`** - Detailed documentation
6. **`EXAMPLE_USAGE.md`** - Usage examples
7. **`README_STRUCTURED_OUTPUT.md`** - This file

## 🚀 Quick Start

### 1. API Endpoint

The endpoint now returns structured data:

```bash
POST /api/v1/qa-tests/browser-use/execute

Request:
{
  "task": "Go to https://www.w3schools.com and sign in",
  "ai_provider": "google"
}

Response:
{
  "task": "...",
  "status": "completed",
  "structured_history": { ... },  # Full Pydantic models
  "formatted_summary": { ... },   # Display-ready format
  "executed_at": "2024-01-01T00:00:00Z"
}
```

### 2. Response Structure

The response includes two formats:

#### A. Full Structured History (`structured_history`)

Complete Pydantic models with all details:

```json
{
  "task": "Your task",
  "status": "completed",
  "total_steps": 5,
  "actions": [
    {
      "step_number": 1,
      "action_result": {
        "is_done": false,
        "extracted_content": "Navigated to https://example.com",
        "success": null,
        "error": null
      },
      "model_action": {
        "action_type": "navigate",
        "navigate": {
          "url": "https://example.com",
          "new_tab": false
        }
      }
    }
  ],
  "visited_urls": ["https://example.com"],
  "extracted_content": [...],
  "errors": [],
  "final_result": "...",
  "is_done": true,
  "is_successful": true,
  "has_errors": false
}
```

#### B. Formatted Summary (`formatted_summary`)

Simplified format for easy display:

```json
{
  "task": "Your task",
  "summary": {
    "total_steps": 5,
    "visited_urls_count": 3,
    "has_errors": false,
    "is_successful": true
  },
  "visited_urls": ["https://example.com"],
  "final_result": "...",
  "actions_summary": [
    {
      "step": 1,
      "action_type": "navigate",
      "extracted_content": "...",
      "error": null,
      "success": true
    }
  ]
}
```

## 📊 Data Structures

### Action Types

1. **Navigate** - URL navigation
   - `url`: Target URL
   - `new_tab`: Open in new tab boolean

2. **Click** - Element clicking
   - `index`: Element index
   - `interacted_element`: DOM element details

3. **Input** - Text input
   - `index`: Element index
   - `text`: Input text
   - `clear`: Clear before typing

4. **Extract** - Content extraction
   - `query`: Extraction query
   - `extract_links`: Extract links boolean
   - `start_from_char`: Starting position

5. **Done** - Task completion
   - `text`: Completion message
   - `success`: Success flag
   - `files_to_display`: Output files

### Element Details

- `node_id`: Element node ID
- `backend_node_id`: Backend node ID
- `node_type`: Element type
- `node_name`: Tag name (DIV, INPUT, etc.)
- `attributes`: Element attributes
- `bounds`: DOM rect (x, y, width, height)
- `x_path`: XPath to element
- `element_hash`: Unique hash

## 🎨 Frontend Display

The frontend now shows:

1. **Execution Summary** with stats:
   - Total steps
   - URLs visited count
   - Error status
   - Success status

2. **Visited URLs** list with links

3. **Actions Timeline** with:
   - Step number and action type
   - Success/failure indicator
   - Extracted content
   - Error messages

4. **Final Result** from the agent

## 💡 Usage Examples

### Python Backend

```python
from qa_agent.utils.browser_use_parser import parse_agent_history
from browser_use import Agent, ChatGoogle

# Run agent
llm = ChatGoogle(model="gemini-flash-latest", api_key="key")
agent = Agent(task="Your task", llm=llm)
history = await agent.run()

# Parse structured data
structured = parse_agent_history(history, "Your task")

# Access data
print(f"Steps: {structured.total_steps}")
print(f"URLs: {structured.visited_urls}")
print(f"Final: {structured.final_result}")
```

### Frontend React

```jsx
// Display structured summary
{result.formatted_summary && (
  <div>
    <h3>Summary</h3>
    <p>Steps: {result.formatted_summary.summary.total_steps}</p>
    <p>Success: {result.formatted_summary.summary.is_successful}</p>
  </div>
)}
```

## 🔍 Documentation Sources

Documentation was obtained using:

1. **Tavily MCP** - Web search for browser-use library
2. **Context7** - Resolved library ID and fetched documentation
3. **GitHub** - Repository documentation for browser-use

## ✅ Benefits

1. **Type-Safe**: Pydantic models ensure data integrity
2. **Structured**: Organized action history
3. **Error Tracking**: Separate error lists
4. **Element Details**: Full DOM interaction information
5. **Display Ready**: Pre-formatted summary included
6. **API Integration**: Ready for frontend consumption

## 📚 Additional Resources

- `STRUCTURED_OUTPUT_GUIDE.md` - Detailed guide
- `EXAMPLE_USAGE.md` - Usage examples
- [Browser-Use GitHub](https://github.com/browser-use/browser-use)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 🎯 Next Steps

1. Test the structured output with real browser-use agent runs
2. Customize the frontend display as needed
3. Add more analysis and reporting features
4. Export structured data to JSON/CSV for reporting

---

**Created using Tavily MCP and Context7 documentation tools.**


