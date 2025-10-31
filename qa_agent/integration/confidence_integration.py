"""
Confidence Scoring Integration Helper

This module provides easy integration of the confidence scoring system
with the existing QA Agent backend.
"""
import os
import asyncio
from typing import Optional

try:
    from browser_use import Agent as BrowserAgent, ChatGoogle
except ImportError:
    print("Warning: browser_use not installed")
    BrowserAgent = None
    ChatGoogle = None

from qa_agent.confident_browser_agent import ConfidentBrowserAgent, create_confident_agent
from qa_agent.confidence_scorer import (
    confidence_scorer,
    ConfidenceScore,
    ActionContext,
    ConfidenceLevel
)
from qa_agent.api.routes.approvals import request_user_approval
from qa_agent.core.logging import get_logger

logger = get_logger(__name__)


class ConfidenceIntegration:
    """
    Helper class to integrate confidence scoring with existing backend.

    This provides a drop-in replacement for the browser-use agent
    with confidence scoring enabled.
    """

    @staticmethod
    def create_approval_callback():
        """
        Create an approval callback that uses the API endpoint.

        This callback will be used by the ConfidentBrowserAgent to
        request user approval for critical actions.
        """
        async def approval_callback(confidence_score: ConfidenceScore, context: ActionContext, timeout: int):
            """Request approval via API endpoint."""
            try:
                approved = await request_user_approval(
                    action_description=context.action_description,
                    confidence_score=confidence_score.score,
                    confidence_level=confidence_score.level.value,
                    reasoning=confidence_score.reasoning,
                    risk_factors=confidence_score.risk_factors,
                    current_url=context.current_url,
                    element_text=context.element_text,
                    timeout_seconds=timeout
                )

                logger.info(
                    "User approval received",
                    approved=approved,
                    action=context.action_description
                )

                return approved

            except Exception as e:
                logger.error("Error requesting approval", error=str(e))
                # Default to deny on error
                return False

        return approval_callback

    @staticmethod
    def create_confident_browser_agent(
        task: str,
        ai_provider: str = "google",
        api_key: Optional[str] = None
    ) -> ConfidentBrowserAgent:
        """
        Create a ConfidentBrowserAgent with proper configuration.

        Args:
            task: The task to perform
            ai_provider: AI provider ("google", "openai", "anthropic")
            api_key: Optional API key (will use env vars if not provided)

        Returns:
            Configured ConfidentBrowserAgent
        """
        if BrowserAgent is None or ChatGoogle is None:
            raise ImportError("browser_use package not installed")

        # Get API key from environment if not provided
        if api_key is None:
            if ai_provider == "google":
                api_key = os.getenv("GOOGLE_API_KEY")
            elif ai_provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
            elif ai_provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")

        # Create LLM instance (currently only Google is supported in this example)
        if ai_provider == "google":
            llm = ChatGoogle(model="gemini-flash-latest", api_key=api_key)
        else:
            raise ValueError(f"AI provider '{ai_provider}' not supported yet")

        # Create approval callback
        approval_callback = ConfidenceIntegration.create_approval_callback()

        # Create confident agent
        agent = create_confident_agent(
            task=task,
            llm=llm,
            approval_callback=approval_callback,
            auto_approve_high_confidence=True,
            auto_approve_medium_confidence=True,
            log_all_actions=True
        )

        logger.info("Confident browser agent created", task=task, provider=ai_provider)

        return agent

    @staticmethod
    async def execute_task_with_confidence_scoring(
        task: str,
        ai_provider: str = "google",
        api_key: Optional[str] = None
    ) -> dict:
        """
        Execute a browser task with confidence scoring enabled.

        This is a drop-in replacement for the standard browser-use execution.

        Args:
            task: The task to perform
            ai_provider: AI provider to use
            api_key: Optional API key

        Returns:
            Dictionary with execution results and statistics
        """
        try:
            # Create confident agent
            agent = ConfidenceIntegration.create_confident_browser_agent(
                task=task,
                ai_provider=ai_provider,
                api_key=api_key
            )

            # Execute task
            logger.info("Starting task execution with confidence scoring", task=task)
            result = await agent.run()

            # Get statistics
            stats = agent.get_statistics()

            logger.info(
                "Task execution completed",
                total_actions=stats['total_actions'],
                approvals_requested=stats['total_approvals_requested']
            )

            return {
                'success': True,
                'result': result,
                'statistics': stats,
                'action_history': agent.get_action_history(),
                'approval_history': agent.get_approval_history()
            }

        except Exception as e:
            logger.error("Task execution failed", error=str(e))
            return {
                'success': False,
                'error': str(e)
            }


# Convenience functions for easy integration

async def execute_with_confidence(task: str, ai_provider: str = "google") -> dict:
    """
    Convenience function to execute a task with confidence scoring.

    Usage:
        result = await execute_with_confidence("Go to example.com and click login")
    """
    return await ConfidenceIntegration.execute_task_with_confidence(task, ai_provider)


def enable_confidence_scoring_globally():
    """
    Enable confidence scoring globally for all browser-use agents.

    This modifies the default behavior to include confidence scoring.
    Call this once at application startup.
    """
    logger.info("Confidence scoring enabled globally")

    # Set up approval callback globally
    approval_callback = ConfidenceIntegration.create_approval_callback()
    confidence_scorer.set_approval_callback(approval_callback)


# Example usage
async def example_usage():
    """
    Example of how to use the confidence scoring integration.
    """
    # Enable confidence scoring globally
    enable_confidence_scoring_globally()

    # Execute a task with confidence scoring
    task = "Go to https://example.com and click on 'About' link"

    result = await execute_with_confidence(task, ai_provider="google")

    if result['success']:
        print("Task completed successfully!")
        print(f"Statistics: {result['statistics']}")
        print(f"Total actions: {result['statistics']['total_actions']}")
        print(f"Approvals requested: {result['statistics']['total_approvals_requested']}")
    else:
        print(f"Task failed: {result['error']}")


if __name__ == "__main__":
    asyncio.run(example_usage())
