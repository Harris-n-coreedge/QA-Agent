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
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from urllib.parse import urlparse
import logging
import ipaddress

logger = logging.getLogger(__name__)

# Try to import optional libraries with graceful fallback
try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP, sr1, sr, get_if_list
    from scapy.layers.inet import traceroute
    SCAPY_AVAILABLE = True
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
            
            # Test DNSSEC
            try:
                # Try to get DNSKEY record
                dnskeys = dns.resolver.resolve(hostname, 'DNSKEY', lifetime=5)
                metrics["dnssec_enabled"] = True
            except Exception:
                metrics["dnssec_enabled"] = False
                metrics["recommendations"].append("DNSSEC is not enabled")
            
            # DNS leak test - check which DNS servers are used
            try:
                resolver = dns.resolver.Resolver()
                metrics["dns_servers"] = [str(server) for server in resolver.nameservers]
                
                # Check if using public DNS (potential leak)
                public_dns = ['8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1']
                for server in metrics["dns_servers"]:
                    if server in public_dns:
                        metrics["dns_leak_detected"] = True
                        metrics["leaked_servers"].append(server)
            except Exception as e:
                logger.debug(f"DNS leak test error: {e}")
            
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
            "average_ping_time": 0,
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
            
            # Ping test (ICMP)
            if SCAPY_AVAILABLE:
                try:
                    ping_times = []
                    for _ in range(3):  # 3 ping attempts
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
                        except Exception:
                            pass
                    
                    if ping_times:
                        metrics["ping_times"] = ping_times
                        metrics["average_ping_time"] = sum(ping_times) / len(ping_times)
                except Exception as e:
                    logger.debug(f"Ping test failed (may require privileges): {e}")
                    metrics["issues_found"].append("ICMP ping test failed (may require admin privileges)")
            else:
                # Fallback: try socket connection as ping alternative
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    start_time = asyncio.get_event_loop().time()
                    result = sock.connect_ex((hostname, 80))
                    end_time = asyncio.get_event_loop().time()
                    sock.close()
                    
                    if result == 0:
                        metrics["ping_success"] = True
                        metrics["average_ping_time"] = (end_time - start_time) * 1000
                except Exception:
                    pass
            
            # DNS resolution test
            try:
                start_time = asyncio.get_event_loop().time()
                socket.gethostbyname(hostname)
                end_time = asyncio.get_event_loop().time()
                metrics["dns_resolution"] = True
                metrics["dns_resolution_time"] = (end_time - start_time) * 1000
            except Exception as e:
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
                metrics["recommendations"].append("Host may be unreachable or firewall blocking ICMP")
            if not metrics["dns_resolution"]:
                metrics["recommendations"].append("DNS resolution failed - check DNS servers")
            if not metrics["http_connection"] and not metrics["https_connection"]:
                metrics["recommendations"].append("No HTTP/HTTPS connectivity - check firewall rules")
            
        except Exception as e:
            logger.error(f"Connectivity diagnostics error: {e}", exc_info=True)
            metrics["error"] = str(e)
        
        return metrics
    
    async def run_protocol_traffic_analysis(
        self, 
        target_url: str, 
        duration: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze network traffic at packet level (passive)"""
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
            metrics["error"] = "Scapy not available for packet capture"
            return metrics
        
        try:
            hostname = self._extract_hostname(target_url)
            
            # Capture packets for specified duration
            captured_packets = []
            
            def packet_handler(packet):
                """Handle captured packets"""
                captured_packets.append(packet)
            
            # Sniff packets (passive - only captures, doesn't send)
            try:
                # Filter for traffic to/from target hostname
                # Note: This is a simplified filter - in production, you'd want more sophisticated filtering
                packets = await asyncio.to_thread(
                    sniff,
                    timeout=duration,
                    prn=packet_handler,
                    store=True,
                    filter=f"host {hostname}" if hostname else None
                )
                
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
                
            except Exception as e:
                logger.warning(f"Packet capture failed (may require privileges): {e}")
                metrics["error"] = f"Packet capture failed: {str(e)} (may require admin privileges)"
        
        except Exception as e:
            logger.error(f"Protocol traffic analysis error: {e}", exc_info=True)
            metrics["error"] = str(e)
        
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

