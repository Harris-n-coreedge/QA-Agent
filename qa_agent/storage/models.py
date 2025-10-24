"""
SQLModel database models.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum


class RunStatus(str, Enum):
    """Run status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AuthType(str, Enum):
    """Authentication type enumeration."""
    NONE = "none"
    BASIC = "basic"
    OAUTH = "oauth"
    API_KEY = "api_key"


class Project(SQLModel, table=True):
    """Project model."""
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    target_sites: List["TargetSite"] = Relationship(back_populates="project")
    flows: List["Flow"] = Relationship(back_populates="project")
    runs: List["Run"] = Relationship(back_populates="project")


class TargetSite(SQLModel, table=True):
    """Target site model."""
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(..., foreign_key="project.id")
    name: str = Field(..., description="Site name")
    base_url: str = Field(..., description="Base URL")
    auth_type: AuthType = Field(default=AuthType.NONE, description="Authentication type")
    auth_config: Optional[str] = Field(None, description="Authentication configuration (JSON)")
    robots_respected: bool = Field(default=True, description="Whether to respect robots.txt")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    project: Project = Relationship(back_populates="target_sites")
    runs: List["Run"] = Relationship(back_populates="target_site")


class Flow(SQLModel, table=True):
    """Flow model."""
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(..., foreign_key="project.id")
    name: str = Field(..., description="Flow name")
    description: Optional[str] = Field(None, description="Flow description")
    latest_version_id: Optional[UUID] = Field(None, foreign_key="flowversion.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    project: Project = Relationship(back_populates="flows")
    versions: List["FlowVersion"] = Relationship(back_populates="flow")
    runs: List["Run"] = Relationship(back_populates="flow")


class FlowVersion(SQLModel, table=True):
    """Flow version model."""
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    flow_id: UUID = Field(..., foreign_key="flow.id")
    version: int = Field(..., description="Version number")
    dsl_json: str = Field(..., description="Flow DSL as JSON")
    description: Optional[str] = Field(None, description="Version description")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    flow: Flow = Relationship(back_populates="versions")
    runs: List["Run"] = Relationship(back_populates="flow_version")


class Run(SQLModel, table=True):
    """Run model."""
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(..., foreign_key="project.id")
    flow_id: UUID = Field(..., foreign_key="flow.id")
    flow_version_id: UUID = Field(..., foreign_key="flowversion.id")
    target_site_id: UUID = Field(..., foreign_key="targetsite.id")
    status: RunStatus = Field(default=RunStatus.PENDING, description="Run status")
    started_at: Optional[datetime] = Field(None, description="Start time")
    finished_at: Optional[datetime] = Field(None, description="Finish time")
    kernel_browser_id: Optional[str] = Field(None, description="Kernel browser ID")
    kernel_replay_url: Optional[str] = Field(None, description="Kernel replay URL")
    live_view_url: Optional[str] = Field(None, description="Live view URL")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    project: Project = Relationship(back_populates="runs")
    flow: Flow = Relationship(back_populates="runs")
    flow_version: FlowVersion = Relationship(back_populates="runs")
    target_site: TargetSite = Relationship(back_populates="runs")
    steps: List["RunStep"] = Relationship(back_populates="run")
    events: List["SessionEvent"] = Relationship(back_populates="run")
    friction_issues: List["FrictionIssue"] = Relationship(back_populates="run")


class RunStep(SQLModel, table=True):
    """Run step model."""
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    run_id: UUID = Field(..., foreign_key="run.id")
    index: int = Field(..., description="Step index")
    name: str = Field(..., description="Step name")
    step_type: str = Field(..., description="Step type")
    status: RunStatus = Field(default=RunStatus.PENDING, description="Step status")
    started_at: Optional[datetime] = Field(None, description="Step start time")
    finished_at: Optional[datetime] = Field(None, description="Step finish time")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    result_data: Optional[str] = Field(None, description="Step result data (JSON)")
    
    # Relationships
    run: Run = Relationship(back_populates="steps")
    events: List["SessionEvent"] = Relationship(back_populates="step")
    friction_issues: List["FrictionIssue"] = Relationship(back_populates="step")


class SessionEvent(SQLModel, table=True):
    """Session event model."""
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    run_id: UUID = Field(..., foreign_key="run.id")
    step_id: Optional[UUID] = Field(None, foreign_key="runstep.id")
    event_type: str = Field(..., description="Event type")
    timestamp: float = Field(..., description="Event timestamp")
    payload_json: str = Field(..., description="Event payload as JSON")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    run: Run = Relationship(back_populates="events")
    step: Optional[RunStep] = Relationship(back_populates="events")


class FrictionIssue(SQLModel, table=True):
    """Friction issue model."""
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    run_id: UUID = Field(..., foreign_key="run.id")
    step_id: Optional[UUID] = Field(None, foreign_key="runstep.id")
    friction_type: str = Field(..., description="Type of friction")
    severity: str = Field(..., description="Severity level")
    score: float = Field(..., description="Friction score")
    evidence_json: str = Field(..., description="Evidence data as JSON")
    recommendation: str = Field(..., description="Recommendation")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    run: Run = Relationship(back_populates="friction_issues")
    step: Optional[RunStep] = Relationship(back_populates="friction_issues")


class BrowserProfile(SQLModel, table=True):
    """Browser profile model."""
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(..., foreign_key="project.id")
    name: str = Field(..., description="Profile name")
    kernel_profile_name: str = Field(..., description="Kernel profile name")
    description: Optional[str] = Field(None, description="Profile description")
    last_used_at: Optional[datetime] = Field(None, description="Last used timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    project: Project = Relationship()
