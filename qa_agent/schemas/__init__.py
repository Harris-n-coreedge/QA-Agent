"""
Pydantic request/response models for API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


# Enums
class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AuthType(str, Enum):
    NONE = "none"
    BASIC = "basic"
    OAUTH = "oauth"
    API_KEY = "api_key"


class FrictionSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Project schemas
class ProjectCreate(BaseModel):
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Project name")
    description: Optional[str] = Field(None, description="Project description")


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Target site schemas
class TargetSiteCreate(BaseModel):
    project_id: UUID = Field(..., description="Project ID")
    name: str = Field(..., description="Site name")
    base_url: str = Field(..., description="Base URL")
    auth_type: AuthType = Field(default=AuthType.NONE, description="Authentication type")
    auth_config: Optional[str] = Field(None, description="Authentication configuration")
    robots_respected: bool = Field(default=True, description="Whether to respect robots.txt")


class TargetSiteUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Site name")
    base_url: Optional[str] = Field(None, description="Base URL")
    auth_type: Optional[AuthType] = Field(None, description="Authentication type")
    auth_config: Optional[str] = Field(None, description="Authentication configuration")
    robots_respected: Optional[bool] = Field(None, description="Whether to respect robots.txt")


class TargetSiteResponse(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    base_url: str
    auth_type: AuthType
    auth_config: Optional[str]
    robots_respected: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Flow schemas
class FlowStep(BaseModel):
    type: str = Field(..., description="Step type")
    selector: Optional[str] = Field(None, description="Element selector")
    text: Optional[str] = Field(None, description="Text to type")
    url: Optional[str] = Field(None, description="URL to navigate to")
    timeout: Optional[int] = Field(5000, description="Timeout in milliseconds")
    expect: Optional[Dict[str, Any]] = Field(None, description="Assertion expectations")


class FlowCreate(BaseModel):
    project_id: UUID = Field(..., description="Project ID")
    name: str = Field(..., description="Flow name")
    description: Optional[str] = Field(None, description="Flow description")
    start_url: str = Field(..., description="Starting URL")
    steps: List[FlowStep] = Field(..., description="Flow steps")


class FlowUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Flow name")
    description: Optional[str] = Field(None, description="Flow description")
    start_url: Optional[str] = Field(None, description="Starting URL")
    steps: Optional[List[FlowStep]] = Field(None, description="Flow steps")


class FlowResponse(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    description: Optional[str]
    latest_version_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Run schemas
class RunCreate(BaseModel):
    project_id: UUID = Field(..., description="Project ID")
    flow_id: UUID = Field(..., description="Flow ID")
    target_site_id: UUID = Field(..., description="Target site ID")
    profile: Optional[str] = Field(None, description="Browser profile")


class RunUpdate(BaseModel):
    status: Optional[RunStatus] = Field(None, description="Run status")
    error_message: Optional[str] = Field(None, description="Error message")


class RunResponse(BaseModel):
    id: UUID
    project_id: UUID
    flow_id: UUID
    flow_version_id: UUID
    target_site_id: UUID
    status: RunStatus
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    kernel_browser_id: Optional[str]
    kernel_replay_url: Optional[str]
    live_view_url: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Event schemas
class SessionEventResponse(BaseModel):
    id: UUID
    run_id: UUID
    step_id: Optional[UUID]
    event_type: str
    timestamp: float
    payload: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Friction schemas
class FrictionIssueResponse(BaseModel):
    id: UUID
    run_id: UUID
    step_id: Optional[UUID]
    friction_type: str
    severity: FrictionSeverity
    score: float
    evidence: Dict[str, Any]
    recommendation: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class FrictionSummaryResponse(BaseModel):
    run_id: UUID
    total_issues: int
    overall_score: float
    severity_distribution: Dict[str, int]
    type_distribution: Dict[str, int]
    critical_issues: int
    recommendations: List[str]


# Metrics schemas
class ProjectMetricsResponse(BaseModel):
    project_id: UUID
    total_runs: int
    run_status_counts: Dict[str, int]
    total_flows: int
    total_target_sites: int


# WebSocket schemas
class WebSocketEvent(BaseModel):
    type: str
    timestamp: float
    data: Dict[str, Any]


class RunStatusEvent(WebSocketEvent):
    type: str = "run_status"
    status: str
    details: Dict[str, Any]


class StepEvent(WebSocketEvent):
    type: str = "step_event"
    step_index: int
    step_info: Dict[str, Any]


class FrictionEvent(WebSocketEvent):
    type: str = "friction_detected"
    friction_info: Dict[str, Any]


class MilestoneEvent(WebSocketEvent):
    type: str = "milestone"
    milestone: str
    details: Dict[str, Any]


# Browser automation schemas
class AIProvider(str, Enum):
    google = "google"
    openai = "openai"


class BrowserUseRequest(BaseModel):
    task: str = Field(..., description="Browser automation task")
    ai_provider: AIProvider = Field(default=AIProvider.google, description="AI provider to use")


class BrowserUseResponse(BaseModel):
    task: str
    status: str
    result: str
    executed_at: str


class TestResultResponse(BaseModel):
    id: str
    test_name: str
    status: str
    result: str
    executed_at: str
