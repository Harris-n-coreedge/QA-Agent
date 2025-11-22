"""
Standalone QA Agent Backend - Works independently of existing qa_agent package
This provides the full functionality for the frontend without dependencies on other routes
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Callable
from enum import Enum
from contextlib import asynccontextmanager
import asyncio
import json
from datetime import datetime
import uuid
import sys
import os
import logging

logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Store global agent and test results
global_agent: Optional[Any] = None
agent_status: str = "uninitialized"  # uninitialized, initializing, active, failed
agent_error: Optional[str] = None
commands_executed: int = 0
test_results: Dict[str, Dict] = {}
# Store external browsers to keep them alive
external_browsers: Dict[str, Any] = {}  # Store playwright and browser instances

# Test execution queue system
test_queue: asyncio.Queue = asyncio.Queue()
current_test: Optional[str] = None  # test_id currently running
test_tasks: Dict[str, asyncio.Task] = {}  # Store task references for cancellation
queue_processor_running: bool = False


class AIProvider(str, Enum):
    """Supported AI providers"""
    openai = "openai"
    anthropic = "anthropic"
    google = "google"


class TestStatus(str, Enum):
    """Test execution status"""
    pending = "pending"
    running = "running"
    completed = "completed"
    passed = "passed"
    failed = "failed"
    cancelled = "cancelled"


class CommandRequest(BaseModel):
    """Request to execute a command"""
    command: str = Field(..., description="Natural language command to execute")


class NavigateRequest(BaseModel):
    """Request to navigate to a website URL"""
    website_url: str = Field(..., description="Website URL to navigate to")


class CrossBrowserTestRequest(BaseModel):
    """Request for cross-browser testing"""
    website_url: Optional[str] = Field(default=None, description="Website URL to test (uses current URL if not provided)")
    browser_type: Optional[str] = Field(default=None, description="Specific browser to test (chromium, firefox, webkit). If not provided, tests all.")


class BrowserUseRequest(BaseModel):
    """Request for browser-use simple automation"""
    task: str = Field(..., description="Task description for browser automation")
    ai_provider: AIProvider = Field(default=AIProvider.google, description="AI provider (default: google)")


class CommandResponse(BaseModel):
    """Response after executing a command"""
    command: str
    result: str
    status: TestStatus
    executed_at: str
    duration_ms: Optional[float] = None


class StandardizedTestResult(BaseModel):
    """Standardized test result structure for all performance tests"""
    test_type: str = Field(..., description="Type of test (e.g., 'load_test', 'benchmark', 'stress_test')")
    test_name: str = Field(..., description="Name of the test")
    status: TestStatus = Field(..., description="Test execution status")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Test-specific metrics")
    visualizations: Optional[Dict[str, Any]] = Field(default=None, description="Chart data and visualizations")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Key summary statistics")
    raw_data: Optional[Dict[str, Any]] = Field(default=None, description="Full test data")
    started_at: str = Field(..., description="Test start timestamp")
    completed_at: Optional[str] = Field(default=None, description="Test completion timestamp")
    duration_ms: float = Field(..., description="Test duration in milliseconds")
    error: Optional[str] = Field(default=None, description="Error message if test failed")
    progress: Optional[float] = Field(default=None, description="Progress percentage (0-100)")


class PerformanceTestRequest(BaseModel):
    """Base request for performance tests"""
    website_url: Optional[str] = Field(default=None, description="Website URL to test")
    test_name: Optional[str] = Field(default=None, description="Name of the test")


class LoadTestRequest(PerformanceTestRequest):
    """Request for load test"""
    users: int = Field(default=50, description="Number of concurrent users")
    duration: int = Field(default=60, description="Test duration in seconds")
    ramp_up: int = Field(default=10, description="Ramp-up time in seconds")
    target_url: Optional[str] = Field(default=None, description="Target URL (overrides website_url)")


class StressTestRequest(PerformanceTestRequest):
    """Request for stress test"""
    max_users: int = Field(default=500, description="Maximum number of users")
    step_users: int = Field(default=50, description="User increment step")
    duration: int = Field(default=300, description="Test duration in seconds")


class SpikeTestRequest(PerformanceTestRequest):
    """Request for spike test"""
    initial_users: int = Field(default=10, description="Initial number of users")
    spike_users: int = Field(default=200, description="Spike number of users")
    duration: int = Field(default=120, description="Test duration in seconds")


class SoakTestRequest(PerformanceTestRequest):
    """Request for soak test"""
    users: int = Field(default=50, description="Number of concurrent users")
    duration_hours: int = Field(default=1, description="Test duration in hours")


class RampUpTestRequest(PerformanceTestRequest):
    """Request for ramp-up test"""
    max_users: int = Field(default=100, description="Maximum number of users")
    ramp_up_time: int = Field(default=60, description="Ramp-up time in seconds")
    duration: int = Field(default=120, description="Test duration in seconds")


class ThroughputTestRequest(PerformanceTestRequest):
    """Request for throughput test"""
    target_rps: int = Field(default=100, description="Target requests per second")
    duration: int = Field(default=60, description="Test duration in seconds")


class EndpointPerformanceTestRequest(PerformanceTestRequest):
    """Request for endpoint performance test"""
    endpoint: str = Field(..., description="Endpoint to test")
    users: int = Field(default=50, description="Number of concurrent users")
    duration: int = Field(default=60, description="Test duration in seconds")


class ApiLoadTestRequest(PerformanceTestRequest):
    """Request for API load test"""
    users: int = Field(default=50, description="Number of concurrent users")
    duration: int = Field(default=60, description="Test duration in seconds")


class WebsiteLoadTestRequest(PerformanceTestRequest):
    """Request for website load test"""
    users: int = Field(default=50, description="Number of concurrent users")
    duration: int = Field(default=60, description="Test duration in seconds")


class VolumeTestRequest(PerformanceTestRequest):
    """Request for volume test"""
    users: int = Field(default=100, description="Number of concurrent users")
    duration: int = Field(default=300, description="Test duration in seconds")


class ConcurrentUserTestRequest(PerformanceTestRequest):
    """Request for concurrent user test"""
    concurrent_users: int = Field(default=100, description="Number of concurrent users")
    duration: int = Field(default=60, description="Test duration in seconds")


class ResponseTimeDistributionTestRequest(PerformanceTestRequest):
    """Request for response time distribution test"""
    users: int = Field(default=50, description="Number of concurrent users")
    duration: int = Field(default=60, description="Test duration in seconds")


# Network test request models
class NetworkTestRequest(PerformanceTestRequest):
    """Base request for network tests"""
    user_permission: bool = Field(default=False, description="User permission for restricted tests")
    target_url: Optional[str] = Field(default=None, description="Target URL (overrides website_url)")


class SslTlsValidationRequest(NetworkTestRequest):
    """Request for SSL/TLS certificate validation"""
    pass


class DnsSecurityTestRequest(NetworkTestRequest):
    """Request for DNS security test"""
    pass


class ConnectivityDiagnosticsRequest(NetworkTestRequest):
    """Request for network connectivity diagnostics"""
    pass


class ProtocolTrafficAnalysisRequest(NetworkTestRequest):
    """Request for protocol traffic analysis"""
    duration: int = Field(default=10, description="Capture duration in seconds")


class NetworkSecurityScanRequest(NetworkTestRequest):
    """Request for network security scan"""
    ports: Optional[List[int]] = Field(default=None, description="List of ports to scan (default: common ports)")
    scan_type: str = Field(default="stealth", description="Scan type: stealth, tcp, or default")


class EndpointDiscoveryRequest(NetworkTestRequest):
    """Request for endpoint discovery"""
    discovery_method: str = Field(default="passive", description="Discovery method: passive or active")


# Internal helpers for global agent management
async def _ensure_global_agent() -> bool:
    """Ensure the global agent exists and is active. Returns True if agent is ready."""
    global global_agent, agent_status, agent_error
    
    try:
        # If already active or initializing, return status
        if agent_status in {"active", "initializing"}:
            return agent_status == "active"
        
        # If failed, don't retry automatically
        if agent_status == "failed":
            return False

        # Lazy import to reuse existing logic
        from dotenv import load_dotenv
        load_dotenv()
        # Prefer provider from env; fallback to google from qa_config.yaml if any
        preferred_provider = os.getenv("QA_AGENT_AI_PROVIDER")
        if not preferred_provider:
            try:
                import yaml
                cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qa_config.yaml")
                if os.path.exists(cfg_path):
                    with open(cfg_path, "r", encoding="utf-8") as f:
                        cfg = yaml.safe_load(f) or {}
                        preferred_provider = (cfg.get("ai") or {}).get("provider")
            except Exception:
                preferred_provider = None
        preferred_provider = (preferred_provider or AIProvider.google.value).lower()

        # Map to enum safely
        provider_enum = AIProvider(preferred_provider) if preferred_provider in {p.value for p in AIProvider} else AIProvider.google

        # Read API key for chosen provider
        if provider_enum == AIProvider.openai:
            api_key = os.getenv("OPENAI_API_KEY")
        elif provider_enum == AIProvider.anthropic:
            api_key = os.getenv("ANTHROPIC_API_KEY")
        else:
            api_key = os.getenv("GOOGLE_API_KEY")

        # If missing API key, mark as failed
        if not api_key:
            agent_status = "failed"
            agent_error = f"API key for {provider_enum.value} not found in environment variables. Please add it to your .env file."
            return False

        # Import and construct agent (lazy initialization - don't start browser session yet)
        from multi_ai_qa_agent import MultiAIQAAgent
        agent_status = "uninitialized"  # Changed from "initializing" - browser not started yet
        global_agent = MultiAIQAAgent(ai_provider=provider_enum.value, api_key=api_key)

        # Browser session will be initialized on-demand when first test runs
        # Do NOT start browser session here - it will be started lazily when needed

        return False  # Agent object created but browser session not started
    except Exception as e:
        agent_status = "failed"
        agent_error = str(e)
        return False

async def _start_browser_session(website_url: str = "https://www.w3schools.com/", auto_check: bool = False):
    """Start browser session lazily when needed (on-demand initialization)"""
    global global_agent, agent_status, agent_error
    
    # If already active, return
    if agent_status == "active":
        return True
    
    # If already initializing, wait for it
    if agent_status == "initializing":
        # Wait up to 60 seconds for initialization
        for _ in range(60):
            await asyncio.sleep(1)
            if agent_status == "active":
                return True
            if agent_status == "failed":
                return False
        return False
    
    # Ensure agent object exists
    if global_agent is None:
        await _ensure_global_agent()
    
    if global_agent is None:
        return False
    
    # Start browser session
    # IMPORTANT: We'll modify start_session to accept headless parameter
    try:
        agent_status = "initializing"
        
        # Start browser session in headless mode for embedding
        # We need to directly initialize browser instead of using start_session
        # because start_session has headless=False hardcoded
        from playwright.async_api import async_playwright
        print("Multi-AI QA Agent Starting (Headless for Embedding)...")
        print("=" * 40)
        print(f"Opening: {website_url}")
        print(f"AI Provider: {global_agent.ai_provider.upper()}")
        print("Browser Mode: HEADLESS (embedded)")
        
        global_agent.playwright = await async_playwright().start()
        global_agent.browser = await global_agent.playwright.chromium.launch(
            headless=True,  # Run headless - no external window
            slow_mo=500,    # Slower interactions for stability
            args=[
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        global_agent.context = await global_agent.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        global_agent.current_page = await global_agent.context.new_page()
        
        try:
            global_agent.current_page.set_default_timeout(60000)
            global_agent.current_page.set_default_navigation_timeout(90000)
        except Exception:
            pass
        
        # Navigate to the website
        try:
            await global_agent.current_page.goto(website_url, wait_until="domcontentloaded", timeout=45000)
        except Exception as e1:
            try:
                await global_agent.current_page.goto(website_url, wait_until="load", timeout=60000)
            except Exception as e2:
                try:
                    await global_agent.current_page.goto(website_url, wait_until="commit", timeout=30000)
                except Exception as e3:
                    print(f" Navigation still timing out: {e3}. Continuing best-effort.")
        
        try:
            await global_agent.current_page.wait_for_selector("body", timeout=10000)
        except Exception:
            pass
        await global_agent.current_page.wait_for_timeout(2000)
        
        # Analyze page characteristics
        try:
            await global_agent._analyze_page_characteristics()
        except Exception as e:
            print(f"Page analysis failed: {e}")
        
        # Auto-check if requested
        if auto_check:
            try:
                summary = await global_agent._run_auto_checks()
                print(summary)
            except Exception as e:
                print(f"Auto-checks failed: {e}")
        
        global_agent.current_url = website_url
        print("Agent ready (Headless)! I can understand natural language commands.")
        agent_status = "active"
        agent_error = None
        return True
    except Exception as e:
        agent_status = "failed"
        agent_error = str(e)
        return False

def _get_agent_status():
    """Get current agent status"""
    return {
        "status": agent_status,
        "commands_executed": commands_executed,
        "error": agent_error,
    }


async def _execute_test_queue():
    """Background task to process test queue"""
    global current_test, queue_processor_running, test_tasks
    
    queue_processor_running = True
    
    while True:
        try:
            # Get next test from queue
            test_item = await test_queue.get()
            
            if test_item is None:  # Shutdown signal
                break
            
            test_id, test_type, test_func, test_params = test_item
            
            # Update current test
            current_test = test_id
            
            # Update test status to running
            if test_id in test_results:
                test_results[test_id]["status"] = TestStatus.running
                test_results[test_id]["progress"] = 0.0
            
            try:
                # Execute test
                task = asyncio.create_task(test_func(**test_params))
                test_tasks[test_id] = task
                
                result = await task
                
                # Add target_url to metrics if available (for network tests)
                if "target_url" in test_params and isinstance(result, dict):
                    result["target_url"] = test_params["target_url"]
                
                # Format result into standardized structure
                completed_at = datetime.utcnow()
                started_at = datetime.fromisoformat(test_results[test_id]["started_at"])
                
                standardized_result = _format_standardized_result(
                    test_type=test_type,
                    test_name=test_results[test_id].get("test_name", "Test"),
                    metrics=result,
                    started_at=started_at,
                    completed_at=completed_at,
                    raw_data=result
                )
                
                # Update test results
                if test_id in test_results:
                    # Merge standardized result, preserving test_id
                    test_results[test_id].update(standardized_result)
                    test_results[test_id]["test_id"] = test_id  # Ensure test_id is preserved
                    test_results[test_id]["status"] = TestStatus.completed
                    test_results[test_id]["progress"] = 100.0
                    
                    # Log the stored result for debugging
                    logger.info(f"Stored test result for {test_id}: metrics keys={list(standardized_result.get('metrics', {}).keys())}")
                    logger.debug(f"Full stored result: {test_results[test_id]}")
                
            except asyncio.CancelledError:
                # Test was cancelled
                if test_id in test_results:
                    test_results[test_id]["status"] = TestStatus.cancelled
                    test_results[test_id]["completed_at"] = datetime.utcnow().isoformat()
            except Exception as e:
                # Test failed
                if test_id in test_results:
                    test_results[test_id]["status"] = TestStatus.failed
                    test_results[test_id]["error"] = str(e)
                    test_results[test_id]["completed_at"] = datetime.utcnow().isoformat()
                logger.error(f"Test {test_id} failed: {str(e)}")
            finally:
                # Clean up
                current_test = None
                if test_id in test_tasks:
                    del test_tasks[test_id]
                test_queue.task_done()
                
        except Exception as e:
            logger.error(f"Error in test queue processor: {str(e)}")
            await asyncio.sleep(1)
    
    queue_processor_running = False


def _format_standardized_result(
    test_type: str,
    test_name: str,
    metrics: Dict[str, Any],
    started_at: datetime,
    completed_at: Optional[datetime] = None,
    error: Optional[str] = None,
    raw_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Format test results into standardized structure"""
    duration_ms = 0
    if completed_at:
        duration_ms = (completed_at - started_at).total_seconds() * 1000
    
    # Extract error from metrics if not provided directly
    if not error and isinstance(metrics, dict) and "error" in metrics:
        error = metrics.get("error")
    
    # Create visualizations based on metrics
    visualizations = _create_visualizations(test_type, metrics)
    
    # Create summary
    summary = _create_summary(test_type, metrics)
    
    return {
        "test_type": test_type,
        "test_name": test_name,
        "status": TestStatus.completed if not error else TestStatus.failed,
        "metrics": metrics,
        "visualizations": visualizations,
        "summary": summary,
        "raw_data": raw_data,
        "started_at": started_at.isoformat(),
        "completed_at": completed_at.isoformat() if completed_at else None,
        "duration_ms": duration_ms,
        "error": error
    }


def _create_visualizations(test_type: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Create visualization data based on test type and metrics"""
    visualizations = {}
    
    if test_type.startswith("load") or test_type.startswith("stress") or test_type.startswith("spike"):
        # Response time chart
        if "avg_response_time" in metrics:
            visualizations["response_time_chart"] = {
                "type": "line",
                "data": [
                    {"time": "0s", "value": metrics.get("min_response_time", 0)},
                    {"time": "50%", "value": metrics.get("avg_response_time", 0)},
                    {"time": "100%", "value": metrics.get("max_response_time", 0)}
                ],
                "title": "Response Time Distribution"
            }
        
        # Throughput chart
        if "requests_per_second" in metrics:
            visualizations["throughput_chart"] = {
                "type": "bar",
                "data": [{"label": "RPS", "value": metrics["requests_per_second"]}],
                "title": "Requests Per Second"
            }
    
    elif test_type.startswith("benchmark"):
        # Time distribution histogram
        if "avg_time_ms" in metrics:
            visualizations["time_distribution"] = {
                "type": "histogram",
                "data": [
                    {"range": "min", "value": metrics.get("min_time_ms", 0)},
                    {"range": "avg", "value": metrics.get("avg_time_ms", 0)},
                    {"range": "max", "value": metrics.get("max_time_ms", 0)}
                ],
                "title": "Time Distribution"
            }
    
    # Network test visualizations
    elif test_type.startswith("ssl_tls") or test_type.startswith("ssl") or test_type.startswith("tls"):
        # SSL/TLS visualizations
        if "protocol_versions" in metrics and metrics["protocol_versions"]:
            visualizations["protocol_versions"] = {
                "type": "bar",
                "data": [{"label": version, "value": 1} for version in metrics["protocol_versions"]],
                "title": "Protocol Versions Supported"
            }
        
        if "cipher_suites" in metrics and metrics["cipher_suites"]:
            # Group cipher suites by strength
            cipher_strength = {"Weak": 0, "Medium": 0, "Strong": 0}
            for cipher in metrics["cipher_suites"]:
                bits = cipher.get("bits", 0)
                if bits < 128:
                    cipher_strength["Weak"] += 1
                elif bits < 256:
                    cipher_strength["Medium"] += 1
                else:
                    cipher_strength["Strong"] += 1
            
            visualizations["cipher_strength"] = {
                "type": "bar",
                "data": [{"label": strength, "value": count} for strength, count in cipher_strength.items()],
                "title": "Cipher Suite Strength"
            }
    
    elif test_type.startswith("dns"):
        # DNS test visualizations
        if "dns_resolution_times" in metrics:
            visualizations["dns_resolution_times"] = {
                "type": "bar",
                "data": [
                    {"label": qtype, "value": time or 0} 
                    for qtype, time in metrics["dns_resolution_times"].items()
                ],
                "title": "DNS Resolution Times by Query Type"
            }
    
    elif test_type.startswith("connectivity"):
        # Connectivity diagnostics visualizations
        if "ping_times" in metrics and metrics["ping_times"]:
            visualizations["ping_times"] = {
                "type": "line",
                "data": [
                    {"time": f"Ping {i+1}", "value": time, "label": f"Ping {i+1}"} 
                    for i, time in enumerate(metrics["ping_times"])
                ],
                "title": "Ping Times (ms)"
            }
        
        # Connection tests visualization
        connection_data = []
        # Use connection_tests dict if available, otherwise use direct metrics
        if "connection_tests" in metrics and metrics["connection_tests"]:
            for test, success in metrics["connection_tests"].items():
                connection_data.append({
                    "label": test.upper(),
                    "value": 1 if success else 0,
                    "success": bool(success)
                })
        else:
            # Fallback to direct connection metrics
            if "http_connection" in metrics:
                http_success = bool(metrics.get("http_connection"))
                connection_data.append({
                    "label": "HTTP",
                    "value": 1 if http_success else 0,
                    "success": http_success
                })
            if "https_connection" in metrics:
                https_success = bool(metrics.get("https_connection"))
                connection_data.append({
                    "label": "HTTPS",
                    "value": 1 if https_success else 0,
                    "success": https_success
                })
        
        if connection_data:
            visualizations["connection_tests"] = {
                "type": "bar",
                "data": connection_data,
                "title": "Connection Test Results"
            }
    
    elif test_type.startswith("protocol_traffic") or test_type.startswith("protocol"):
        # Protocol traffic analysis visualizations
        # Always create protocol distribution visualization, even if empty
        if "protocol_distribution" in metrics:
            # Filter out transport layer protocols (TCP, UDP, ICMP) from visualization
            # They're shown in summary text but not in the chart to avoid confusion
            transport_protocols = {'TCP', 'UDP', 'ICMP'}
            protocol_data = [
                {"label": protocol, "value": count} 
                for protocol, count in metrics["protocol_distribution"].items()
                if protocol not in transport_protocols
            ]
            # If empty, add a placeholder to show "No data"
            if not protocol_data:
                protocol_data = [{"label": "No Data", "value": 0}]
            
            visualizations["protocol_distribution"] = {
                "type": "bar",
                "data": protocol_data,
                "title": "Protocol Distribution"
            }
        
        # Always create packet size distribution, even if empty
        if "packet_sizes" in metrics:
            # Create histogram data
            size_ranges = {"0-100": 0, "100-500": 0, "500-1000": 0, "1000+": 0}
            if metrics["packet_sizes"]:
                for size in metrics["packet_sizes"]:
                    if size < 100:
                        size_ranges["0-100"] += 1
                    elif size < 500:
                        size_ranges["100-500"] += 1
                    elif size < 1000:
                        size_ranges["500-1000"] += 1
                    else:
                        size_ranges["1000+"] += 1
            
            # Always create the visualization, even with zero values
            visualizations["packet_size_distribution"] = {
                "type": "histogram",
                "data": [
                    {"range": range_name, "value": count} 
                    for range_name, count in size_ranges.items()
                ],
                "title": "Packet Size Distribution"
            }
    
    elif test_type.startswith("network_security") or test_type.startswith("security_scan"):
        # Network security scan visualizations
        # Always create port status visualization, even if empty
        port_status = {
            "Open": len(metrics.get("open_ports", [])),
            "Closed": len(metrics.get("closed_ports", [])),
            "Filtered": len(metrics.get("filtered_ports", []))
        }
        
        # Create port status chart (always show, even with zeros)
        port_status_data = [
            {"label": status, "value": count} 
            for status, count in port_status.items()
        ]
        visualizations["port_status"] = {
            "type": "bar",
            "data": port_status_data,
            "title": "Port Status Distribution"
        }
        
        # Open ports by service (only if there are open ports)
        if "open_ports" in metrics and metrics["open_ports"]:
            # Group by service type
            service_counts = {}
            for port_data in metrics["open_ports"]:
                service = port_data.get("service", "unknown")
                service_counts[service] = service_counts.get(service, 0) + 1
            
            if service_counts:
                visualizations["open_ports_by_service"] = {
                    "type": "bar",
                    "data": [
                        {"label": service, "value": count} 
                        for service, count in service_counts.items()
                    ],
                    "title": "Open Ports by Service Type"
                }
    
    elif test_type.startswith("endpoint_discovery") or (test_type.startswith("endpoint") and not test_type.startswith("endpoint_performance")):
        # Endpoint discovery visualizations
        if "endpoints_found" in metrics and metrics["endpoints_found"]:
            # Group by HTTP method
            method_counts = {}
            for endpoint in metrics["endpoints_found"]:
                method = endpoint.get("method", "GET")
                method_counts[method] = method_counts.get(method, 0) + 1
            
            if method_counts:
                visualizations["endpoints_by_method"] = {
                    "type": "bar",
                    "data": [
                        {"label": method, "value": count} 
                        for method, count in method_counts.items()
                    ],
                    "title": "Endpoints by HTTP Method"
                }
            
            # Group by status code
            status_counts = {}
            for endpoint in metrics["endpoints_found"]:
                status = str(endpoint.get("status_code", "unknown"))
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if status_counts:
                visualizations["endpoints_by_status"] = {
                    "type": "bar",
                    "data": [
                        {"label": f"Status {status}", "value": count} 
                        for status, count in status_counts.items()
                    ],
                    "title": "Endpoints by Status Code"
                }
    
    return visualizations


def _create_summary(test_type: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Create summary statistics based on test type with human-readable analysis"""
    summary = {}
    
    # Handle endpoint_discovery FIRST (before load test check)
    # This prevents it from matching the load test condition
    # Check for all load test variations (exclude endpoint_discovery)
    if ((test_type.startswith("load") or test_type.startswith("stress") or 
        test_type.startswith("spike") or test_type.startswith("soak") or
        test_type.startswith("ramp") or test_type.startswith("throughput") or
        test_type.startswith("endpoint_performance") or test_type.startswith("api") or
        test_type.startswith("website") or test_type.startswith("volume") or
        test_type.startswith("concurrent") or test_type.startswith("response_time")) and
        not test_type.startswith("endpoint_discovery")):
        
        total_requests = metrics.get("total_requests", 0)
        successful_requests = metrics.get("successful_requests", 0)
        failed_requests = metrics.get("failed_requests", 0)
        avg_response_time = round(metrics.get("avg_response_time", 0), 2)
        min_response_time = round(metrics.get("min_response_time", 0), 2)
        max_response_time = round(metrics.get("max_response_time", 0), 2)
        median_response_time = round(metrics.get("median_response_time", 0), 2)
        requests_per_second = round(metrics.get("requests_per_second", 0), 2)
        
        # Calculate success rate
        success_rate = (
            round((successful_requests / total_requests) * 100, 2)
            if total_requests > 0 else 0.0
        )
        failure_rate = round((failed_requests / total_requests) * 100, 2) if total_requests > 0 else 0.0
        
        # Get failure details
        failures = metrics.get("failures", [])
        failure_details = []
        if failures:
            for failure in failures:
                error_msg = failure.get("error", "Unknown error")
                occurrences = failure.get("occurrences", 0)
                failure_details.append(f"{occurrences} error(s): {error_msg}")
        
        # Build human-readable summary text
        summary_text = []
        
        # Request Statistics
        summary_text.append("## Request Statistics\n")
        summary_text.append(f"**Total requests:** {total_requests:,} — Total HTTP requests sent during the test\n")
        summary_text.append(f"**Successful requests:** {successful_requests:,} — Requests that returned 200 OK\n")
        summary_text.append(f"**Failed requests:** {failed_requests:,} — Requests that failed ({failure_rate}% failure rate)\n")
        summary_text.append(f"**Success rate:** {success_rate}% — Indicates how well the system handled requests\n")
        
        # Response Time Metrics
        summary_text.append("\n## Response Time Metrics\n")
        summary_text.append(f"**Average response time:** {avg_response_time:,.2f} ms ({avg_response_time/1000:.2f} seconds) — Average time to respond\n")
        summary_text.append(f"**Median response time:** {median_response_time:,.2f} ms — Half of requests were faster than this\n")
        summary_text.append(f"**Min response time:** {min_response_time:,.2f} ms — Fastest response\n")
        summary_text.append(f"**Max response time:** {max_response_time:,.2f} ms ({max_response_time/1000:.2f} seconds) — Slowest response\n")
        
        # Performance Indicators
        summary_text.append("\n## Performance Indicators\n")
        summary_text.append(f"**Requests per second:** {requests_per_second:.2f} — Throughput under load\n")
        if failure_details:
            summary_text.append(f"**Failures:** {', '.join(failure_details)}\n")
        
        # Analysis
        summary_text.append("\n## What This Tells You\n")
        
        # Overall assessment
        if success_rate >= 99:
            summary_text.append(f"**Overall:** {success_rate}% success rate is excellent — System handled requests very well\n")
        elif success_rate >= 95:
            summary_text.append(f"**Overall:** {success_rate}% success rate is good — System handled most requests successfully\n")
        elif success_rate >= 90:
            summary_text.append(f"**Overall:** {success_rate}% success rate is acceptable but needs attention — Some failures detected\n")
        else:
            summary_text.append(f"**Overall:** {success_rate}% success rate is concerning — High failure rate indicates system issues\n")
        
        # Response time analysis
        if avg_response_time < 500:
            summary_text.append(f"**Response times:** Average {avg_response_time/1000:.2f}s is excellent — Very fast response times\n")
        elif avg_response_time < 1000:
            summary_text.append(f"**Response times:** Average {avg_response_time/1000:.2f}s is good — Acceptable response times\n")
        elif avg_response_time < 2000:
            summary_text.append(f"**Response times:** Average {avg_response_time/1000:.2f}s is moderate — Some optimization may be needed\n")
        else:
            summary_text.append(f"**Response times:** Average {avg_response_time/1000:.2f}s is slow — Optimization recommended\n")
        
        if median_response_time < avg_response_time * 0.5:
            summary_text.append(f"**Response time distribution:** Median {median_response_time/1000:.2f}s is much better than average, indicating some very slow requests\n")
        
        # Outlier analysis
        if max_response_time > avg_response_time * 10:
            summary_text.append(f"**Outlier:** Max {max_response_time/1000:.2f} seconds suggests occasional timeouts or very slow endpoints — Investigate specific slow requests\n")
        elif max_response_time > avg_response_time * 5:
            summary_text.append(f"**Outlier:** Max {max_response_time/1000:.2f} seconds indicates some slow requests — Review endpoint performance\n")
        
        # Throughput analysis
        if requests_per_second > 100:
            summary_text.append(f"**Throughput:** {requests_per_second:.2f} RPS is high — Good system capacity\n")
        elif requests_per_second > 50:
            summary_text.append(f"**Throughput:** {requests_per_second:.2f} RPS is moderate — Adequate for most use cases\n")
        else:
            summary_text.append(f"**Throughput:** {requests_per_second:.2f} RPS is low — May need scaling or optimization\n")
        
        # Recommendations
        summary_text.append("\n## Recommendations\n")
        
        if failed_requests > 0:
            summary_text.append(f"• **Investigate the {failed_requests} failed request(s)** — Check the failures array for details and fix underlying issues\n")
        
        if max_response_time > avg_response_time * 5:
            summary_text.append(f"• **Investigate slow requests** (max {max_response_time/1000:.2f}s) — May indicate a specific slow endpoint or resource that needs optimization\n")
        
        if avg_response_time > 1000:
            summary_text.append(f"• **Optimize response times** — Average {avg_response_time/1000:.2f}s is above optimal; consider caching, database optimization, or code improvements\n")
        
        if median_response_time < avg_response_time * 0.7:
            summary_text.append(f"• **Identify slow endpoints** — Large gap between median ({median_response_time/1000:.2f}s) and average ({avg_response_time/1000:.2f}s) suggests specific endpoints need attention\n")
        
        if requests_per_second < 10 and total_requests > 100:
            summary_text.append(f"• **Review system capacity** — Low throughput ({requests_per_second:.2f} RPS) may indicate bottlenecks; consider load balancing or scaling\n")
        
        if not failed_requests and avg_response_time < 1000 and requests_per_second > 50:
            summary_text.append("• **System performance is good** — Continue monitoring and consider stress testing to find breaking points\n")
        
        # Combine all text
        full_summary_text = "\n".join(summary_text)
        
        # Return both structured metrics and human-readable summary
        summary = {
            "total_requests": float(total_requests),
            "successful_requests": float(successful_requests),
            "failed_requests": float(failed_requests),
            "success_rate": success_rate,
            "avg_response_time_ms": avg_response_time,
            "min_response_time_ms": min_response_time,
            "max_response_time_ms": max_response_time,
            "median_response_time_ms": median_response_time,
            "requests_per_second": requests_per_second,
            "summary_text": full_summary_text  # Human-readable summary
        }
            
    elif test_type.startswith("benchmark"):
        avg_time = round(metrics.get("avg_time_ms", 0), 2)
        min_time = round(metrics.get("min_time_ms", 0), 2)
        max_time = round(metrics.get("max_time_ms", 0), 2)
        std_dev = round(metrics.get("std_dev", 0), 2)
        iterations = metrics.get("iterations", 0)
        
        summary_text = []
        summary_text.append("## Benchmark Results\n")
        summary_text.append(f"**Average execution time:** {avg_time:,.2f} ms\n")
        summary_text.append(f"**Min execution time:** {min_time:,.2f} ms\n")
        summary_text.append(f"**Max execution time:** {max_time:,.2f} ms\n")
        summary_text.append(f"**Standard deviation:** {std_dev:,.2f} ms — Indicates consistency of performance\n")
        summary_text.append(f"**Iterations:** {iterations:,} — Number of test runs\n")
        
        summary = {
            "avg_time_ms": avg_time,
            "min_time_ms": min_time,
            "max_time_ms": max_time,
            "std_dev_ms": std_dev,
            "iterations": iterations,
            "summary_text": "\n".join(summary_text)
        }
    
    # Network test summaries
    elif test_type.startswith("ssl_tls") or test_type.startswith("ssl") or test_type.startswith("tls"):
        summary_text = []
        
        # Add target URL at the top
        target_url = metrics.get("target_url", "Unknown")
        if target_url and target_url != "Unknown":
            summary_text.append(f"## Test Target\n")
            summary_text.append(f"**Website:** [{target_url}]({target_url}) — Target being tested\n\n")
        
        summary_text.append("## Certificate Information\n")
        
        # Initialize days_remaining before the if/else block
        days_remaining = metrics.get("certificate_days_remaining", 0)
        
        if metrics.get("certificate_valid"):
            # Extract issuer info
            issuer = metrics.get('certificate_issuer')
            if issuer and isinstance(issuer, dict):
                issuer_name = (
                    issuer.get('organizationName') or 
                    issuer.get('commonName') or 
                    issuer.get('organizationalUnitName') or 
                    'Unknown'
                )
            else:
                issuer_name = 'Unknown'
            
            # Extract subject info
            subject = metrics.get('certificate_subject')
            if subject and isinstance(subject, dict):
                subject_name = (
                    subject.get('commonName') or 
                    subject.get('organizationName') or 
                    'Unknown'
                )
            else:
                subject_name = 'Unknown'
            
            summary_text.append(f"**Issuer:** {issuer_name} — Certificate authority\n")
            summary_text.append(f"**Subject:** {subject_name} — Certificate subject\n")
            summary_text.append(f"**Valid From:** {metrics.get('certificate_valid_from', 'Unknown')} — Certificate validity start\n")
            summary_text.append(f"**Valid To:** {metrics.get('certificate_valid_to', 'Unknown')} — Certificate expiration date\n")
            
            if days_remaining > 0:
                summary_text.append(f"**Days Remaining:** {days_remaining} days — Time until certificate expires\n")
            else:
                summary_text.append(f"**Days Remaining:** {days_remaining} days — Certificate may be expired or date parsing failed\n")
        else:
            summary_text.append("**Certificate Status:** Invalid or not found\n")
        
        summary_text.append("\n## Security Assessment\n")
        summary_text.append(f"**Protocol Versions:** {', '.join(metrics.get('protocol_versions', []))} — Supported TLS versions\n")
        summary_text.append(f"**Cipher Suites:** {len(metrics.get('cipher_suites', []))} — Number of available cipher suites\n")
        summary_text.append(f"**Security Rating:** {metrics.get('security_rating', 'Unknown')} — Overall security assessment\n")
        
        summary_text.append("\n## Recommendations\n")
        recommendations = metrics.get("recommendations", [])
        
        # Debug logging
        logger.debug(f"SSL/TLS recommendations from metrics: {recommendations}")
        logger.debug(f"Certificate valid: {metrics.get('certificate_valid')}, days_remaining: {days_remaining}")
        
        # Filter out empty recommendations
        valid_recommendations = [r for r in recommendations if r and isinstance(r, str) and r.strip()]
        
        # Add recommendations from metrics if they exist
        for rec in valid_recommendations:
            summary_text.append(f"• {rec}\n")
        
        # Add fallback recommendations if none were provided or all were empty
        if not valid_recommendations:
            certificate_valid = metrics.get("certificate_valid", False)
            protocol_versions = metrics.get("protocol_versions", [])
            
            # Priority 1: Certificate expiration issues
            if not certificate_valid:
                if days_remaining <= 0:
                    summary_text.append("• Certificate has expired — Immediate renewal required\n")
                else:
                    summary_text.append("• Certificate validation failed — Check certificate configuration\n")
            elif days_remaining < 30:
                summary_text.append(f"• Renew certificate soon — Expires in {days_remaining} days\n")
            
            # Priority 2: TLS version improvements
            if certificate_valid and days_remaining >= 30:
                if "TLSv1.3" not in protocol_versions:
                    if "TLSv1.2" in protocol_versions:
                        summary_text.append("• Consider upgrading to TLS 1.3 for enhanced security\n")
                    else:
                        summary_text.append("• Upgrade to TLS 1.2 or 1.3 — Current version may be insecure\n")
            
            # If still no recommendations were added, add a positive note for secure configurations
            # Check if we added any recommendations after the "## Recommendations\n" header
            recommendations_added = len([line for line in summary_text if line.startswith("•")])
            if recommendations_added == 0:
                if certificate_valid and days_remaining >= 30 and "TLSv1.3" in protocol_versions:
                    summary_text.append("• No action required — Certificate and TLS configuration are secure\n")
                elif certificate_valid and days_remaining >= 30:
                    summary_text.append("• Certificate is valid and secure\n")
        
        summary = {
            "certificate_valid": metrics.get("certificate_valid", False),
            "certificate_days_remaining": metrics.get("certificate_days_remaining", 0),
            "security_rating": metrics.get("security_rating", "Unknown"),
            "protocol_versions_count": len(metrics.get("protocol_versions", [])),
            "cipher_suites_count": len(metrics.get("cipher_suites", [])),
            "summary_text": "".join(summary_text)
        }
    
    elif test_type.startswith("dns"):
        summary_text = []
        
        # Add target URL at the top
        target_url = metrics.get("target_url", "Unknown")
        if target_url and target_url != "Unknown":
            summary_text.append(f"## Test Target\n")
            summary_text.append(f"**Website:** [{target_url}]({target_url}) — Target being tested\n\n")
        
        summary_text.append("## DNS Performance\n")
        avg_time = metrics.get("average_resolution_time", 0)
        summary_text.append(f"**Average Resolution Time:** {avg_time:.2f} ms — DNS query response time\n")
        summary_text.append(f"**DNSSEC Status:** {'Enabled' if metrics.get('dnssec_enabled') else 'Disabled'} — DNSSEC validation status\n")
        summary_text.append(f"**DNS Leak Test:** {'Potential Leak Detected' if metrics.get('dns_leak_detected') else 'No Leak Detected'} — Privacy leak detection\n")
        
        summary_text.append("\n## DNS Servers\n")
        dns_servers = metrics.get("dns_servers", [])
        if dns_servers:
            for i, server in enumerate(dns_servers, 1):
                summary_text.append(f"**Server {i}:** {server}\n")
        
        # DNS Leak Status
        dns_leak_detected = metrics.get("dns_leak_detected", False)
        leaked_servers = metrics.get("leaked_servers", [])
        if dns_leak_detected and leaked_servers:
            summary_text.append(f"\n**DNS Leak Status:** Potential leak detected — Public DNS servers ({', '.join(leaked_servers)}) detected alongside other servers\n")
            summary_text.append("**Note:** This may indicate queries are bypassing your intended DNS servers (e.g., VPN DNS). Verify your DNS configuration.\n")
        elif not dns_leak_detected and dns_servers:
            summary_text.append(f"\n**DNS Leak Status:** No leak detected — DNS configuration appears consistent\n")
        
        summary_text.append("\n## Recommendations\n")
        
        # Add recommendations from metrics if they exist
        recommendations = metrics.get("recommendations", [])
        valid_recommendations = [r for r in recommendations if r and isinstance(r, str) and r.strip()]
        for rec in valid_recommendations:
            summary_text.append(f"• {rec}\n")
        
        # Add fallback recommendations if none were provided
        if not valid_recommendations:
            if not metrics.get("dnssec_enabled"):
                summary_text.append("• Enable DNSSEC for improved DNS security and protection against DNS spoofing\n")
            if dns_leak_detected:
                summary_text.append("• Review DNS configuration — Ensure queries go to intended servers (e.g., VPN DNS if using VPN)\n")
                summary_text.append("• Consider using a single consistent DNS provider to avoid potential leaks\n")
            if avg_time > 100:
                summary_text.append(f"• DNS resolution time ({avg_time:.2f}ms) is high — Consider using faster DNS servers like Cloudflare (1.1.1.1) or Google (8.8.8.8)\n")
        else:
            # If we have recommendations from metrics, add additional context if needed
            if dns_leak_detected and not any("leak" in r.lower() for r in valid_recommendations):
                summary_text.append("• Review DNS configuration — Ensure queries go to intended servers (e.g., VPN DNS if using VPN)\n")
            if avg_time > 100 and not any("resolution time" in r.lower() or "slow" in r.lower() for r in valid_recommendations):
                summary_text.append(f"• DNS resolution time ({avg_time:.2f}ms) is high — Consider using faster DNS servers\n")
        
        summary = {
            "average_resolution_time_ms": avg_time,
            "dnssec_enabled": metrics.get("dnssec_enabled", False),
            "dns_leak_detected": metrics.get("dns_leak_detected", False),
            "dns_servers_count": len(dns_servers),
            "summary_text": "".join(summary_text)
        }
    
    elif test_type.startswith("connectivity"):
        summary_text = []
        
        # Add target URL at the top
        target_url = metrics.get("target_url", "Unknown")
        if target_url and target_url != "Unknown":
            summary_text.append(f"## Test Target\n")
            summary_text.append(f"**Website:** [{target_url}]({target_url}) — Target being tested\n\n")
        
        summary_text.append("## Connectivity Test Results\n")
        summary_text.append(f"**Ping Test:** {'Success' if metrics.get('ping_success') else 'Failed'} — ICMP connectivity\n")
        summary_text.append(f"**DNS Resolution:** {'Success' if metrics.get('dns_resolution') else 'Failed'} — DNS query test\n")
        summary_text.append(f"**HTTP Connection:** {'Success' if metrics.get('http_connection') else 'Failed'} — HTTP connectivity\n")
        summary_text.append(f"**HTTPS Connection:** {'Success' if metrics.get('https_connection') else 'Failed'} — HTTPS connectivity\n")
        
        summary_text.append("\n## Performance Metrics\n")
        avg_ping = metrics.get("average_ping_time")
        dns_time = metrics.get("dns_resolution_time", 0)
        
        # Handle None/None ping time (failed ping)
        if avg_ping is None or (avg_ping == 0 and not metrics.get("ping_success")):
            summary_text.append(f"**Average Ping Time:** N/A — Ping test failed\n")
        else:
            summary_text.append(f"**Average Ping Time:** {avg_ping:.2f} ms — Network latency\n")
        
        summary_text.append(f"**DNS Resolution Time:** {dns_time:.2f} ms — DNS query time\n")
        
        success_count = sum([
            metrics.get("ping_success", False),
            metrics.get("dns_resolution", False),
            metrics.get("http_connection", False),
            metrics.get("https_connection", False)
        ])
        success_rate = (success_count / 4) * 100
        summary_text.append(f"**Connection Success Rate:** {success_rate:.0f}% — Overall connectivity\n")
        
        summary_text.append("\n## Diagnostics\n")
        issues = metrics.get("issues_found", [])
        
        # Add ping failure to issues if not already present
        if not metrics.get("ping_success") and not any("ping" in str(issue).lower() for issue in issues):
            issues.append("Ping test failed - host may be unreachable or ICMP blocked")
        
        if issues:
            summary_text.append("**Issues Found:**\n")
            for issue in issues:
                summary_text.append(f"• {issue}\n")
            
            # Add explanation for ping failures
            if not metrics.get("ping_success"):
                summary_text.append("\n**Why Ping May Fail:**\n")
                
                # Check for Windows Npcap issue
                issues_text = " ".join([str(issue) for issue in issues]).lower()
                if "npcap" in issues_text or "windows" in issues_text:
                    summary_text.append("• **Windows Npcap Required**: On Windows, Scapy requires Npcap library or administrator privileges to send ICMP packets\n")
                    summary_text.append("  - **Solution**: Install Npcap from https://npcap.com/ (recommended)\n")
                    summary_text.append("  - **Alternative**: Run the application as administrator\n")
                
                summary_text.append("• **ICMP Blocking**: Many websites/servers block ICMP (ping) for security reasons\n")
                summary_text.append("• **Firewall Rules**: Local or remote firewalls may block ICMP packets\n")
                summary_text.append("• **Privileges**: Sending ICMP packets requires administrator/root privileges on some systems\n")
                summary_text.append("• **Network Configuration**: Some networks disable ICMP entirely\n")
                summary_text.append("• **Note**: Ping failure does NOT mean the website is down - HTTP/HTTPS connections can still work\n")
        else:
            summary_text.append("**No issues detected** — All connectivity tests passed\n")
        
        summary_text.append("\n## Recommendations\n")
        recommendations = metrics.get("recommendations", [])
        valid_recommendations = [r for r in recommendations if r and isinstance(r, str) and r.strip()]
        
        # Add recommendations from metrics if they exist
        for rec in valid_recommendations:
            summary_text.append(f"• {rec}\n")
        
        # Add fallback recommendations if none were provided
        if not valid_recommendations:
            # Check for specific issues and provide recommendations
            if not metrics.get("ping_success"):
                summary_text.append("• Host may be unreachable or firewall blocking ICMP — Ping test failed\n")
            if not metrics.get("dns_resolution"):
                summary_text.append("• DNS resolution failed — Check DNS server configuration\n")
            if not metrics.get("http_connection") and not metrics.get("https_connection"):
                summary_text.append("• No HTTP/HTTPS connectivity — Check firewall rules and server status\n")
            elif not metrics.get("https_connection") and metrics.get("http_connection"):
                summary_text.append("• HTTPS connection failed but HTTP succeeded — Check SSL/TLS configuration\n")
            
            # If everything is working, provide positive feedback
            if (metrics.get("ping_success") and 
                metrics.get("dns_resolution") and 
                metrics.get("http_connection") and 
                metrics.get("https_connection")):
                summary_text.append("• All connectivity tests passed — Network connectivity is healthy\n")
                summary_text.append("• Consider monitoring these metrics regularly to detect issues early\n")
        
        summary = {
            "ping_success": metrics.get("ping_success", False),
            "dns_resolution": metrics.get("dns_resolution", False),
            "http_connection": metrics.get("http_connection", False),
            "https_connection": metrics.get("https_connection", False),
            "average_ping_time_ms": avg_ping if avg_ping is not None else None,
            "dns_resolution_time_ms": dns_time,
            "connection_success_rate": success_rate,
            "issues_count": len(issues),
            "summary_text": "".join(summary_text)
        }
    
    elif test_type.startswith("protocol_traffic") or test_type.startswith("protocol"):
        summary_text = []
        
        # Add target URL at the top
        target_url = metrics.get("target_url", "Unknown")
        if target_url and target_url != "Unknown":
            summary_text.append(f"## Test Target\n")
            summary_text.append(f"**Website:** [{target_url}]({target_url}) — Target being tested\n\n")
        
        summary_text.append("## Traffic Overview\n")
        total_packets = metrics.get("total_packets", 0)
        traffic_volume = metrics.get("traffic_volume_bytes", 0)
        analysis_method = metrics.get("analysis_method", "packet_capture")
        
        if analysis_method == "application_level":
            summary_text.append(f"**Total Packets:** {total_packets:,} — Estimated packets (application-level analysis)\n")
            summary_text.append(f"**Protocols Detected:** {', '.join(metrics.get('protocols_detected', []))} — Network protocols found\n")
            summary_text.append(f"**Traffic Volume:** {traffic_volume / (1024*1024):.2f} MB — Total data transferred\n")
            if metrics.get("note"):
                summary_text.append(f"**Note:** {metrics.get('note')}\n")
        else:
            summary_text.append(f"**Total Packets:** {total_packets:,} — Packets captured\n")
            summary_text.append(f"**Protocols Detected:** {', '.join(metrics.get('protocols_detected', []))} — Network protocols found\n")
            summary_text.append(f"**Traffic Volume:** {traffic_volume / (1024*1024):.2f} MB — Total data transferred\n")
        
        summary_text.append("\n## Protocol Distribution\n")
        protocol_dist = metrics.get("protocol_distribution", {})
        
        # Separate application protocols from transport protocols
        app_protocols = [p for p in protocol_dist.keys() if p not in ['TCP', 'UDP', 'ICMP']]
        transport_protocols = [p for p in protocol_dist.keys() if p in ['TCP', 'UDP', 'ICMP']]
        
        if app_protocols and transport_protocols:
            # Calculate percentages based on application protocols only for cleaner display
            app_total = sum(protocol_dist[p] for p in app_protocols)
            
            # Show application protocols
            for protocol in app_protocols:
                count = protocol_dist[protocol]
                percentage = (count / app_total * 100) if app_total > 0 else 0
                summary_text.append(f"**{protocol}:** {percentage:.1f}% — {count} packets\n")
            
            # Show transport protocols separately (they're the underlying layer)
            for protocol in transport_protocols:
                count = protocol_dist[protocol]
                summary_text.append(f"**{protocol}:** {count} packets (transport layer)\n")
        elif protocol_dist:
            # Normal display if no special handling needed
            total_protocol_packets = sum(protocol_dist.values())
            for protocol, count in protocol_dist.items():
                percentage = (count / total_protocol_packets * 100) if total_protocol_packets > 0 else 0
                summary_text.append(f"**{protocol}:** {percentage:.1f}% — {count} packets\n")
        
        summary_text.append("\n## Analysis\n")
        if protocol_dist:
            most_active = max(protocol_dist.items(), key=lambda x: x[1])[0]
            summary_text.append(f"**Most Active Protocol:** {most_active}\n")
        
        avg_packet_size = metrics.get("average_packet_size", 0)
        summary_text.append(f"**Average Packet Size:** {avg_packet_size:.2f} bytes\n")
        
        summary = {
            "total_packets": total_packets,
            "traffic_volume_bytes": traffic_volume,
            "protocols_detected_count": len(metrics.get("protocols_detected", [])),
            "average_packet_size_bytes": avg_packet_size,
            "summary_text": "".join(summary_text)
        }
    
    elif test_type.startswith("network_security") or test_type.startswith("security_scan"):
        summary_text = []
        
        # Add target URL at the top (prefer target_url from metrics, fallback to target)
        target_url = metrics.get("target_url") or metrics.get("target", "Unknown")
        if target_url and target_url != "Unknown":
            summary_text.append(f"## Test Target\n")
            summary_text.append(f"**Website:** [{target_url}]({target_url}) — Target being tested\n\n")
        
        summary_text.append("## Scan Results\n")
        target = metrics.get("target", target_url)
        if target and target != target_url:  # Only show if different from target_url
            summary_text.append(f"**Target:** {target}\n")
        summary_text.append(f"**Ports Scanned:** {metrics.get('ports_scanned', 0)} — Total ports tested\n")
        summary_text.append(f"**Open Ports:** {len(metrics.get('open_ports', []))} — Ports accepting connections\n")
        summary_text.append(f"**Filtered Ports:** {len(metrics.get('filtered_ports', []))} — Ports with firewall filtering\n")
        summary_text.append(f"**Closed Ports:** {len(metrics.get('closed_ports', []))} — Ports not accepting connections\n")
        
        summary_text.append("\n## Security Assessment\n")
        vulnerabilities = metrics.get("vulnerabilities", [])
        summary_text.append(f"**Vulnerabilities Found:** {len(vulnerabilities)} — Security issues detected\n")
        
        open_ports_count = len(metrics.get("open_ports", []))
        if open_ports_count == 0:
            risk_level = "Low"
        elif open_ports_count < 5:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        summary_text.append(f"**Risk Level:** {risk_level} — Overall risk assessment\n")
        
        services = metrics.get("services", {})
        if services:
            summary_text.append(f"**Exposed Services:** {', '.join([s.get('name', 'unknown') for s in services.values()])} — Services accessible from network\n")
        
        summary_text.append("\n## Recommendations\n")
        if open_ports_count > 0:
            summary_text.append(f"• Review {open_ports_count} open port(s) — Ensure they are necessary and properly secured\n")
        if vulnerabilities:
            summary_text.append(f"• Address {len(vulnerabilities)} vulnerability/vulnerabilities found\n")
        if risk_level == "High":
            summary_text.append("• High number of open ports detected — Consider closing unnecessary services\n")
        
        summary = {
            "ports_scanned": metrics.get("ports_scanned", 0),
            "open_ports_count": open_ports_count,
            "filtered_ports_count": len(metrics.get("filtered_ports", [])),
            "closed_ports_count": len(metrics.get("closed_ports", [])),
            "vulnerabilities_count": len(vulnerabilities),
            "risk_level": risk_level,
            "summary_text": "".join(summary_text)
        }
    
    if test_type.startswith("endpoint_discovery") or (test_type.startswith("endpoint") and not test_type.startswith("endpoint_performance")):
        summary_text = []
        
        # Add target URL at the top
        target_url = metrics.get("target_url") or metrics.get("target", "Unknown")
        if target_url and target_url != "Unknown":
            summary_text.append(f"## Test Target\n")
            summary_text.append(f"**Website:** [{target_url}]({target_url}) — Target being tested\n\n")
        
        summary_text.append("## Discovery Results\n")
        total_endpoints = metrics.get("total_endpoints", 0)
        summary_text.append(f"**Total Endpoints Found:** {total_endpoints} — API endpoints discovered\n")
        methods = metrics.get("methods_detected", [])
        summary_text.append(f"**HTTP Methods:** {', '.join(methods) if methods else 'None'} — Methods detected\n")
        
        status_codes = metrics.get("status_codes", {})
        if status_codes:
            summary_text.append(f"**Status Codes:** {', '.join(status_codes.keys())} — Response status codes\n")
        
        summary_text.append("\n## Endpoint Analysis\n")
        endpoints = metrics.get("endpoints_found", [])
        # Count successful (2xx) vs failed (4xx/5xx) endpoints
        successful_count = sum(1 for e in endpoints if 200 <= e.get("status_code", 0) < 300)
        failed_count = sum(1 for e in endpoints if e.get("status_code", 0) >= 400)
        public_count = sum(1 for e in endpoints if e.get("status_code", 0) < 400)
        protected_count = sum(1 for e in endpoints if e.get("status_code", 0) >= 400)
        
        summary_text.append(f"**Successful Endpoints:** {successful_count} — Endpoints returning 2xx status\n")
        summary_text.append(f"**Not Found Endpoints:** {failed_count} — Endpoints returning 4xx status (may be missing or protected)\n")
        summary_text.append(f"**Unprotected Endpoints:** {public_count} — Endpoints accessible without authentication\n")
        summary_text.append(f"**Protected Endpoints:** {protected_count} — Endpoints requiring auth or returning errors\n")
        
        avg_response = metrics.get("average_response_time", 0)
        summary_text.append(f"**Average Response Time:** {avg_response:.2f} ms — Endpoint performance\n")
        
        summary_text.append("\n## Recommendations\n")
        if successful_count > 0:
            summary_text.append(f"• {successful_count} endpoint(s) are accessible — Review security and authentication\n")
        if failed_count > 0:
            summary_text.append(f"• {failed_count} endpoint(s) returned 4xx status — May indicate missing or protected endpoints\n")
        if public_count > protected_count:
            summary_text.append("• Review unprotected endpoints — Ensure proper authentication and authorization\n")
        if avg_response > 1000:
            summary_text.append(f"• Optimize slow endpoints — Average response time ({avg_response:.2f}ms) is high\n")
        
        summary = {
            "total_endpoints": total_endpoints,
            "methods_detected_count": len(methods),
            "successful_endpoints_count": successful_count,
            # Don't include failed_endpoints_count in summary cards - it's shown in summary text
            # "failed_endpoints_count": failed_count,  # Removed - redundant with summary text
            "unprotected_endpoints_count": public_count,  # Renamed from public_endpoints_count
            "protected_endpoints_count": protected_count,
            "average_response_time_ms": avg_response,
            "summary_text": "".join(summary_text)
        }
    
    return summary


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup - DO NOT auto-initialize browser (lazy initialization)
    # Agent object will be created on first request, browser session starts on first test
    # Start test queue processor
    global queue_processor_running
    queue_task = None
    if not queue_processor_running:
        queue_task = asyncio.create_task(_execute_test_queue())
    
    yield
    
    # Shutdown - cleanup browser if it was started
    global global_agent, external_browsers, test_queue, test_tasks
    
    # Stop queue processor
    if queue_task:
        await test_queue.put(None)  # Shutdown signal
        try:
            await asyncio.wait_for(queue_task, timeout=5.0)
        except asyncio.TimeoutError:
            queue_task.cancel()
    
    # Cancel any running tests
    for test_id, task in test_tasks.items():
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    try:
        if global_agent:
            if hasattr(global_agent, 'browser') and global_agent.browser:
                await global_agent.browser.close()
            if hasattr(global_agent, 'playwright') and global_agent.playwright:
                await global_agent.playwright.stop()
        # Close all external browsers
        for browser_key, browser_info in external_browsers.items():
            try:
                if 'browser' in browser_info:
                    await browser_info['browser'].close()
                if 'playwright' in browser_info:
                    await browser_info['playwright'].stop()
            except Exception:
                pass
        external_browsers.clear()
    except Exception:
        pass


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="QA Agent API",
    description="Backend service for multi-AI QA automation",
    version="1.0.0",
    lifespan=lifespan,
)

# Ensure screenshots directory exists and mount static serving
SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mobile_test_screenshots")
try:
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
except Exception:
    pass

app.mount("/static/mobile", StaticFiles(directory=SCREENSHOTS_DIR), name="mobile_screenshots")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MobileTestRequest(BaseModel):
    """Request to run a mobile responsiveness test"""
    deviceName: Optional[str] = Field(default="iPhone 17 Pro Max", description="Device name to emulate")
    custom: Optional[Dict[str, Any]] = Field(default=None, description="Custom dimensions { width, height, deviceScaleFactor? }")
    overlapPercent: Optional[float] = Field(default=0.12, description="Fractional overlap between successive screenshots (e.g., 0.1 for 10%)")

class MobileTestResponse(BaseModel):
    """Response for mobile test run"""
    device_name: str
    device: Dict[str, Any]
    screenshots: list
    served_base_url: str
    message: str



class TestResultResponse(BaseModel):
    """Test result details"""
    test_id: str
    command: str
    status: TestStatus
    result: str
    started_at: str
    completed_at: Optional[str] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "QA Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/qa-tests/health"
    }


@app.get("/api/v1/qa-tests/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_status": agent_status,
        "commands_executed": commands_executed,
        "total_test_results": len(test_results),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/qa-tests/agent-status")
async def get_agent_status():
    """Get current agent status"""
    await _ensure_global_agent()
    return _get_agent_status()


@app.get("/api/v1/qa-tests/browser-view")
async def get_browser_view():
    """Get browser view - returns screenshot for embedding in frontend"""
    global global_agent, agent_status
    
    # Check if browser is active
    if agent_status != "active":
        return {
            "active": False,
            "message": f"Browser is not active. Status: {agent_status}",
            "status": agent_status
        }
    
    try:
        browser = getattr(global_agent, "browser", None)
        page = getattr(global_agent, "current_page", None)
        
        if browser is None or page is None:
            return {
                "active": False,
                "message": "Browser page not available",
                "status": agent_status
            }
        
        # Capture screenshot and return as base64
        try:
            screenshot_bytes = await page.screenshot(full_page=False)
            import base64
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            current_url = page.url
            
            return {
                "active": True,
                "page_url": current_url,
                "screenshot": screenshot_b64,
                "screenshot_data_url": f"data:image/png;base64,{screenshot_b64}",
                "message": "Browser is active and ready",
                "status": agent_status,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as screenshot_error:
            return {
                "active": True,
                "page_url": page.url if page else None,
                "screenshot": None,
                "message": f"Screenshot failed: {str(screenshot_error)}",
                "status": agent_status
            }
    except Exception as e:
        return {
            "active": False,
            "message": f"Error getting browser view: {str(e)}",
            "status": agent_status
        }


@app.post("/api/v1/qa-tests/navigate")
async def navigate_to_url(request: NavigateRequest):
    """Navigate to a website URL"""
    # Ensure agent object exists (may be uninitialized)
    await _ensure_global_agent()
    
    # Lazy initialize browser session if not already active
    if agent_status not in {"active", "initializing"}:
        # Start browser session with the requested URL (no auto_check)
        if not await _start_browser_session(website_url=request.website_url.strip(), auto_check=False):
            if agent_status == "failed":
                raise HTTPException(
                    status_code=400,
                    detail=f"Browser initialization failed. Status: {agent_status}. Error: {agent_error or 'Unknown error'}"
                )
            raise HTTPException(
                status_code=400,
                detail=f"Browser is not ready. Status: {agent_status}. Please wait for initialization."
            )
    
    # If still initializing, wait for it
    if agent_status == "initializing":
        for _ in range(60):
            await asyncio.sleep(1)
            if agent_status == "active":
                break
            if agent_status == "failed":
                raise HTTPException(
                    status_code=400,
                    detail=f"Browser initialization failed. Error: {agent_error or 'Unknown error'}"
                )
    
    if agent_status != "active":
        raise HTTPException(
            status_code=400,
            detail=f"Browser is not ready. Status: {agent_status}. Please wait for initialization."
        )

    try:
        # Get the current page from the agent
        page = getattr(global_agent, "current_page", None)
        if page is None:
            raise HTTPException(status_code=400, detail="No active page available")

        # Navigate to the new URL
        website_url = request.website_url.strip()
        if not website_url.startswith(('http://', 'https://')):
            website_url = f'https://{website_url}'

        try:
            await page.goto(website_url, wait_until="domcontentloaded", timeout=45000)
        except Exception as e1:
            try:
                await page.goto(website_url, wait_until="load", timeout=60000)
            except Exception as e2:
                try:
                    await page.goto(website_url, wait_until="commit", timeout=30000)
                except Exception as e3:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to navigate to {website_url}: {str(e3)}"
                    )

        # Wait for page to be ready
        try:
            await page.wait_for_selector("body", timeout=10000)
        except Exception:
            pass
        await page.wait_for_timeout(2000)

        # Verify navigation succeeded by checking actual page URL
        actual_url = page.url
        if not actual_url.startswith(website_url.split('?')[0]) and not actual_url.startswith(website_url.replace('https://', 'http://').split('?')[0]):
            # Check if it's a redirect - normalize both URLs for comparison
            normalized_target = website_url.rstrip('/').split('?')[0].split('#')[0]
            normalized_actual = actual_url.rstrip('/').split('?')[0].split('#')[0]
            if normalized_actual != normalized_target and not normalized_actual.startswith(normalized_target):
                raise HTTPException(
                    status_code=500,
                    detail=f"Navigation verification failed: expected {website_url} but page is at {actual_url}"
                )

        # Update agent's current URL
        global_agent.current_url = website_url

        # Run page analysis after navigation (similar to start_session)
        # This helps the agent understand the new page
        try:
            if hasattr(global_agent, '_analyze_page_characteristics'):
                await global_agent._analyze_page_characteristics()
        except Exception as e:
            # Log but don't fail - page analysis is optional
            print(f"Page analysis after navigation failed: {e}")

        return {
            "message": f"Successfully navigated to {website_url}",
            "website_url": website_url,
            "actual_url": actual_url,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Navigation failed: {str(e)}")


@app.post("/api/v1/qa-tests/commands", response_model=CommandResponse)
async def execute_command(request: CommandRequest):
    """Execute a natural language command"""
    global commands_executed
    
    # Ensure agent object exists (may be uninitialized)
    await _ensure_global_agent()
    
    # Lazy initialize browser session if not already active
    if agent_status not in {"active", "initializing"}:
        # Start browser session with default URL (will navigate to user's URL later)
        if not await _start_browser_session(website_url="https://www.w3schools.com/", auto_check=False):
            if agent_status == "failed":
                raise HTTPException(
                    status_code=400,
                    detail=f"Browser initialization failed. Status: {agent_status}. Error: {agent_error or 'Unknown error'}"
                )
            raise HTTPException(
                status_code=400,
                detail=f"Browser is not ready. Status: {agent_status}. Please wait for initialization."
            )
    
    # If still initializing, wait for it
    if agent_status == "initializing":
        # Wait up to 60 seconds for initialization
        for _ in range(60):
            await asyncio.sleep(1)
            if agent_status == "active":
                break
            if agent_status == "failed":
                raise HTTPException(
                    status_code=400,
                    detail=f"Browser initialization failed. Error: {agent_error or 'Unknown error'}"
                )
    
    # Final check
    if agent_status != "active":
        raise HTTPException(
            status_code=400,
            detail=f"Browser is not ready. Status: {agent_status}. Please wait for initialization."
        )

    try:
        start_time = datetime.utcnow()

        # For auto check and auto audit commands, add scrolling behavior before execution
        command_lower = request.command.lower().strip()
        if command_lower == 'auto check' or command_lower == 'auto audit':
            try:
                page = getattr(global_agent, "current_page", None)
                if page:
                    # Scroll to top first
                    await page.evaluate("window.scrollTo(0, 0)")
                    await asyncio.sleep(0.5)
                    
                    # Get page height
                    page_height = await page.evaluate("document.body.scrollHeight || document.documentElement.scrollHeight")
                    viewport_height = await page.evaluate("window.innerHeight")
                    
                    # Scroll from top to bottom smoothly
                    scroll_step = viewport_height // 2
                    scroll_position = 0
                    
                    while scroll_position < page_height:
                        await page.evaluate(f"window.scrollTo(0, {scroll_position})")
                        await asyncio.sleep(0.2)  # Smooth scrolling
                        scroll_position += scroll_step
                    
                    # Scroll to bottom and stay there
                    await page.evaluate(f"window.scrollTo(0, {page_height})")
                    await asyncio.sleep(1)
                    
                    # Keep at bottom for a moment before executing command
                    await asyncio.sleep(0.5)
            except Exception as scroll_error:
                print(f"Scrolling during {command_lower} failed: {scroll_error}")

        # Execute the command
        result = await global_agent.process_command(request.command)

        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000

        # Update stats
        commands_executed += 1

        # Store test result
        test_id = str(uuid.uuid4())
        test_results[test_id] = {
            "test_id": test_id,
            "command": request.command,
            "result": result,
            "status": TestStatus.completed,
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat(),
            "duration_ms": duration_ms
        }

        return CommandResponse(
            command=request.command,
            result=result,
            status=TestStatus.completed,
            executed_at=end_time.isoformat(),
            duration_ms=duration_ms
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {str(e)}")


@app.post("/api/v1/qa-tests/open-browser-external")
async def open_browser_external(request: CrossBrowserTestRequest):
    """Open a browser externally in headful mode with full UI"""
    global global_agent, external_browsers
    
    # Ensure agent object exists
    await _ensure_global_agent()
    
    # Use the provided URL or current URL from agent
    test_url = request.website_url or getattr(global_agent, "current_url", None) or "https://www.w3schools.com/"
    
    # Get browser type from request
    browser_type = getattr(request, 'browser_type', 'chromium')
    
    if browser_type not in ['chromium', 'firefox', 'webkit']:
        raise HTTPException(status_code=400, detail="Invalid browser type. Use: chromium, firefox, or webkit")
    
    try:
        from playwright.async_api import async_playwright
        
        # Close existing browser of this type if it exists
        browser_key = f"{browser_type}_external"
        if browser_key in external_browsers:
            try:
                existing = external_browsers[browser_key]
                if 'browser' in existing:
                    await existing['browser'].close()
                if 'playwright' in existing:
                    await existing['playwright'].stop()
            except Exception:
                pass  # Ignore errors closing old browser
            del external_browsers[browser_key]
        
        # Launch browser in headful mode (visible, with full UI)
        playwright = await async_playwright().start()
        
        if browser_type == 'chromium':
            browser = await playwright.chromium.launch(
                headless=False,  # Show full browser UI
                slow_mo=500,
                args=['--start-maximized']  # Maximize window
            )
        elif browser_type == 'firefox':
            browser = await playwright.firefox.launch(
                headless=False,  # Show full browser UI
                slow_mo=500
            )
        elif browser_type == 'webkit':
            browser = await playwright.webkit.launch(
                headless=False,  # Show full browser UI
                slow_mo=500
            )
        
        # Create context and page
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        # Navigate to URL
        try:
            await page.goto(test_url, wait_until="domcontentloaded", timeout=45000)
        except Exception as e1:
            try:
                await page.goto(test_url, wait_until="load", timeout=60000)
            except Exception as e2:
                await page.goto(test_url, wait_until="commit", timeout=30000)
        
        await page.wait_for_timeout(1000)
        
        # Store browser instances to keep them alive
        external_browsers[browser_key] = {
            'playwright': playwright,
            'browser': browser,
            'context': context,
            'page': page,
            'browser_type': browser_type,
            'url': test_url,
            'opened_at': datetime.utcnow().isoformat()
        }
        
        return {
            "message": f"Opened {browser_type} externally",
            "browser_type": browser_type,
            "url": test_url,
            "status": "opened",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to open browser externally: {str(e)}")


@app.post("/api/v1/qa-tests/cross-browser-test")
async def run_cross_browser_test(request: CrossBrowserTestRequest):
    """Run cross-browser test - can test all browsers or a specific one"""
    global global_agent, agent_status, commands_executed, test_results
    
    # Ensure agent object exists (may be uninitialized)
    await _ensure_global_agent()
    
    # Use the provided URL or current URL from agent
    test_url = request.website_url or getattr(global_agent, "current_url", None) or "https://www.w3schools.com/"
    
    # Get browser type from request if provided
    browser_type = getattr(request, 'browser_type', None)
    
    start_time = datetime.utcnow()
    
    try:
        from playwright.async_api import async_playwright
        
        # If specific browser requested, test only that one
        if browser_type and browser_type in ['chromium', 'firefox', 'webkit']:
            browsers_to_test = [browser_type]
        else:
            browsers_to_test = ['chromium', 'firefox', 'webkit']
        
        results = {}
        
        for browser_type in browsers_to_test:
            try:
                print(f"Testing on {browser_type}...")
                
                # Launch browser in headless mode (for embedding)
                playwright = await async_playwright().start()
                
                if browser_type == 'chromium':
                    browser = await playwright.chromium.launch(headless=True, slow_mo=500)
                elif browser_type == 'firefox':
                    browser = await playwright.firefox.launch(headless=True, slow_mo=500)
                elif browser_type == 'webkit':
                    browser = await playwright.webkit.launch(headless=True, slow_mo=500)
                else:
                    results[browser_type] = {"status": "failed", "error": f"Unknown browser: {browser_type}"}
                    continue
                
                # Create context and page
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    ignore_https_errors=True
                )
                page = await context.new_page()
                
                # Navigate to URL
                try:
                    await page.goto(test_url, wait_until="domcontentloaded", timeout=45000)
                except Exception as e1:
                    try:
                        await page.goto(test_url, wait_until="load", timeout=60000)
                    except Exception as e2:
                        await page.goto(test_url, wait_until="commit", timeout=30000)
                
                await page.wait_for_timeout(2000)
                
                # Get page info
                title = await page.title()
                url = page.url
                
                # Take screenshot
                screenshot_bytes = await page.screenshot(full_page=False)
                import base64
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                
                # Close browser
                await browser.close()
                await playwright.stop()
                
                results[browser_type] = {
                    "status": "success",
                    "title": title,
                    "url": url,
                    "screenshot": f"data:image/png;base64,{screenshot_b64}"
                }
                
            except Exception as e:
                results[browser_type] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Determine overall test status
        success_count = len([r for r in results.values() if r.get("status") == "success"])
        total_count = len(browsers_to_test)
        
        if success_count == total_count:
            overall_status = TestStatus.passed
        elif success_count > 0:
            overall_status = TestStatus.completed
        else:
            overall_status = TestStatus.failed
        
        # Update stats
        commands_executed += 1
        
        # Store test result for dashboard
        test_id = str(uuid.uuid4())
        
        # Format result text
        result_lines = [f"🌐 Cross-Browser Test Results for {test_url}:"]
        for browser_name, browser_result in results.items():
            if browser_result.get("status") == "success":
                result_lines.append(f"   ✅ {browser_name.capitalize()}: Success - {browser_result.get('title', 'N/A')}")
            else:
                result_lines.append(f"   ❌ {browser_name.capitalize()}: Failed - {browser_result.get('error', 'Unknown error')}")
        
        result_text = "\n".join(result_lines)
        
        test_results[test_id] = {
            "test_id": test_id,
            "command": f"cross-browser test ({', '.join(browsers_to_test)})",
            "result": result_text,
            "status": overall_status,
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat(),
            "duration_ms": duration_ms,
            "executed_at": end_time.isoformat()
        }
        
        return {
            "test_url": test_url,
            "browsers": results,
            "total_browsers": len(browsers_to_test),
            "completed": success_count,
            "test_id": test_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        # Still record the test as failed
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        commands_executed += 1
        
        test_id = str(uuid.uuid4())
        test_results[test_id] = {
            "test_id": test_id,
            "command": f"cross-browser test ({', '.join(browsers_to_test) if 'browsers_to_test' in locals() else 'all browsers'})",
            "result": f"Cross-browser test failed: {str(e)}",
            "status": TestStatus.failed,
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat(),
            "duration_ms": duration_ms,
            "executed_at": end_time.isoformat(),
            "error": str(e)
        }
        
        raise HTTPException(status_code=500, detail=f"Cross-browser test failed: {str(e)}")


@app.post("/api/v1/qa-tests/mobile-test", response_model=MobileTestResponse)
async def run_mobile_test(request: MobileTestRequest, http_request: Request):
    """Run a non-interactive mobile test and return screenshot URLs."""
    # Ensure agent object exists (may be uninitialized)
    await _ensure_global_agent()
    
    # Lazy initialize browser session if not already active
    if agent_status not in {"active", "initializing"}:
        # Start browser session with default URL (will navigate to user's URL later)
        if not await _start_browser_session(website_url="https://www.w3schools.com/", auto_check=False):
            if agent_status == "failed":
                raise HTTPException(
                    status_code=400,
                    detail=f"Browser initialization failed. Status: {agent_status}. Error: {agent_error or 'Unknown error'}"
                )
            raise HTTPException(
                status_code=400,
                detail=f"Browser is not ready. Status: {agent_status}. Please wait for initialization."
            )
    
    # If still initializing, wait for it
    if agent_status == "initializing":
        for _ in range(60):
            await asyncio.sleep(1)
            if agent_status == "active":
                break
            if agent_status == "failed":
                raise HTTPException(
                    status_code=400,
                    detail=f"Browser initialization failed. Error: {agent_error or 'Unknown error'}"
                )
    
    if agent_status != "active":
        raise HTTPException(
            status_code=400,
            detail=f"Browser is not ready. Status: {agent_status}. Please wait for initialization."
        )

    try:
        started_at = datetime.utcnow()
        test_id = str(uuid.uuid4())
        page = getattr(global_agent, "current_page", None)
        if page is None:
            raise HTTPException(status_code=400, detail="No active page available. Wait for initialization to complete.")

        # Resolve device config from agent's MobileDeviceManager or custom
        device_name = request.deviceName or "iPhone 17 Pro Max"
        device_cfg: Dict[str, Any]
        if request.custom and isinstance(request.custom, dict):
            # Validate custom dimensions
            width = int(request.custom.get("width", 0))
            height = int(request.custom.get("height", 0))
            scale = int(request.custom.get("deviceScaleFactor", 1) or 1)
            if width <= 0 or height <= 0:
                raise HTTPException(status_code=400, detail="Custom width and height must be positive integers")
            device_cfg = {"width": width, "height": height, "deviceScaleFactor": scale}
            device_name = request.custom.get("name") or f"Custom {width}x{height}"
        else:
            devices = getattr(global_agent.mobile_device_manager, "devices", {})
            device_cfg = devices.get(device_name)
            if not device_cfg:
                raise HTTPException(status_code=400, detail=f"Unknown device: {device_name}")

        # Store original viewport
        original_viewport = page.viewport_size

        # Set viewport to device
        await page.set_viewport_size({
            "width": device_cfg["width"],
            "height": device_cfg["height"],
        })

        # Allow layout to stabilize
        await page.wait_for_timeout(500)

        # Measure page height and scroll, capturing screenshots
        try:
            page_height = await page.evaluate("document.body.scrollHeight")
        except Exception:
            page_height = device_cfg["height"]

        viewport_h = device_cfg["height"]
        scroll_position = 0
        count = 0
        screenshot_urls = []

        # Calculate overlap: default 12% (10-15% requested)
        try:
            overlap_fraction = float(request.overlapPercent if request.overlapPercent is not None else 0.12)
        except Exception:
            overlap_fraction = 0.12
        # Clamp reasonable bounds [0, 0.3]
        overlap_fraction = max(0.0, min(0.3, overlap_fraction))
        step = max(1, int(viewport_h * (1.0 - overlap_fraction)))

        # Namespace files in a per-test directory
        test_dir = os.path.join(SCREENSHOTS_DIR, test_id)
        try:
            os.makedirs(test_dir, exist_ok=True)
        except Exception:
            pass

        while scroll_position < page_height and count < 40:
            # Scroll and wait
            await page.evaluate(f"window.scrollTo(0, {scroll_position})")
            await page.wait_for_timeout(400)

            count += 1
            filename = f"{device_name.replace(' ', '_')}_{count}.png"
            filepath = os.path.join(test_dir, filename)
            try:
                await page.screenshot(path=filepath)
                rel = f"/static/mobile/{test_id}/{filename}"
                base = str(http_request.base_url).rstrip('/')
                screenshot_urls.append(f"{base}{rel}")
            except Exception:
                # Skip failures but continue
                pass

            scroll_position += step

        # Scroll back to top and reset viewport
        try:
            await page.evaluate("window.scrollTo(0, 0)")
        except Exception:
            pass
        try:
            await page.set_viewport_size(original_viewport)
        except Exception:
            pass

        # Persist test result for Test Results page
        try:
            completed_at = datetime.utcnow()
            duration_ms = (completed_at - started_at).total_seconds() * 1000
            test_results[test_id] = {
                "test_id": test_id,
                "command": "mobile test",
                "status": TestStatus.completed,
                "result": f"Captured {len(screenshot_urls)} screenshots on {device_name} ({device_cfg.get('width')}x{device_cfg.get('height')})",
                "started_at": started_at.isoformat(),
                "completed_at": completed_at.isoformat(),
                "duration_ms": duration_ms,
                "device": {
                    "name": device_name,
                    "width": device_cfg.get("width"),
                    "height": device_cfg.get("height"),
                    "deviceScaleFactor": device_cfg.get("deviceScaleFactor", 1),
                },
                "screenshots": screenshot_urls,
            }
        except Exception:
            pass

        return MobileTestResponse(
            device_name=device_name,
            device={
                "name": device_name,
                "width": device_cfg.get("width"),
                "height": device_cfg.get("height"),
                "deviceScaleFactor": device_cfg.get("deviceScaleFactor", 1),
            },
            screenshots=screenshot_urls,
            served_base_url=str(http_request.base_url).rstrip('/') + "/static/mobile/",
            message=f"Captured {len(screenshot_urls)} screenshots"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mobile test failed: {str(e)}")


@app.post("/api/v1/qa-tests/browser-use/execute")
async def execute_browser_use(request: BrowserUseRequest):
    """
    Execute a simple browser automation task using browser-use library.
    Returns structured output of agent execution history.
    """
    started_at = datetime.utcnow()
    test_id = str(uuid.uuid4())
    
    try:
        # Import browser_use components
        try:
            from browser_use import Agent as BrowserAgent, ChatGoogle
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="browser-use library not installed. Install with: pip install browser-use"
            )

        # Import parser utility - use only the simple formatter to avoid schema dependencies
        from qa_agent.utils.browser_use_parser import format_terminal_output_simple

        # Import appropriate chat model
        if request.ai_provider == AIProvider.google:
            # Get API key from environment
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise HTTPException(
                    status_code=400,
                    detail="Google API key not found in environment variables. Please add GOOGLE_API_KEY to your .env file."
                )
            llm = ChatGoogle(model="gemini-flash-latest", api_key=api_key)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Browser-use currently only supports Google AI provider"
            )

        # Create agent and execute task
        agent = BrowserAgent(task=request.task, llm=llm)

        # Run the task and get history
        history = await agent.run()
        
        # Create terminal-style output (simple version that doesn't need schemas)
        terminal_output = format_terminal_output_simple(history, request.task)

        # Determine test status by parsing terminal output
        # Use regex patterns similar to frontend logic for more robust matching
        import re
        terminal_text = terminal_output
        
        # Check for explicit PASSED/FAILED markers using regex (case-insensitive)
        passed_patterns = [
            r'(?:\n|^)\s*✓\s*TEST\s+CASE\s+STATUS:\s*PASSED',
            r'(?:\n|^)\s*TEST\s+CASE:\s*PASSED',
            r'test\s+case\s+is\s*\*\*passed\*\*',
            r'Test\s+case\s+is\s+PASSED',
            r'test\s+case\s+status:\s*passed',
            r'test\s+case:\s*passed',
        ]
        failed_patterns = [
            r'(?:\n|^)\s*✗\s*TEST\s+CASE\s+STATUS:\s*FAILED',
            r'(?:\n|^)\s*TEST\s+CASE:\s*FAILED',
            r'test\s+case\s+is\s*\*\*failed\*\*',
            r'Test\s+case\s+is\s+FAILED',
            r'test\s+case\s+status:\s*failed',
            r'test\s+case:\s*failed',
            r'Conclusion:\s*Test\s+case\s+failed',  # Catch conclusion patterns
            r'Conclusion:.*[Tt]est\s+case\s+failed',  # Catch variations
        ]
        
        passed_marker = any(re.search(pattern, terminal_text, re.IGNORECASE | re.MULTILINE) for pattern in passed_patterns)
        failed_marker = any(re.search(pattern, terminal_text, re.IGNORECASE | re.MULTILINE) for pattern in failed_patterns)
        
        # Determine status
        if passed_marker and not failed_marker:
            test_status = TestStatus.passed
        elif failed_marker:
            test_status = TestStatus.failed
        else:
            test_status = TestStatus.completed

        completed_at = datetime.utcnow()
        duration_ms = (completed_at - started_at).total_seconds() * 1000

        # Store test result
        test_results[test_id] = {
            "test_id": test_id,
            "command": request.task,
            "status": test_status.value,
            "result": terminal_output,
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "duration_ms": duration_ms
        }

        return {
            "task": request.task,
            "status": test_status.value,
            "terminal_output": terminal_output,  # Terminal-style formatted output
            "executed_at": completed_at.isoformat(),
            "test_id": test_id
        }

    except HTTPException:
        raise
    except Exception as e:
        # Store failed test result
        completed_at = datetime.utcnow()
        duration_ms = (completed_at - started_at).total_seconds() * 1000
        test_results[test_id] = {
            "test_id": test_id,
            "command": request.task,
            "status": TestStatus.failed.value,
            "result": f"Browser automation failed: {str(e)}",
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "duration_ms": duration_ms,
            "error": str(e)
        }
        raise HTTPException(status_code=500, detail=f"Browser automation failed: {str(e)}")


async def _queue_test(
    test_type: str,
    test_name: str,
    test_func: Callable,
    test_params: Dict[str, Any],
    website_url: Optional[str] = None
) -> str:
    """Queue a test for execution and return test_id"""
    global test_queue, test_results
    
    # Get target URL
    target_url = website_url or getattr(global_agent, "current_url", None) or "https://www.w3schools.com/"
    
    # Validate URL
    if not target_url or not target_url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="Valid website URL is required")
    
    # Generate test ID
    test_id = str(uuid.uuid4())
    started_at = datetime.utcnow()
    
    # Initialize test result
    test_results[test_id] = {
        "test_id": test_id,
        "test_type": test_type,
        "test_name": test_name,
        "status": TestStatus.pending,
        "started_at": started_at.isoformat(),
        "progress": 0.0
    }
    
    # Update test_params with target_url
    test_params["target_url"] = target_url
    
    # Queue test
    await test_queue.put((test_id, test_type, test_func, test_params))
    
    return test_id


@app.post("/api/v1/qa-tests/load-test")
async def run_load_test(request: LoadTestRequest):
    """Run basic load test"""
    try:
        from qa_agent.utils.locust_runner import LocustTestRunner
        
        runner = LocustTestRunner()
        test_id = await _queue_test(
            "load_test",
            request.test_name or "Basic Load Test",
            runner.run_load_test,
            {
                "users": request.users,
                "spawn_rate": request.ramp_up,
                "duration": request.duration
            },
            request.target_url or request.website_url
        )
        
        return {"test_id": test_id, "status": "queued", "message": "Load test queued for execution"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue load test: {str(e)}")


@app.post("/api/v1/qa-tests/stress-test")
async def run_stress_test(request: StressTestRequest):
    """Run stress test"""
    try:
        from qa_agent.utils.locust_runner import LocustTestRunner
        
        runner = LocustTestRunner()
        test_id = await _queue_test(
            "stress_test",
            request.test_name or "Stress Test",
            runner.run_stress_test,
            {
                "max_users": request.max_users,
                "step_users": request.step_users,
                "duration": request.duration
            },
            request.website_url
        )
        
        return {"test_id": test_id, "status": "queued", "message": "Stress test queued for execution"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue stress test: {str(e)}")


@app.post("/api/v1/qa-tests/spike-test")
async def run_spike_test(request: SpikeTestRequest):
    """Run spike test"""
    try:
        from qa_agent.utils.locust_runner import LocustTestRunner
        
        runner = LocustTestRunner()
        test_id = await _queue_test(
            "spike_test",
            request.test_name or "Spike Test",
            runner.run_spike_test,
            {
                "initial_users": request.initial_users,
                "spike_users": request.spike_users,
                "duration": request.duration
            },
            request.website_url
        )
        
        return {"test_id": test_id, "status": "queued", "message": "Spike test queued for execution"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue spike test: {str(e)}")


@app.post("/api/v1/qa-tests/soak-test")
async def run_soak_test(request: SoakTestRequest):
    """Run soak test"""
    try:
        from qa_agent.utils.locust_runner import LocustTestRunner
        
        runner = LocustTestRunner()
        test_id = await _queue_test(
            "soak_test",
            request.test_name or "Soak Test",
            runner.run_soak_test,
            {
                "users": request.users,
                "duration_hours": request.duration_hours
            },
            request.website_url
        )
        
        return {"test_id": test_id, "status": "queued", "message": "Soak test queued for execution"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue soak test: {str(e)}")


@app.post("/api/v1/qa-tests/ramp-up-test")
async def run_ramp_up_test(request: RampUpTestRequest):
    """Run ramp-up test"""
    try:
        from qa_agent.utils.locust_runner import LocustTestRunner
        
        runner = LocustTestRunner()
        test_id = await _queue_test(
            "ramp_up_test",
            request.test_name or "Ramp-Up Test",
            runner.run_ramp_up_test,
            {
                "max_users": request.max_users,
                "ramp_up_time": request.ramp_up_time,
                "duration": request.duration
            },
            request.website_url
        )
        
        return {"test_id": test_id, "status": "queued", "message": "Ramp-up test queued for execution"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue ramp-up test: {str(e)}")


@app.post("/api/v1/qa-tests/throughput-test")
async def run_throughput_test(request: ThroughputTestRequest):
    """Run throughput test"""
    try:
        from qa_agent.utils.locust_runner import LocustTestRunner
        
        runner = LocustTestRunner()
        test_id = await _queue_test(
            "throughput_test",
            request.test_name or "Throughput Test",
            runner.run_throughput_test,
            {
                "target_rps": request.target_rps,
                "duration": request.duration
            },
            request.website_url
        )
        
        return {"test_id": test_id, "status": "queued", "message": "Throughput test queued for execution"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue throughput test: {str(e)}")


@app.post("/api/v1/qa-tests/endpoint-performance-test")
async def run_endpoint_performance_test(request: EndpointPerformanceTestRequest):
    """Run endpoint performance test"""
    try:
        from qa_agent.utils.locust_runner import LocustTestRunner
        
        runner = LocustTestRunner()
        test_id = await _queue_test(
            "endpoint_performance_test",
            request.test_name or f"Endpoint Performance Test: {request.endpoint}",
            runner.run_endpoint_performance_test,
            {
                "endpoint": request.endpoint,
                "users": request.users,
                "duration": request.duration
            },
            request.website_url
        )
        
        return {"test_id": test_id, "status": "queued", "message": "Endpoint performance test queued for execution"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue endpoint performance test: {str(e)}")


@app.post("/api/v1/qa-tests/api-load-test")
async def run_api_load_test(request: ApiLoadTestRequest):
    """Run API load test"""
    try:
        from qa_agent.utils.locust_runner import LocustTestRunner
        
        runner = LocustTestRunner()
        test_id = await _queue_test(
            "api_load_test",
            request.test_name or "API Load Test",
            runner.run_api_load_test,
            {
                "users": request.users,
                "duration": request.duration
            },
            request.website_url
        )
        
        return {"test_id": test_id, "status": "queued", "message": "API load test queued for execution"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue API load test: {str(e)}")


@app.post("/api/v1/qa-tests/website-load-test")
async def run_website_load_test(request: WebsiteLoadTestRequest):
    """Run website load test"""
    try:
        from qa_agent.utils.locust_runner import LocustTestRunner
        
        runner = LocustTestRunner()
        test_id = await _queue_test(
            "website_load_test",
            request.test_name or "Website Load Test",
            runner.run_website_load_test,
            {
                "users": request.users,
                "duration": request.duration
            },
            request.website_url
        )
        
        return {"test_id": test_id, "status": "queued", "message": "Website load test queued for execution"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue website load test: {str(e)}")


@app.post("/api/v1/qa-tests/volume-test")
async def run_volume_test(request: VolumeTestRequest):
    """Run volume test"""
    try:
        from qa_agent.utils.locust_runner import LocustTestRunner
        
        runner = LocustTestRunner()
        test_id = await _queue_test(
            "volume_test",
            request.test_name or "Volume Test",
            runner.run_volume_test,
            {
                "users": request.users,
                "duration": request.duration
            },
            request.website_url
        )
        
        return {"test_id": test_id, "status": "queued", "message": "Volume test queued for execution"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue volume test: {str(e)}")


@app.post("/api/v1/qa-tests/concurrent-user-test")
async def run_concurrent_user_test(request: ConcurrentUserTestRequest):
    """Run concurrent user test"""
    try:
        from qa_agent.utils.locust_runner import LocustTestRunner
        
        runner = LocustTestRunner()
        test_id = await _queue_test(
            "concurrent_user_test",
            request.test_name or "Concurrent User Test",
            runner.run_concurrent_user_test,
            {
                "concurrent_users": request.concurrent_users,
                "duration": request.duration
            },
            request.website_url
        )
        
        return {"test_id": test_id, "status": "queued", "message": "Concurrent user test queued for execution"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue concurrent user test: {str(e)}")


@app.post("/api/v1/qa-tests/response-time-distribution-test")
async def run_response_time_distribution_test(request: ResponseTimeDistributionTestRequest):
    """Run response time distribution test"""
    try:
        from qa_agent.utils.locust_runner import LocustTestRunner
        
        runner = LocustTestRunner()
        test_id = await _queue_test(
            "response_time_distribution_test",
            request.test_name or "Response Time Distribution Test",
            runner.run_response_time_distribution_test,
            {
                "users": request.users,
                "duration": request.duration
            },
            request.website_url
        )
        
        return {"test_id": test_id, "status": "queued", "message": "Response time distribution test queued for execution"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue response time distribution test: {str(e)}")


# Network test endpoints
@app.post("/api/v1/qa-tests/ssl-tls-validation")
async def run_ssl_tls_validation(request: SslTlsValidationRequest):
    """Run SSL/TLS certificate validation test"""
    try:
        from qa_agent.utils.network_runner import NetworkTestRunner
        
        runner = NetworkTestRunner()
        test_id = await _queue_test(
            "ssl_tls_validation",
            request.test_name or "SSL/TLS Certificate Validation",
            runner.run_ssl_tls_validation,
            {},
            request.website_url or request.target_url
        )
        
        return {"test_id": test_id, "status": "queued", "message": "SSL/TLS validation test queued for execution"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue SSL/TLS validation test: {str(e)}")


@app.post("/api/v1/qa-tests/dns-security-test")
async def run_dns_security_test(request: DnsSecurityTestRequest):
    """Run DNS security test"""
    try:
        from qa_agent.utils.network_runner import NetworkTestRunner
        
        runner = NetworkTestRunner()
        test_id = await _queue_test(
            "dns_security_test",
            request.test_name or "DNS Security Test",
            runner.run_dns_security_test,
            {},
            request.website_url or request.target_url
        )
        
        return {"test_id": test_id, "status": "queued", "message": "DNS security test queued for execution"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue DNS security test: {str(e)}")


@app.post("/api/v1/qa-tests/connectivity-diagnostics")
async def run_connectivity_diagnostics(request: ConnectivityDiagnosticsRequest):
    """Run network connectivity diagnostics"""
    try:
        from qa_agent.utils.network_runner import NetworkTestRunner
        
        runner = NetworkTestRunner()
        test_id = await _queue_test(
            "connectivity_diagnostics",
            request.test_name or "Network Connectivity Diagnostics",
            runner.run_connectivity_diagnostics,
            {},
            request.website_url or request.target_url
        )
        
        return {"test_id": test_id, "status": "queued", "message": "Connectivity diagnostics test queued for execution"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue connectivity diagnostics test: {str(e)}")


@app.post("/api/v1/qa-tests/protocol-traffic-analysis")
async def run_protocol_traffic_analysis(request: ProtocolTrafficAnalysisRequest):
    """Run protocol traffic analysis"""
    try:
        from qa_agent.utils.network_runner import NetworkTestRunner
        
        runner = NetworkTestRunner()
        test_id = await _queue_test(
            "protocol_traffic_analysis",
            request.test_name or "Protocol Traffic Analysis",
            runner.run_protocol_traffic_analysis,
            {"duration": request.duration},
            request.website_url or request.target_url
        )
        
        return {"test_id": test_id, "status": "queued", "message": "Protocol traffic analysis test queued for execution"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue protocol traffic analysis test: {str(e)}")


@app.post("/api/v1/qa-tests/network-security-scan")
async def run_network_security_scan(request: NetworkSecurityScanRequest):
    """Run network security scan (restricted test - requires permission)"""
    try:
        from qa_agent.utils.network_runner import NetworkTestRunner
        from qa_agent.utils.network_safety import NetworkSafetyValidator
        
        # Validate safety
        validator = NetworkSafetyValidator()
        target_url = request.website_url or request.target_url
        is_valid, error_msg = validator.validate_target(
            target_url, "network_security_scan", request.user_permission
        )
        
        if not is_valid:
            raise HTTPException(status_code=403, detail=error_msg)
        
        runner = NetworkTestRunner()
        test_id = await _queue_test(
            "network_security_scan",
            request.test_name or "Network Security Scan",
            runner.run_network_security_scan,
            {
                "ports": request.ports,
                "scan_type": request.scan_type,
                "user_permission": request.user_permission
            },
            target_url
        )
        
        logger.warning(f"Network security scan queued for {target_url} (permission: {request.user_permission})")
        return {"test_id": test_id, "status": "queued", "message": "Network security scan queued for execution"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue network security scan: {str(e)}")


@app.post("/api/v1/qa-tests/endpoint-discovery")
async def run_endpoint_discovery(request: EndpointDiscoveryRequest):
    """Run endpoint discovery (restricted test - requires permission)"""
    try:
        from qa_agent.utils.network_runner import NetworkTestRunner
        from qa_agent.utils.network_safety import NetworkSafetyValidator
        
        # Validate safety
        validator = NetworkSafetyValidator()
        target_url = request.website_url or request.target_url
        is_valid, error_msg = validator.validate_target(
            target_url, "endpoint_discovery", request.user_permission
        )
        
        if not is_valid:
            raise HTTPException(status_code=403, detail=error_msg)
        
        runner = NetworkTestRunner()
        test_id = await _queue_test(
            "endpoint_discovery",
            request.test_name or "Endpoint Discovery",
            runner.run_endpoint_discovery,
            {
                "discovery_method": request.discovery_method,
                "user_permission": request.user_permission
            },
            target_url
        )
        
        logger.warning(f"Endpoint discovery queued for {target_url} (permission: {request.user_permission})")
        return {"test_id": test_id, "status": "queued", "message": "Endpoint discovery test queued for execution"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue endpoint discovery test: {str(e)}")


@app.get("/api/v1/qa-tests/test-status/{test_id}")
async def get_test_status(test_id: str):
    """Get current test status and progress"""
    if test_id not in test_results:
        raise HTTPException(status_code=404, detail=f"Test {test_id} not found")
    
    result = test_results[test_id]
    return {
        "test_id": test_id,
        "status": result.get("status", "unknown"),
        "progress": result.get("progress", 0.0),
        "started_at": result.get("started_at"),
        "completed_at": result.get("completed_at"),
        "error": result.get("error")
    }


@app.post("/api/v1/qa-tests/cancel-test/{test_id}")
async def cancel_test(test_id: str):
    """Cancel a running or queued test"""
    global test_tasks, test_queue, current_test
    
    if test_id not in test_results:
        raise HTTPException(status_code=404, detail=f"Test {test_id} not found")
    
    # Cancel task if running
    if test_id in test_tasks:
        task = test_tasks[test_id]
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    # Update status
    test_results[test_id]["status"] = TestStatus.cancelled
    test_results[test_id]["completed_at"] = datetime.utcnow().isoformat()
    
    if current_test == test_id:
        current_test = None
    
    return {"test_id": test_id, "status": "cancelled", "message": "Test cancelled successfully"}


@app.get("/api/v1/qa-tests/test-results/{test_id}", response_model=TestResultResponse)
async def get_test_result(test_id: str):
    """Get details of a specific test result"""
    if test_id not in test_results:
        raise HTTPException(status_code=404, detail=f"Test result {test_id} not found")

    return test_results[test_id]


@app.get("/api/v1/qa-tests/test-results")
async def list_test_results(limit: int = 50):
    """List test results"""
    results = list(test_results.values())

    # Sort by most recent first
    results.sort(key=lambda x: x["started_at"], reverse=True)

    return {
        "results": results[:limit],
        "total": len(results)
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("QA Agent Backend - Standalone Version")
    print("=" * 60)
    print(f"API: http://localhost:8000")
    print(f"Docs: http://localhost:8000/docs")
    print(f"Frontend: http://localhost:3000")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
