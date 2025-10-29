"""
RQ job to post-process run and compute friction analysis.
"""
from typing import Dict, Any
from uuid import UUID
import asyncio
import json

from qa_agent.friction.heuristics import friction_heuristics
from qa_agent.friction.scoring import friction_scorer
from qa_agent.storage.repo import RunRepository, EventRepository, FrictionRepository
from qa_agent.storage.models import FrictionIssue
from qa_agent.core.db import AsyncSessionLocal
from qa_agent.core.logging import get_logger

logger = get_logger(__name__)


async def post_process_run_task(run_id: str) -> Dict[str, Any]:
    """Post-process a run and compute friction analysis."""
    run_uuid = UUID(run_id)
    
    async with AsyncSessionLocal() as session:
        try:
            logger.info("Starting run post-processing", run_id=run_id)
            
            # Get run details
            run_repo = RunRepository(session)
            run = await run_repo.get_run_with_details(run_uuid)
            
            if not run:
                raise ValueError(f"Run {run_id} not found")
            
            # Get events for the run
            event_repo = EventRepository(session)
            events = await event_repo.get_events_for_run(run_uuid)
            
            if not events:
                logger.warning("No events found for run", run_id=run_id)
                return {
                    "status": "completed",
                    "run_id": run_id,
                    "friction_issues": 0,
                    "overall_score": 0.0
                }
            
            # Convert events to analysis format
            event_data = []
            for event in events:
                event_data.append({
                    "type": event.event_type,
                    "timestamp": event.timestamp,
                    "payload": json.loads(event.payload_json)
                })
            
            # Analyze friction
            friction_issues = friction_heuristics.analyze_events(event_data)
            
            logger.info("Friction analysis completed", issues_found=len(friction_issues))
            
            # Calculate friction score
            friction_score = friction_scorer.calculate_friction_score(friction_issues)
            
            # Store friction issues in database
            friction_repo = FrictionRepository(session)
            
            stored_issues = []
            for issue in friction_issues:
                db_issue = FrictionIssue(
                    run_id=run_uuid,
                    friction_type=issue.type.value,
                    severity=issue.severity.value,
                    score=issue.score,
                    evidence_json=json.dumps(issue.evidence),
                    recommendation=issue.recommendation
                )
                
                stored_issue = await friction_repo.create(db_issue)
                stored_issues.append(str(stored_issue.id))
            
            logger.info("Friction issues stored", issues_stored=len(stored_issues))
            
            # Generate summary
            summary = {
                "status": "completed",
                "run_id": run_id,
                "total_events": len(events),
                "friction_issues": len(friction_issues),
                "overall_score": friction_score.overall_score,
                "severity_distribution": friction_score.severity_distribution,
                "type_distribution": friction_score.type_distribution,
                "critical_issues": len(friction_score.critical_issues),
                "recommendations": friction_score.recommendations,
                "stored_issue_ids": stored_issues
            }
            
            logger.info("Run post-processing completed", run_id=run_id, overall_score=friction_score.overall_score)
            
            return summary
            
        except Exception as e:
            logger.error("Run post-processing failed", run_id=run_id, error=str(e))
            raise


def post_process_run(run_id: str) -> Dict[str, Any]:
    """RQ job wrapper for run post-processing."""
    return asyncio.run(post_process_run_task(run_id))
