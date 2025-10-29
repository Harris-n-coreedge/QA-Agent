# Kernel Integration (Browsers-as-a-Service)

This module implements the complete Kernel integration as specified in the plan, providing browsers-as-a-service capabilities for the QA Agent.

## Features

### Core Kernel Features
- **Headless Mode**: Run browsers in headless mode for automation
- **Stealth Mode**: Anti-detection capabilities to avoid bot detection
- **Standby Mode**: Fast next-run with warm browser instances
- **Persistence**: Reuse sessions and cookies with profile management

### Advanced Capabilities
- **Live View**: Debug and human-in-the-loop capabilities during runs
- **Replays**: Video review capabilities after runs complete
- **CDP Integration**: Connect Playwright over CDP to remote Kernel browsers
- **Profile Management**: Persistent browser profiles for session reuse

## Usage

### Basic Connection

```python
from qa_agent.kernel.browser import connect_kernel_browser, disconnect_kernel_browser
from uuid import uuid4

async def basic_example():
    run_id = uuid4()
    
    # Connect to Kernel browser
    browser, context, page, browser_response = await connect_kernel_browser(
        run_id=run_id,
        stealth=True,
        profile="my_profile",
        standby=True
    )
    
    try:
        # Use the browser
        await page.goto("https://example.com")
        await page.click("text=Sign up")
        
        # Get debugging URLs
        live_view_url = kernel_client.get_live_view_url(browser_response)
        replay_url = kernel_client.get_replay_url(browser_response)
        
    finally:
        # Cleanup
        await disconnect_kernel_browser(run_id)
```

### Profile Persistence

```python
# First session - create profile
browser1, context1, page1, response1 = await connect_kernel_browser(
    run_id=uuid4(),
    profile="user_profile",
    stealth=True
)

# Login and set cookies
await page1.goto("https://example.com/login")
await page1.fill("input[name='email']", "user@example.com")
await page1.click("button[type='submit']")

await disconnect_kernel_browser(run_id1)

# Second session - reuse profile (user still logged in)
browser2, context2, page2, response2 = await connect_kernel_browser(
    run_id=uuid4(),
    profile="user_profile",  # Same profile
    stealth=True
)

await page2.goto("https://example.com/dashboard")  # Already logged in
```

### Stealth Mode

```python
# Enable anti-detection
browser, context, page, response = await connect_kernel_browser(
    run_id=uuid4(),
    stealth=True,  # Anti-detection enabled
    headless=True
)

# Navigate to sites that detect automation
await page.goto("https://bot.sannysoft.com/")
```

## Configuration

### Environment Variables

```bash
# Required
KERNEL_API_KEY=your_kernel_api_key_here

# Optional
DEFAULT_STEALTH=true
```

### Settings

The integration uses these configuration options:

- `stealth`: Enable anti-detection (default: from settings)
- `profile`: Persistent profile name for session reuse
- `standby`: Enable standby mode for fast next-run
- `headless`: Run in headless mode (default: true)

## API Reference

### KernelClient

Main client for Kernel API interactions.

```python
from qa_agent.kernel.client import kernel_client

# Create browser
response = await kernel_client.create_browser(
    stealth=True,
    profile="my_profile",
    standby=True
)

# Get URLs
cdp_url = kernel_client.get_cdp_url(response)
live_view_url = kernel_client.get_live_view_url(response)
replay_url = kernel_client.get_replay_url(response)

# Terminate browser
await kernel_client.terminate_browser(browser_id)
```

### BrowserManager

Manages browser lifecycle and connections.

```python
from qa_agent.kernel.browser import browser_manager

# Create session
browser, context, page, response = await browser_manager.create_browser_session(
    run_id=uuid4(),
    stealth=True,
    profile="my_profile"
)

# Get session info
info = browser_manager.get_session_info(run_id)

# Terminate session
await browser_manager.terminate_browser_session(run_id)
```

## Examples

See `qa_agent/kernel/examples.py` for comprehensive examples demonstrating:

- Basic Kernel connection and navigation
- Stealth mode anti-detection
- Profile persistence and session reuse
- Standby mode for fast runs
- Live View debugging
- Replay review capabilities

## Integration Points

The Kernel integration connects to other QA Agent modules:

- **Simulation Engine**: Uses Kernel browsers for flow execution
- **Visibility Module**: Stores Live View and Replay URLs
- **Storage Models**: Tracks browser IDs and URLs in database
- **Workers**: Creates and manages Kernel browsers for runs

## Error Handling

The integration includes comprehensive error handling:

- Defensive cleanup of Kernel browsers on timeout/failure
- Graceful handling of CDP connection failures
- Automatic retry logic for browser creation
- Proper resource cleanup in all scenarios

## Performance

Kernel's speed advantages:

- Sub-millisecond cold starts
- Fast browser creation and termination
- Efficient CDP WebSocket connections
- Optimized for high-scale automation
