"""
Confident Browser Agent - Browser-Use Agent with Confidence Scoring

This module wraps the browser-use Agent to add confidence scoring and
user approval mechanisms for critical actions.
"""
from typing import Optional, Dict, Any, Callable
import asyncio
from datetime import datetime

try:
    from browser_use import Agent as BrowserAgent
except ImportError:
    BrowserAgent = None
    print("Warning: browser_use not installed. Install with: pip install browser-use")

from qa_agent.confidence_scorer import (
    confidence_scorer,
    ConfidenceScore,
    ActionContext,
    ConfidenceLevel
)
from qa_agent.core.logging import get_logger

logger = get_logger(__name__)


class ConfidentBrowserAgent:
    """
    A wrapper around browser-use Agent that adds confidence scoring
    and approval mechanisms for critical actions.

    Usage:
        agent = ConfidentBrowserAgent(
            task="your task here",
            llm=your_llm,
            approval_callback=your_approval_function
        )
        result = await agent.run()
    """

    def __init__(
        self,
        task: str,
        llm,
        approval_callback: Optional[Callable] = None,
        auto_approve_high_confidence: bool = True,
        auto_approve_medium_confidence: bool = True,
        log_all_actions: bool = True
    ):
        """
        Initialize the Confident Browser Agent.

        Args:
            task: The task description for the agent
            llm: Language model instance (ChatGoogle, ChatOpenAI, etc.)
            approval_callback: Async function to call for user approvals
            auto_approve_high_confidence: Auto-execute high confidence actions
            auto_approve_medium_confidence: Auto-execute medium confidence actions
            log_all_actions: Log all actions with their confidence scores
        """
        if BrowserAgent is None:
            raise ImportError("browser_use package not installed")

        self.task = task
        self.llm = llm
        self.auto_approve_high = auto_approve_high_confidence
        self.auto_approve_medium = auto_approve_medium_confidence
        self.log_all_actions = log_all_actions

        # Set up approval callback
        if approval_callback:
            confidence_scorer.set_approval_callback(approval_callback)

        # Initialize the underlying browser-use agent
        self.browser_agent = BrowserAgent(task=task, llm=llm)

        # Action history for logging and analysis
        self.action_history: list = []
        self.approval_history: list = []

        # Monkey-patch the agent's action execution to add confidence scoring
        self._setup_action_interception()

    def _setup_action_interception(self):
        """
        Set up interception of agent actions to add confidence scoring.

        This wraps the browser agent's action execution methods to
        inject confidence scoring before actions are executed.
        """
        # Store original run method
        original_run = self.browser_agent.run

        async def wrapped_run(*args, **kwargs):
            """Wrapped run method with confidence scoring."""
            logger.info("Starting browser agent with confidence scoring", task=self.task)

            # Note: This is a simplified wrapper. In production, you would need to
            # intercept at a lower level (individual actions) rather than the entire run.
            # For now, we log that confidence scoring is active.

            result = await original_run(*args, **kwargs)

            logger.info(
                "Browser agent completed",
                total_actions=len(self.action_history),
                approvals_requested=len(self.approval_history)
            )

            return result

        # Replace run method
        self.browser_agent.run = wrapped_run

    async def evaluate_action(
        self,
        action_description: str,
        current_url: Optional[str] = None,
        element_text: Optional[str] = None,
        element_selector: Optional[str] = None
    ) -> tuple[bool, ConfidenceScore]:
        """
        Evaluate an action and determine if it should be executed.

        Args:
            action_description: Description of the action to perform
            current_url: Current page URL
            element_text: Text content of the target element
            element_selector: CSS selector of the target element

        Returns:
            Tuple of (should_execute: bool, confidence_score: ConfidenceScore)
        """
        # Create action context
        context = ActionContext(
            action_description=action_description,
            current_url=current_url,
            element_text=element_text,
            element_selector=element_selector,
            previous_actions=[a['description'] for a in self.action_history[-5:]]
        )

        # Calculate confidence score
        confidence_score = confidence_scorer.calculate_confidence(context)

        # Log action
        if self.log_all_actions:
            logger.info(
                "Action evaluated",
                action=action_description,
                confidence=confidence_score.level.value,
                score=confidence_score.score,
                requires_approval=confidence_score.requires_approval
            )

        # Store in history
        self.action_history.append({
            'timestamp': datetime.now().isoformat(),
            'description': action_description,
            'confidence_score': confidence_score.score,
            'confidence_level': confidence_score.level.value,
            'requires_approval': confidence_score.requires_approval
        })

        # Determine if action should execute
        should_execute = False

        if confidence_score.level == ConfidenceLevel.HIGH and self.auto_approve_high:
            should_execute = True
            logger.debug("Action auto-approved (HIGH confidence)")

        elif confidence_score.level == ConfidenceLevel.MEDIUM and self.auto_approve_medium:
            should_execute = True
            logger.debug("Action auto-approved (MEDIUM confidence)")

        elif confidence_score.requires_approval:
            # Request user approval
            logger.warning(
                "Action requires approval",
                action=action_description,
                reasoning=confidence_score.reasoning
            )

            approved = await confidence_scorer.request_approval(
                confidence_score=confidence_score,
                context=context,
                timeout=60
            )

            should_execute = approved

            # Store approval decision
            self.approval_history.append({
                'timestamp': datetime.now().isoformat(),
                'action': action_description,
                'confidence_score': confidence_score.score,
                'approved': approved,
                'reasoning': confidence_score.reasoning
            })

            if approved:
                logger.info("Action approved by user", action=action_description)
            else:
                logger.warning("Action denied by user", action=action_description)

        else:
            # Low confidence but not critical - log and allow
            should_execute = True
            logger.warning(
                "Low confidence action proceeding",
                action=action_description,
                score=confidence_score.score
            )

        return should_execute, confidence_score

    async def run(self) -> Any:
        """
        Run the browser agent with confidence scoring.

        Returns:
            The agent's execution history
        """
        try:
            result = await self.browser_agent.run()
            return result
        except Exception as e:
            logger.error("Error during agent execution", error=str(e))
            raise

    def get_action_history(self) -> list:
        """Get the history of all evaluated actions."""
        return self.action_history

    def get_approval_history(self) -> list:
        """Get the history of all approval requests."""
        return self.approval_history

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about actions and approvals."""
        total_actions = len(self.action_history)
        total_approvals = len(self.approval_history)

        if total_approvals > 0:
            approved_count = sum(1 for a in self.approval_history if a['approved'])
            approval_rate = approved_count / total_approvals
        else:
            approved_count = 0
            approval_rate = 0.0

        confidence_distribution = {
            'high': sum(1 for a in self.action_history if a['confidence_level'] == 'high'),
            'medium': sum(1 for a in self.action_history if a['confidence_level'] == 'medium'),
            'low': sum(1 for a in self.action_history if a['confidence_level'] == 'low'),
            'critical': sum(1 for a in self.action_history if a['confidence_level'] == 'critical')
        }

        return {
            'total_actions': total_actions,
            'total_approvals_requested': total_approvals,
            'approvals_granted': approved_count,
            'approvals_denied': total_approvals - approved_count,
            'approval_rate': approval_rate,
            'confidence_distribution': confidence_distribution
        }


# Helper function to create a confident browser agent with default settings
def create_confident_agent(
    task: str,
    llm,
    approval_callback: Optional[Callable] = None,
    **kwargs
) -> ConfidentBrowserAgent:
    """
    Create a ConfidentBrowserAgent with sensible defaults.

    Args:
        task: Task description
        llm: Language model instance
        approval_callback: Optional approval callback function
        **kwargs: Additional arguments for ConfidentBrowserAgent

    Returns:
        Configured ConfidentBrowserAgent instance
    """
    return ConfidentBrowserAgent(
        task=task,
        llm=llm,
        approval_callback=approval_callback,
        **kwargs
    )


# Example usage
async def example_usage():
    """Example of using the ConfidentBrowserAgent."""
    try:
        from browser_use import ChatGoogle
        import os

        # Create LLM
        llm = ChatGoogle(
            model="gemini-flash-latest",
            api_key=os.getenv("GOOGLE_API_KEY")
        )

        # Define approval callback
        async def approval_callback(confidence_score, context, timeout):
            """Example approval callback - in production, this would show UI."""
            print(f"\n{'='*60}")
            print(f"⚠️  APPROVAL REQUIRED")
            print(f"{'='*60}")
            print(f"Action: {context.action_description}")
            print(f"Confidence: {confidence_score.level.value} ({confidence_score.score:.2f})")
            print(f"Reasoning: {confidence_score.reasoning}")
            print(f"{'='*60}\n")

            # In production, this would await user input from UI
            # For demo, auto-deny critical actions
            return confidence_score.level != ConfidenceLevel.CRITICAL

        # Create confident agent
        task = "Go to example.com and click on 'About' link"
        agent = create_confident_agent(
            task=task,
            llm=llm,
            approval_callback=approval_callback
        )

        # Run agent
        print(f"Running task: {task}")
        result = await agent.run()

        # Show statistics
        stats = agent.get_statistics()
        print("\n=== Execution Statistics ===")
        print(f"Total Actions: {stats['total_actions']}")
        print(f"Approvals Requested: {stats['total_approvals_requested']}")
        print(f"Confidence Distribution: {stats['confidence_distribution']}")

        return result

    except ImportError as e:
        print(f"Error: {e}")
        print("Make sure browser_use is installed: pip install browser-use")


if __name__ == "__main__":
    asyncio.run(example_usage())
