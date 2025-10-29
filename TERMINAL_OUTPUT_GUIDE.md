# Terminal-Style Output Guide

This guide explains how the terminal-style output feature works in the QA Agent system.

## Overview

The system now supports terminal-style formatted output that displays agent execution history in a readable, structured format similar to command-line interfaces.

## Features

### 1. Terminal-Style Formatting

The `format_terminal_output()` function creates a structured text representation of agent execution history with:

- Visual separators using Unicode box-drawing characters
- Step-by-step execution details
- Action descriptions
- Click/input positions
- Status indicators (✓ SUCCESS / ✗ FAILED)
- Visited URLs
- Final results

### 2. Format Example

```text
═══════════════════════════════════════════════════════
  AGENT EXECUTION HISTORY
═══════════════════════════════════════════════════════

Task: Go to website and sign in
───────────────────────────────────────────────────────
STEP 1
───────────────────────────────────────────────────────
Action: Found initial url and automatically loaded it.
Result: Navigated to https://www.w3schools.com
Details: Navigate to: https://www.w3schools.com
Status: ✓ SUCCESS

───────────────────────────────────────────────────────
STEP 2
───────────────────────────────────────────────────────
Action: Clicked element
Click Position: (120, 250)
Details: Click element at index: 5
Status: ✓ SUCCESS

───────────────────────────────────────────────────────
STEP 3
───────────────────────────────────────────────────────
Action: Input 'abc@dd.com' into element 25
Input Position: (150, 300)
Details: Input into element 25: 'abc@dd.com'
Status: ✓ SUCCESS

───────────────────────────────────────────────────────
VISITED URLs
───────────────────────────────────────────────────────
  • https://www.w3schools.com
  • https://www.w3schools.com/login

───────────────────────────────────────────────────────
FINAL RESULT
───────────────────────────────────────────────────────
Task completed: True - The test case verification is complete.

═══════════════════════════════════════════════════════
```

## API Response

The endpoint returns three formats:

### 1. Terminal Output (New)
```json
{
  "terminal_output": "════════════════════════════════════...",
  ...
}
```

### 2. Structured History (Full Data)
```json
{
  "structured_history": {
    "task": "...",
    "total_steps": 5,
    "actions": [...],
    ...
  }
}
```

### 3. Formatted Summary (Display-Ready)
```json
{
  "formatted_summary": {
    "summary": {
      "total_steps": 5,
      "visited_urls_count": 3,
      ...
    }
  }
}
```

## Frontend Display

The frontend displays the terminal output in a styled container:

```jsx
<div className="bg-gray-900 p-6 rounded-xl border border-gray-700">
  <div className="bg-black/50 p-4 rounded-lg max-h-[600px] overflow-y-auto scrollbar-thin">
    <pre className="text-white whitespace-pre-wrap font-mono">
      {result.terminal_output || 'No output available'}
    </pre>
  </div>
</div>
```

## Features

### Scrollable Container
- Max height: 600px
- Custom scrollbar styling
- Smooth scrolling
- Dark theme

### Monospace Font
- Uses `font-mono` for consistent character spacing
- Preserves whitespace and formatting

### Color Scheme
- Dark gray background (#1a1a1a)
- Black inner container
- White text
- Custom scrollbar with hover effects

## Benefits

1. **Readable**: Terminal-style format is easy to read
2. **Structured**: Clear step-by-step breakdown
3. **Scrollable**: Proper scrolling functionality
4. **Formatted**: Visual separators and status indicators
5. **Comprehensive**: Shows all execution details

## Usage

### Backend
```python
from qa_agent.utils.browser_use_parser import format_terminal_output

history = await agent.run()
terminal_output = format_terminal_output(history, task)

return {
    "terminal_output": terminal_output,
    ...
}
```

### Frontend
```jsx
const result = response.data;

<div className="terminal-container">
  <pre className="terminal-text">
    {result.terminal_output}
  </pre>
</div>
```

## Customization

You can customize the output by modifying the `format_terminal_output()` function:

- Change separators (══════, ────────)
- Add color codes for terminal output
- Modify spacing and formatting
- Add additional details

## Troubleshooting

### Scrollbar Not Working
- Ensure the container has `overflow-y-auto` or `overflow-y-scroll`
- Check that content height exceeds container max-height
- Verify CSS classes are applied

### Text Not Wrapping
- Use `whitespace-pre-wrap` for text preservation
- Set appropriate container width
- Check font size

### Colors Not Visible
- Ensure proper contrast ratios
- Check background/foreground colors
- Verify CSS specificity

## Next Steps

1. Test with real browser-use agent runs
2. Customize formatting as needed
3. Add syntax highlighting for specific content types
4. Implement copy-to-clipboard functionality


