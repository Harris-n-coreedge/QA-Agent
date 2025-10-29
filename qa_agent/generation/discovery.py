"""
Flow discovery and auto-generation.
"""
from typing import List, Dict, Any, Set
from urllib.parse import urljoin, urlparse
import asyncio
from playwright.async_api import Page

from qa_agent.core.logging import get_logger

logger = get_logger(__name__)


class FlowDiscovery:
    """Discovers key user flows from websites."""
    
    def __init__(self):
        self.visited_urls: Set[str] = set()
        self.discovered_flows: List[Dict[str, Any]] = []
    
    async def discover_flows(
        self,
        page: Page,
        start_url: str,
        max_depth: int = 3,
        max_pages: int = 50
    ) -> List[Dict[str, Any]]:
        """Discover flows by crawling and analyzing pages."""
        logger.info("Starting flow discovery", start_url=start_url)
        
        self.visited_urls.clear()
        self.discovered_flows.clear()
        
        await self._crawl_site(page, start_url, max_depth, max_pages)
        await self._analyze_discovered_patterns()
        
        logger.info("Flow discovery completed", flows_found=len(self.discovered_flows))
        return self.discovered_flows
    
    async def _crawl_site(
        self,
        page: Page,
        start_url: str,
        max_depth: int,
        max_pages: int
    ) -> None:
        """Crawl the site to discover pages and interactions."""
        urls_to_visit = [(start_url, 0)]
        
        while urls_to_visit and len(self.visited_urls) < max_pages:
            current_url, depth = urls_to_visit.pop(0)
            
            if current_url in self.visited_urls or depth > max_depth:
                continue
            
            try:
                await page.goto(current_url, wait_until="domcontentloaded")
                self.visited_urls.add(current_url)
                
                # Discover links and forms
                links = await self._discover_links(page, current_url)
                forms = await self._discover_forms(page, current_url)
                
                # Add new URLs to visit
                for link in links:
                    if link not in self.visited_urls:
                        urls_to_visit.append((link, depth + 1))
                
                # Store page analysis
                await self._analyze_page(page, current_url, forms)
                
            except Exception as e:
                logger.warning("Error crawling page", url=current_url, error=str(e))
    
    async def _discover_links(self, page: Page, base_url: str) -> List[str]:
        """Discover all links on a page."""
        links = await page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a[href]'));
                return links.map(link => link.href).filter(href => href);
            }
        """)
        
        # Filter and normalize URLs
        valid_links = []
        base_domain = urlparse(base_url).netloc
        
        for link in links:
            parsed = urlparse(link)
            if parsed.netloc == base_domain or not parsed.netloc:
                normalized = urljoin(base_url, link)
                valid_links.append(normalized)
        
        return valid_links
    
    async def _discover_forms(self, page: Page, url: str) -> List[Dict[str, Any]]:
        """Discover forms on a page."""
        forms = await page.evaluate("""
            () => {
                const forms = Array.from(document.querySelectorAll('form'));
                return forms.map(form => {
                    const inputs = Array.from(form.querySelectorAll('input, select, textarea'));
                    return {
                        action: form.action,
                        method: form.method,
                        inputs: inputs.map(input => ({
                            type: input.type,
                            name: input.name,
                            placeholder: input.placeholder,
                            required: input.required,
                            label: input.labels?.[0]?.textContent?.trim()
                        }))
                    };
                });
            }
        """)
        
        return forms
    
    async def _analyze_page(
        self,
        page: Page,
        url: str,
        forms: List[Dict[str, Any]]
    ) -> None:
        """Analyze a page for flow patterns."""
        
        # Detect common flow patterns
        patterns = await self._detect_flow_patterns(page, url, forms)
        
        for pattern in patterns:
            self.discovered_flows.append({
                "url": url,
                "pattern": pattern,
                "confidence": pattern.get("confidence", 0.5)
            })
    
    async def _detect_flow_patterns(
        self,
        page: Page,
        url: str,
        forms: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect common flow patterns."""
        patterns = []
        
        # Login flow detection
        login_pattern = await self._detect_login_flow(page, forms)
        if login_pattern:
            patterns.append(login_pattern)
        
        # Signup flow detection
        signup_pattern = await self._detect_signup_flow(page, forms)
        if signup_pattern:
            patterns.append(signup_pattern)
        
        # Search flow detection
        search_pattern = await self._detect_search_flow(page, forms)
        if search_pattern:
            patterns.append(search_pattern)
        
        # Checkout flow detection
        checkout_pattern = await self._detect_checkout_flow(page, forms)
        if checkout_pattern:
            patterns.append(checkout_pattern)
        
        return patterns
    
    async def _detect_login_flow(self, page: Page, forms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect login flow patterns."""
        for form in forms:
            inputs = form.get("inputs", [])
            
            # Look for email/password combination
            has_email = any(
                inp.get("type") in ["email", "text"] and 
                ("email" in inp.get("name", "").lower() or "login" in inp.get("name", "").lower())
                for inp in inputs
            )
            
            has_password = any(
                inp.get("type") == "password"
                for inp in inputs
            )
            
            if has_email and has_password:
                return {
                    "type": "login",
                    "confidence": 0.9,
                    "form": form,
                    "steps": [
                        {"type": "click", "selector": "input[type='email'], input[name*='email']"},
                        {"type": "type", "selector": "input[type='email'], input[name*='email']", "text": "test@example.com"},
                        {"type": "click", "selector": "input[type='password']"},
                        {"type": "type", "selector": "input[type='password']", "text": "password123"},
                        {"type": "click", "selector": "button[type='submit'], input[type='submit']"}
                    ]
                }
        
        return None
    
    async def _detect_signup_flow(self, page: Page, forms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect signup flow patterns."""
        for form in forms:
            inputs = form.get("inputs", [])
            
            # Look for signup indicators
            signup_indicators = ["signup", "register", "create", "join"]
            form_text = str(form).lower()
            
            if any(indicator in form_text for indicator in signup_indicators):
                return {
                    "type": "signup",
                    "confidence": 0.8,
                    "form": form,
                    "steps": [
                        {"type": "click", "selector": "input[name*='email'], input[type='email']"},
                        {"type": "type", "selector": "input[name*='email'], input[type='email']", "text": "test@example.com"},
                        {"type": "click", "selector": "input[type='password']"},
                        {"type": "type", "selector": "input[type='password']", "text": "password123"},
                        {"type": "click", "selector": "button[type='submit'], input[type='submit']"}
                    ]
                }
        
        return None
    
    async def _detect_search_flow(self, page: Page, forms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect search flow patterns."""
        for form in forms:
            inputs = form.get("inputs", [])
            
            # Look for search input
            has_search = any(
                inp.get("type") in ["search", "text"] and 
                ("search" in inp.get("name", "").lower() or "query" in inp.get("name", "").lower())
                for inp in inputs
            )
            
            if has_search:
                return {
                    "type": "search",
                    "confidence": 0.7,
                    "form": form,
                    "steps": [
                        {"type": "click", "selector": "input[type='search'], input[name*='search']"},
                        {"type": "type", "selector": "input[type='search'], input[name*='search']", "text": "test query"},
                        {"type": "click", "selector": "button[type='submit'], input[type='submit']"}
                    ]
                }
        
        return None
    
    async def _detect_checkout_flow(self, page: Page, forms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect checkout flow patterns."""
        checkout_indicators = ["checkout", "payment", "billing", "order"]
        page_text = await page.text_content("body")
        
        if any(indicator in page_text.lower() for indicator in checkout_indicators):
            return {
                "type": "checkout",
                "confidence": 0.6,
                "steps": [
                    {"type": "click", "selector": "button:has-text('Checkout'), button:has-text('Buy')"},
                    {"type": "type", "selector": "input[name*='email']", "text": "test@example.com"},
                    {"type": "click", "selector": "button[type='submit']"}
                ]
            }
        
        return None
    
    async def _analyze_discovered_patterns(self) -> None:
        """Analyze and rank discovered patterns."""
        # Group similar patterns
        pattern_groups = {}
        for flow in self.discovered_flows:
            pattern_type = flow["pattern"]["type"]
            if pattern_type not in pattern_groups:
                pattern_groups[pattern_type] = []
            pattern_groups[pattern_type].append(flow)
        
        # Rank patterns by confidence and frequency
        ranked_patterns = []
        for pattern_type, flows in pattern_groups.items():
            avg_confidence = sum(f["confidence"] for f in flows) / len(flows)
            ranked_patterns.append({
                "type": pattern_type,
                "confidence": avg_confidence,
                "frequency": len(flows),
                "flows": flows
            })
        
        # Sort by confidence and frequency
        ranked_patterns.sort(key=lambda x: (x["confidence"], x["frequency"]), reverse=True)
        
        self.discovered_flows = ranked_patterns
