"""
Lightweight Confidence Scoring System for Browser Automation

This module provides confidence scoring for browser actions to prevent
unintended critical operations. When the model feels uncertain about an action,
it flags it for user review before execution.
"""
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
import re
import asyncio


class ConfidenceLevel(Enum):
    """Confidence levels for actions."""
    HIGH = "high"           # 0.8 - 1.0: Execute automatically
    MEDIUM = "medium"       # 0.6 - 0.79: Execute with logging
    LOW = "low"            # 0.4 - 0.59: Flag for review (optional approval)
    CRITICAL = "critical"   # 0.0 - 0.39: Require user approval


class ActionType(Enum):
    """Types of browser actions."""
    NAVIGATE = "navigate"
    CLICK = "click"
    INPUT = "input"
    SUBMIT = "submit"
    DELETE = "delete"
    PURCHASE = "purchase"
    PAYMENT = "payment"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    UNKNOWN = "unknown"


@dataclass
class ConfidenceScore:
    """Represents a confidence score for an action."""
    score: float  # 0.0 to 1.0
    level: ConfidenceLevel
    action_type: ActionType
    reasoning: str
    requires_approval: bool
    risk_factors: List[str]


@dataclass
class ActionContext:
    """Context information for an action."""
    action_description: str
    current_url: Optional[str] = None
    element_text: Optional[str] = None
    element_selector: Optional[str] = None
    page_content: Optional[str] = None
    previous_actions: Optional[List[str]] = None


class ConfidenceScorer:
    """
    Calculates confidence scores for browser automation actions.

    Identifies critical operations that require user approval before execution.
    """

    def __init__(self):
        # Critical keywords that indicate high-risk operations
        self.critical_keywords = {
            'purchase': ['buy', 'purchase', 'checkout', 'place order', 'confirm order',
                        'complete purchase', 'pay now', 'submit payment'],
            'payment': ['payment', 'credit card', 'debit card', 'billing', 'card number',
                       'cvv', 'card details', 'payment method'],
            'delete': ['delete', 'remove', 'cancel', 'terminate', 'deactivate',
                      'close account', 'unsubscribe permanently'],
            'transfer': ['transfer', 'send money', 'wire', 'remit'],
            'submit': ['submit', 'send', 'post', 'publish', 'share publicly'],
            'download': ['download', 'install', 'get app'],
            'upload': ['upload', 'attach file', 'choose file'],
            'irreversible': ['permanent', 'irreversible', 'cannot be undone',
                           'final', 'no refund']
        }

        # Medium-risk keywords
        self.medium_risk_keywords = {
            'login': ['login', 'sign in', 'authenticate'],
            'register': ['register', 'sign up', 'create account'],
            'modify': ['edit', 'update', 'change', 'modify'],
            'navigation': ['navigate', 'go to', 'open']
        }

        # URL patterns that indicate critical pages
        self.critical_url_patterns = [
            r'checkout', r'payment', r'billing', r'cart/confirm',
            r'purchase', r'order/confirm', r'/pay', r'transaction'
        ]

        # User approval callback (can be set externally)
        self.approval_callback: Optional[Callable] = None

    def calculate_confidence(self, context: ActionContext) -> ConfidenceScore:
        """
        Calculate confidence score for an action.

        Args:
            context: Action context information

        Returns:
            ConfidenceScore with detailed reasoning
        """
        action_description = context.action_description.lower()
        current_url = (context.current_url or "").lower()
        element_text = (context.element_text or "").lower()

        # Determine action type
        action_type = self._classify_action(action_description, element_text)

        # Initialize score (start with high confidence)
        base_score = 0.9
        risk_factors = []

        # Check for critical keywords in action
        for category, keywords in self.critical_keywords.items():
            if any(keyword in action_description or keyword in element_text
                   for keyword in keywords):
                base_score -= 0.4
                risk_factors.append(f"Critical operation detected: {category}")

        # Check for critical URL patterns
        for pattern in self.critical_url_patterns:
            if re.search(pattern, current_url):
                base_score -= 0.3
                risk_factors.append(f"On critical page: {pattern}")

        # Check for medium-risk keywords
        for category, keywords in self.medium_risk_keywords.items():
            if any(keyword in action_description for keyword in keywords):
                base_score -= 0.15
                risk_factors.append(f"Medium-risk operation: {category}")

        # Special case: Payment or purchase actions
        if action_type in [ActionType.PAYMENT, ActionType.PURCHASE]:
            base_score = min(base_score, 0.3)  # Force critical level
            risk_factors.append("Financial transaction detected")

        # Special case: Delete actions
        if action_type == ActionType.DELETE:
            base_score = min(base_score, 0.4)
            risk_factors.append("Destructive operation detected")

        # Check for uncertainty indicators in the action description
        uncertainty_keywords = ['maybe', 'might', 'possibly', 'uncertain',
                               'not sure', 'probably', 'seems like']
        if any(keyword in action_description for keyword in uncertainty_keywords):
            base_score -= 0.2
            risk_factors.append("Uncertain action description")

        # Ensure score is within bounds
        final_score = max(0.0, min(1.0, base_score))

        # Determine confidence level
        confidence_level = self._score_to_level(final_score)

        # Determine if approval is required
        requires_approval = confidence_level in [ConfidenceLevel.CRITICAL, ConfidenceLevel.LOW]

        # Generate reasoning
        reasoning = self._generate_reasoning(
            action_type, confidence_level, risk_factors, final_score
        )

        return ConfidenceScore(
            score=final_score,
            level=confidence_level,
            action_type=action_type,
            reasoning=reasoning,
            requires_approval=requires_approval,
            risk_factors=risk_factors
        )

    def _classify_action(self, action_description: str, element_text: str) -> ActionType:
        """Classify the type of action being performed."""
        action_lower = action_description.lower()
        element_lower = element_text.lower()

        # Check for specific action types
        if any(word in action_lower for word in ['navigate', 'go to', 'open', 'visit']):
            return ActionType.NAVIGATE

        if any(word in action_lower or word in element_lower
               for word in self.critical_keywords['payment']):
            return ActionType.PAYMENT

        if any(word in action_lower or word in element_lower
               for word in self.critical_keywords['purchase']):
            return ActionType.PURCHASE

        if any(word in action_lower or word in element_lower
               for word in self.critical_keywords['delete']):
            return ActionType.DELETE

        if any(word in action_lower for word in ['submit', 'send form', 'post']):
            return ActionType.SUBMIT

        if any(word in action_lower for word in ['click', 'press', 'tap']):
            return ActionType.CLICK

        if any(word in action_lower for word in ['type', 'input', 'enter', 'fill']):
            return ActionType.INPUT

        if any(word in action_lower for word in ['download', 'get file']):
            return ActionType.DOWNLOAD

        if any(word in action_lower for word in ['upload', 'attach']):
            return ActionType.UPLOAD

        return ActionType.UNKNOWN

    def _score_to_level(self, score: float) -> ConfidenceLevel:
        """Convert numerical score to confidence level."""
        if score >= 0.8:
            return ConfidenceLevel.HIGH
        elif score >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.CRITICAL

    def _generate_reasoning(
        self,
        action_type: ActionType,
        level: ConfidenceLevel,
        risk_factors: List[str],
        score: float
    ) -> str:
        """Generate human-readable reasoning for the confidence score."""
        if level == ConfidenceLevel.HIGH:
            return f"High confidence ({score:.2f}). Standard {action_type.value} action with no critical risks."

        elif level == ConfidenceLevel.MEDIUM:
            return f"Medium confidence ({score:.2f}). {action_type.value} action. " + \
                   (f"Risks: {', '.join(risk_factors[:2])}" if risk_factors else "Minor risks detected.")

        elif level == ConfidenceLevel.LOW:
            risks_text = ', '.join(risk_factors[:3]) if risk_factors else "Uncertain operation"
            return f"Low confidence ({score:.2f}). {action_type.value} action flagged. {risks_text}. Review recommended."

        else:  # CRITICAL
            risks_text = ', '.join(risk_factors) if risk_factors else "Critical operation"
            return f"Critical ({score:.2f}). {action_type.value} requires approval. {risks_text}."

    async def request_approval(
        self,
        confidence_score: ConfidenceScore,
        context: ActionContext,
        timeout: int = 60
    ) -> bool:
        """
        Request user approval for an action.

        Args:
            confidence_score: The calculated confidence score
            context: Action context
            timeout: Timeout in seconds (default 60)

        Returns:
            True if approved, False if denied or timeout
        """
        if self.approval_callback:
            try:
                # Call the custom approval callback
                approved = await self.approval_callback(
                    confidence_score=confidence_score,
                    context=context,
                    timeout=timeout
                )
                return approved
            except Exception as e:
                print(f"Error in approval callback: {e}")
                return False
        else:
            # Fallback: Return False for critical actions without callback
            print(f"\n{'='*60}")
            print(f"⚠️  USER APPROVAL REQUIRED")
            print(f"{'='*60}")
            print(f"Action: {context.action_description}")
            print(f"Confidence: {confidence_score.level.value.upper()} ({confidence_score.score:.2f})")
            print(f"Reasoning: {confidence_score.reasoning}")
            if confidence_score.risk_factors:
                print(f"Risk Factors:")
                for factor in confidence_score.risk_factors:
                    print(f"  • {factor}")
            if context.current_url:
                print(f"Current URL: {context.current_url}")
            print(f"{'='*60}")
            print("⚠️  No approval callback configured. Action blocked by default.")
            print(f"{'='*60}\n")
            return False

    def set_approval_callback(self, callback: Callable):
        """Set a custom approval callback function."""
        self.approval_callback = callback

    def should_auto_execute(self, confidence_score: ConfidenceScore) -> bool:
        """Determine if action should execute automatically without approval."""
        return confidence_score.level in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM]


# Global confidence scorer instance
confidence_scorer = ConfidenceScorer()


# Example usage function
async def evaluate_action_example():
    """Example of how to use the confidence scorer."""

    # Example 1: Safe action
    safe_context = ActionContext(
        action_description="Click on the 'About Us' link",
        current_url="https://example.com/home",
        element_text="About Us"
    )
    safe_score = confidence_scorer.calculate_confidence(safe_context)
    print(f"Safe Action: {safe_score.level.value} - {safe_score.reasoning}")

    # Example 2: Critical action
    critical_context = ActionContext(
        action_description="Click on 'Complete Purchase' button",
        current_url="https://example.com/checkout",
        element_text="Complete Purchase - $299.99"
    )
    critical_score = confidence_scorer.calculate_confidence(critical_context)
    print(f"\nCritical Action: {critical_score.level.value} - {critical_score.reasoning}")

    if critical_score.requires_approval:
        print("⚠️  This action requires user approval!")
        # In real implementation, this would trigger UI approval dialog
        approved = await confidence_scorer.request_approval(critical_score, critical_context)
        print(f"Approved: {approved}")


if __name__ == "__main__":
    # Run example
    asyncio.run(evaluate_action_example())
