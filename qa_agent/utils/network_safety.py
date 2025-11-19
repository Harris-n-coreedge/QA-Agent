"""
Network Safety Validation Module
Provides safety controls for network tests including permission checks, rate limiting, and scope validation
"""
import logging
import asyncio
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse
import ipaddress

logger = logging.getLogger(__name__)


class NetworkSafetyValidator:
    """Validates network test targets and enforces safety controls"""
    
    # Restricted test types that require explicit permission
    RESTRICTED_TESTS = {
        "network_security_scan",
        "endpoint_discovery"
    }
    
    # Safe test types (no permission required)
    SAFE_TESTS = {
        "ssl_tls_validation",
        "dns_security_test",
        "connectivity_diagnostics",
        "protocol_traffic_analysis"
    }
    
    def __init__(self, whitelist_domains: Optional[List[str]] = None, rate_limit_delay: float = 1.5):
        """
        Initialize safety validator
        
        Args:
            whitelist_domains: List of allowed domains/IPs (default: localhost only)
            rate_limit_delay: Delay in seconds between scans (default: 1.5)
        """
        self.whitelist_domains = whitelist_domains or []
        self.rate_limit_delay = rate_limit_delay
        self.last_scan_time = {}  # Track last scan time per target
        
        # Always allow localhost
        self.whitelist_domains.extend([
            "localhost",
            "127.0.0.1",
            "::1",
            "0.0.0.0"
        ])
    
    def require_permission(self, test_type: str) -> bool:
        """Check if a test type requires explicit user permission"""
        return test_type in self.RESTRICTED_TESTS
    
    def is_localhost(self, target_url: str) -> bool:
        """Check if target is localhost"""
        try:
            parsed = urlparse(target_url)
            hostname = parsed.hostname or parsed.path.split('/')[0]
            
            if not hostname:
                return False
            
            # Check if it's localhost
            if hostname.lower() in ["localhost", "127.0.0.1", "::1", "0.0.0.0"]:
                return True
            
            # Check if it's a local IP address
            try:
                ip = ipaddress.ip_address(hostname)
                return ip.is_loopback or ip.is_private
            except ValueError:
                return False
                
        except Exception as e:
            logger.warning(f"Error checking localhost: {e}")
            return False
    
    def check_whitelist(self, target_url: str) -> bool:
        """Check if target is in whitelist"""
        try:
            parsed = urlparse(target_url)
            hostname = parsed.hostname or parsed.path.split('/')[0]
            
            if not hostname:
                return False
            
            # Check exact match
            if hostname in self.whitelist_domains:
                return True
            
            # Check domain match (e.g., example.com matches *.example.com)
            for whitelisted in self.whitelist_domains:
                if whitelisted.startswith('*.'):
                    domain = whitelisted[2:]
                    if hostname.endswith('.' + domain) or hostname == domain:
                        return True
                elif hostname == whitelisted:
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking whitelist: {e}")
            return False
    
    def validate_target(
        self, 
        target_url: str, 
        test_type: str, 
        user_permission: bool = False
    ) -> tuple:
        """
        Validate if target is safe to test
        
        Returns:
            (is_valid, error_message)
        """
        # Check if test requires permission
        if self.require_permission(test_type):
            if not user_permission:
                return False, "This test requires explicit user permission. Please confirm you understand the risks."
        
        # Check if target is localhost (always allowed)
        if self.is_localhost(target_url):
            return True, None
        
        # Check whitelist
        if self.check_whitelist(target_url):
            # For restricted tests, still require permission even for whitelisted domains
            if self.require_permission(test_type) and not user_permission:
                return False, "This test requires explicit user permission even for whitelisted domains."
            return True, None
        
        # For restricted tests on non-whitelisted domains, require permission
        if self.require_permission(test_type):
            if not user_permission:
                return False, "This test requires explicit user permission. Target is not in whitelist."
            # User has permission, allow but log warning
            logger.warning(f"Restricted test {test_type} allowed on non-whitelisted target: {target_url} (user permission granted)")
            return True, None
        
        # Safe tests are allowed on any target
        return True, None
    
    async def add_rate_limit_delay(self, target_url: str) -> None:
        """Add rate limiting delay between scans"""
        try:
            parsed = urlparse(target_url)
            target_key = parsed.hostname or target_url
            
            if target_key in self.last_scan_time:
                elapsed = asyncio.get_event_loop().time() - self.last_scan_time[target_key]
                if elapsed < self.rate_limit_delay:
                    delay = self.rate_limit_delay - elapsed
                    logger.info(f"Rate limiting: waiting {delay:.2f}s before next scan")
                    await asyncio.sleep(delay)
            
            self.last_scan_time[target_key] = asyncio.get_event_loop().time()
            
        except Exception as e:
            logger.warning(f"Error in rate limiting: {e}")
            # Continue anyway, but log the error

