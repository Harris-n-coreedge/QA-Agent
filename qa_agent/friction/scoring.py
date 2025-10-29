"""
Friction scoring and aggregation.
"""
from typing import List, Dict, Any
from dataclasses import dataclass
import statistics

from qa_agent.friction.heuristics import FrictionIssue, FrictionSeverity, FrictionType


@dataclass
class FrictionScore:
    """Aggregated friction score."""
    overall_score: float
    severity_distribution: Dict[FrictionSeverity, int]
    type_distribution: Dict[FrictionType, int]
    critical_issues: List[FrictionIssue]
    recommendations: List[str]


class FrictionScorer:
    """Calculates and aggregates friction scores."""
    
    def __init__(self):
        self.weights = {
            FrictionType.LONG_DWELL: 0.2,
            FrictionType.RAGE_CLICK: 0.25,
            FrictionType.VALIDATION_LOOP: 0.3,
            FrictionType.CONSOLE_ERROR: 0.15,
            FrictionType.NETWORK_ERROR: 0.2,
            FrictionType.VISUAL_INSTABILITY: 0.1,
            FrictionType.BACKTRACK: 0.1
        }
        
        self.severity_weights = {
            FrictionSeverity.CRITICAL: 1.0,
            FrictionSeverity.HIGH: 0.7,
            FrictionSeverity.MEDIUM: 0.4,
            FrictionSeverity.LOW: 0.1
        }
    
    def calculate_friction_score(self, issues: List[FrictionIssue]) -> FrictionScore:
        """Calculate overall friction score from issues."""
        if not issues:
            return FrictionScore(
                overall_score=0.0,
                severity_distribution={},
                type_distribution={},
                critical_issues=[],
                recommendations=[]
            )
        
        # Calculate weighted score
        weighted_scores = []
        for issue in issues:
            type_weight = self.weights.get(issue.type, 0.1)
            severity_weight = self.severity_weights.get(issue.severity, 0.1)
            weighted_score = issue.score * type_weight * severity_weight
            weighted_scores.append(weighted_score)
        
        # Calculate overall score (0-100)
        overall_score = min(sum(weighted_scores) * 100, 100)
        
        # Calculate distributions
        severity_distribution = self._calculate_severity_distribution(issues)
        type_distribution = self._calculate_type_distribution(issues)
        
        # Get critical issues
        critical_issues = [issue for issue in issues if issue.severity == FrictionSeverity.CRITICAL]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(issues)
        
        return FrictionScore(
            overall_score=overall_score,
            severity_distribution=severity_distribution,
            type_distribution=type_distribution,
            critical_issues=critical_issues,
            recommendations=recommendations
        )
    
    def _calculate_severity_distribution(self, issues: List[FrictionIssue]) -> Dict[FrictionSeverity, int]:
        """Calculate distribution of issues by severity."""
        distribution = {severity: 0 for severity in FrictionSeverity}
        
        for issue in issues:
            distribution[issue.severity] += 1
        
        return distribution
    
    def _calculate_type_distribution(self, issues: List[FrictionIssue]) -> Dict[FrictionType, int]:
        """Calculate distribution of issues by type."""
        distribution = {friction_type: 0 for friction_type in FrictionType}
        
        for issue in issues:
            distribution[issue.type] += 1
        
        return distribution
    
    def _generate_recommendations(self, issues: List[FrictionIssue]) -> List[str]:
        """Generate actionable recommendations from issues."""
        recommendations = []
        
        # Group issues by type for better recommendations
        issues_by_type = {}
        for issue in issues:
            if issue.type not in issues_by_type:
                issues_by_type[issue.type] = []
            issues_by_type[issue.type].append(issue)
        
        # Generate type-specific recommendations
        for friction_type, type_issues in issues_by_type.items():
            if friction_type == FrictionType.LONG_DWELL:
                avg_dwell = statistics.mean([issue.score * 30 for issue in type_issues])  # Convert back to seconds
                recommendations.append(f"Optimize page loading performance. Average dwell time is {avg_dwell:.1f}s")
            
            elif friction_type == FrictionType.RAGE_CLICK:
                recommendations.append("Improve element responsiveness and visual feedback for clickable elements")
            
            elif friction_type == FrictionType.VALIDATION_LOOP:
                recommendations.append("Enhance form validation with clearer error messages and real-time feedback")
            
            elif friction_type == FrictionType.CONSOLE_ERROR:
                recommendations.append("Fix JavaScript errors to improve user experience and functionality")
            
            elif friction_type == FrictionType.NETWORK_ERROR:
                recommendations.append("Investigate and fix API endpoints and network connectivity issues")
            
            elif friction_type == FrictionType.VISUAL_INSTABILITY:
                recommendations.append("Optimize page layout and loading to reduce layout shifts")
            
            elif friction_type == FrictionType.BACKTRACK:
                recommendations.append("Improve navigation flow and user guidance")
        
        # Add general recommendations based on overall score
        if len(issues) > 10:
            recommendations.append("Consider conducting a comprehensive UX audit")
        
        if any(issue.severity == FrictionSeverity.CRITICAL for issue in issues):
            recommendations.append("Address critical issues immediately to prevent user abandonment")
        
        return recommendations
    
    def get_friction_trend(self, historical_scores: List[float]) -> Dict[str, Any]:
        """Analyze friction score trends over time."""
        if len(historical_scores) < 2:
            return {"trend": "insufficient_data", "change": 0}
        
        # Calculate trend
        recent_avg = statistics.mean(historical_scores[-3:]) if len(historical_scores) >= 3 else historical_scores[-1]
        older_avg = statistics.mean(historical_scores[:-3]) if len(historical_scores) > 3 else historical_scores[0]
        
        change = recent_avg - older_avg
        change_percent = (change / older_avg * 100) if older_avg > 0 else 0
        
        if abs(change_percent) < 5:
            trend = "stable"
        elif change_percent > 0:
            trend = "worsening"
        else:
            trend = "improving"
        
        return {
            "trend": trend,
            "change": change,
            "change_percent": change_percent,
            "current_score": recent_avg,
            "previous_score": older_avg
        }
    
    def compare_with_baseline(self, current_score: float, baseline_score: float) -> Dict[str, Any]:
        """Compare current score with baseline."""
        difference = current_score - baseline_score
        difference_percent = (difference / baseline_score * 100) if baseline_score > 0 else 0
        
        if abs(difference_percent) < 10:
            status = "within_baseline"
        elif difference_percent > 0:
            status = "above_baseline"
        else:
            status = "below_baseline"
        
        return {
            "status": status,
            "difference": difference,
            "difference_percent": difference_percent,
            "current_score": current_score,
            "baseline_score": baseline_score
        }
    
    def get_priority_actions(self, issues: List[FrictionIssue]) -> List[Dict[str, Any]]:
        """Get prioritized list of actions based on impact."""
        # Calculate impact score for each issue type
        impact_scores = {}
        
        for issue in issues:
            if issue.type not in impact_scores:
                impact_scores[issue.type] = 0
            
            # Impact = frequency * severity * type_weight
            frequency = 1  # Could be calculated from multiple occurrences
            severity_multiplier = self.severity_weights.get(issue.severity, 0.1)
            type_weight = self.weights.get(issue.type, 0.1)
            
            impact_scores[issue.type] += frequency * severity_multiplier * type_weight
        
        # Sort by impact
        sorted_actions = sorted(impact_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Generate action items
        actions = []
        for friction_type, impact in sorted_actions:
            actions.append({
                "type": friction_type.value,
                "impact_score": impact,
                "priority": "high" if impact > 0.5 else "medium" if impact > 0.2 else "low",
                "action": self._get_action_for_type(friction_type)
            })
        
        return actions
    
    def _get_action_for_type(self, friction_type: FrictionType) -> str:
        """Get recommended action for friction type."""
        actions = {
            FrictionType.LONG_DWELL: "Optimize page loading and performance",
            FrictionType.RAGE_CLICK: "Improve element responsiveness and feedback",
            FrictionType.VALIDATION_LOOP: "Enhance form validation and error handling",
            FrictionType.CONSOLE_ERROR: "Fix JavaScript errors and exceptions",
            FrictionType.NETWORK_ERROR: "Investigate and fix network issues",
            FrictionType.VISUAL_INSTABILITY: "Optimize layout and reduce shifts",
            FrictionType.BACKTRACK: "Improve navigation and user flow"
        }
        
        return actions.get(friction_type, "Investigate and resolve issue")


# Global friction scorer
friction_scorer = FrictionScorer()
