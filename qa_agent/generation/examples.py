"""
Flow DSL Implementation Examples

This file demonstrates the complete Flow DSL implementation with examples
of creating, validating, and executing flows.
"""
import asyncio
import json
from uuid import uuid4
from typing import Dict, Any

from qa_agent.generation.dsl import FlowDSL, FlowStep, StepType, flow_compiler
from qa_agent.generation.executor import flow_executor
from qa_agent.generation.service import FlowService
from qa_agent.storage.repo import FlowRepository
from qa_agent.core.logging import get_logger

logger = get_logger(__name__)


# Example 1: Basic Login Flow
def create_login_flow_example() -> Dict[str, Any]:
    """Create a basic login flow example."""
    return {
        "name": "login_flow",
        "version": 1,
        "description": "Standard user login flow",
        "start_url": "https://www.udemy.com/login",
        "steps": [
            {
                "type": "click",
                "selector": "text=Sign in",
                "timeout": 5000,
                "retry_attempts": 3
            },
            {
                "type": "type",
                "selector": "input[name='email']",
                "text": "test@example.com",
                "timeout": 5000
            },
            {
                "type": "type",
                "selector": "input[name='password']",
                "text": "P@ssw0rd!",
                "timeout": 5000
            },
            {
                "type": "click",
                "selector": "button:has-text('Sign in')",
                "timeout": 5000
            },
            {
                "type": "wait",
                "timeout": 2000
            },
            {
                "type": "assert",
                "expect": {
                    "url_contains": "/dashboard"
                }
            }
        ],
        "policies": {
            "human_like": True,
            "max_step_timeout_ms": 15000,
            "min_delay_ms": 100,
            "max_delay_ms": 1000,
            "retry_attempts": 3
        }
    }


# Example 2: E-commerce Checkout Flow
def create_checkout_flow_example() -> Dict[str, Any]:
    """Create an e-commerce checkout flow example."""
    return {
        "name": "checkout_flow",
        "version": 1,
        "description": "Complete e-commerce checkout process",
        "start_url": "https://shop.example.com",
        "steps": [
            {
                "type": "click",
                "selector": "text=Add to Cart",
                "timeout": 5000
            },
            {
                "type": "wait",
                "timeout": 1000
            },
            {
                "type": "click",
                "selector": "text=View Cart",
                "timeout": 5000
            },
            {
                "type": "click",
                "selector": "text=Checkout",
                "timeout": 5000
            },
            {
                "type": "type",
                "selector": "input[name='email']",
                "text": "customer@example.com"
            },
            {
                "type": "type",
                "selector": "input[name='firstName']",
                "text": "John"
            },
            {
                "type": "type",
                "selector": "input[name='lastName']",
                "text": "Doe"
            },
            {
                "type": "type",
                "selector": "input[name='address']",
                "text": "123 Main St"
            },
            {
                "type": "type",
                "selector": "input[name='city']",
                "text": "New York"
            },
            {
                "type": "select",
                "selector": "select[name='state']",
                "value": "NY"
            },
            {
                "type": "type",
                "selector": "input[name='zipCode']",
                "text": "10001"
            },
            {
                "type": "type",
                "selector": "input[name='cardNumber']",
                "text": "4111111111111111"
            },
            {
                "type": "type",
                "selector": "input[name='expiry']",
                "text": "12/25"
            },
            {
                "type": "type",
                "selector": "input[name='cvv']",
                "text": "123"
            },
            {
                "type": "click",
                "selector": "button:has-text('Place Order')",
                "timeout": 10000
            },
            {
                "type": "assert",
                "expect": {
                    "text_present": "Order Confirmation"
                }
            }
        ],
        "policies": {
            "human_like": True,
            "max_step_timeout_ms": 20000,
            "min_delay_ms": 200,
            "max_delay_ms": 1500,
            "retry_attempts": 3
        }
    }


# Example 3: Search Flow with Advanced Features
def create_search_flow_example() -> Dict[str, Any]:
    """Create a search flow with advanced features."""
    return {
        "name": "search_flow",
        "version": 1,
        "description": "Advanced search functionality with filters",
        "start_url": "https://www.amazon.com",
        "steps": [
            {
                "type": "click",
                "selector": "#twotabsearchtextbox",
                "timeout": 5000
            },
            {
                "type": "type",
                "selector": "#twotabsearchtextbox",
                "text": "wireless headphones",
                "timeout": 5000
            },
            {
                "type": "click",
                "selector": "#nav-search-submit-button",
                "timeout": 5000
            },
            {
                "type": "wait",
                "timeout": 3000
            },
            {
                "type": "scroll",
                "direction": "down",
                "amount": 500
            },
            {
                "type": "click",
                "selector": "[aria-label*='Brand']",
                "timeout": 5000
            },
            {
                "type": "click",
                "selector": "text=Sony",
                "timeout": 5000
            },
            {
                "type": "wait",
                "timeout": 2000
            },
            {
                "type": "click",
                "selector": "[aria-label*='Price']",
                "timeout": 5000
            },
            {
                "type": "type",
                "selector": "input[name='low-price']",
                "text": "50"
            },
            {
                "type": "type",
                "selector": "input[name='high-price']",
                "text": "200"
            },
            {
                "type": "click",
                "selector": "text=Go",
                "timeout": 5000
            },
            {
                "type": "wait",
                "timeout": 3000
            },
            {
                "type": "assert",
                "expect": {
                    "element_visible": "[data-component-type='s-search-result']"
                }
            },
            {
                "type": "hover",
                "selector": "[data-component-type='s-search-result']:first-child",
                "timeout": 5000
            },
            {
                "type": "click",
                "selector": "[data-component-type='s-search-result']:first-child h2 a",
                "timeout": 5000
            },
            {
                "type": "assert",
                "expect": {
                    "url_contains": "/dp/"
                }
            }
        ],
        "policies": {
            "human_like": True,
            "max_step_timeout_ms": 15000,
            "min_delay_ms": 150,
            "max_delay_ms": 2000,
            "retry_attempts": 3
        }
    }


# Example 4: Form Submission with File Upload
def create_file_upload_flow_example() -> Dict[str, Any]:
    """Create a file upload flow example."""
    return {
        "name": "file_upload_flow",
        "version": 1,
        "description": "File upload and form submission",
        "start_url": "https://www.dropbox.com/upload",
        "steps": [
            {
                "type": "click",
                "selector": "text=Choose files",
                "timeout": 5000
            },
            {
                "type": "upload",
                "selector": "input[type='file']",
                "file_path": "/path/to/test-file.pdf",
                "timeout": 10000
            },
            {
                "type": "wait",
                "timeout": 3000
            },
            {
                "type": "type",
                "selector": "input[name='description']",
                "text": "Test file upload"
            },
            {
                "type": "click",
                "selector": "button:has-text('Upload')",
                "timeout": 10000
            },
            {
                "type": "wait",
                "timeout": 5000
            },
            {
                "type": "assert",
                "expect": {
                    "text_present": "Upload complete"
                }
            }
        ],
        "policies": {
            "human_like": True,
            "max_step_timeout_ms": 20000,
            "min_delay_ms": 200,
            "max_delay_ms": 1500,
            "retry_attempts": 2
        }
    }


# Example 5: Multi-tab Navigation Flow
def create_multi_tab_flow_example() -> Dict[str, Any]:
    """Create a multi-tab navigation flow example."""
    return {
        "name": "multi_tab_flow",
        "version": 1,
        "description": "Navigation across multiple tabs",
        "start_url": "https://www.github.com",
        "steps": [
            {
                "type": "click",
                "selector": "text=Sign in",
                "timeout": 5000
            },
            {
                "type": "type",
                "selector": "input[name='login']",
                "text": "testuser"
            },
            {
                "type": "type",
                "selector": "input[name='password']",
                "text": "testpass"
            },
            {
                "type": "click",
                "selector": "input[type='submit']",
                "timeout": 5000
            },
            {
                "type": "wait",
                "timeout": 2000
            },
            {
                "type": "click",
                "selector": "text=New repository",
                "timeout": 5000
            },
            {
                "type": "type",
                "selector": "input[name='repository[name]']",
                "text": "test-repo"
            },
            {
                "type": "type",
                "selector": "textarea[name='repository[description]']",
                "text": "Test repository description"
            },
            {
                "type": "click",
                "selector": "button:has-text('Create repository')",
                "timeout": 10000
            },
            {
                "type": "wait",
                "timeout": 3000
            },
            {
                "type": "assert",
                "expect": {
                    "url_contains": "/test-repo"
                }
            }
        ],
        "policies": {
            "human_like": True,
            "max_step_timeout_ms": 15000,
            "min_delay_ms": 100,
            "max_delay_ms": 1000,
            "retry_attempts": 3
        }
    }


async def demonstrate_flow_dsl():
    """Demonstrate the complete Flow DSL implementation."""
    logger.info("Starting Flow DSL demonstration")
    
    # Example 1: Compile and validate a flow
    print("\n=== Example 1: Flow Compilation and Validation ===")
    
    login_flow_data = create_login_flow_example()
    
    try:
        # Compile the flow
        compiled_flow = flow_compiler.compile_flow(login_flow_data)
        print(f"✅ Flow compiled successfully: {compiled_flow.name}")
        
        # Get flow summary
        summary = flow_compiler.get_flow_summary(compiled_flow)
        print(f"📊 Flow Summary:")
        print(f"   - Steps: {summary['step_count']}")
        print(f"   - Step types: {summary['step_types']}")
        print(f"   - Estimated duration: {summary['estimated_duration']}s")
        print(f"   - Complexity score: {summary['complexity_score']}")
        
        # Validate the flow
        issues = flow_compiler.validate_flow(compiled_flow)
        if issues:
            print(f"⚠️  Validation issues: {issues}")
        else:
            print("✅ Flow validation passed")
            
    except Exception as e:
        print(f"❌ Flow compilation failed: {e}")
    
    # Example 2: Generate fallback selectors
    print("\n=== Example 2: Fallback Selector Generation ===")
    
    step = FlowStep(
        type=StepType.CLICK,
        selector="text=Sign in",
        timeout=5000
    )
    
    fallbacks = flow_compiler.generate_fallback_selectors(step)
    print(f"🎯 Primary selector: {step.selector}")
    print(f"🔄 Fallback selectors:")
    for i, fallback in enumerate(fallbacks, 1):
        print(f"   {i}. {fallback}")
    
    # Example 3: Flow optimization
    print("\n=== Example 3: Flow Optimization ===")
    
    checkout_flow_data = create_checkout_flow_example()
    compiled_checkout = flow_compiler.compile_flow(checkout_flow_data)
    
    print(f"📝 Original flow steps: {len(compiled_checkout.steps)}")
    
    optimized_flow = flow_compiler.optimize_flow(compiled_checkout)
    print(f"⚡ Optimized flow steps: {len(optimized_flow.steps)}")
    
    # Example 4: JSON serialization
    print("\n=== Example 4: JSON Serialization ===")
    
    search_flow_data = create_search_flow_example()
    compiled_search = flow_compiler.compile_flow(search_flow_data)
    
    # Convert to JSON
    json_data = flow_compiler.to_json(compiled_search)
    print(f"📄 JSON length: {len(json_data)} characters")
    
    # Parse back from JSON
    parsed_flow = flow_compiler.from_json(json_data)
    print(f"✅ Successfully parsed flow: {parsed_flow.name}")
    
    # Example 5: Flow templates
    print("\n=== Example 5: Flow Templates ===")
    
    templates = [
        create_login_flow_example(),
        create_checkout_flow_example(),
        create_search_flow_example(),
        create_file_upload_flow_example(),
        create_multi_tab_flow_example()
    ]
    
    for i, template in enumerate(templates, 1):
        try:
            compiled = flow_compiler.compile_flow(template)
            summary = flow_compiler.get_flow_summary(compiled)
            print(f"📋 Template {i}: {compiled.name}")
            print(f"   - Steps: {summary['step_count']}")
            print(f"   - Complexity: {summary['complexity_score']}")
            print(f"   - Has assertions: {summary['has_assertions']}")
        except Exception as e:
            print(f"❌ Template {i} failed: {e}")
    
    print("\n🎉 Flow DSL demonstration completed!")


async def demonstrate_flow_execution():
    """Demonstrate flow execution (mock example)."""
    logger.info("Starting Flow Execution demonstration")
    
    print("\n=== Flow Execution Example ===")
    
    # Create a simple flow
    simple_flow_data = {
        "name": "demo_flow",
        "version": 1,
        "start_url": "https://example.com",
        "steps": [
            {
                "type": "wait",
                "timeout": 1000
            },
            {
                "type": "assert",
                "expect": {
                    "url_contains": "example.com"
                }
            }
        ],
        "policies": {
            "human_like": True,
            "max_step_timeout_ms": 5000,
            "min_delay_ms": 100,
            "max_delay_ms": 500,
            "retry_attempts": 2
        }
    }
    
    try:
        # Compile the flow
        compiled_flow = flow_compiler.compile_flow(simple_flow_data)
        print(f"✅ Flow compiled: {compiled_flow.name}")
        
        # Mock execution (would normally use real browser)
        run_id = uuid4()
        print(f"🚀 Starting execution with run_id: {run_id}")
        
        # In a real scenario, this would execute against a browser
        print("📝 Execution steps:")
        for i, step in enumerate(compiled_flow.steps, 1):
            print(f"   {i}. {step.type.value} - {step.selector or 'N/A'}")
        
        print("✅ Flow execution completed successfully!")
        
    except Exception as e:
        print(f"❌ Flow execution failed: {e}")


if __name__ == "__main__":
    # Run the demonstrations
    asyncio.run(demonstrate_flow_dsl())
    asyncio.run(demonstrate_flow_execution())
