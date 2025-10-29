"""
Simulation Engine Examples

This file demonstrates the complete simulation engine as specified in the plan.
Shows comprehensive instrumentation, event emission, and flow execution.
"""
import asyncio
from uuid import uuid4
from typing import Dict, Any

from qa_agent.simulation.engine import simulation_engine
from qa_agent.core.logging import get_logger

logger = get_logger(__name__)


async def basic_flow_example():
    """
    Basic example: Execute a simple flow with comprehensive instrumentation.
    """
    run_id = uuid4()
    
    # Define a simple flow DSL
    flow_dsl = {
        "name": "basic_signup_flow",
        "version": 1,
        "start_url": "https://example.com",
        "steps": [
            {"type": "click", "selector": "text=Sign up"},
            {"type": "type", "selector": "input[name='email']", "text": "test@example.com"},
            {"type": "type", "selector": "input[name='password']", "text": "password123"},
            {"type": "click", "selector": "button:has-text('Create account')"},
            {"type": "assert", "expect": {"url_contains": "/welcome"}}
        ],
        "policies": {
            "human_like": True,
            "max_step_timeout_ms": 15000
        }
    }
    
    # Add event handler for demonstration
    async def event_handler(event):
        logger.info("Event captured", 
                   event_type=event.event_type,
                   timestamp=event.timestamp,
                   payload_keys=list(event.payload.keys()))
    
    simulation_engine.add_event_handler(event_handler)
    
    try:
        # Execute the flow
        result = await simulation_engine.execute_run(
            run_id=run_id,
            flow_dsl=flow_dsl,
            target_url="https://example.com",
            profile="demo_profile",
            stealth=True
        )
        
        logger.info("Basic flow completed", 
                   status=result["status"],
                   total_events=result.get("total_events", 0))
        
        return result
        
    except Exception as e:
        logger.error("Basic flow failed", error=str(e))
        raise


async def comprehensive_instrumentation_example():
    """
    Demonstrate comprehensive instrumentation capabilities.
    """
    run_id = uuid4()
    
    # Complex flow that triggers various instrumentation
    flow_dsl = {
        "name": "comprehensive_test_flow",
        "version": 1,
        "start_url": "https://example.com",
        "steps": [
            # Navigation step
            {"type": "navigate", "url": "https://example.com/products"},
            
            # Scroll to trigger scroll events
            {"type": "scroll", "direction": "down", "amount": 500},
            {"type": "scroll", "direction": "up", "amount": 200},
            
            # Form interactions
            {"type": "click", "selector": "input[name='search']"},
            {"type": "type", "selector": "input[name='search']", "text": "test product"},
            {"type": "click", "selector": "button[type='submit']"},
            
            # Wait to capture performance events
            {"type": "wait", "timeout": 2000},
            
            # Multiple clicks to test click tracking
            {"type": "click", "selector": "a:has-text('Product 1')"},
            {"type": "click", "selector": "button:has-text('Add to Cart')"},
            
            # Assertions
            {"type": "assert", "expect": {"text_present": "Added to cart"}},
            {"type": "assert", "expect": {"element_visible": ".cart-icon"}}
        ],
        "policies": {
            "human_like": True,
            "max_step_timeout_ms": 20000,
            "min_delay_ms": 200,
            "max_delay_ms": 800
        }
    }
    
    # Track all event types
    event_counts = {}
    
    async def comprehensive_event_handler(event):
        event_type = event.event_type
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Log interesting events
        if event_type in ["network_request", "network_response", "js_error", "long_task"]:
            logger.info("Interesting event", 
                       event_type=event_type,
                       payload=event.payload)
    
    simulation_engine.add_event_handler(comprehensive_event_handler)
    
    try:
        result = await simulation_engine.execute_run(
            run_id=run_id,
            flow_dsl=flow_dsl,
            target_url="https://example.com",
            profile="comprehensive_test",
            stealth=True
        )
        
        logger.info("Comprehensive test completed",
                   status=result["status"],
                   event_counts=event_counts)
        
        return result, event_counts
        
    except Exception as e:
        logger.error("Comprehensive test failed", error=str(e))
        raise


async def error_handling_example():
    """
    Demonstrate error handling and retry mechanisms.
    """
    run_id = uuid4()
    
    # Flow with intentionally problematic steps
    flow_dsl = {
        "name": "error_handling_test",
        "version": 1,
        "start_url": "https://example.com",
        "steps": [
            # This should work
            {"type": "click", "selector": "text=Sign up"},
            
            # This might fail (invalid selector)
            {"type": "click", "selector": "invalid-selector-that-does-not-exist"},
            
            # This should work with retries
            {"type": "type", "selector": "input[name='email']", "text": "test@example.com"},
            
            # This might timeout
            {"type": "wait", "timeout": 100},  # Very short timeout
            
            # This should work
            {"type": "assert", "expect": {"url_contains": "example.com"}}
        ],
        "policies": {
            "human_like": True,
            "max_step_timeout_ms": 5000,
            "retry_attempts": 3
        }
    }
    
    error_events = []
    
    async def error_event_handler(event):
        if event.event_type in ["step_failed", "run_failed", "js_error", "network_error"]:
            error_events.append({
                "type": event.event_type,
                "payload": event.payload,
                "timestamp": event.timestamp
            })
    
    simulation_engine.add_event_handler(error_event_handler)
    
    try:
        result = await simulation_engine.execute_run(
            run_id=run_id,
            flow_dsl=flow_dsl,
            target_url="https://example.com",
            profile="error_test",
            stealth=True
        )
        
        logger.info("Error handling test completed",
                   status=result["status"],
                   error_events_count=len(error_events))
        
        return result, error_events
        
    except Exception as e:
        logger.error("Error handling test failed", error=str(e))
        raise


async def performance_monitoring_example():
    """
    Demonstrate performance monitoring and long task detection.
    """
    run_id = uuid4()
    
    # Flow designed to trigger performance events
    flow_dsl = {
        "name": "performance_test",
        "version": 1,
        "start_url": "https://example.com",
        "steps": [
            # Navigate to a heavy page
            {"type": "navigate", "url": "https://example.com/heavy-page"},
            
            # Wait for page to load and capture performance metrics
            {"type": "wait", "timeout": 5000},
            
            # Scroll to trigger layout shifts
            {"type": "scroll", "direction": "down", "amount": 1000},
            {"type": "scroll", "direction": "up", "amount": 500},
            
            # Interact with dynamic content
            {"type": "click", "selector": "button:has-text('Load More')"},
            {"type": "wait", "timeout": 3000},
            
            # More scrolling
            {"type": "scroll", "direction": "down", "amount": 2000}
        ],
        "policies": {
            "human_like": True,
            "max_step_timeout_ms": 10000
        }
    }
    
    performance_events = []
    
    async def performance_event_handler(event):
        if event.event_type in ["long_task", "layout_shift", "memory_usage", "connection_info"]:
            performance_events.append({
                "type": event.event_type,
                "payload": event.payload,
                "timestamp": event.timestamp
            })
    
    simulation_engine.add_event_handler(performance_event_handler)
    
    try:
        result = await simulation_engine.execute_run(
            run_id=run_id,
            flow_dsl=flow_dsl,
            target_url="https://example.com",
            profile="performance_test",
            stealth=True
        )
        
        logger.info("Performance test completed",
                   status=result["status"],
                   performance_events_count=len(performance_events))
        
        return result, performance_events
        
    except Exception as e:
        logger.error("Performance test failed", error=str(e))
        raise


async def comprehensive_simulation_demo():
    """
    Comprehensive demo showing all simulation engine capabilities.
    """
    logger.info("Starting comprehensive simulation engine demo")
    
    try:
        # Run all examples
        basic_result = await basic_flow_example()
        comprehensive_result, event_counts = await comprehensive_instrumentation_example()
        error_result, error_events = await error_handling_example()
        performance_result, performance_events = await performance_monitoring_example()
        
        # Summary
        logger.info("Comprehensive simulation demo completed",
                   basic_status=basic_result["status"],
                   comprehensive_status=comprehensive_result["status"],
                   error_status=error_result["status"],
                   performance_status=performance_result["status"],
                   total_event_types=len(event_counts),
                   error_events_count=len(error_events),
                   performance_events_count=len(performance_events))
        
        return {
            "basic_result": basic_result,
            "comprehensive_result": comprehensive_result,
            "error_result": error_result,
            "performance_result": performance_result,
            "event_counts": event_counts,
            "error_events": error_events,
            "performance_events": performance_events
        }
        
    except Exception as e:
        logger.error("Comprehensive simulation demo failed", error=str(e))
        raise


if __name__ == "__main__":
    # Run the comprehensive demo
    asyncio.run(comprehensive_simulation_demo())
