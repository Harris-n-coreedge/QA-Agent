"""
RQ job to execute a simulation run.
"""
from typing import Dict, Any
from uuid import UUID
import asyncio
import json

from qa_agent.simulation.engine import simulation_engine
from qa_agent.storage.repo import RunRepository
from qa_agent.storage.models import RunStatus
from qa_agent.core.db import AsyncSessionLocal
from qa_agent.core.logging import get_logger

logger = get_logger(__name__)


async def run_simulation_task(run_id: str) -> Dict[str, Any]:
    """Execute a simulation run."""
    run_uuid = UUID(run_id)
    
    async with AsyncSessionLocal() as session:
        try:
            logger.info("Starting simulation run", run_id=run_id)
            
            # Get run details
            run_repo = RunRepository(session)
            run = await run_repo.get_run_with_details(run_uuid)
            
            if not run:
                raise ValueError(f"Run {run_id} not found")
            
            # Update status to running
            await run_repo.update_run_status(run_uuid, RunStatus.RUNNING)
            
            # Get flow DSL
            flow_version = run.flow_version
            flow_dsl = json.loads(flow_version.dsl_json)
            
            # Get target site URL
            target_url = run.target_site.base_url
            
            # Execute simulation
            result = await simulation_engine.execute_run(
                run_id=run_uuid,
                flow_dsl=flow_dsl,
                target_url=target_url,
                profile=run.kernel_browser_id
            )
            
            # Update run with results
            if result["status"] == "completed":
                await run_repo.update_run_status(run_uuid, RunStatus.COMPLETED)
                
                # Store browser info
                browser_info = result.get("browser_info", {})
                run.kernel_replay_url = browser_info.get("replay_url")
                run.live_view_url = browser_info.get("live_view_url")
                
            else:
                await run_repo.update_run_status(
                    run_uuid, 
                    RunStatus.FAILED,
                    error_message=result.get("error", "Unknown error")
                )
            
            logger.info("Simulation run completed", run_id=run_id, status=result["status"])
            
            return result
            
        except Exception as e:
            logger.error("Simulation run failed", run_id=run_id, error=str(e))
            
            # Update status to failed
            try:
                await run_repo.update_run_status(
                    run_uuid, 
                    RunStatus.FAILED,
                    error_message=str(e)
                )
            except Exception:
                pass  # Ignore errors updating status
            
            raise


def run_simulation(run_id: str) -> Dict[str, Any]:
    """RQ job wrapper for simulation run."""
    return asyncio.run(run_simulation_task(run_id))
