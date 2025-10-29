"""
Data access patterns and repository classes.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from sqlmodel import SQLModel

from qa_agent.storage.models import (
    Project, TargetSite, Flow, FlowVersion, Run, RunStep, 
    SessionEvent, FrictionIssue, BrowserProfile, RunStatus
)


class BaseRepository:
    """Base repository with common operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, model: SQLModel) -> SQLModel:
        """Create a new model instance."""
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model
    
    async def get_by_id(self, model_class, id: UUID) -> Optional[SQLModel]:
        """Get model by ID."""
        result = await self.session.execute(select(model_class).where(model_class.id == id))
        return result.scalar_one_or_none()
    
    async def update(self, model: SQLModel) -> SQLModel:
        """Update a model instance."""
        await self.session.commit()
        await self.session.refresh(model)
        return model
    
    async def delete(self, model: SQLModel) -> None:
        """Delete a model instance."""
        await self.session.delete(model)
        await self.session.commit()


class ProjectRepository(BaseRepository):
    """Project repository."""
    
    async def list_projects(self) -> List[Project]:
        """List all projects."""
        result = await self.session.execute(select(Project))
        return result.scalars().all()
    
    async def get_project_with_relations(self, project_id: UUID) -> Optional[Project]:
        """Get project with all relations."""
        result = await self.session.execute(
            select(Project)
            .where(Project.id == project_id)
            .options(
                selectinload(Project.target_sites),
                selectinload(Project.flows),
                selectinload(Project.runs)
            )
        )
        return result.scalar_one_or_none()


class TargetSiteRepository(BaseRepository):
    """Target site repository."""
    
    async def list_target_sites(self, project_id: Optional[UUID] = None) -> List[TargetSite]:
        """List target sites, optionally filtered by project."""
        query = select(TargetSite)
        if project_id:
            query = query.where(TargetSite.project_id == project_id)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_by_url(self, url: str) -> Optional[TargetSite]:
        """Get target site by URL."""
        result = await self.session.execute(
            select(TargetSite).where(TargetSite.base_url == url)
        )
        return result.scalar_one_or_none()


class FlowRepository(BaseRepository):
    """Flow repository with comprehensive flow management."""
    
    async def list_flows(self, project_id: Optional[UUID] = None) -> List[Flow]:
        """List flows, optionally filtered by project."""
        query = select(Flow)
        if project_id:
            query = query.where(Flow.project_id == project_id)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_flow_with_versions(self, flow_id: UUID) -> Optional[Flow]:
        """Get flow with all versions."""
        result = await self.session.execute(
            select(Flow)
            .where(Flow.id == flow_id)
            .options(selectinload(Flow.versions))
        )
        return result.scalar_one_or_none()
    
    async def get_latest_version(self, flow_id: UUID) -> Optional[FlowVersion]:
        """Get latest version of a flow."""
        result = await self.session.execute(
            select(FlowVersion)
            .where(FlowVersion.flow_id == flow_id)
            .order_by(FlowVersion.version.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def create_flow_with_version(
        self,
        project_id: UUID,
        name: str,
        description: Optional[str],
        dsl_json: str,
        version: int = 1
    ) -> Flow:
        """Create a new flow with its first version."""
        # Create flow
        flow = Flow(
            project_id=project_id,
            name=name,
            description=description
        )
        await self.create(flow)
        
        # Create first version
        flow_version = FlowVersion(
            flow_id=flow.id,
            version=version,
            dsl_json=dsl_json
        )
        await self.create(flow_version)
        
        # Update flow with latest version
        flow.latest_version_id = flow_version.id
        await self.update(flow)
        
        return flow
    
    async def add_flow_version(
        self,
        flow_id: UUID,
        dsl_json: str,
        description: Optional[str] = None
    ) -> FlowVersion:
        """Add a new version to an existing flow."""
        # Get current latest version
        latest_version = await self.get_latest_version(flow_id)
        new_version_number = (latest_version.version + 1) if latest_version else 1
        
        # Create new version
        flow_version = FlowVersion(
            flow_id=flow_id,
            version=new_version_number,
            dsl_json=dsl_json,
            description=description
        )
        await self.create(flow_version)
        
        # Update flow's latest version reference
        flow = await self.get_by_id(Flow, flow_id)
        if flow:
            flow.latest_version_id = flow_version.id
            await self.update(flow)
        
        return flow_version
    
    async def get_flow_by_name(self, project_id: UUID, name: str) -> Optional[Flow]:
        """Get flow by name within a project."""
        result = await self.session.execute(
            select(Flow)
            .where(Flow.project_id == project_id)
            .where(Flow.name == name)
        )
        return result.scalar_one_or_none()
    
    async def search_flows(
        self,
        project_id: Optional[UUID] = None,
        name_pattern: Optional[str] = None,
        description_pattern: Optional[str] = None
    ) -> List[Flow]:
        """Search flows with pattern matching."""
        query = select(Flow)
        
        if project_id:
            query = query.where(Flow.project_id == project_id)
        
        if name_pattern:
            query = query.where(Flow.name.ilike(f"%{name_pattern}%"))
        
        if description_pattern:
            query = query.where(Flow.description.ilike(f"%{description_pattern}%"))
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_flow_statistics(self, flow_id: UUID) -> Dict[str, Any]:
        """Get statistics for a flow."""
        # Get run counts by status
        runs_result = await self.session.execute(
            select(Run.status, Run.id).where(Run.flow_id == flow_id)
        )
        runs = runs_result.all()
        
        status_counts = {}
        for status, _ in runs:
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Get version count
        versions_result = await self.session.execute(
            select(FlowVersion.id).where(FlowVersion.flow_id == flow_id)
        )
        version_count = len(versions_result.scalars().all())
        
        # Get latest version info
        latest_version = await self.get_latest_version(flow_id)
        
        return {
            "flow_id": str(flow_id),
            "total_runs": len(runs),
            "run_status_counts": status_counts,
            "version_count": version_count,
            "latest_version": latest_version.version if latest_version else None,
            "latest_version_created": latest_version.created_at if latest_version else None
        }

class RunRepository(BaseRepository):
    """Run repository."""
    
    async def list_runs(
        self, 
        project_id: Optional[UUID] = None,
        flow_id: Optional[UUID] = None,
        status: Optional[RunStatus] = None
    ) -> List[Run]:
        """List runs with optional filters."""
        query = select(Run)
        
        if project_id:
            query = query.where(Run.project_id == project_id)
        if flow_id:
            query = query.where(Run.flow_id == flow_id)
        if status:
            query = query.where(Run.status == status)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_run_with_details(self, run_id: UUID) -> Optional[Run]:
        """Get run with all related data."""
        result = await self.session.execute(
            select(Run)
            .where(Run.id == run_id)
            .options(
                selectinload(Run.steps),
                selectinload(Run.events),
                selectinload(Run.friction_issues)
            )
        )
        return result.scalar_one_or_none()
    
    async def update_run_status(
        self, 
        run_id: UUID, 
        status: RunStatus,
        error_message: Optional[str] = None
    ) -> Optional[Run]:
        """Update run status."""
        run = await self.get_by_id(Run, run_id)
        if run:
            run.status = status
            if error_message:
                run.error_message = error_message
            await self.update(run)
        return run


class EventRepository(BaseRepository):
    """Event repository."""
    
    async def get_events_for_run(
        self,
        run_id: UUID,
        event_type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[SessionEvent]:
        """Get events for a run with optional filtering."""
        query = select(SessionEvent).where(SessionEvent.run_id == run_id)
        
        if event_type:
            query = query.where(SessionEvent.event_type == event_type)
        
        query = query.order_by(SessionEvent.timestamp).offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_event_summary(self, run_id: UUID) -> Dict[str, Any]:
        """Get event summary for a run."""
        events = await self.get_events_for_run(run_id)
        
        if not events:
            return {"total_events": 0, "event_types": {}}
        
        # Count by type
        event_types = {}
        for event in events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
        
        return {
            "total_events": len(events),
            "event_types": event_types,
            "first_event": min(e.timestamp for e in events),
            "last_event": max(e.timestamp for e in events)
        }


class FrictionRepository(BaseRepository):
    """Friction issue repository."""
    
    async def get_friction_for_run(self, run_id: UUID) -> List[FrictionIssue]:
        """Get friction issues for a run."""
        result = await self.session.execute(
            select(FrictionIssue).where(FrictionIssue.run_id == run_id)
        )
        return result.scalars().all()
    
    async def get_friction_summary(self, run_id: UUID) -> Dict[str, Any]:
        """Get friction summary for a run."""
        issues = await self.get_friction_for_run(run_id)
        
        if not issues:
            return {"total_issues": 0, "severity_distribution": {}}
        
        # Count by severity
        severity_distribution = {}
        for issue in issues:
            severity_distribution[issue.severity] = severity_distribution.get(issue.severity, 0) + 1
        
        # Calculate average score
        avg_score = sum(issue.score for issue in issues) / len(issues)
        
        return {
            "total_issues": len(issues),
            "severity_distribution": severity_distribution,
            "average_score": avg_score,
            "max_score": max(issue.score for issue in issues)
        }


class MetricsRepository(BaseRepository):
    """Metrics repository."""
    
    async def get_project_metrics(self, project_id: UUID) -> Dict[str, Any]:
        """Get metrics for a project."""
        # Get run counts by status
        runs_result = await self.session.execute(
            select(Run.status, Run.id).where(Run.project_id == project_id)
        )
        runs = runs_result.all()
        
        status_counts = {}
        for status, _ in runs:
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Get flow count
        flows_result = await self.session.execute(
            select(Flow.id).where(Flow.project_id == project_id)
        )
        flow_count = len(flows_result.scalars().all())
        
        # Get target site count
        sites_result = await self.session.execute(
            select(TargetSite.id).where(TargetSite.project_id == project_id)
        )
        site_count = len(sites_result.scalars().all())
        
        return {
            "project_id": str(project_id),
            "total_runs": len(runs),
            "run_status_counts": status_counts,
            "total_flows": flow_count,
            "total_target_sites": site_count
        }
