"""
Flow ranking and prioritization.
"""
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class FlowPriority(Enum):
    """Flow priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class FlowRanking:
    """Flow ranking information."""
    flow_id: str
    priority: FlowPriority
    score: float
    reasons: List[str]


class FlowRanker:
    """Ranks and prioritizes discovered flows."""
    
    def __init__(self):
        self.priority_patterns = {
            FlowPriority.CRITICAL: [
                "login", "signup", "checkout", "payment", "password_reset"
            ],
            FlowPriority.HIGH: [
                "search", "add_to_cart", "profile", "settings", "contact"
            ],
            FlowPriority.MEDIUM: [
                "browse", "view_product", "newsletter", "help"
            ],
            FlowPriority.LOW: [
                "about", "terms", "privacy", "footer"
            ]
        }
    
    def rank_flows(self, flows: List[Dict[str, Any]]) -> List[FlowRanking]:
        """Rank flows by importance and priority."""
        rankings = []
        
        for flow in flows:
            ranking = self._calculate_flow_ranking(flow)
            rankings.append(ranking)
        
        # Sort by score (descending)
        rankings.sort(key=lambda x: x.score, reverse=True)
        
        return rankings
    
    def _calculate_flow_ranking(self, flow: Dict[str, Any]) -> FlowRanking:
        """Calculate ranking for a single flow."""
        flow_type = flow.get("type", "").lower()
        confidence = flow.get("confidence", 0.5)
        frequency = flow.get("frequency", 1)
        
        # Determine priority
        priority = self._determine_priority(flow_type)
        
        # Calculate score
        score = self._calculate_score(flow_type, confidence, frequency)
        
        # Generate reasons
        reasons = self._generate_reasons(flow_type, priority, confidence, frequency)
        
        return FlowRanking(
            flow_id=flow.get("id", flow_type),
            priority=priority,
            score=score,
            reasons=reasons
        )
    
    def _determine_priority(self, flow_type: str) -> FlowPriority:
        """Determine priority based on flow type."""
        for priority, patterns in self.priority_patterns.items():
            if any(pattern in flow_type.lower() for pattern in patterns):
                return priority
        
        return FlowPriority.MEDIUM
    
    def _calculate_score(self, flow_type: str, confidence: float, frequency: int) -> float:
        """Calculate numerical score for flow."""
        base_score = confidence * 100
        
        # Priority multiplier
        priority_multiplier = {
            FlowPriority.CRITICAL: 2.0,
            FlowPriority.HIGH: 1.5,
            FlowPriority.MEDIUM: 1.0,
            FlowPriority.LOW: 0.5
        }
        
        priority = self._determine_priority(flow_type)
        multiplier = priority_multiplier[priority]
        
        # Frequency bonus
        frequency_bonus = min(frequency * 5, 25)  # Cap at 25
        
        # Business value bonus
        business_bonus = self._calculate_business_value(flow_type)
        
        final_score = (base_score * multiplier) + frequency_bonus + business_bonus
        
        return min(final_score, 100)  # Cap at 100
    
    def _calculate_business_value(self, flow_type: str) -> float:
        """Calculate business value bonus."""
        business_value_map = {
            "login": 20,
            "signup": 25,
            "checkout": 30,
            "payment": 30,
            "add_to_cart": 15,
            "search": 10,
            "profile": 8,
            "settings": 5,
            "contact": 5,
            "password_reset": 15
        }
        
        return business_value_map.get(flow_type.lower(), 0)
    
    def _generate_reasons(self, flow_type: str, priority: FlowPriority, confidence: float, frequency: int) -> List[str]:
        """Generate human-readable reasons for ranking."""
        reasons = []
        
        # Priority reason
        reasons.append(f"Priority: {priority.value}")
        
        # Confidence reason
        if confidence > 0.8:
            reasons.append("High confidence detection")
        elif confidence > 0.6:
            reasons.append("Medium confidence detection")
        else:
            reasons.append("Low confidence detection")
        
        # Frequency reason
        if frequency > 3:
            reasons.append(f"Found on {frequency} pages")
        elif frequency > 1:
            reasons.append(f"Found on {frequency} pages")
        
        # Business value reason
        business_value = self._calculate_business_value(flow_type)
        if business_value > 15:
            reasons.append("High business value")
        elif business_value > 5:
            reasons.append("Medium business value")
        
        # Flow type specific reasons
        if flow_type == "login":
            reasons.append("Essential for user authentication")
        elif flow_type == "signup":
            reasons.append("Critical for user acquisition")
        elif flow_type == "checkout":
            reasons.append("Directly impacts revenue")
        elif flow_type == "search":
            reasons.append("Core functionality")
        
        return reasons
    
    def filter_flows_by_priority(self, rankings: List[FlowRanking], min_priority: FlowPriority) -> List[FlowRanking]:
        """Filter flows by minimum priority."""
        priority_order = {
            FlowPriority.CRITICAL: 4,
            FlowPriority.HIGH: 3,
            FlowPriority.MEDIUM: 2,
            FlowPriority.LOW: 1
        }
        
        min_level = priority_order[min_priority]
        
        return [
            ranking for ranking in rankings
            if priority_order[ranking.priority] >= min_level
        ]
    
    def get_top_flows(self, rankings: List[FlowRanking], limit: int = 10) -> List[FlowRanking]:
        """Get top N flows by score."""
        return rankings[:limit]
    
    def group_by_priority(self, rankings: List[FlowRanking]) -> Dict[FlowPriority, List[FlowRanking]]:
        """Group flows by priority level."""
        groups = {priority: [] for priority in FlowPriority}
        
        for ranking in rankings:
            groups[ranking.priority].append(ranking)
        
        return groups


# Global flow ranker
flow_ranker = FlowRanker()
