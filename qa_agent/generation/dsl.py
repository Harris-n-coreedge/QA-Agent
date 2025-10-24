"""
Flow DSL schema and validation.

Goal: declarative steps, stable selectors, pre/post conditions, timeouts.
Compiler validates selectors, inserts waits, and adds fallbacks (text, role, CSS, XPath).
"""
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator
import json
import re
from enum import Enum


class StepType(str, Enum):
    """Supported step types."""
    CLICK = "click"
    TYPE = "type"
    WAIT = "wait"
    NAVIGATE = "navigate"
    ASSERT = "assert"
    SCROLL = "scroll"
    HOVER = "hover"
    SELECT = "select"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    SWITCH_TAB = "switch_tab"
    CLOSE_TAB = "close_tab"
    EXECUTE_SCRIPT = "execute_script"


class FlowStep(BaseModel):
    """Individual step in a flow with comprehensive validation."""
    type: StepType = Field(..., description="Step type")
    selector: Optional[str] = Field(None, description="Element selector")
    text: Optional[str] = Field(None, description="Text to type")
    url: Optional[str] = Field(None, description="URL to navigate to")
    timeout: Optional[int] = Field(5000, description="Timeout in milliseconds")
    retry_attempts: Optional[int] = Field(3, description="Number of retry attempts")
    expect: Optional[Dict[str, Any]] = Field(None, description="Assertion expectations")
    
    # Additional step-specific fields
    direction: Optional[str] = Field(None, description="Scroll direction (up/down/left/right)")
    amount: Optional[int] = Field(None, description="Scroll amount in pixels")
    file_path: Optional[str] = Field(None, description="File path for upload")
    script: Optional[str] = Field(None, description="JavaScript to execute")
    tab_index: Optional[int] = Field(None, description="Tab index for tab operations")
    value: Optional[str] = Field(None, description="Value for select operations")
    
    # Pre/post conditions
    pre_conditions: Optional[List[Dict[str, Any]]] = Field(None, description="Pre-step conditions")
    post_conditions: Optional[List[Dict[str, Any]]] = Field(None, description="Post-step conditions")
    
    # Fallback selectors
    fallback_selectors: Optional[List[str]] = Field(None, description="Fallback selectors")
    
    @validator('type')
    def validate_step_type(cls, v):
        return v
    
    @validator('selector')
    def validate_selector(cls, v, values):
        step_type = values.get('type')
        if step_type in [StepType.CLICK, StepType.TYPE, StepType.HOVER, StepType.SELECT] and not v:
            raise ValueError(f'{step_type} step requires a selector')
        return v
    
    @validator('text')
    def validate_text(cls, v, values):
        step_type = values.get('type')
        if step_type == StepType.TYPE and not v:
            raise ValueError('type step requires text')
        return v
    
    @validator('url')
    def validate_url(cls, v, values):
        step_type = values.get('type')
        if step_type == StepType.NAVIGATE and not v:
            raise ValueError('navigate step requires url')
        return v
    
    @validator('direction')
    def validate_direction(cls, v, values):
        step_type = values.get('type')
        if step_type == StepType.SCROLL and v and v not in ['up', 'down', 'left', 'right']:
            raise ValueError('scroll direction must be up, down, left, or right')
        return v


class FlowPolicies(BaseModel):
    """Policies for flow execution."""
    human_like: bool = Field(True, description="Enable human-like behavior")
    max_step_timeout_ms: int = Field(15000, description="Maximum step timeout")
    min_delay_ms: int = Field(100, description="Minimum delay between steps")
    max_delay_ms: int = Field(1000, description="Maximum delay between steps")
    retry_attempts: int = Field(3, description="Default retry attempts")


class FlowDSL(BaseModel):
    """Flow DSL schema."""
    name: str = Field(..., description="Flow name")
    version: int = Field(1, description="Flow version")
    description: Optional[str] = Field(None, description="Flow description")
    start_url: str = Field(..., description="Starting URL")
    steps: List[FlowStep] = Field(..., description="Flow steps")
    policies: FlowPolicies = Field(default_factory=FlowPolicies, description="Execution policies")
    
    @validator('steps')
    def validate_steps(cls, v):
        if not v:
            raise ValueError('Flow must have at least one step')
        return v


class FlowCompiler:
    """
    Compiles and validates flow DSL with comprehensive selector validation and fallbacks.
    
    Features:
    - Validates selectors and generates fallbacks (text, role, CSS, XPath)
    - Inserts waits and optimizes flow execution
    - Pre/post condition validation
    - Comprehensive error reporting
    """
    
    def __init__(self):
        self.compiled_flows: Dict[str, FlowDSL] = {}
        self.selector_patterns = {
            'css': re.compile(r'^[.#]?[a-zA-Z][\w\-]*(\s*[.#]?[a-zA-Z][\w\-]*)*$'),
            'xpath': re.compile(r'^//'),
            'text': re.compile(r'^text='),
            'role': re.compile(r'^role='),
            'aria': re.compile(r'^\[aria-'),
            'data': re.compile(r'^\[data-'),
            'id': re.compile(r'^#'),
            'class': re.compile(r'^\.')
        }
    
    def compile_flow(self, flow_data: Dict[str, Any]) -> FlowDSL:
        """Compile flow data into validated DSL with optimizations."""
        try:
            # Convert string step types to enum
            if 'steps' in flow_data:
                for step in flow_data['steps']:
                    if isinstance(step.get('type'), str):
                        step['type'] = StepType(step['type'])
            
            flow_dsl = FlowDSL(**flow_data)
            
            # Generate fallback selectors for all steps
            self._add_fallback_selectors(flow_dsl)
            
            # Validate and optimize
            issues = self.validate_flow(flow_dsl)
            if issues:
                raise ValueError(f"Flow validation failed: {'; '.join(issues)}")
            
            # Optimize flow
            optimized_flow = self.optimize_flow(flow_dsl)
            
            self.compiled_flows[optimized_flow.name] = optimized_flow
            return optimized_flow
            
        except Exception as e:
            raise ValueError(f"Flow compilation failed: {e}")
    
    def validate_flow(self, flow_dsl: FlowDSL) -> List[str]:
        """Validate flow and return any issues."""
        issues = []
        
        # Check basic flow structure
        if not flow_dsl.steps:
            issues.append("Flow must have at least one step")
        
        if len(flow_dsl.steps) > 100:
            issues.append("Flow has too many steps (potential infinite loop)")
        
        # Validate each step
        for i, step in enumerate(flow_dsl.steps):
            step_issues = self._validate_step(step, i)
            issues.extend(step_issues)
        
        # Check for circular navigation
        navigation_steps = [s for s in flow_dsl.steps if s.type == StepType.NAVIGATE]
        if len(navigation_steps) > 10:
            issues.append("Too many navigation steps (potential circular navigation)")
        
        return issues
    
    def _validate_step(self, step: FlowStep, index: int) -> List[str]:
        """Validate individual step."""
        issues = []
        
        # Validate selector format
        if step.selector:
            selector_issues = self._validate_selector(step.selector)
            if selector_issues:
                issues.extend([f"Step {index}: {issue}" for issue in selector_issues])
        
        # Validate step-specific requirements
        if step.type == StepType.TYPE and not step.text:
            issues.append(f"Step {index}: type step requires text")
        
        if step.type == StepType.NAVIGATE and not step.url:
            issues.append(f"Step {index}: navigate step requires url")
        
        if step.type == StepType.SCROLL and step.direction and step.direction not in ['up', 'down', 'left', 'right']:
            issues.append(f"Step {index}: invalid scroll direction '{step.direction}'")
        
        if step.type == StepType.UPLOAD and not step.file_path:
            issues.append(f"Step {index}: upload step requires file_path")
        
        if step.type == StepType.EXECUTE_SCRIPT and not step.script:
            issues.append(f"Step {index}: execute_script step requires script")
        
        # Validate pre/post conditions
        if step.pre_conditions:
            for j, condition in enumerate(step.pre_conditions):
                if not self._validate_condition(condition):
                    issues.append(f"Step {index}: invalid pre-condition {j}")
        
        if step.post_conditions:
            for j, condition in enumerate(step.post_conditions):
                if not self._validate_condition(condition):
                    issues.append(f"Step {index}: invalid post-condition {j}")
        
        return issues
    
    def _validate_selector(self, selector: str) -> List[str]:
        """Validate selector format and return issues."""
        issues = []
        
        # Check if selector matches known patterns
        matched_pattern = False
        for pattern_name, pattern in self.selector_patterns.items():
            if pattern.match(selector):
                matched_pattern = True
                break
        
        if not matched_pattern:
            issues.append(f"Selector '{selector}' doesn't match known patterns")
        
        # Check for potentially problematic selectors
        if selector.count(' ') > 5:
            issues.append(f"Selector '{selector}' is too complex (too many spaces)")
        
        if '//' in selector and not selector.startswith('//'):
            issues.append(f"XPath selector '{selector}' should start with '//'")
        
        return issues
    
    def _validate_condition(self, condition: Dict[str, Any]) -> bool:
        """Validate pre/post condition."""
        required_fields = ['type', 'value']
        return all(field in condition for field in required_fields)
    
    def optimize_flow(self, flow_dsl: FlowDSL) -> FlowDSL:
        """Optimize flow by adding waits and fallbacks."""
        optimized_steps = []
        
        for i, step in enumerate(flow_dsl.steps):
            # Add pre-step waits for certain actions
            if step.type in [StepType.CLICK, StepType.TYPE] and i > 0:
                wait_step = FlowStep(
                    type=StepType.WAIT,
                    timeout=step.policies.min_delay_ms if hasattr(step, 'policies') else 100,
                    retry_attempts=1
                )
                optimized_steps.append(wait_step)
            
            optimized_steps.append(step)
            
            # Add post-step waits for certain actions
            if step.type in [StepType.CLICK, StepType.TYPE, StepType.NAVIGATE]:
                wait_step = FlowStep(
                    type=StepType.WAIT,
                    timeout=step.policies.min_delay_ms if hasattr(step, 'policies') else 1000,
                    retry_attempts=1
                )
                optimized_steps.append(wait_step)
        
        # Create optimized flow
        optimized_flow = flow_dsl.copy()
        optimized_flow.steps = optimized_steps
        
        return optimized_flow
    
    def _add_fallback_selectors(self, flow_dsl: FlowDSL) -> None:
        """Add fallback selectors to all steps that need them."""
        for step in flow_dsl.steps:
            if step.selector and not step.fallback_selectors:
                step.fallback_selectors = self.generate_fallback_selectors(step)
    
    def generate_fallback_selectors(self, step: FlowStep) -> List[str]:
        """Generate comprehensive fallback selectors for a step."""
        if not step.selector:
            return []
        
        fallbacks = [step.selector]
        
        # Generate fallbacks based on selector type
        if step.selector.startswith('text='):
            text = step.selector[5:]
            fallbacks.extend([
                f"button:has-text('{text}')",
                f"a:has-text('{text}')",
                f"[aria-label*='{text}']",
                f"[title*='{text}']",
                f"[placeholder*='{text}']",
                f"//button[contains(text(), '{text}')]",
                f"//a[contains(text(), '{text}')]"
            ])
        
        elif step.selector.startswith('role='):
            role = step.selector[5:]
            fallbacks.extend([
                f"[role='{role}']",
                f"//*[@role='{role}']"
            ])
        
        elif step.selector.startswith('#'):
            element_id = step.selector[1:]
            fallbacks.extend([
                f"[id='{element_id}']",
                f"//*[@id='{element_id}']"
            ])
        
        elif step.selector.startswith('.'):
            class_name = step.selector[1:]
            fallbacks.extend([
                f"[class*='{class_name}']",
                f"//*[contains(@class, '{class_name}')]"
            ])
        
        elif step.selector.startswith('[') and step.selector.endswith(']'):
            # Attribute selector
            fallbacks.append(f"//*{step.selector}")
        
        # Add generic fallbacks
        fallbacks.extend([
            f"//*[@data-testid='{step.selector}']",
            f"//*[@data-qa='{step.selector}']",
            f"//*[@data-cy='{step.selector}']"
        ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_fallbacks = []
        for fallback in fallbacks:
            if fallback not in seen:
                seen.add(fallback)
                unique_fallbacks.append(fallback)
        
        return unique_fallbacks
    
    def to_json(self, flow_dsl: FlowDSL) -> str:
        """Convert flow DSL to JSON."""
        return flow_dsl.json(indent=2)
    
    def from_json(self, json_str: str) -> FlowDSL:
        """Create flow DSL from JSON."""
        data = json.loads(json_str)
        return self.compile_flow(data)
    
    def get_flow_summary(self, flow_dsl: FlowDSL) -> Dict[str, Any]:
        """Get comprehensive summary information about a flow."""
        step_types = [step.type.value for step in flow_dsl.steps]
        step_type_counts = {}
        for step_type in step_types:
            step_type_counts[step_type] = step_type_counts.get(step_type, 0) + 1
        
        return {
            "name": flow_dsl.name,
            "version": flow_dsl.version,
            "description": flow_dsl.description,
            "start_url": flow_dsl.start_url,
            "step_count": len(flow_dsl.steps),
            "step_types": list(set(step_types)),
            "step_type_counts": step_type_counts,
            "estimated_duration": len(flow_dsl.steps) * 2,  # Rough estimate in seconds
            "has_assertions": any(step.type == StepType.ASSERT for step in flow_dsl.steps),
            "has_navigation": any(step.type == StepType.NAVIGATE for step in flow_dsl.steps),
            "has_file_operations": any(step.type in [StepType.UPLOAD, StepType.DOWNLOAD] for step in flow_dsl.steps),
            "policies": flow_dsl.policies.dict(),
            "complexity_score": self._calculate_complexity_score(flow_dsl)
        }
    
    def _calculate_complexity_score(self, flow_dsl: FlowDSL) -> int:
        """Calculate complexity score for the flow."""
        score = 0
        
        # Base score from step count
        score += len(flow_dsl.steps)
        
        # Add complexity for different step types
        for step in flow_dsl.steps:
            if step.type in [StepType.ASSERT, StepType.EXECUTE_SCRIPT]:
                score += 2
            elif step.type in [StepType.UPLOAD, StepType.DOWNLOAD, StepType.SWITCH_TAB]:
                score += 3
            elif step.fallback_selectors and len(step.fallback_selectors) > 3:
                score += 1
        
        return score


# Global flow compiler
flow_compiler = FlowCompiler()
