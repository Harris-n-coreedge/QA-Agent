"""
Flow Service Layer

Integrates DSL compiler, executor, and repository for comprehensive flow management.
Provides high-level API for flow operations including creation, validation, execution, and management.
"""
from typing import Dict, Any, List, Optional, Union
from uuid import UUID
import json

from qa_agent.generation.dsl import FlowDSL, flow_compiler, StepType
from qa_agent.generation.executor import flow_executor
from qa_agent.storage.repo import FlowRepository
from qa_agent.storage.models import Flow, FlowVersion, Project
from qa_agent.core.logging import get_logger

logger = get_logger(__name__)


class FlowService:
    """
    High-level service for flow management operations.
    
    Features:
    - Flow creation and validation
    - DSL compilation and optimization
    - Flow execution coordination
    - Version management
    - Flow statistics and analytics
    """
    
    def __init__(self, flow_repo: FlowRepository):
        self.flow_repo = flow_repo
        self.compiler = flow_compiler
        self.executor = flow_executor
    
    async def create_flow(
        self,
        project_id: UUID,
        name: str,
        description: Optional[str],
        flow_data: Dict[str, Any]
    ) -> Flow:
        """
        Create a new flow with validation and compilation.
        
        Args:
            project_id: Project ID
            name: Flow name
            description: Flow description
            flow_data: Raw flow data (will be compiled)
        
        Returns:
            Created Flow instance
        """
        logger.info("Creating new flow", project_id=str(project_id), name=name)
        
        # Check if flow name already exists
        existing_flow = await self.flow_repo.get_flow_by_name(project_id, name)
        if existing_flow:
            raise ValueError(f"Flow with name '{name}' already exists in project")
        
        # Compile and validate flow DSL
        try:
            compiled_flow = self.compiler.compile_flow(flow_data)
        except Exception as e:
            logger.error("Flow compilation failed", error=str(e), name=name)
            raise ValueError(f"Flow compilation failed: {e}")
        
        # Convert to JSON for storage
        dsl_json = self.compiler.to_json(compiled_flow)
        
        # Create flow in database
        flow = await self.flow_repo.create_flow_with_version(
            project_id=project_id,
            name=name,
            description=description,
            dsl_json=dsl_json
        )
        
        logger.info("Flow created successfully", flow_id=str(flow.id), name=name)
        return flow
    
    async def update_flow(
        self,
        flow_id: UUID,
        flow_data: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Flow:
        """
        Update an existing flow.
        
        Args:
            flow_id: Flow ID
            flow_data: New flow data (creates new version)
            name: New flow name
            description: New flow description
        
        Returns:
            Updated Flow instance
        """
        logger.info("Updating flow", flow_id=str(flow_id))
        
        flow = await self.flow_repo.get_by_id(Flow, flow_id)
        if not flow:
            raise ValueError(f"Flow {flow_id} not found")
        
        # Update basic fields
        if name is not None:
            flow.name = name
        if description is not None:
            flow.description = description
        
        # If flow_data is provided, create new version
        if flow_data is not None:
            try:
                compiled_flow = self.compiler.compile_flow(flow_data)
                dsl_json = self.compiler.to_json(compiled_flow)
                
                await self.flow_repo.add_flow_version(
                    flow_id=flow_id,
                    dsl_json=dsl_json,
                    description=f"Updated flow data"
                )
                
                logger.info("New flow version created", flow_id=str(flow_id))
                
            except Exception as e:
                logger.error("Flow update compilation failed", error=str(e), flow_id=str(flow_id))
                raise ValueError(f"Flow update failed: {e}")
        
        # Update flow in database
        await self.flow_repo.update(flow)
        
        logger.info("Flow updated successfully", flow_id=str(flow_id))
        return flow
    
    async def get_flow(self, flow_id: UUID, include_versions: bool = False) -> Optional[Flow]:
        """Get flow by ID with optional version details."""
        if include_versions:
            return await self.flow_repo.get_flow_with_versions(flow_id)
        else:
            return await self.flow_repo.get_by_id(Flow, flow_id)
    
    async def get_flow_dsl(self, flow_id: UUID, version: Optional[int] = None) -> Optional[FlowDSL]:
        """
        Get compiled Flow DSL for a flow.
        
        Args:
            flow_id: Flow ID
            version: Specific version (None for latest)
        
        Returns:
            Compiled FlowDSL instance
        """
        if version is None:
            flow_version = await self.flow_repo.get_latest_version(flow_id)
        else:
            # Get specific version (would need additional repo method)
            flow_version = await self.flow_repo.get_by_id(FlowVersion, flow_id)
        
        if not flow_version:
            return None
        
        try:
            return self.compiler.from_json(flow_version.dsl_json)
        except Exception as e:
            logger.error("Failed to parse flow DSL", error=str(e), flow_id=str(flow_id))
            return None
    
    async def validate_flow(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate flow data without creating it.
        
        Args:
            flow_data: Raw flow data to validate
        
        Returns:
            Validation results with issues and summary
        """
        try:
            compiled_flow = self.compiler.compile_flow(flow_data)
            issues = self.compiler.validate_flow(compiled_flow)
            summary = self.compiler.get_flow_summary(compiled_flow)
            
            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "summary": summary,
                "compiled_flow": compiled_flow.dict()
            }
            
        except Exception as e:
            return {
                "valid": False,
                "issues": [str(e)],
                "summary": None,
                "compiled_flow": None
            }
    
    async def list_flows(
        self,
        project_id: Optional[UUID] = None,
        name_pattern: Optional[str] = None,
        description_pattern: Optional[str] = None
    ) -> List[Flow]:
        """List flows with optional filtering."""
        if name_pattern or description_pattern:
            return await self.flow_repo.search_flows(
                project_id=project_id,
                name_pattern=name_pattern,
                description_pattern=description_pattern
            )
        else:
            return await self.flow_repo.list_flows(project_id=project_id)
    
    async def get_flow_statistics(self, flow_id: UUID) -> Dict[str, Any]:
        """Get comprehensive statistics for a flow."""
        stats = await self.flow_repo.get_flow_statistics(flow_id)
        
        # Add DSL analysis
        flow_dsl = await self.get_flow_dsl(flow_id)
        if flow_dsl:
            dsl_summary = self.compiler.get_flow_summary(flow_dsl)
            stats["dsl_summary"] = dsl_summary
        
        return stats
    
    async def delete_flow(self, flow_id: UUID) -> bool:
        """Delete a flow and all its versions."""
        logger.info("Deleting flow", flow_id=str(flow_id))
        
        flow = await self.flow_repo.get_by_id(Flow, flow_id)
        if not flow:
            return False
        
        # Delete flow (cascade will handle versions)
        await self.flow_repo.delete(flow)
        
        logger.info("Flow deleted successfully", flow_id=str(flow_id))
        return True
    
    async def duplicate_flow(
        self,
        source_flow_id: UUID,
        new_name: str,
        project_id: Optional[UUID] = None
    ) -> Flow:
        """
        Duplicate an existing flow.
        
        Args:
            source_flow_id: Source flow ID
            new_name: Name for the new flow
            project_id: Target project ID (defaults to source project)
        
        Returns:
            New Flow instance
        """
        logger.info("Duplicating flow", source_flow_id=str(source_flow_id), new_name=new_name)
        
        # Get source flow
        source_flow = await self.flow_repo.get_by_id(Flow, source_flow_id)
        if not source_flow:
            raise ValueError(f"Source flow {source_flow_id} not found")
        
        # Use source project if not specified
        target_project_id = project_id or source_flow.project_id
        
        # Get latest version DSL
        latest_version = await self.flow_repo.get_latest_version(source_flow_id)
        if not latest_version:
            raise ValueError(f"No versions found for flow {source_flow_id}")
        
        # Create new flow with same DSL
        new_flow = await self.flow_repo.create_flow_with_version(
            project_id=target_project_id,
            name=new_name,
            description=f"Duplicated from {source_flow.name}",
            dsl_json=latest_version.dsl_json
        )
        
        logger.info("Flow duplicated successfully", 
                   source_flow_id=str(source_flow_id), 
                   new_flow_id=str(new_flow.id))
        
        return new_flow
    
    async def export_flow(self, flow_id: UUID, format: str = "json") -> Union[str, Dict[str, Any]]:
        """
        Export flow in specified format.
        
        Args:
            flow_id: Flow ID
            format: Export format ("json" or "yaml")
        
        Returns:
            Exported flow data
        """
        flow_dsl = await self.get_flow_dsl(flow_id)
        if not flow_dsl:
            raise ValueError(f"Flow {flow_id} not found or invalid")
        
        if format == "json":
            return self.compiler.to_json(flow_dsl)
        elif format == "dict":
            return flow_dsl.dict()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def import_flow(
        self,
        project_id: UUID,
        flow_data: Union[str, Dict[str, Any]],
        name: str,
        description: Optional[str] = None
    ) -> Flow:
        """
        Import flow from external data.
        
        Args:
            project_id: Target project ID
            flow_data: Flow data (JSON string or dict)
            name: Flow name
            description: Flow description
        
        Returns:
            Created Flow instance
        """
        logger.info("Importing flow", project_id=str(project_id), name=name)
        
        # Parse flow data
        if isinstance(flow_data, str):
            try:
                flow_dict = json.loads(flow_data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format: {e}")
        else:
            flow_dict = flow_data
        
        # Create flow using existing method
        return await self.create_flow(
            project_id=project_id,
            name=name,
            description=description,
            flow_data=flow_dict
        )
    
    async def get_flow_templates(self) -> List[Dict[str, Any]]:
        """Get predefined flow templates."""
        templates = [
            {
                "name": "login_flow",
                "description": "Standard login flow",
                "template": {
                    "name": "login_flow",
                    "version": 1,
                    "start_url": "https://example.com/login",
                    "steps": [
                        {"type": "type", "selector": "input[name='email']", "text": "user@example.com"},
                        {"type": "type", "selector": "input[name='password']", "text": "password123"},
                        {"type": "click", "selector": "button[type='submit']"},
                        {"type": "assert", "expect": {"url_contains": "/dashboard"}}
                    ],
                    "policies": {"human_like": True, "max_step_timeout_ms": 15000}
                }
            },
            {
                "name": "signup_flow",
                "description": "User registration flow",
                "template": {
                    "name": "signup_flow",
                    "version": 1,
                    "start_url": "https://example.com/signup",
                    "steps": [
                        {"type": "type", "selector": "input[name='email']", "text": "newuser@example.com"},
                        {"type": "type", "selector": "input[name='password']", "text": "newpassword123"},
                        {"type": "type", "selector": "input[name='confirm_password']", "text": "newpassword123"},
                        {"type": "click", "selector": "button:has-text('Sign Up')"},
                        {"type": "assert", "expect": {"text_present": "Welcome"}}
                    ],
                    "policies": {"human_like": True, "max_step_timeout_ms": 15000}
                }
            },
            {
                "name": "search_flow",
                "description": "Search functionality flow",
                "template": {
                    "name": "search_flow",
                    "version": 1,
                    "start_url": "https://example.com",
                    "steps": [
                        {"type": "click", "selector": "input[placeholder*='Search']"},
                        {"type": "type", "selector": "input[placeholder*='Search']", "text": "test query"},
                        {"type": "click", "selector": "button:has-text('Search')"},
                        {"type": "wait", "timeout": 2000},
                        {"type": "assert", "expect": {"element_visible": ".search-results"}}
                    ],
                    "policies": {"human_like": True, "max_step_timeout_ms": 15000}
                }
            }
        ]
        
        return templates
    
    async def create_flow_from_template(
        self,
        project_id: UUID,
        template_name: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> Flow:
        """
        Create a flow from a predefined template.
        
        Args:
            project_id: Project ID
            template_name: Template name
            customizations: Optional customizations to apply
        
        Returns:
            Created Flow instance
        """
        templates = await self.get_flow_templates()
        template = next((t for t in templates if t["name"] == template_name), None)
        
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        # Apply customizations if provided
        flow_data = template["template"].copy()
        if customizations:
            flow_data.update(customizations)
        
        return await self.create_flow(
            project_id=project_id,
            name=flow_data["name"],
            description=template["description"],
            flow_data=flow_data
        )


# Global flow service instance
def create_flow_service(flow_repo: FlowRepository) -> FlowService:
    """Create a FlowService instance."""
    return FlowService(flow_repo)
