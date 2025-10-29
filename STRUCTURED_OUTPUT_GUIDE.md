# Browser-Use Structured Output Guide

This guide explains how to get structured output from browser-use AgentHistoryList data, as shown in the test results image.

## Overview

When you run a browser-use agent using the `Agent.run()` method, it returns an `AgentHistoryList` object containing:
- `all_results`: List of `ActionResult` objects
- `all_model_outputs`: List of dictionaries representing model actions

## Using the Structured Output

### 1. Backend Endpoint

The updated `execute_browser_use` endpoint now returns structured data:

```python
POST /api/v1/qa-tests/browser-use/execute

Request:
{
  "task": "Your task description",
  "ai_provider": "google"
}

Response:
{
  "task": "Your task description",
  "status": "completed",
  "structured_history": {
    "task": "...",
    "status": "completed",
    "total_steps": 5,
    "actions": [...],
    "visited_urls": [...],
    "extracted_content": [...],
    "errors": [...],
    "final_result": "...",
    "is_done": true,
    "is_successful": true,
    "has_errors": false,
    "executed_at": "2024-01-01T00:00:00Z"
  },
  "formatted_summary": {
    "task": "...",
    "status": "completed",
    "summary": {
      "total_steps": 5,
      "visited_urls_count": 3,
      "has_errors": false,
      "is_successful": true,
      "is_done": true
    },
    "visited_urls": [...],
    "final_result": "...",
    "actions_summary": [...],
    "executed_at": "..."
  },
  "executed_at": "2024-01-01T00:00:00Z"
}
```

### 2. Data Structures

#### Model Action Types

The parser handles these action types from browser-use:

1. **Navigate Action**
   - `url`: Target URL
   - `new_tab`: Boolean for opening in new tab

2. **Click Action**
   - `index`: Element index to click
   - `interacted_element`: DOM element details

3. **Input Action**
   - `index`: Element index
   - `text`: Text to input
   - `clear`: Whether to clear before typing

4. **Extract Action**
   - `query`: Extraction query
   - `extract_links`: Boolean for link extraction
   - `start_from_char`: Starting character position

5. **Done Action**
   - `text`: Completion message
   - `success`: Success flag
   - `files_to_display`: List of files

#### DOM Element Structure

Each interacted element includes:
- `node_id`: Element node ID
- `backend_node_id`: Backend node ID
- `node_type`: Element type (ELEMENT_NODE, etc.)
- `node_name`: Tag name (DIV, INPUT, BUTTON, etc.)
- `attributes`: Element attributes
- `bounds`: DOM rect (x, y, width, height)
- `x_path`: XPath to element
- `element_hash`: Unique hash

## Example Usage

### Python Backend

```python
from browser_use import Agent, ChatGoogle
from qa_agent.utils.browser_use_parser import parse_agent_history, format_history_for_display

# Initialize agent
llm = ChatGoogle(model="gemini-flash-latest", api_key="your-key")
agent = Agent(task="Your task", llm=llm)

# Run and get history
history = await agent.run()

# Parse into structured format
structured = parse_agent_history(history, task="Your task")

# Get formatted summary
formatted = format_history_for_display(structured)

# Access specific data
print(f"Total steps: {structured.total_steps}")
print(f"Visited URLs: {structured.visited_urls}")
print(f"Final result: {structured.final_result}")

# Access individual actions
for action in structured.actions:
    print(f"Step {action.step_number}: {action.model_action.action_type}")
    if action.action_result.extracted_content:
        print(f"  Extracted: {action.action_result.extracted_content}")
```

### Frontend Display

The response includes both:
1. **`structured_history`**: Full detailed data (Pydantic models)
2. **`formatted_summary`**: Simplified display-ready format

Use `formatted_summary` for quick display:
```javascript
const result = response.data.formatted_summary;

// Display summary
console.log(`Task: ${result.task}`);
console.log(`Steps: ${result.summary.total_steps}`);
console.log(`Success: ${result.summary.is_successful}`);
console.log(`URLs visited: ${result.summary.visited_urls_count}`);

// Display actions
result.actions_summary.forEach(action => {
  console.log(`Step ${action.step}: ${action.action_type}`);
});
```

## Integration with Frontend

The frontend receives structured data that can be easily displayed:

```javascript
// Example: Display test results
function displayStructuredResults(data) {
  const { structured_history, formatted_summary } = data;
  
  // Show summary
  document.getElementById('summary').innerHTML = `
    <h3>Task: ${formatted_summary.task}</h3>
    <p>Total Steps: ${formatted_summary.summary.total_steps}</p>
    <p>Visited URLs: ${formatted_summary.summary.visited_urls_count}</p>
    <p>Status: ${formatted_summary.summary.is_successful ? '✅ Success' : '❌ Failed'}</p>
  `;
  
  // Show visited URLs
  const urls = formatted_summary.visited_urls.map(url => 
    `<li><a href="${url}">${url}</a></li>`
  ).join('');
  document.getElementById('urls').innerHTML = `<ul>${urls}</ul>`;
  
  // Show actions
  const actions = formatted_summary.actions_summary.map(action => 
    `<li>Step ${action.step}: ${action.action_type}
      ${action.error ? `<br><small style="color:red">${action.error}</small>` : ''}
      ${action.extracted_content ? `<br><small>${action.extracted_content}</small>` : ''}
    </li>`
  ).join('');
  document.getElementById('actions').innerHTML = `<ul>${actions}</ul>`;
  
  // Show final result
  if (formatted_summary.final_result) {
    document.getElementById('final-result').innerHTML = 
      `<pre>${formatted_summary.final_result}</pre>`;
  }
}
```

## Benefits

1. **Structured Data**: Type-safe Pydantic models
2. **Easy Parsing**: Organized action history
3. **Error Tracking**: Separate error lists
4. **Element Details**: Full DOM interaction information
5. **Display Ready**: Pre-formatted summary included
6. **API Integration**: Ready for frontend consumption

## References

- [Browser-Use Documentation](https://github.com/browser-use/browser-use)
- [Pydantic Models](https://docs.pydantic.dev/)
- Created using Tavily MCP and Context7 documentation


