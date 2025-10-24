"""
Flow management routes with comprehensive DSL support.

Provides REST API endpoints for:
- Flow CRUD operations
- DSL validation and compilation
- Flow execution coordination
- Version management
- Flow templates and import/export
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
import json

from qa_agent.schemas import (
    FlowCreate, FlowResponse, FlowUpdate, 
    FlowStep, ProjectResponse
)
from qa_agent.storage.repo import FlowRepository
from qa_agent.generation.service import FlowService
from qa_agent.generation.dsl import flow_compiler
from qa_agent.core.db import get_db_session
from qa_agent.core.queues import get_queue
from qa_agent.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


def get_flow_service(session = Depends(get_db_session)) -> FlowService:
    """Dependency to get FlowService instance."""
    flow_repo = FlowRepository(session)
    return FlowService(flow_repo)


@router.post("/flows", response_model=FlowResponse)
async def create_flow(
    flow: FlowCreate,
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Create a new flow with DSL validation and compilation.
    
    The flow data will be compiled and validated before storage.
    Returns the created flow with its first version.
    """
    try:
        # Convert FlowCreate to flow data dict
        flow_data = {
            "name": flow.name,
            "version": 1,
            "start_url": flow.start_url,
            "steps": [step.dict() for step in flow.steps],
            "policies": {
                "human_like": True,
                "max_step_timeout_ms": 15000,
                "min_delay_ms": 100,
                "max_delay_ms": 1000,
                "retry_attempts": 3
            }
        }
        
        created_flow = await flow_service.create_flow(
            project_id=flow.project_id,
            name=flow.name,
            description=flow.description,
            flow_data=flow_data
        )
        
        logger.info("Flow created via API", flow_id=str(created_flow.id), name=flow.name)
        return FlowResponse.from_orm(created_flow)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Flow creation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/flows/validate")
async def validate_flow(
    flow_data: Dict[str, Any] = Body(...),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Validate flow DSL without creating it.
    
    Returns validation results including:
    - Validation status
    - List of issues
    - Flow summary
    - Compiled flow data
    """
    try:
        validation_result = await flow_service.validate_flow(flow_data)
        
        return {
            "valid": validation_result["valid"],
            "issues": validation_result["issues"],
            "summary": validation_result["summary"],
            "compiled_flow": validation_result["compiled_flow"]
        }
        
    except Exception as e:
        logger.error("Flow validation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/flows/auto-generate")
async def auto_generate_flows(
    target_site_id: UUID,
    flow_service: FlowService = Depends(get_flow_service),
    queue = Depends(get_queue)
):
    """
    Start auto-generation of flows for a target site.
    
    This endpoint initiates the flow discovery process that will:
    1. Crawl the target site
    2. Detect key user flows (login, signup, search, etc.)
    3. Generate and validate flow DSLs
    4. Store discovered flows
    
    Returns a job ID for tracking the generation process.
    """
    try:
        from qa_agent.workers.auto_generate import auto_generate_flows
        
        # Queue the auto-generation job
        job = queue.enqueue(
            auto_generate_flows,
            target_site_id=str(target_site_id),
            job_timeout='30m'  # 30 minute timeout for discovery
        )
        
        logger.info("Auto-generation job queued", 
                   target_site_id=str(target_site_id), 
                   job_id=job.id)
        
        return {
            "status": "queued",
            "job_id": job.id,
            "target_site_id": str(target_site_id),
            "message": "Flow auto-generation job has been queued"
        }
        
    except Exception as e:
        logger.error("Failed to queue auto-generation job", 
                    target_site_id=str(target_site_id), 
                    error=str(e))
        raise HTTPException(status_code=500, detail="Failed to start auto-generation")


@router.get("/flows/auto-generate/{job_id}/status")
async def get_auto_generation_status(
    job_id: str,
    queue = Depends(get_queue)
):
    """
    Get the status of an auto-generation job.
    
    Returns the current status and results if completed.
    """
    try:
        from rq import get_current_job
        
        # Get job from queue
        job = queue.fetch_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        status_info = {
            "job_id": job_id,
            "status": job.get_status(),
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "finished_at": job.finished_at.isoformat() if job.finished_at else None,
        }
        
        # Add result if completed successfully
        if job.is_finished and job.result:
            status_info["result"] = job.result
        
        # Add error if failed
        if job.is_failed:
            status_info["error"] = str(job.exc_info) if job.exc_info else "Unknown error"
        
        return status_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get job status", job_id=job_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get job status")


@router.get("/flows", response_model=List[FlowResponse])
async def list_flows(
    project_id: Optional[UUID] = Query(None, description="Filter by project ID"),
    name_pattern: Optional[str] = Query(None, description="Filter by name pattern"),
    description_pattern: Optional[str] = Query(None, description="Filter by description pattern"),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    List flows with optional filtering.
    
    Supports filtering by:
    - Project ID
    - Name pattern (partial match)
    - Description pattern (partial match)
    """
    try:
        flows = await flow_service.list_flows(
            project_id=project_id,
            name_pattern=name_pattern,
            description_pattern=description_pattern
        )
        
        return [FlowResponse.from_orm(flow) for flow in flows]
        
    except Exception as e:
        logger.error("Flow listing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/flows/{flow_id}", response_model=FlowResponse)
async def get_flow(
    flow_id: UUID,
    include_versions: bool = Query(False, description="Include version details"),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Get a specific flow by ID.
    
    Optionally include version details for comprehensive flow information.
    """
    try:
        flow = await flow_service.get_flow(flow_id, include_versions=include_versions)
        
        if not flow:
            raise HTTPException(status_code=404, detail="Flow not found")
        
        return FlowResponse.from_orm(flow)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Flow retrieval failed", error=str(e), flow_id=str(flow_id))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/flows/{flow_id}/dsl")
async def get_flow_dsl(
    flow_id: UUID,
    version: Optional[int] = Query(None, description="Specific version (default: latest)"),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Get the compiled DSL for a flow.
    
    Returns the Flow DSL in JSON format, optionally for a specific version.
    """
    try:
        flow_dsl = await flow_service.get_flow_dsl(flow_id, version=version)
        
        if not flow_dsl:
            raise HTTPException(status_code=404, detail="Flow or version not found")
        
        return flow_dsl.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Flow DSL retrieval failed", error=str(e), flow_id=str(flow_id))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/flows/{flow_id}", response_model=FlowResponse)
async def update_flow(
    flow_id: UUID,
    flow_update: FlowUpdate,
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Update an existing flow.
    
    Can update basic fields (name, description) and/or flow data.
    Updating flow data creates a new version.
    """
    try:
        # Convert FlowUpdate to appropriate parameters
        flow_data = None
        if flow_update.steps:
            # Convert steps to flow data format
            flow_data = {
                "name": flow_update.name or "updated_flow",
                "version": 1,
                "start_url": flow_update.start_url or "https://example.com",
                "steps": [step.dict() for step in flow_update.steps],
                "policies": {
                    "human_like": True,
                    "max_step_timeout_ms": 15000,
                    "min_delay_ms": 100,
                    "max_delay_ms": 1000,
                    "retry_attempts": 3
                }
            }
        
        updated_flow = await flow_service.update_flow(
            flow_id=flow_id,
            flow_data=flow_data,
            name=flow_update.name,
            description=flow_update.description
        )
        
        logger.info("Flow updated via API", flow_id=str(flow_id))
        return FlowResponse.from_orm(updated_flow)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Flow update failed", error=str(e), flow_id=str(flow_id))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/flows/{flow_id}")
async def delete_flow(
    flow_id: UUID,
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Delete a flow and all its versions.
    
    This operation is irreversible and will also delete associated runs.
    """
    try:
        success = await flow_service.delete_flow(flow_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Flow not found")
        
        logger.info("Flow deleted via API", flow_id=str(flow_id))
        return {"message": "Flow deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Flow deletion failed", error=str(e), flow_id=str(flow_id))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/flows/{flow_id}/duplicate", response_model=FlowResponse)
async def duplicate_flow(
    flow_id: UUID,
    new_name: str = Body(..., embed=True),
    project_id: Optional[UUID] = Body(None, embed=True),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Duplicate an existing flow.
    
    Creates a new flow with the same DSL as the source flow's latest version.
    """
    try:
        duplicated_flow = await flow_service.duplicate_flow(
            source_flow_id=flow_id,
            new_name=new_name,
            project_id=project_id
        )
        
        logger.info("Flow duplicated via API", 
                   source_flow_id=str(flow_id), 
                   new_flow_id=str(duplicated_flow.id))
        
        return FlowResponse.from_orm(duplicated_flow)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Flow duplication failed", error=str(e), flow_id=str(flow_id))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/flows/{flow_id}/statistics")
async def get_flow_statistics(
    flow_id: UUID,
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Get comprehensive statistics for a flow.
    
    Returns:
    - Run statistics (counts by status)
    - Version information
    - DSL analysis
    - Performance metrics
    """
    try:
        stats = await flow_service.get_flow_statistics(flow_id)
        return stats
        
    except Exception as e:
        logger.error("Flow statistics retrieval failed", error=str(e), flow_id=str(flow_id))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/flows/{flow_id}/export")
async def export_flow(
    flow_id: UUID,
    format: str = Query("json", description="Export format (json, dict)"),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Export flow in specified format.
    
    Supported formats:
    - json: JSON string
    - dict: Python dictionary
    """
    try:
        exported_data = await flow_service.export_flow(flow_id, format=format)
        
        if format == "json":
            return {"flow_data": exported_data}
        else:
            return exported_data
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Flow export failed", error=str(e), flow_id=str(flow_id))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/flows/import", response_model=FlowResponse)
async def import_flow(
    project_id: UUID = Body(..., embed=True),
    name: str = Body(..., embed=True),
    flow_data: Union[str, Dict[str, Any]] = Body(..., embed=True),
    description: Optional[str] = Body(None, embed=True),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Import flow from external data.
    
    Accepts flow data as JSON string or dictionary.
    The flow will be validated and compiled before creation.
    """
    try:
        imported_flow = await flow_service.import_flow(
            project_id=project_id,
            flow_data=flow_data,
            name=name,
            description=description
        )
        
        logger.info("Flow imported via API", flow_id=str(imported_flow.id), name=name)
        return FlowResponse.from_orm(imported_flow)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Flow import failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/flows/templates")
async def get_flow_templates(
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Get predefined flow templates.
    
    Returns a list of available templates that can be used to create flows.
    """
    try:
        templates = await flow_service.get_flow_templates()
        return {"templates": templates}
        
    except Exception as e:
        logger.error("Flow templates retrieval failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/flows/templates/{template_name}")
async def create_flow_from_template(
    template_name: str,
    project_id: UUID = Body(..., embed=True),
    customizations: Optional[Dict[str, Any]] = Body(None, embed=True),
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    Create a flow from a predefined template.
    
    Applies optional customizations to the template before creating the flow.
    """
    try:
        created_flow = await flow_service.create_flow_from_template(
            project_id=project_id,
            template_name=template_name,
            customizations=customizations
        )
        
        logger.info("Flow created from template via API", 
                   flow_id=str(created_flow.id), 
                   template_name=template_name)
        
        return FlowResponse.from_orm(created_flow)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Flow creation from template failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
