"""
Network Test Runner Module
Implements network analysis tests using scapy, python-nmap, and netaddr
Uses latest library documentation patterns
"""
import asyncio
import socket
import ssl
import dns.resolver
import dns.query
import dns.dnssec
import subprocess
import platform
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from urllib.parse import urlparse
import logging
import ipaddress

logger = logging.getLogger(__name__)

# Try to import optional libraries with graceful fallback
try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP, sr1, sr, get_if_list, conf
    from scapy.layers.inet import traceroute
    SCAPY_AVAILABLE = True
    # Suppress Scapy cleanup warnings on Windows (known issue with Npcap)
    import warnings
    warnings.filterwarnings('ignore', category=RuntimeWarning, module='scapy')
    warnings.filterwarnings('ignore', category=UserWarning, module='scapy')
    # Suppress AttributeError during socket cleanup on Windows (known Scapy issue)
    import logging
    scapy_logger = logging.getLogger('scapy')
    scapy_logger.setLevel(logging.ERROR)  # Only show errors, not warnings
    
    # Suppress cleanup AttributeError exceptions on Windows (known Scapy bug #4795)
    # These happen during __del__ when L3WinSocket objects don't have 'ins' attribute
    import sys
    original_excepthook = sys.excepthook
    
    def filtered_excepthook(exc_type, exc_value, exc_traceback):
        """Filter out harmless Scapy cleanup exceptions on Windows"""
        # Suppress AttributeError in SuperSocket.__del__ for L3WinSocket
        if (exc_type == AttributeError and 
            exc_traceback and 
            hasattr(exc_traceback, 'tb_frame') and
            exc_traceback.tb_frame and
            'SuperSocket.__del__' in str(exc_traceback.tb_frame) and
            "'L3WinSocket' object has no attribute 'ins'" in str(exc_value)):
            # This is a harmless cleanup exception, ignore it
            return
        # For all other exceptions, use the original handler
        original_excepthook(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = filtered_excepthook
except ImportError:
    SCAPY_AVAILABLE = False
    logger.warning("Scapy not available. Some network tests will be limited.")

try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    try:
        import nmap3
        NMAP_AVAILABLE = True
        nmap = nmap3  # Alias for compatibility
    except ImportError:
        NMAP_AVAILABLE = False
        logger.warning("python-nmap not available. Port scanning tests will be limited.")

try:
    import netaddr
    NETADDR_AVAILABLE = True
except ImportError:
    NETADDR_AVAILABLE = False
    logger.warning("netaddr not available. Some network utilities will be limited.")

from qa_agent.utils.network_safety import NetworkSafetyValidator


class NetworkTestRunner:
    """Runner for executing network analysis tests"""
    
    def __init__(self):
        self.safety_validator = NetworkSafetyValidator()
        self.packet_capture = []  # Store captured packets for analysis
    
    def _extract_hostname(self, url: str) -> str:
        """Extract hostname from URL"""
        try:
            parsed = urlparse(url)
            return parsed.hostname or parsed.path.split('/')[0] or "localhost"
        except Exception:
            return url
    
    async def _ping_via_subprocess(self, hostname: str, metrics: Dict[str, Any]) -> None:
        """Fallback ping method using system ping command (cross-platform)"""
        logger.info(f"Starting subprocess ping test for {hostname}")
        ping_times = []
        ping_errors = []
        
        # Determine ping command based on OS
        is_windows = platform.system().lower() == 'windows'
        ping_count = 3
        logger.debug(f"Using {'Windows' if is_windows else 'Linux/Mac'} ping command format")
        
        for attempt in range(ping_count):
            try:
                start_time = asyncio.get_event_loop().time()
                
                # Build ping command
                if is_windows:
                    # Windows: ping -n count hostname
                    cmd = ['ping', '-n', '1', '-w', '2000', hostname]
                else:
                    # Linux/Mac: ping -c count -W timeout hostname
                    cmd = ['ping', '-c', '1', '-W', '2', hostname]
                
                # Execute ping command
                process = await asyncio.to_thread(
                    subprocess.run,
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                end_time = asyncio.get_event_loop().time()
                
                # Check if ping was successful
                if process.returncode == 0:
                    # Parse ping time from output
                    ping_output = process.stdout
                    ping_time_ms = None
                    
                    # Try to extract time from ping output
                    # Windows format: "time=123ms" or "time<1ms" or "time=1ms"
                    # Linux format: "time=123 ms" or "time=0.123 ms"
                    time_patterns = [
                        r'time[<=](\d+(?:\.\d+)?)\s*ms',  # Windows/Linux standard: time=1ms or time<1ms
                        r'(\d+(?:\.\d+)?)\s*ms',          # Just number and ms
                    ]
                    
                    # Search in each line of output
                    logger.debug(f"Ping command output (first 500 chars): {ping_output[:500]}")
                    for line in ping_output.split('\n'):
                        line = line.strip()
                        if not line:
                            continue
                        for pattern in time_patterns:
                            match = re.search(pattern, line, re.IGNORECASE)
                            if match:
                                ping_time_ms = float(match.group(1))
                                logger.info(f"Successfully parsed ping time from line: '{line}' -> {ping_time_ms}ms")
                                break
                        if ping_time_ms is not None:
                            break
                    
                    # If we couldn't parse, use elapsed time as fallback
                    if ping_time_ms is None:
                        ping_time_ms = (end_time - start_time) * 1000
                        logger.warning(f"Could not parse ping time from output, using elapsed time: {ping_time_ms:.2f}ms")
                        logger.debug(f"Full ping output:\n{ping_output}")
                    
                    ping_times.append(ping_time_ms)
                    metrics["ping_success"] = True
                    logger.debug(f"Subprocess ping attempt {attempt + 1} successful: {ping_time_ms:.2f}ms")
                else:
                    ping_errors.append(f"Attempt {attempt + 1}: Ping command failed (return code {process.returncode})")
                    logger.debug(f"Subprocess ping attempt {attempt + 1} failed: {process.stderr}")
            
            except subprocess.TimeoutExpired:
                ping_errors.append(f"Attempt {attempt + 1}: Ping timeout")
                logger.debug(f"Subprocess ping attempt {attempt + 1} timed out")
            except FileNotFoundError:
                ping_errors.append("Ping command not found - ping utility not available on this system")
                logger.warning("Ping command not found")
                break  # Don't retry if ping command doesn't exist
            except Exception as e:
                ping_errors.append(f"Attempt {attempt + 1}: {str(e)}")
                logger.debug(f"Subprocess ping attempt {attempt + 1} error: {e}")
        
        # Process results
        if ping_times:
            metrics["ping_times"] = ping_times
            metrics["average_ping_time"] = sum(ping_times) / len(ping_times)
            logger.info(f"Ping test successful using system ping: {len(ping_times)}/{ping_count} attempts succeeded, avg: {metrics['average_ping_time']:.2f}ms")
            # Clear any previous errors since we succeeded
            if metrics.get("issues_found"):
                metrics["issues_found"] = [issue for issue in metrics["issues_found"] if "ping" not in issue.lower()]
    
    def _extract_port(self, url: str, default_port: int = 443) -> int:
        """Extract port from URL"""
        try:
            parsed = urlparse(url)
            if parsed.port:
                return parsed.port
            elif parsed.scheme == "https":
                return 443
            elif parsed.scheme == "http":
                return 80
            return default_port
        except Exception:
            return default_port
    
    async def run_ssl_tls_validation(
        self, 
        target_url: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Validate SSL/TLS certificate, cipher suites, and protocol versions"""
        metrics = {
            "certificate_valid": False,
            "certificate_issuer": None,
            "certificate_subject": None,
            "certificate_valid_from": None,
            "certificate_valid_to": None,
            "certificate_days_remaining": 0,
            "protocol_versions": [],
            "cipher_suites": [],
            "security_rating": "Unknown",
            "recommendations": []
        }
        
        try:
            hostname = self._extract_hostname(target_url)
            port = self._extract_port(target_url, 443)
            
            cert = None
            cipher = None
            version = None
            
            # Method 1: Try using ssl.get_server_certificate() - more reliable for getting cert
            try:
                logger.info(f"Attempting to get certificate using ssl.get_server_certificate() for {hostname}:{port}")
                cert_pem = ssl.get_server_certificate((hostname, port), timeout=10)
                if cert_pem:
                    # Parse PEM certificate using cryptography library if available
                    try:
                        from cryptography import x509
                        from cryptography.hazmat.backends import default_backend
                        cert_obj = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())
                        
                        # Extract certificate info from cryptography object
                        # Map OID names to standard names used by Python's ssl module
                        def get_attr_name(oid):
                            """Map cryptography OID to standard attribute name"""
                            oid_name = oid._name if hasattr(oid, '_name') else str(oid)
                            # Map common OIDs to standard names
                            oid_map = {
                                'commonName': 'commonName',
                                'CN': 'commonName',
                                'organizationName': 'organizationName',
                                'O': 'organizationName',
                                'organizationalUnitName': 'organizationalUnitName',
                                'OU': 'organizationalUnitName',
                                'countryName': 'countryName',
                                'C': 'countryName',
                                'stateOrProvinceName': 'stateOrProvinceName',
                                'ST': 'stateOrProvinceName',
                                'localityName': 'localityName',
                                'L': 'localityName',
                            }
                            # Try to find in map, or use the OID name directly
                            for key, value in oid_map.items():
                                if key.lower() in oid_name.lower():
                                    return value
                            return oid_name
                        
                        cert = {
                            'subject': [(get_attr_name(attr.oid), str(attr.value)) for attr in cert_obj.subject],
                            'issuer': [(get_attr_name(attr.oid), str(attr.value)) for attr in cert_obj.issuer],
                            'notBefore': cert_obj.not_valid_before.strftime('%b %d %H:%M:%S %Y %Z'),
                            'notAfter': cert_obj.not_valid_after.strftime('%b %d %H:%M:%S %Y %Z'),
                        }
                        logger.info(f"Successfully parsed certificate using cryptography library")
                        
                        # Also get cipher and version info via a quick connection
                        try:
                            context = ssl.create_default_context()
                            context.check_hostname = False
                            with socket.create_connection((hostname, port), timeout=5) as quick_sock:
                                with context.wrap_socket(quick_sock, server_hostname=hostname) as quick_ssock:
                                    cipher = quick_ssock.cipher()
                                    version = quick_ssock.version()
                        except Exception:
                            pass  # Cipher/version will be None, that's okay
                    except ImportError:
                        logger.debug("cryptography library not available, will try alternative method")
                        cert = None
                    except Exception as e:
                        logger.debug(f"Error parsing certificate with cryptography: {e}")
                        cert = None
            except Exception as e:
                logger.debug(f"ssl.get_server_certificate() failed: {e}, trying socket method")
            
            # Method 2: If Method 1 failed, try socket connection with proper SSL context
            if not cert:
                try:
                    # Create SSL context with verification enabled to get certificate
                    context = ssl.create_default_context()
                    context.check_hostname = False  # Disable hostname check but keep cert retrieval
                    # Don't set CERT_NONE - we need verification to get the cert
                    
                    with socket.create_connection((hostname, port), timeout=10) as sock:
                        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            # Try to get certificate
                            cert = ssock.getpeercert(binary_form=False)
                            cipher = ssock.cipher()
                            version = ssock.version()
                            
                            logger.info(f"SSL connection established: version={version}, cipher={cipher}, cert={cert is not None if cert else False}")
                            
                            # If getpeercert() returns None or empty dict, try binary form
                            if not cert or (isinstance(cert, dict) and len(cert) == 0):
                                logger.debug("getpeercert() returned None/empty, trying binary form")
                                cert_binary = ssock.getpeercert(binary_form=True)
                                if cert_binary:
                                    # Try to parse binary certificate
                                    try:
                                        from cryptography import x509
                                        from cryptography.hazmat.backends import default_backend
                                        cert_obj = x509.load_der_x509_certificate(cert_binary, default_backend())
                                        # Map OID names to standard names
                                        def get_attr_name(oid):
                                            oid_name = oid._name if hasattr(oid, '_name') else str(oid)
                                            oid_map = {
                                                'commonName': 'commonName', 'CN': 'commonName',
                                                'organizationName': 'organizationName', 'O': 'organizationName',
                                                'organizationalUnitName': 'organizationalUnitName', 'OU': 'organizationalUnitName',
                                                'countryName': 'countryName', 'C': 'countryName',
                                            }
                                            for key, value in oid_map.items():
                                                if key.lower() in oid_name.lower():
                                                    return value
                                            return oid_name
                                        
                                        cert = {
                                            'subject': [(get_attr_name(attr.oid), str(attr.value)) for attr in cert_obj.subject],
                                            'issuer': [(get_attr_name(attr.oid), str(attr.value)) for attr in cert_obj.issuer],
                                            'notBefore': cert_obj.not_valid_before.strftime('%b %d %H:%M:%S %Y %Z'),
                                            'notAfter': cert_obj.not_valid_after.strftime('%b %d %H:%M:%S %Y %Z'),
                                        }
                                        logger.info(f"Successfully parsed binary certificate")
                                    except (ImportError, Exception) as e:
                                        logger.debug(f"Could not parse binary certificate: {e}")
                                        cert = None
                except ssl.SSLError as ssl_err:
                    logger.warning(f"SSL error during certificate retrieval: {ssl_err}")
                    # Try one more time with CERT_NONE as last resort
                    try:
                        context = ssl.create_default_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        with socket.create_connection((hostname, port), timeout=10) as sock:
                            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                                cert = ssock.getpeercert(binary_form=False)
                                cipher = ssock.cipher()
                                version = ssock.version()
                                logger.info(f"Fallback connection: version={version}, cipher={cipher}, cert={cert is not None if cert else False}")
                    except Exception as e:
                        logger.error(f"All certificate retrieval methods failed: {e}")
                except Exception as e:
                    logger.error(f"Error during SSL connection: {e}")
            
            # Extract certificate info if we have it
            if cert:
                # Parse issuer - cert['issuer'] is a list of tuples like [('countryName', 'US'), ('organizationName', 'Example Inc')]
                try:
                    issuer_dict = {}
                    for item in cert.get('issuer', []):
                        if isinstance(item, tuple) and len(item) >= 2:
                            issuer_dict[item[0]] = item[1]
                    metrics["certificate_issuer"] = issuer_dict if issuer_dict else None
                except Exception as e:
                    logger.debug(f"Error parsing issuer: {e}")
                    metrics["certificate_issuer"] = None
                
                # Parse subject - same format as issuer
                try:
                    subject_dict = {}
                    for item in cert.get('subject', []):
                        if isinstance(item, tuple) and len(item) >= 2:
                            subject_dict[item[0]] = item[1]
                    metrics["certificate_subject"] = subject_dict if subject_dict else None
                except Exception as e:
                    logger.debug(f"Error parsing subject: {e}")
                    metrics["certificate_subject"] = None
                
                # Parse dates and validate certificate expiration
                not_before = cert.get('notBefore')
                not_after = cert.get('notAfter')
                valid_from = None
                valid_to = None
                
                if not_before:
                    metrics["certificate_valid_from"] = not_before
                    # Parse valid_from date
                    try:
                        date_formats = [
                            '%b %d %H:%M:%S %Y %Z',  # "Jan 01 12:00:00 2024 GMT"
                            '%b %d %H:%M:%S %Y',      # "Jan 01 12:00:00 2024" (no timezone)
                            '%Y%m%d%H%M%SZ',         # "20240101120000Z"
                            '%Y-%m-%d %H:%M:%S',     # "2024-01-01 12:00:00"
                        ]
                        for fmt in date_formats:
                            try:
                                valid_from = datetime.strptime(not_before.strip(), fmt)
                                break
                            except ValueError:
                                continue
                    except Exception as e:
                        logger.debug(f"Error parsing valid_from date: {e}")
                
                if not_after:
                    metrics["certificate_valid_to"] = not_after
                    try:
                        # Try different date formats
                        date_formats = [
                            '%b %d %H:%M:%S %Y %Z',  # "Jan 01 12:00:00 2024 GMT"
                            '%b %d %H:%M:%S %Y',      # "Jan 01 12:00:00 2024" (no timezone)
                            '%Y%m%d%H%M%SZ',         # "20240101120000Z"
                            '%Y-%m-%d %H:%M:%S',     # "2024-01-01 12:00:00"
                        ]
                        for fmt in date_formats:
                            try:
                                valid_to = datetime.strptime(not_after.strip(), fmt)
                                break
                            except ValueError:
                                continue
                        
                        if valid_to:
                            now = datetime.utcnow()
                            days_remaining = (valid_to - now).days
                            metrics["certificate_days_remaining"] = days_remaining
                            
                            # Validate certificate based on dates
                            # Certificate is valid only if:
                            # 1. Current time is after valid_from (certificate has started)
                            # 2. Current time is before valid_to (certificate hasn't expired)
                            # 3. Days remaining > 0 (not expired)
                            if valid_from and now < valid_from:
                                # Certificate not yet valid
                                metrics["certificate_valid"] = False
                                metrics["recommendations"].append(f"Certificate not yet valid (starts {not_before})")
                            elif days_remaining <= 0:
                                # Certificate expired
                                metrics["certificate_valid"] = False
                                metrics["recommendations"].append(f"Certificate expired on {not_after}")
                            else:
                                # Certificate is valid
                                metrics["certificate_valid"] = True
                        else:
                            # Couldn't parse date, assume invalid
                            metrics["certificate_valid"] = False
                            metrics["recommendations"].append("Could not parse certificate expiration date")
                    except Exception as e:
                        logger.debug(f"Error parsing certificate date: {e}")
                        metrics["certificate_valid"] = False
                        metrics["recommendations"].append("Error parsing certificate dates")
                else:
                    # No expiration date found
                    metrics["certificate_valid"] = False
                    metrics["recommendations"].append("Certificate expiration date not found")
            
            # Get protocol version (always available if connection succeeded)
            if version:
                if version not in metrics["protocol_versions"]:
                    metrics["protocol_versions"].append(version)
            
            # Get cipher suite (always available if connection succeeded)
            if cipher:
                cipher_info = {
                    "name": cipher[0] if len(cipher) > 0 else "Unknown",
                    "version": cipher[1] if len(cipher) > 1 else "Unknown",
                    "bits": cipher[2] if len(cipher) > 2 else 0
                }
                # Check if this cipher suite is already in the list
                if not any(c.get("name") == cipher_info["name"] for c in metrics["cipher_suites"]):
                    metrics["cipher_suites"].append(cipher_info)
            
            # If certificate is None but connection succeeded, try to get basic info
            if not cert and version:
                logger.warning(f"Certificate not available but connection succeeded with {version}")
                # Still mark as having some security info
                metrics["certificate_valid"] = False
                # But we still have protocol and cipher info
            
            # Test other protocol versions (only if we don't have version info yet)
            if not version or len(metrics["protocol_versions"]) < 2:
                # Note: PROTOCOL_TLSv1_3 doesn't exist - use PROTOCOL_TLS which auto-selects best protocol
                tls_versions_to_test = []
                
                # Add available protocol constants
                if hasattr(ssl, 'PROTOCOL_TLS'):
                    tls_versions_to_test.append(ssl.PROTOCOL_TLS)  # Modern - auto-selects best (TLS 1.3 if available)
                if hasattr(ssl, 'PROTOCOL_TLSv1_2'):
                    tls_versions_to_test.append(ssl.PROTOCOL_TLSv1_2)
                if hasattr(ssl, 'PROTOCOL_TLSv1_1'):
                    tls_versions_to_test.append(ssl.PROTOCOL_TLSv1_1)
                if hasattr(ssl, 'PROTOCOL_TLSv1'):
                    tls_versions_to_test.append(ssl.PROTOCOL_TLSv1)
                
                for tls_version in tls_versions_to_test:
                    try:
                        test_context = ssl.SSLContext(tls_version)
                        test_context.check_hostname = False
                        test_context.verify_mode = ssl.CERT_NONE
                        with socket.create_connection((hostname, port), timeout=5) as test_sock:
                            with test_context.wrap_socket(test_sock, server_hostname=hostname) as test_ssock:
                                test_version = test_ssock.version()
                                if test_version and test_version not in metrics["protocol_versions"]:
                                    metrics["protocol_versions"].append(test_version)
                    except Exception as ex:
                        logger.debug(f"Failed to test TLS version {tls_version}: {ex}")
                        pass
            
            # Security rating - evaluate based on available information
            # IMPORTANT: Certificate must be valid for good/excellent rating
            logger.debug(f"Evaluating security rating. certificate_valid={metrics['certificate_valid']}, days_remaining={metrics.get('certificate_days_remaining', 0)}, recommendations={metrics['recommendations']}")
            
            if not metrics["certificate_valid"]:
                # Certificate is invalid - always Poor rating
                protocol_versions_str = " ".join(metrics["protocol_versions"])
                if "TLSv1.3" in protocol_versions_str or "TLSv1.2" in protocol_versions_str:
                    metrics["security_rating"] = "Poor"
                    if metrics["certificate_days_remaining"] <= 0:
                        if "Certificate expired on" not in " ".join(metrics["recommendations"]):
                            metrics["recommendations"].append("Certificate has expired - immediate renewal required")
                    else:
                        if not any("validation failed" in r for r in metrics["recommendations"]):
                            metrics["recommendations"].append("Connection established but certificate validation failed")
                else:
                    metrics["security_rating"] = "Poor"
                    if not any("validation failed" in r or "unavailable" in r for r in metrics["recommendations"]):
                        metrics["recommendations"].append("Certificate validation failed or unavailable")
            elif metrics["certificate_days_remaining"] <= 0:
                # Certificate expired (shouldn't happen if certificate_valid is True, but check anyway)
                metrics["certificate_valid"] = False
                metrics["security_rating"] = "Poor"
                if "Certificate expired" not in " ".join(metrics["recommendations"]):
                    metrics["recommendations"].append("Certificate has expired - immediate renewal required")
            elif metrics["certificate_days_remaining"] < 30:
                # Certificate expiring soon
                metrics["security_rating"] = "Moderate"
                if f"expires in {metrics['certificate_days_remaining']} days" not in " ".join(metrics["recommendations"]):
                    metrics["recommendations"].append(f"Certificate expires in {metrics['certificate_days_remaining']} days")
            else:
                # Certificate is valid - check protocol versions
                protocol_versions_str = " ".join(metrics["protocol_versions"])
                if "TLSv1.3" in protocol_versions_str:
                    metrics["security_rating"] = "Excellent"
                elif "TLSv1.2" in protocol_versions_str:
                    metrics["security_rating"] = "Good"
                else:
                    metrics["security_rating"] = "Moderate"
                    if "upgrading to TLS" not in " ".join(metrics["recommendations"]):
                        metrics["recommendations"].append("Consider upgrading to TLS 1.2 or 1.3")
            
            # Final debug log
            logger.debug(f"Final recommendations before return: {metrics['recommendations']}")
            
        except ssl.SSLError as e:
            logger.error(f"SSL/TLS validation SSL error: {e}", exc_info=True)
            metrics["error"] = f"SSL Error: {str(e)}"
            metrics["security_rating"] = "Error"
        except socket.timeout as e:
            logger.error(f"SSL/TLS validation timeout: {e}")
            metrics["error"] = f"Connection timeout: {str(e)}"
            metrics["security_rating"] = "Error"
        except Exception as e:
            logger.error(f"SSL/TLS validation error: {e}", exc_info=True)
            metrics["error"] = str(e)
            metrics["security_rating"] = "Error"
        
        return metrics
    
    async def run_dns_security_test(
        self, 
        target_url: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Test DNS resolution, DNSSEC, and DNS leaks"""
        metrics = {
            "dns_resolution_times": {},
            "dnssec_enabled": False,
            "dns_leak_detected": False,
            "dns_servers": [],
            "leaked_servers": [],
            "average_resolution_time": 0,
            "recommendations": []
        }
        
        try:
            hostname = self._extract_hostname(target_url)
            
            # Test different DNS query types
            query_types = ['A', 'AAAA', 'MX', 'TXT']
            resolution_times = []
            
            for qtype in query_types:
                try:
                    start_time = asyncio.get_event_loop().time()
                    answers = dns.resolver.resolve(hostname, qtype, lifetime=5)
                    end_time = asyncio.get_event_loop().time()
                    resolution_time = (end_time - start_time) * 1000  # Convert to ms
                    
                    metrics["dns_resolution_times"][qtype] = resolution_time
                    resolution_times.append(resolution_time)
                    
                except Exception as e:
                    logger.debug(f"DNS query {qtype} failed: {e}")
                    metrics["dns_resolution_times"][qtype] = None
            
            # Calculate average
            if resolution_times:
                metrics["average_resolution_time"] = sum(resolution_times) / len(resolution_times)
                # Add recommendation for high resolution time
                if metrics["average_resolution_time"] > 100:
                    metrics["recommendations"].append(f"DNS resolution time ({metrics['average_resolution_time']:.2f}ms) is high - Consider using faster DNS servers")
            
            # Test DNSSEC
            try:
                # Try to get DNSKEY record
                dnskeys = dns.resolver.resolve(hostname, 'DNSKEY', lifetime=5)
                metrics["dnssec_enabled"] = True
            except Exception:
                metrics["dnssec_enabled"] = False
                metrics["recommendations"].append("DNSSEC is not enabled")
            
            # DNS leak test - improved detection logic
            try:
                resolver = dns.resolver.Resolver()
                configured_servers = [str(server) for server in resolver.nameservers]
                metrics["dns_servers"] = configured_servers
                
                # Known public DNS servers
                public_dns_servers = {
                    '8.8.8.8': 'Google DNS',
                    '8.8.4.4': 'Google DNS',
                    '1.1.1.1': 'Cloudflare DNS',
                    '1.0.0.1': 'Cloudflare DNS',
                    '208.67.222.222': 'OpenDNS',
                    '208.67.220.220': 'OpenDNS',
                    '9.9.9.9': 'Quad9',
                    '149.112.112.112': 'Quad9'
                }
                
                # Check for potential DNS leak
                # A leak occurs when:
                # 1. There's a mix of public DNS and private/local DNS (queries may bypass intended servers)
                # 2. All servers are public but queries might go to ISP DNS (hard to detect without packet capture)
                
                public_servers = []
                private_servers = []
                
                for server in configured_servers:
                    server_str = str(server)
                    # Check if it's a known public DNS
                    if server_str in public_dns_servers:
                        public_servers.append(server_str)
                    else:
                        # Check if it's a private/local IP
                        try:
                            ip = ipaddress.ip_address(server_str)
                            if ip.is_private or ip.is_loopback:
                                private_servers.append(server_str)
                            else:
                                # Unknown public IP - could be ISP DNS or other
                                private_servers.append(server_str)
                        except ValueError:
                            # Not an IP, might be a hostname
                            private_servers.append(server_str)
                
                # Detect potential leak: mix of public and private DNS suggests queries might bypass intended servers
                if public_servers and private_servers:
                    # This is a potential leak - queries might go to public DNS instead of private/VPN DNS
                    metrics["dns_leak_detected"] = True
                    metrics["leaked_servers"] = public_servers
                    logger.info(f"Potential DNS leak detected: Mix of public ({public_servers}) and private ({private_servers}) DNS servers")
                elif len(public_servers) > 1 and len(set(public_servers)) < len(configured_servers):
                    # Multiple different public DNS servers configured - less likely to be intentional
                    metrics["dns_leak_detected"] = True
                    metrics["leaked_servers"] = public_servers
                elif len(configured_servers) == 1 and configured_servers[0] in public_dns_servers:
                    # Single public DNS - likely intentional, not a leak
                    metrics["dns_leak_detected"] = False
                    metrics["leaked_servers"] = []
                elif len(public_servers) == len(configured_servers) and len(set(public_servers)) == 1:
                    # All servers are the same public DNS - likely intentional
                    metrics["dns_leak_detected"] = False
                    metrics["leaked_servers"] = []
                else:
                    # Default: if we have public DNS mixed with others, flag as potential leak
                    if public_servers:
                        metrics["dns_leak_detected"] = True
                        metrics["leaked_servers"] = public_servers
                    else:
                        metrics["dns_leak_detected"] = False
                        metrics["leaked_servers"] = []
                
                # Add recommendation if leak detected
                if metrics["dns_leak_detected"]:
                    metrics["recommendations"].append("Potential DNS leak detected - Review DNS configuration to ensure queries go to intended servers")
                
            except Exception as e:
                logger.debug(f"DNS leak test error: {e}")
                metrics["dns_leak_detected"] = False
            
        except Exception as e:
            logger.error(f"DNS security test error: {e}", exc_info=True)
            metrics["error"] = str(e)
        
        return metrics
    
    async def run_connectivity_diagnostics(
        self, 
        target_url: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Diagnose network connectivity issues"""
        metrics = {
            "ping_success": False,
            "ping_times": [],
            "average_ping_time": None,  # None indicates no data collected (failed ping)
            "dns_resolution": False,
            "dns_resolution_time": 0,
            "http_connection": False,
            "https_connection": False,
            "connection_tests": {},
            "issues_found": [],
            "recommendations": []
        }
        
        try:
            hostname = self._extract_hostname(target_url)
            parsed = urlparse(target_url)
            scheme = parsed.scheme or "https"
            
            # Ping test (ICMP) - Try Scapy first, fallback to subprocess
            ping_attempted = False
            if SCAPY_AVAILABLE:
                try:
                    ping_attempted = True
                    ping_times = []
                    ping_errors = []
                    for attempt in range(3):  # 3 ping attempts
                        start_time = asyncio.get_event_loop().time()
                        # Use scapy to send ICMP ping
                        # Note: This requires root/admin privileges on some systems
                        try:
                            ans = await asyncio.to_thread(
                                sr1, 
                                IP(dst=hostname)/ICMP(), 
                                timeout=2, 
                                verbose=0
                            )
                            if ans:
                                end_time = asyncio.get_event_loop().time()
                                ping_time = (end_time - start_time) * 1000
                                ping_times.append(ping_time)
                                metrics["ping_success"] = True
                                logger.debug(f"Ping attempt {attempt + 1} successful: {ping_time:.2f}ms")
                            else:
                                ping_errors.append(f"Attempt {attempt + 1}: No response")
                                logger.debug(f"Ping attempt {attempt + 1} failed: No response from {hostname}")
                        except PermissionError as pe:
                            ping_errors.append(f"Attempt {attempt + 1}: Permission denied (requires admin/root)")
                            logger.warning(f"Ping attempt {attempt + 1} failed: {pe}")
                            break  # Don't retry if it's a permission issue
                        except Exception as e:
                            error_str = str(e)
                            # Check for Windows-specific Npcap error
                            if "Npcap" in error_str or "L3 Raw sockets" in error_str or "administrator" in error_str.lower():
                                ping_errors.append(f"Windows requires Npcap or administrator privileges for ICMP")
                                logger.warning(f"Windows Npcap/Admin issue detected: {error_str}")
                                # Break immediately and try subprocess ping
                                break  # Don't retry - this is a system configuration issue
                            else:
                                ping_errors.append(f"Attempt {attempt + 1}: {error_str}")
                                logger.debug(f"Ping attempt {attempt + 1} failed: {e}")
                    
                    if ping_times:
                        metrics["ping_times"] = ping_times
                        metrics["average_ping_time"] = sum(ping_times) / len(ping_times)
                        logger.info(f"Ping test successful: {len(ping_times)}/{3} attempts succeeded, avg: {metrics['average_ping_time']:.2f}ms")
                    else:
                        # Ping attempts failed - try subprocess ping as fallback
                        logger.info("Scapy ping failed, trying system ping command as fallback")
                        await self._ping_via_subprocess(hostname, metrics)
                        
                        # Only add error messages if subprocess also failed
                        if not metrics["ping_success"]:
                            # Determine the most likely reason for failure
                            error_msg = "ICMP ping test failed"
                            if ping_errors:
                                # Check for Windows Npcap issue first (most specific)
                                if any("Npcap" in err or "L3 Raw sockets" in err for err in ping_errors):
                                    error_msg = "ICMP ping test failed - Windows requires Npcap library or administrator privileges. Install Npcap from https://npcap.com/ or run as administrator"
                                    metrics["issues_found"].append(error_msg)
                                    metrics["recommendations"].append("Install Npcap (https://npcap.com/) to enable ICMP ping on Windows without administrator privileges")
                                # Check if it's a permission issue
                                elif any("Permission" in err or "permission" in err.lower() or "administrator" in err.lower() for err in ping_errors):
                                    error_msg = "ICMP ping test failed - requires administrator/root privileges to send ICMP packets"
                                    metrics["issues_found"].append(error_msg)
                                elif any("No response" in err for err in ping_errors):
                                    error_msg = "ICMP ping test failed - host may be unreachable or ICMP blocked by firewall"
                                    metrics["issues_found"].append(error_msg)
                                else:
                                    # Use the first error message
                                    error_msg = ping_errors[0] if ping_errors else "ICMP ping test failed - Unknown error"
                                    metrics["issues_found"].append(error_msg)
                            else:
                                metrics["issues_found"].append("ICMP ping test failed - host may be unreachable or ICMP blocked")
                            
                except Exception as e:
                    logger.error(f"Ping test error: {e}", exc_info=True)
                    metrics["ping_success"] = False
                    metrics["average_ping_time"] = None
                    error_detail = str(e)
                    
                    # Check for Windows Npcap issue
                    if "Npcap" in error_detail or "L3 Raw sockets" in error_detail or ("administrator" in error_detail.lower() and "Windows" in error_detail):
                        # Try subprocess ping as fallback
                        logger.info("Scapy requires Npcap, trying system ping command as fallback")
                        await self._ping_via_subprocess(hostname, metrics)
                        
                        # If subprocess also failed, add Npcap recommendation
                        if not metrics["ping_success"]:
                            error_msg = "ICMP ping test failed - Windows requires Npcap library or administrator privileges. Install Npcap from https://npcap.com/ or run as administrator"
                            metrics["issues_found"].append(error_msg)
                            metrics["recommendations"].append("Install Npcap (https://npcap.com/) to enable ICMP ping on Windows without administrator privileges")
                    elif "Permission" in error_detail or "permission" in error_detail.lower():
                        # Try subprocess ping as fallback
                        logger.info("Scapy requires privileges, trying system ping command as fallback")
                        await self._ping_via_subprocess(hostname, metrics)
                        
                        if not metrics["ping_success"]:
                            metrics["issues_found"].append("ICMP ping test failed - requires administrator/root privileges")
                    else:
                        # Try subprocess ping as fallback
                        logger.info("Scapy ping failed, trying system ping command as fallback")
                        await self._ping_via_subprocess(hostname, metrics)
                        
                        if not metrics["ping_success"]:
                            metrics["issues_found"].append(f"ICMP ping test failed - {error_detail}")
            else:
                # Scapy not available, use subprocess ping directly
                logger.info("Scapy not available, using system ping command")
                await self._ping_via_subprocess(hostname, metrics)
            
            # DNS resolution test
            try:
                start_time = asyncio.get_event_loop().time()
                # Use asyncio.to_thread for proper async execution and timing
                await asyncio.to_thread(socket.gethostbyname, hostname)
                end_time = asyncio.get_event_loop().time()
                metrics["dns_resolution"] = True
                resolution_time_ms = (end_time - start_time) * 1000
                # Round to 2 decimal places, minimum 0.01ms if resolution was successful
                metrics["dns_resolution_time"] = max(0.01, round(resolution_time_ms, 2))
                logger.debug(f"DNS resolution time: {metrics['dns_resolution_time']:.2f}ms")
            except Exception as e:
                metrics["dns_resolution"] = False
                metrics["issues_found"].append(f"DNS resolution failed: {str(e)}")
                metrics["recommendations"].append("Check DNS configuration")
            
            # HTTP connection test
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((hostname, 80))
                sock.close()
                metrics["http_connection"] = (result == 0)
                metrics["connection_tests"]["http"] = result == 0
            except Exception as e:
                metrics["connection_tests"]["http"] = False
                metrics["issues_found"].append(f"HTTP connection failed: {str(e)}")
            
            # HTTPS connection test
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((hostname, 443))
                sock.close()
                metrics["https_connection"] = (result == 0)
                metrics["connection_tests"]["https"] = result == 0
            except Exception as e:
                metrics["connection_tests"]["https"] = False
                metrics["issues_found"].append(f"HTTPS connection failed: {str(e)}")
            
            # Generate recommendations
            if not metrics["ping_success"]:
                # Check if it's a Windows Npcap issue - if so, recommendation already added above
                issues_text = " ".join([str(issue) for issue in metrics["issues_found"]]).lower()
                if "npcap" not in issues_text and "windows" not in issues_text:
                    # Only add generic recommendation if it's not a Windows/Npcap issue
                    metrics["recommendations"].append("Host may be unreachable or firewall blocking ICMP")
            if not metrics["dns_resolution"]:
                metrics["recommendations"].append("DNS resolution failed - check DNS servers")
            if not metrics["http_connection"] and not metrics["https_connection"]:
                metrics["recommendations"].append("No HTTP/HTTPS connectivity - check firewall rules")
            
        except Exception as e:
            logger.error(f"Connectivity diagnostics error: {e}", exc_info=True)
            metrics["error"] = str(e)
        
        return metrics
    
    async def _analyze_traffic_via_http(self, target_url: str, duration: int = 10) -> Dict[str, Any]:
        """
        Fallback method: Analyze network traffic using application-level HTTP/HTTPS requests
        This works without Npcap/winpcap by using httpx to make requests and analyze responses
        """
        metrics = {
            "total_packets": 0,
            "protocol_distribution": {},
            "packet_sizes": [],
            "average_packet_size": 0,
            "traffic_volume_bytes": 0,
            "protocols_detected": [],
            "traffic_patterns": {},
            "analysis_method": "application_level"
        }
        
        try:
            import httpx
            import time
            from urllib.parse import urlparse
            
            parsed = urlparse(target_url)
            protocol = parsed.scheme.lower() if parsed.scheme else "https"
            hostname = parsed.hostname or parsed.path.split('/')[0] or "localhost"
            
            # Ensure we have http or https
            if protocol not in ['http', 'https']:
                protocol = 'https'
            
            full_url = f"{protocol}://{hostname}{parsed.path or '/'}"
            
            logger.info(f"Using application-level analysis for {full_url}")
            
            # Make multiple requests to simulate traffic
            request_count = min(10, max(3, duration))  # 3-10 requests based on duration
            total_request_size = 0
            total_response_size = 0
            protocols_used = set()
            packet_sizes = []
            
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                start_time = time.time()
                
                for i in range(request_count):
                    try:
                        # Make different types of requests
                        if i == 0:
                            # Full GET request
                            response = await client.get(full_url)
                        elif i == 1:
                            # HEAD request (smaller)
                            response = await client.head(full_url)
                        else:
                            # GET request with different paths
                            response = await client.get(full_url)
                        
                        # Calculate request size (approximate)
                        request_size = len(f"{response.request.method} {response.request.url} HTTP/1.1\r\n")
                        request_size += sum(len(f"{k}: {v}\r\n") for k, v in response.request.headers.items())
                        request_size += len("\r\n")
                        
                        # Get response size
                        response_size = len(response.content)
                        response_headers_size = sum(len(f"{k}: {v}\r\n") for k, v in response.headers.items())
                        total_response_size += response_size + response_headers_size
                        total_request_size += request_size
                        
                        # Track protocol
                        protocols_used.add(protocol.upper())
                        
                        # Estimate packet sizes (typical TCP/IP overhead + data)
                        # Average TCP/IP header: ~40 bytes
                        # Typical packet size: 1500 bytes (MTU), but can vary
                        tcp_overhead = 40
                        
                        # Estimate packets for request
                        if request_size > 0:
                            request_packets = max(1, (request_size + tcp_overhead - 1) // 1460 + 1)  # 1460 = 1500 - 40
                            for _ in range(request_packets):
                                packet_sizes.append(min(1500, request_size // request_packets + tcp_overhead))
                        
                        # Estimate packets for response
                        if response_size > 0:
                            response_packets = max(1, (response_size + tcp_overhead - 1) // 1460 + 1)
                            for _ in range(response_packets):
                                packet_sizes.append(min(1500, response_size // response_packets + tcp_overhead))
                        
                        # Small delay between requests
                        await asyncio.sleep(0.5)
                        
                    except Exception as req_error:
                        logger.debug(f"Request {i+1} failed: {req_error}")
                        continue
                    
                    # Check if we've exceeded duration
                    if time.time() - start_time >= duration:
                        break
            
            # Calculate metrics
            total_traffic = total_request_size + total_response_size
            total_packets = len(packet_sizes)
            
            # Protocol distribution
            # Note: TCP is the underlying transport for HTTP/HTTPS
            # We show application protocols (HTTP/HTTPS) with their packet counts
            # TCP is shown separately to indicate it's the transport layer
            protocol_dist = {}
            if protocols_used:
                # For application-level analysis, all packets are for the application protocol
                # Distribute packets across application protocols (HTTP/HTTPS)
                packets_per_protocol = total_packets // len(protocols_used) if len(protocols_used) > 0 else 0
                remaining_packets = total_packets
                
                protocol_list = list(protocols_used)
                for i, proto in enumerate(protocol_list):
                    if i == len(protocol_list) - 1:
                        # Last protocol gets all remaining packets
                        protocol_dist[proto] = remaining_packets
                    else:
                        protocol_dist[proto] = packets_per_protocol
                        remaining_packets -= packets_per_protocol
                
                # Add TCP as transport layer (all packets use TCP as underlying transport)
                # Show it with the same count but label it as transport layer
                if total_packets > 0:
                    protocol_dist["TCP"] = total_packets
            elif total_packets > 0:
                # If no application protocols detected but we have packets, it's TCP
                protocol_dist["TCP"] = total_packets
            
            metrics["total_packets"] = total_packets
            metrics["protocol_distribution"] = protocol_dist
            metrics["packet_sizes"] = packet_sizes
            metrics["traffic_volume_bytes"] = total_traffic
            metrics["protocols_detected"] = list(protocols_used) + (["TCP"] if total_packets > 0 else [])
            
            if packet_sizes:
                metrics["average_packet_size"] = sum(packet_sizes) / len(packet_sizes)
            else:
                metrics["average_packet_size"] = 0
            
            metrics["target_url"] = target_url
            metrics["note"] = "Analysis performed using application-level HTTP/HTTPS requests (no raw packet capture required)"
            
            logger.info(f"Application-level analysis completed: {total_packets} estimated packets, {total_traffic} bytes")
            
        except ImportError:
            metrics["error"] = "httpx library not available for application-level analysis"
        except Exception as e:
            logger.error(f"Application-level traffic analysis error: {e}", exc_info=True)
            metrics["error"] = f"Application-level analysis failed: {str(e)}"
        
        return metrics
    
    async def run_protocol_traffic_analysis(
        self, 
        target_url: str, 
        duration: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze network traffic at packet level (passive) or application level (fallback)"""
        metrics = {
            "total_packets": 0,
            "protocol_distribution": {},
            "packet_sizes": [],
            "average_packet_size": 0,
            "traffic_volume_bytes": 0,
            "protocols_detected": [],
            "traffic_patterns": {}
        }
        
        if not SCAPY_AVAILABLE:
            # Use fallback method if Scapy is not available
            logger.info("Scapy not available, using application-level analysis")
            return await self._analyze_traffic_via_http(target_url, duration)
        
        try:
            hostname = self._extract_hostname(target_url)
            metrics["target_url"] = target_url  # Always set target URL
            
            # Capture packets for specified duration
            captured_packets = []
            
            def packet_handler(packet):
                """Handle captured packets"""
                captured_packets.append(packet)
            
            # Sniff packets (passive - only captures, doesn't send)
            try:
                # Suppress Scapy warnings about unsupported options
                import warnings
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore', message='.*Dropping unsupported option.*')
                    warnings.filterwarnings('ignore', category=RuntimeWarning, module='scapy')
                    
                    # Try layer 2 sniffing first (requires winpcap/npcap on Windows)
                    try:
                        packets = await asyncio.to_thread(
                            sniff,
                            timeout=duration,
                            prn=packet_handler,
                            store=True,
                            filter=f"host {hostname}" if hostname else None
                        )
                    except (OSError, PermissionError) as perm_error:
                        # Catch permission errors early to show clear message
                        error_str = str(perm_error)
                        if "10013" in error_str or "access permissions" in error_str.lower() or "administrator" in error_str.lower():
                            # This is a permission error - use application-level fallback
                            logger.info("Permission error detected, using application-level analysis fallback")
                            return await self._analyze_traffic_via_http(target_url, duration)
                        else:
                            # Re-raise as layer2_error for normal handling
                            raise
                    except Exception as layer2_error:
                        error_str = str(layer2_error)
                        # Check if it's a winpcap/npcap error
                        if "winpcap" in error_str.lower() or "layer 2" in error_str.lower() or "not available at layer 2" in error_str.lower():
                            logger.info("Layer 2 sniffing not available, trying Layer 3 fallback...")
                            # Check if this is a Windows permission error - if so, skip Layer 3 (it will also fail)
                            if platform.system().lower() == 'windows' and ("winpcap" in error_str.lower() or "npcap" in error_str.lower() or "not available at layer 2" in error_str.lower()):
                                # On Windows without Npcap, use application-level fallback instead
                                logger.info("Npcap not available, using application-level analysis fallback")
                                return await self._analyze_traffic_via_http(target_url, duration)
                            else:
                                # Try Layer 3 socket as fallback (may require admin privileges)
                                try:
                                    # Configure scapy to use Layer 3 socket explicitly
                                    # Note: On Windows, this will likely also fail without admin/Npcap
                                    try:
                                        # Check if we're on Windows and don't have Npcap
                                        if platform.system().lower() == 'windows':
                                            # Don't try to configure L3WinSocket - it will fail without admin
                                            logger.debug("Skipping L3WinSocket configuration on Windows without Npcap")
                                    except Exception as config_err:
                                        logger.debug(f"Could not configure L3socket: {config_err}")
                                    
                                    # For Layer 3, we can't passively sniff, but we can send packets and capture responses
                                    # This is a workaround - we'll send a few packets to the target and analyze responses
                                    logger.info(f"Using Layer 3 socket for traffic analysis to {hostname}")
                                    
                                    # Send a few test packets and capture responses
                                    # This is not true passive capture, but provides some traffic analysis
                                    test_packets_sent = 0
                                    responses = []
                                    
                                    # Try to resolve hostname to IP
                                    try:
                                        import socket as stdlib_socket
                                        target_ip = stdlib_socket.gethostbyname(hostname)
                                        logger.debug(f"Resolved {hostname} to {target_ip}")
                                        
                                        # Send ICMP ping (if allowed) - requires admin on Windows
                                        try:
                                            ping_packet = IP(dst=target_ip) / ICMP()
                                            response = await asyncio.to_thread(sr1, ping_packet, timeout=2, verbose=0)
                                            if response:
                                                responses.append(response)
                                                test_packets_sent += 1
                                                logger.debug("ICMP ping successful")
                                        except Exception as ping_err:
                                            logger.debug(f"ICMP ping failed (may require admin): {ping_err}")
                                        
                                        # Try TCP SYN to common ports (less likely to require admin)
                                        common_ports = [80, 443]
                                        for port in common_ports:
                                            try:
                                                syn_packet = IP(dst=target_ip) / TCP(dport=port, flags="S")
                                                response = await asyncio.to_thread(sr1, syn_packet, timeout=1, verbose=0)
                                                if response:
                                                    responses.append(response)
                                                    test_packets_sent += 1
                                                    logger.debug(f"TCP SYN to port {port} successful")
                                            except Exception as syn_err:
                                                logger.debug(f"TCP SYN to port {port} failed: {syn_err}")
                                        
                                        # Analyze captured responses
                                        captured_packets = responses
                                        
                                        # If we got some responses, continue with analysis
                                        if len(captured_packets) > 0:
                                            logger.info(f"Captured {len(captured_packets)} packets via Layer 3")
                                        else:
                                            # No packets captured via Layer 3, try application-level fallback
                                            logger.info("Layer 3 capture failed, using application-level analysis fallback")
                                            return await self._analyze_traffic_via_http(target_url, duration)
                                        
                                    except Exception as resolve_error:
                                        logger.warning(f"Could not resolve hostname or send packets: {resolve_error}")
                                        # Try application-level fallback
                                        logger.info("Layer 3 resolution failed, using application-level analysis fallback")
                                        return await self._analyze_traffic_via_http(target_url, duration)
                                except Exception as layer3_error:
                                    # Both Layer 2 and Layer 3 failed, try application-level fallback
                                    logger.warning(f"Both Layer 2 and Layer 3 packet capture failed, trying application-level fallback")
                                    try:
                                        return await self._analyze_traffic_via_http(target_url, duration)
                                    except Exception as fallback_error:
                                        logger.error(f"All methods failed including fallback: {fallback_error}")
                                        metrics["error"] = (
                                            f"Packet capture failed: {str(layer2_error)}. "
                                            f"Layer 3 fallback also failed: {str(layer3_error)}. "
                                            f"Application-level fallback failed: {str(fallback_error)}. "
                                            f"On Windows, install Npcap (https://nmap.org/npcap/) for full packet capture support."
                                        )
                                        captured_packets = []  # Set empty list to continue processing
                    else:
                        # Different error - try application-level fallback
                        logger.info("Unexpected error, trying application-level analysis fallback")
                        try:
                            return await self._analyze_traffic_via_http(target_url, duration)
                        except Exception as fallback_error:
                            logger.error(f"Fallback also failed: {fallback_error}")
                            metrics["error"] = f"Packet capture failed: {str(layer2_error)}. Fallback also failed: {str(fallback_error)}"
                            captured_packets = []  # Set empty list to continue processing
                
                metrics["total_packets"] = len(captured_packets)
                
                # Analyze packets
                protocol_counts = {}
                total_size = 0
                
                for packet in captured_packets:
                    # Get packet size
                    size = len(packet)
                    metrics["packet_sizes"].append(size)
                    total_size += size
                    
                    # Identify protocol
                    protocol = "Unknown"
                    if packet.haslayer(IP):
                        if packet.haslayer(TCP):
                            protocol = "TCP"
                        elif packet.haslayer(UDP):
                            protocol = "UDP"
                        elif packet.haslayer(ICMP):
                            protocol = "ICMP"
                        else:
                            protocol = "IP"
                    elif packet.haslayer(ARP):
                        protocol = "ARP"
                    
                    protocol_counts[protocol] = protocol_counts.get(protocol, 0) + 1
                
                metrics["protocol_distribution"] = protocol_counts
                metrics["protocols_detected"] = list(protocol_counts.keys())
                metrics["traffic_volume_bytes"] = total_size
                
                if metrics["packet_sizes"]:
                    metrics["average_packet_size"] = sum(metrics["packet_sizes"]) / len(metrics["packet_sizes"])
                else:
                    metrics["average_packet_size"] = 0
                
            except Exception as e:
                logger.warning(f"Packet capture failed: {e}")
                error_msg = str(e)
                if "winpcap" in error_msg.lower() or "layer 2" in error_msg.lower():
                    metrics["error"] = (
                        f"Packet capture failed: {error_msg}. "
                        f"On Windows, install Npcap (https://nmap.org/npcap/) for full packet capture support. "
                        f"Alternatively, run with administrator privileges for Layer 3 access."
                    )
                else:
                    metrics["error"] = f"Packet capture failed: {error_msg} (may require admin privileges)"
                # Ensure all metrics are initialized even on error
                if "protocol_distribution" not in metrics:
                    metrics["protocol_distribution"] = {}
                if "protocols_detected" not in metrics:
                    metrics["protocols_detected"] = []
                if "traffic_volume_bytes" not in metrics:
                    metrics["traffic_volume_bytes"] = 0
                if "average_packet_size" not in metrics:
                    metrics["average_packet_size"] = 0
                metrics["target_url"] = target_url
        
        except Exception as e:
            logger.error(f"Protocol traffic analysis error: {e}", exc_info=True)
            error_str = str(e)
            
            # If it's a winpcap/npcap error, try fallback method
            if "winpcap" in error_str.lower() or "npcap" in error_str.lower() or "layer 2" in error_str.lower():
                logger.info("Packet capture failed, trying application-level analysis fallback")
                try:
                    return await self._analyze_traffic_via_http(target_url, duration)
                except Exception as fallback_error:
                    logger.error(f"Fallback analysis also failed: {fallback_error}")
                    metrics["error"] = f"Both packet capture and fallback analysis failed: {error_str}"
            else:
                metrics["error"] = error_str
            
            # Ensure all metrics are initialized even on error
            if "protocol_distribution" not in metrics:
                metrics["protocol_distribution"] = {}
            if "protocols_detected" not in metrics:
                metrics["protocols_detected"] = []
            if "traffic_volume_bytes" not in metrics:
                metrics["traffic_volume_bytes"] = 0
            if "average_packet_size" not in metrics:
                metrics["average_packet_size"] = 0
            if "target_url" not in metrics:
                metrics["target_url"] = target_url
        
        # Note: Scapy cleanup exceptions on Windows (L3WinSocket AttributeError) are harmless
        # and are automatically suppressed by Python's exception handling in __del__
        
        return metrics
    
    async def run_network_security_scan(
        self, 
        target_url: str, 
        ports: Optional[List[int]] = None,
        scan_type: str = "stealth",
        user_permission: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Perform network security scan (port scanning, service detection)"""
        # Validate safety
        is_valid, error_msg = self.safety_validator.validate_target(
            target_url, "network_security_scan", user_permission
        )
        
        if not is_valid:
            return {
                "error": error_msg,
                "scan_blocked": True
            }
        
        # Apply rate limiting
        await self.safety_validator.add_rate_limit_delay(target_url)
        
        metrics = {
            "target": target_url,
            "ports_scanned": 0,
            "open_ports": [],
            "closed_ports": [],
            "filtered_ports": [],
            "services": {},
            "vulnerabilities": [],
            "scan_type": scan_type
        }
        
        if not NMAP_AVAILABLE:
            metrics["error"] = "python-nmap not available for port scanning"
            return metrics
        
        try:
            hostname = self._extract_hostname(target_url)
            
            # Default ports if not specified
            if not ports:
                ports = [22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995, 3306, 3389, 5432, 8080, 8443]
            
            metrics["ports_scanned"] = len(ports)
            
            # Use nmap for scanning
            # Try python-nmap (standard library) first
            try:
                nm = nmap.PortScanner()
                # Convert ports list to nmap format
                ports_str = ','.join(map(str, ports))
                
                # Perform scan based on scan type
                scan_args = f"-p {ports_str}"
                if scan_type == "stealth":
                    scan_args += " -sS"  # SYN scan
                elif scan_type == "tcp":
                    scan_args += " -sT"  # TCP connect scan
                
                # Run scan
                scan_results = await asyncio.to_thread(
                    nm.scan,
                    hostname,
                    arguments=scan_args
                )
            except AttributeError:
                # Fallback to nmap3 if available
                if hasattr(nmap, 'Nmap'):
                    nm = nmap.Nmap()
                    ports_str = ','.join(map(str, ports))
                    
                    if scan_type == "stealth":
                        scan_results = await asyncio.to_thread(
                            nm.scan_top_ports,
                            hostname,
                            args=f"-p {ports_str} -sS"
                        )
                    elif scan_type == "tcp":
                        scan_results = await asyncio.to_thread(
                            nm.scan_top_ports,
                            hostname,
                            args=f"-p {ports_str} -sT"
                        )
                    else:
                        scan_results = await asyncio.to_thread(
                            nm.scan_top_ports,
                            hostname,
                            args=f"-p {ports_str}"
                        )
                else:
                    raise ImportError("Nmap library not properly configured")
            
            try:
                
                # Parse results (handle both python-nmap and nmap3 formats)
                host_data = None
                
                # Check if it's python-nmap format
                if hasattr(nm, 'scan') and hostname in scan_results:
                    host_data = scan_results[hostname]
                    # python-nmap format
                    if 'tcp' in host_data:
                        for port_num, port_info in host_data['tcp'].items():
                            state = port_info.get('state', 'unknown')
                            service = port_info.get('name', 'unknown')
                            version = port_info.get('version', '')
                            
                            port_data = {
                                "port": int(port_num),
                                "state": state,
                                "service": service,
                                "version": version
                            }
                            
                            if state == "open":
                                metrics["open_ports"].append(port_data)
                            elif state == "closed":
                                metrics["closed_ports"].append(port_data)
                            elif state == "filtered":
                                metrics["filtered_ports"].append(port_data)
                            
                            if service != "unknown":
                                metrics["services"][str(port_num)] = {
                                    "name": service,
                                    "version": version,
                                    "state": state
                                }
                elif isinstance(scan_results, dict) and hostname in scan_results:
                    # nmap3 format
                    host_data = scan_results[hostname]
                    if 'ports' in host_data:
                        for port_info in host_data['ports']:
                            port_num = port_info.get('portid')
                            state = port_info.get('state', {}).get('state', 'unknown')
                            service = port_info.get('service', {}).get('name', 'unknown')
                            version = port_info.get('service', {}).get('version', '')
                            
                            port_data = {
                                "port": int(port_num),
                                "state": state,
                                "service": service,
                                "version": version
                            }
                            
                            if state == "open":
                                metrics["open_ports"].append(port_data)
                            elif state == "closed":
                                metrics["closed_ports"].append(port_data)
                            elif state == "filtered":
                                metrics["filtered_ports"].append(port_data)
                            
                            if service != "unknown":
                                metrics["services"][str(port_num)] = {
                                    "name": service,
                                    "version": version,
                                    "state": state
                                }
                
            except Exception as e:
                logger.warning(f"Nmap scan failed: {e}")
                # Fallback: try basic port scanning with socket
                for port in ports:
                    try:
                        await self.safety_validator.add_rate_limit_delay(target_url)
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)
                        result = sock.connect_ex((hostname, port))
                        sock.close()
                        
                        port_data = {
                            "port": port,
                            "state": "open" if result == 0 else "closed",
                            "service": "unknown",
                            "version": ""
                        }
                        
                        if result == 0:
                            metrics["open_ports"].append(port_data)
                        else:
                            metrics["closed_ports"].append(port_data)
                    except Exception:
                        metrics["filtered_ports"].append({
                            "port": port,
                            "state": "filtered",
                            "service": "unknown",
                            "version": ""
                        })
            
        except Exception as e:
            logger.error(f"Network security scan error: {e}", exc_info=True)
            metrics["error"] = str(e)
        
        return metrics
    
    async def run_endpoint_discovery(
        self, 
        target_url: str, 
        discovery_method: str = "passive",
        user_permission: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Discover API endpoints and services"""
        # Validate safety
        is_valid, error_msg = self.safety_validator.validate_target(
            target_url, "endpoint_discovery", user_permission
        )
        
        if not is_valid:
            return {
                "error": error_msg,
                "discovery_blocked": True
            }
        
        # Apply rate limiting
        await self.safety_validator.add_rate_limit_delay(target_url)
        
        metrics = {
            "target": target_url,
            "endpoints_found": [],
            "total_endpoints": 0,
            "methods_detected": [],
            "status_codes": {},
            "average_response_time": 0,
            "discovery_method": discovery_method
        }
        
        try:
            import httpx
            
            base_url = target_url.rstrip('/')
            hostname = self._extract_hostname(target_url)
            
            # Common endpoints to try
            common_paths = [
                "/", "/api", "/api/v1", "/api/v2",
                "/health", "/status", "/ping",
                "/docs", "/swagger", "/openapi.json",
                "/admin", "/login", "/logout",
                "/users", "/products", "/data"
            ]
            
            # Common HTTP methods
            methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
            
            response_times = []
            
            async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                for path in common_paths:
                    try:
                        await self.safety_validator.add_rate_limit_delay(target_url)
                        
                        url = f"{base_url}{path}"
                        start_time = asyncio.get_event_loop().time()
                        
                        # Try GET first
                        try:
                            response = await client.get(url)
                            end_time = asyncio.get_event_loop().time()
                            response_time = (end_time - start_time) * 1000
                            
                            endpoint_data = {
                                "endpoint": path,
                                "method": "GET",
                                "status_code": response.status_code,
                                "response_time_ms": response_time,
                                "content_type": response.headers.get("content-type", ""),
                                "url": str(response.url)
                            }
                            
                            metrics["endpoints_found"].append(endpoint_data)
                            response_times.append(response_time)
                            
                            # Track status codes
                            status = str(response.status_code)
                            metrics["status_codes"][status] = metrics["status_codes"].get(status, 0) + 1
                            
                            # Track methods
                            if "GET" not in metrics["methods_detected"]:
                                metrics["methods_detected"].append("GET")
                            
                        except Exception:
                            pass
                        
                        # Try OPTIONS to discover allowed methods
                        try:
                            await self.safety_validator.add_rate_limit_delay(target_url)
                            options_response = await client.options(url)
                            allowed_methods = options_response.headers.get("Allow", "")
                            if allowed_methods:
                                for method in allowed_methods.split(','):
                                    method = method.strip()
                                    if method not in metrics["methods_detected"]:
                                        metrics["methods_detected"].append(method)
                        except Exception:
                            pass
                    
                    except Exception as e:
                        logger.debug(f"Endpoint discovery failed for {path}: {e}")
                        continue
            
            metrics["total_endpoints"] = len(metrics["endpoints_found"])
            
            if response_times:
                metrics["average_response_time"] = sum(response_times) / len(response_times)
            
        except Exception as e:
            logger.error(f"Endpoint discovery error: {e}", exc_info=True)
            metrics["error"] = str(e)
        
        return metrics

