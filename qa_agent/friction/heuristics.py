"""
Friction detection heuristics.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio


class FrictionType(Enum):
    """Types of friction detected."""
    LONG_DWELL = "long_dwell"
    RAGE_CLICK = "rage_click"
    VALIDATION_LOOP = "validation_loop"
    CONSOLE_ERROR = "console_error"
    NETWORK_ERROR = "network_error"
    VISUAL_INSTABILITY = "visual_instability"
    BACKTRACK = "backtrack"


class FrictionSeverity(Enum):
    """Friction severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FrictionIssue:
    """Represents a detected friction issue."""
    type: FrictionType
    severity: FrictionSeverity
    score: float
    evidence: List[Dict[str, Any]]
    recommendation: str
    timestamp: float


class FrictionHeuristics:
    """Detects friction patterns in user interactions."""
    
    def __init__(self):
        self.config = {
            "long_dwell_threshold": 10.0,  # seconds
            "rage_click_threshold": 3,  # clicks
            "rage_click_window": 2000,  # milliseconds
            "validation_loop_threshold": 3,  # attempts
            "network_error_threshold": 0.1,  # 10% error rate
            "visual_instability_threshold": 0.1,  # 10% layout shifts
            "backtrack_threshold": 2  # page visits
        }
    
    def analyze_events(self, events: List[Dict[str, Any]]) -> List[FrictionIssue]:
        """Analyze events for friction patterns."""
        issues = []
        
        # Group events by type
        event_groups = self._group_events_by_type(events)
        
        # Detect different friction types
        issues.extend(self._detect_long_dwell(event_groups))
        issues.extend(self._detect_rage_clicks(event_groups))
        issues.extend(self._detect_validation_loops(event_groups))
        issues.extend(self._detect_console_errors(event_groups))
        issues.extend(self._detect_network_errors(event_groups))
        issues.extend(self._detect_visual_instability(event_groups))
        issues.extend(self._detect_backtrack(event_groups))
        
        return issues
    
    def _group_events_by_type(self, events: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group events by their type."""
        groups = {}
        for event in events:
            event_type = event.get("type", "unknown")
            if event_type not in groups:
                groups[event_type] = []
            groups[event_type].append(event)
        return groups
    
    def _detect_long_dwell(self, event_groups: Dict[str, List[Dict[str, Any]]]) -> List[FrictionIssue]:
        """Detect long dwell times on pages."""
        issues = []
        
        # Look for page load events and calculate dwell time
        page_loads = event_groups.get("page_load", [])
        page_unloads = event_groups.get("page_unload", [])
        
        for load_event in page_loads:
            load_time = load_event.get("timestamp", 0)
            
            # Find corresponding unload event
            unload_event = None
            for unload in page_unloads:
                if unload.get("timestamp", 0) > load_time:
                    unload_event = unload
                    break
            
            if unload_event:
                dwell_time = unload_event.get("timestamp", 0) - load_time
                
                if dwell_time > self.config["long_dwell_threshold"]:
                    severity = self._calculate_dwell_severity(dwell_time)
                    
                    issues.append(FrictionIssue(
                        type=FrictionType.LONG_DWELL,
                        severity=severity,
                        score=min(dwell_time / 30.0, 1.0),  # Normalize to 0-1
                        evidence=[load_event, unload_event],
                        recommendation=f"Page took {dwell_time:.1f}s to complete. Consider optimizing loading performance.",
                        timestamp=load_time
                    ))
        
        return issues
    
    def _detect_rage_clicks(self, event_groups: Dict[str, List[Dict[str, Any]]]) -> List[FrictionIssue]:
        """Detect rage clicking patterns."""
        issues = []
        
        click_events = event_groups.get("dom_click", [])
        
        # Group clicks by proximity and time
        click_groups = self._group_clicks_by_proximity(click_events)
        
        for group in click_groups:
            if len(group) >= self.config["rage_click_threshold"]:
                time_span = max(event.get("timestamp", 0) for event in group) - min(event.get("timestamp", 0) for event in group)
                
                if time_span <= self.config["rage_click_window"]:
                    severity = self._calculate_rage_click_severity(len(group))
                    
                    issues.append(FrictionIssue(
                        type=FrictionType.RAGE_CLICK,
                        severity=severity,
                        score=min(len(group) / 10.0, 1.0),  # Normalize to 0-1
                        evidence=group,
                        recommendation=f"User clicked {len(group)} times in {time_span:.0f}ms. Element may be unresponsive or unclear.",
                        timestamp=group[0].get("timestamp", 0)
                    ))
        
        return issues
    
    def _detect_validation_loops(self, event_groups: Dict[str, List[Dict[str, Any]]]) -> List[FrictionIssue]:
        """Detect form validation loops."""
        issues = []
        
        form_submissions = event_groups.get("form_submit", [])
        validation_errors = event_groups.get("validation_error", [])
        
        # Group by form and detect repeated submissions
        form_groups = {}
        for submission in form_submissions:
            form_id = submission.get("form_id", "unknown")
            if form_id not in form_groups:
                form_groups[form_id] = []
            form_groups[form_id].append(submission)
        
        for form_id, submissions in form_groups.items():
            if len(submissions) >= self.config["validation_loop_threshold"]:
                # Check if there were validation errors
                form_errors = [e for e in validation_errors if e.get("form_id") == form_id]
                
                if form_errors:
                    severity = self._calculate_validation_severity(len(submissions))
                    
                    issues.append(FrictionIssue(
                        type=FrictionType.VALIDATION_LOOP,
                        severity=severity,
                        score=min(len(submissions) / 5.0, 1.0),  # Normalize to 0-1
                        evidence=submissions + form_errors,
                        recommendation=f"Form submitted {len(submissions)} times with validation errors. Improve form validation and error messages.",
                        timestamp=submissions[0].get("timestamp", 0)
                    ))
        
        return issues
    
    def _detect_console_errors(self, event_groups: Dict[str, List[Dict[str, Any]]]) -> List[FrictionIssue]:
        """Detect JavaScript console errors."""
        issues = []
        
        console_errors = [e for e in event_groups.get("console_message", []) if e.get("payload", {}).get("type") == "error"]
        
        if console_errors:
            severity = self._calculate_error_severity(len(console_errors))
            
            issues.append(FrictionIssue(
                type=FrictionType.CONSOLE_ERROR,
                severity=severity,
                score=min(len(console_errors) / 10.0, 1.0),  # Normalize to 0-1
                evidence=console_errors,
                recommendation=f"Found {len(console_errors)} JavaScript errors. Fix these to improve user experience.",
                timestamp=console_errors[0].get("timestamp", 0)
            ))
        
        return issues
    
    def _detect_network_errors(self, event_groups: Dict[str, List[Dict[str, Any]]]) -> List[FrictionIssue]:
        """Detect network-related issues."""
        issues = []
        
        network_responses = event_groups.get("network_response", [])
        
        if network_responses:
            error_responses = [r for r in network_responses if r.get("payload", {}).get("status", 200) >= 400]
            error_rate = len(error_responses) / len(network_responses)
            
            if error_rate > self.config["network_error_threshold"]:
                severity = self._calculate_network_severity(error_rate)
                
                issues.append(FrictionIssue(
                    type=FrictionType.NETWORK_ERROR,
                    severity=severity,
                    score=error_rate,
                    evidence=error_responses,
                    recommendation=f"Network error rate is {error_rate:.1%}. Check server stability and API endpoints.",
                    timestamp=network_responses[0].get("timestamp", 0)
                ))
        
        return issues
    
    def _detect_visual_instability(self, event_groups: Dict[str, List[Dict[str, Any]]]) -> List[FrictionIssue]:
        """Detect visual instability (layout shifts)."""
        issues = []
        
        layout_shifts = event_groups.get("layout_shift", [])
        
        if layout_shifts:
            total_shifts = sum(event.get("payload", {}).get("value", 0) for event in layout_shifts)
            
            if total_shifts > self.config["visual_instability_threshold"]:
                severity = self._calculate_visual_severity(total_shifts)
                
                issues.append(FrictionIssue(
                    type=FrictionType.VISUAL_INSTABILITY,
                    severity=severity,
                    score=min(total_shifts, 1.0),  # CLS is already 0-1
                    evidence=layout_shifts,
                    recommendation=f"High layout shift score ({total_shifts:.3f}). Optimize page layout and loading.",
                    timestamp=layout_shifts[0].get("timestamp", 0)
                ))
        
        return issues
    
    def _detect_backtrack(self, event_groups: Dict[str, List[Dict[str, Any]]]) -> List[FrictionIssue]:
        """Detect navigation backtracking."""
        issues = []
        
        navigation_events = event_groups.get("navigation", [])
        
        if len(navigation_events) >= self.config["backtrack_threshold"]:
            # Check for back/forward patterns
            urls = [event.get("payload", {}).get("url", "") for event in navigation_events]
            
            # Simple backtrack detection: same URL visited multiple times
            url_counts = {}
            for url in urls:
                url_counts[url] = url_counts.get(url, 0) + 1
            
            backtrack_urls = [url for url, count in url_counts.items() if count > 1]
            
            if backtrack_urls:
                severity = self._calculate_backtrack_severity(len(backtrack_urls))
                
                issues.append(FrictionIssue(
                    type=FrictionType.BACKTRACK,
                    severity=severity,
                    score=min(len(backtrack_urls) / 5.0, 1.0),  # Normalize to 0-1
                    evidence=navigation_events,
                    recommendation=f"User navigated back to {len(backtrack_urls)} pages. Consider improving navigation flow.",
                    timestamp=navigation_events[0].get("timestamp", 0)
                ))
        
        return issues
    
    def _group_clicks_by_proximity(self, click_events: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group clicks by proximity in time and space."""
        groups = []
        current_group = []
        
        for event in sorted(click_events, key=lambda x: x.get("timestamp", 0)):
            payload = event.get("payload", {})
            x, y = payload.get("x", 0), payload.get("y", 0)
            
            if not current_group:
                current_group.append(event)
            else:
                last_event = current_group[-1]
                last_payload = last_event.get("payload", {})
                last_x, last_y = last_payload.get("x", 0), last_payload.get("y", 0)
                
                # Check proximity (within 50 pixels)
                if abs(x - last_x) < 50 and abs(y - last_y) < 50:
                    current_group.append(event)
                else:
                    if len(current_group) > 1:
                        groups.append(current_group)
                    current_group = [event]
        
        if len(current_group) > 1:
            groups.append(current_group)
        
        return groups
    
    def _calculate_dwell_severity(self, dwell_time: float) -> FrictionSeverity:
        """Calculate severity for dwell time."""
        if dwell_time > 30:
            return FrictionSeverity.CRITICAL
        elif dwell_time > 20:
            return FrictionSeverity.HIGH
        elif dwell_time > 15:
            return FrictionSeverity.MEDIUM
        else:
            return FrictionSeverity.LOW
    
    def _calculate_rage_click_severity(self, click_count: int) -> FrictionSeverity:
        """Calculate severity for rage clicks."""
        if click_count > 10:
            return FrictionSeverity.CRITICAL
        elif click_count > 7:
            return FrictionSeverity.HIGH
        elif click_count > 5:
            return FrictionSeverity.MEDIUM
        else:
            return FrictionSeverity.LOW
    
    def _calculate_validation_severity(self, submission_count: int) -> FrictionSeverity:
        """Calculate severity for validation loops."""
        if submission_count > 5:
            return FrictionSeverity.CRITICAL
        elif submission_count > 4:
            return FrictionSeverity.HIGH
        elif submission_count > 3:
            return FrictionSeverity.MEDIUM
        else:
            return FrictionSeverity.LOW
    
    def _calculate_error_severity(self, error_count: int) -> FrictionSeverity:
        """Calculate severity for console errors."""
        if error_count > 20:
            return FrictionSeverity.CRITICAL
        elif error_count > 10:
            return FrictionSeverity.HIGH
        elif error_count > 5:
            return FrictionSeverity.MEDIUM
        else:
            return FrictionSeverity.LOW
    
    def _calculate_network_severity(self, error_rate: float) -> FrictionSeverity:
        """Calculate severity for network errors."""
        if error_rate > 0.5:
            return FrictionSeverity.CRITICAL
        elif error_rate > 0.3:
            return FrictionSeverity.HIGH
        elif error_rate > 0.2:
            return FrictionSeverity.MEDIUM
        else:
            return FrictionSeverity.LOW
    
    def _calculate_visual_severity(self, shift_score: float) -> FrictionSeverity:
        """Calculate severity for visual instability."""
        if shift_score > 0.25:
            return FrictionSeverity.CRITICAL
        elif shift_score > 0.1:
            return FrictionSeverity.HIGH
        elif shift_score > 0.05:
            return FrictionSeverity.MEDIUM
        else:
            return FrictionSeverity.LOW
    
    def _calculate_backtrack_severity(self, backtrack_count: int) -> FrictionSeverity:
        """Calculate severity for backtracking."""
        if backtrack_count > 5:
            return FrictionSeverity.CRITICAL
        elif backtrack_count > 3:
            return FrictionSeverity.HIGH
        elif backtrack_count > 2:
            return FrictionSeverity.MEDIUM
        else:
            return FrictionSeverity.LOW


# Global friction heuristics
friction_heuristics = FrictionHeuristics()
