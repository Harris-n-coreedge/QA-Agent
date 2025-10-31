"""
Task Confidence Checker - Pre-Execution Analysis

Analyzes the entire task BEFORE execution and prompts for approval
if critical operations are detected. This is a simpler, working approach
that doesn't require intercepting individual actions.
"""
import re
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum


class TaskRiskLevel(Enum):
    """Risk levels for tasks."""
    SAFE = "safe"           # Execute without approval
    MODERATE = "moderate"   # Execute with warning
    RISKY = "risky"        # Prompt for approval
    CRITICAL = "critical"   # Strong warning + approval


@dataclass
class TaskAnalysis:
    """Analysis result for a task."""
    risk_level: TaskRiskLevel
    confidence_score: float  # 0-100
    detected_operations: List[str]
    risk_factors: List[str]
    recommendation: str
    requires_approval: bool


class TaskConfidenceChecker:
    """
    Analyzes task descriptions before execution to detect critical operations.

    This works by analyzing the natural language task description for
    patterns that indicate risky operations (purchases, deletions, etc.).
    """

    def __init__(self):
        # Critical operation patterns
        self.critical_patterns = {
            'purchase': {
                'keywords': ['buy', 'purchase', 'complete order', 'place order',
                           'confirm purchase', 'complete checkout', 'pay now',
                           'submit payment', 'finalize order', 'complete payment'],
                'weight': 1.0,
                'description': 'Purchase/Payment operation'
            },
            'checkout': {
                'keywords': ['checkout', 'proceed to checkout', 'go to checkout',
                           'click checkout', 'billing', 'payment details'],
                'weight': 0.9,
                'description': 'Checkout process'
            },
            'delete': {
                'keywords': ['delete', 'remove account', 'close account',
                           'cancel subscription', 'terminate', 'deactivate account',
                           'permanently delete', 'erase'],
                'weight': 0.95,
                'description': 'Delete/Remove operation'
            },
            'payment': {
                'keywords': ['enter card', 'credit card', 'debit card',
                           'card number', 'cvv', 'card details', 'payment method',
                           'add payment', 'enter payment'],
                'weight': 1.0,
                'description': 'Payment information entry'
            },
            'transfer': {
                'keywords': ['transfer money', 'send money', 'wire transfer',
                           'send payment', 'transfer funds'],
                'weight': 1.0,
                'description': 'Money transfer'
            },
            'submit_form': {
                'keywords': ['submit form', 'send form', 'submit application',
                           'submit order', 'submit request'],
                'weight': 0.6,
                'description': 'Form submission'
            },
            'download_install': {
                'keywords': ['download', 'install', 'download file',
                           'save file', 'install software'],
                'weight': 0.5,
                'description': 'Download/Install operation'
            }
        }

        # Moderate risk patterns
        self.moderate_patterns = {
            'login': ['login', 'sign in', 'log in'],
            'register': ['register', 'sign up', 'create account'],
            'modify': ['edit', 'update', 'change', 'modify']
        }

    def analyze_task(self, task: str) -> TaskAnalysis:
        """
        Analyze a task description for risk level.

        Args:
            task: The task description to analyze

        Returns:
            TaskAnalysis with risk assessment
        """
        task_lower = task.lower()
        detected_operations = []
        risk_factors = []
        total_risk_score = 0.0

        # Check for critical patterns
        for operation, config in self.critical_patterns.items():
            for keyword in config['keywords']:
                if keyword in task_lower:
                    detected_operations.append(config['description'])
                    risk_factors.append(f"Detected: '{keyword}' ({config['description']})")
                    total_risk_score += config['weight']
                    break  # Only count once per operation type

        # Check for moderate patterns
        for operation, keywords in self.moderate_patterns.items():
            for keyword in keywords:
                if keyword in task_lower:
                    detected_operations.append(f"{operation.title()} operation")
                    risk_factors.append(f"Detected: '{keyword}'")
                    total_risk_score += 0.3
                    break

        # Additional risk indicators
        if any(word in task_lower for word in ['confirm', 'final', 'complete']):
            if total_risk_score > 0.5:  # Already risky
                total_risk_score += 0.2
                risk_factors.append("Confirmation language detected")

        # Calculate confidence score (inverse of risk)
        confidence_score = max(0, 100 - (total_risk_score * 50))

        # Determine risk level
        if total_risk_score >= 0.9:
            risk_level = TaskRiskLevel.CRITICAL
            requires_approval = True
            recommendation = "CRITICAL: This task involves high-risk operations. Strong approval recommended."
        elif total_risk_score >= 0.6:
            risk_level = TaskRiskLevel.RISKY
            requires_approval = True
            recommendation = "RISKY: This task may perform critical operations. Approval required."
        elif total_risk_score >= 0.3:
            risk_level = TaskRiskLevel.MODERATE
            requires_approval = False
            recommendation = "MODERATE: Task involves some sensitive operations. Proceed with caution."
        else:
            risk_level = TaskRiskLevel.SAFE
            requires_approval = False
            recommendation = "SAFE: No critical operations detected. Safe to execute."

        return TaskAnalysis(
            risk_level=risk_level,
            confidence_score=confidence_score,
            detected_operations=list(set(detected_operations)),  # Remove duplicates
            risk_factors=risk_factors,
            recommendation=recommendation,
            requires_approval=requires_approval
        )

    def should_prompt_for_approval(self, task: str) -> Tuple[bool, TaskAnalysis]:
        """
        Check if a task should prompt for approval.

        Args:
            task: The task description

        Returns:
            Tuple of (should_prompt: bool, analysis: TaskAnalysis)
        """
        analysis = self.analyze_task(task)
        return (analysis.requires_approval, analysis)

    def get_approval_message(self, analysis: TaskAnalysis, task: str) -> str:
        """
        Generate a user-friendly approval message.

        Args:
            analysis: The task analysis
            task: The original task

        Returns:
            Formatted approval message
        """
        message = f"""
╔══════════════════════════════════════════════════════════════╗
║                  ⚠️  APPROVAL REQUIRED  ⚠️                   ║
╚══════════════════════════════════════════════════════════════╝

RISK LEVEL: {analysis.risk_level.value.upper()}
CONFIDENCE: {analysis.confidence_score:.0f}%

TASK:
{task}

DETECTED OPERATIONS:
"""
        for op in analysis.detected_operations:
            message += f"  • {op}\n"

        message += f"\nRISK FACTORS:\n"
        for factor in analysis.risk_factors:
            message += f"  • {factor}\n"

        message += f"\nRECOMMENDATION:\n{analysis.recommendation}\n"
        message += f"\n{'='*62}\n"
        message += "Do you want to proceed with this task? (yes/no): "

        return message


# Global instance
task_confidence_checker = TaskConfidenceChecker()


# Testing
if __name__ == "__main__":
    checker = TaskConfidenceChecker()

    test_tasks = [
        "Go to example.com and click on About link",
        "Go to amazon.com and add iPhone to cart",
        "Go to wisemarket.com.pk, add product to cart, and complete the checkout",
        "Login to the website and delete my account",
        "Go to the website, enter credit card details, and submit payment"
    ]

    print("Testing Task Confidence Checker")
    print("=" * 70)

    for task in test_tasks:
        print(f"\nTASK: {task}")
        print("-" * 70)
        analysis = checker.analyze_task(task)
        print(f"Risk Level: {analysis.risk_level.value.upper()}")
        print(f"Confidence: {analysis.confidence_score:.0f}%")
        print(f"Requires Approval: {analysis.requires_approval}")
        print(f"Operations: {', '.join(analysis.detected_operations)}")
        print(f"Recommendation: {analysis.recommendation}")
        print()
