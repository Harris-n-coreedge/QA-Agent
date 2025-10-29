"""
RQ job to auto-generate flows for a target site.
"""
from typing import Dict, Any, List
from uuid import UUID
import asyncio
import json

from qa_agent.generation.discovery import FlowDiscovery
from qa_agent.generation.dsl import flow_compiler
from qa_agent.generation.ranking import flow_ranker
from qa_agent.kernel.browser import connect_kernel_browser, disconnect_kernel_browser
from qa_agent.storage.repo import TargetSiteRepository, FlowRepository, FlowVersionRepository
from qa_agent.storage.models import Flow, FlowVersion, TargetSite
from qa_agent.core.db import AsyncSessionLocal
from qa_agent.core.logging import get_logger

logger = get_logger(__name__)


async def auto_generate_flows_task(target_site_id: str) -> Dict[str, Any]:
    """Auto-generate flows for a target site."""
    target_uuid = UUID(target_site_id)
    
    async with AsyncSessionLocal() as session:
        try:
            logger.info("Starting flow auto-generation", target_site_id=target_site_id)
            
            # Get target site details
            target_repo = TargetSiteRepository(session)
            target_site = await target_repo.get_by_id(TargetSite, target_uuid)
            
            if not target_site:
                raise ValueError(f"Target site {target_site_id} not found")
            
            # Create temporary run ID for browser session
            temp_run_id = UUID()
            
            # Connect to browser for discovery
            browser, context, page, browser_response = await connect_kernel_browser(
                run_id=temp_run_id,
                stealth=True
            )
            
            try:
                # Discover flows
                discovery = FlowDiscovery()
                discovered_flows = await discovery.discover_flows(
                    page=page,
                    start_url=target_site.base_url,
                    max_depth=2,
                    max_pages=20
                )
                
                logger.info("Flow discovery completed", flows_found=len(discovered_flows))
                
                # Rank flows
                rankings = flow_ranker.rank_flows(discovered_flows)
                
                # Filter high-priority flows
                high_priority_flows = flow_ranker.filter_flows_by_priority(
                    rankings, 
                    flow_ranker.FlowPriority.HIGH
                )
                
                # Create flows in database
                flow_repo = FlowRepository(session)
                flow_version_repo = FlowVersionRepository(session)
                
                created_flows = []
                
                for ranking in high_priority_flows[:5]:  # Limit to top 5 flows
                    try:
                        # Create flow
                        flow = Flow(
                            project_id=target_site.project_id,
                            name=f"Auto-generated {ranking.flow_id}",
                            description=f"Automatically discovered {ranking.flow_id} flow"
                        )
                        
                        flow = await flow_repo.create(flow)
                        
                        # Create flow version with DSL
                        flow_dsl = {
                            "name": flow.name,
                            "version": 1,
                            "start_url": target_site.base_url,
                            "steps": ranking.flows[0]["pattern"]["steps"],
                            "policies": {
                                "human_like": True,
                                "max_step_timeout_ms": 15000
                            }
                        }
                        
                        # Compile and validate DSL
                        compiled_dsl = flow_compiler.compile_flow(flow_dsl)
                        issues = flow_compiler.validate_flow(compiled_dsl)
                        
                        if issues:
                            logger.warning("Flow validation issues", flow_id=str(flow.id), issues=issues)
                        
                        # Create version
                        flow_version = FlowVersion(
                            flow_id=flow.id,
                            version=1,
                            dsl_json=flow_compiler.to_json(compiled_dsl),
                            description=f"Auto-generated version 1"
                        )
                        
                        flow_version = await flow_version_repo.create(flow_version)
                        
                        # Update flow with latest version
                        flow.latest_version_id = flow_version.id
                        await flow_repo.update(flow)
                        
                        created_flows.append({
                            "flow_id": str(flow.id),
                            "name": flow.name,
                            "priority": ranking.priority.value,
                            "score": ranking.score
                        })
                        
                    except Exception as e:
                        logger.error("Failed to create flow", error=str(e))
                        continue
                
                logger.info("Flow auto-generation completed", flows_created=len(created_flows))
                
                return {
                    "status": "completed",
                    "target_site_id": target_site_id,
                    "flows_discovered": len(discovered_flows),
                    "flows_created": len(created_flows),
                    "created_flows": created_flows
                }
                
            finally:
                # Cleanup browser
                await disconnect_kernel_browser(temp_run_id)
            
        except Exception as e:
            logger.error("Flow auto-generation failed", target_site_id=target_site_id, error=str(e))
            raise


def auto_generate_flows(target_site_id: str) -> Dict[str, Any]:
    """RQ job wrapper for flow auto-generation."""
    return asyncio.run(auto_generate_flows_task(target_site_id))
