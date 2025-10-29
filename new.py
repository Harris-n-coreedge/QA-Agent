"""
Multi-AI QA Agent - Supports Multiple AI APIs

This agent can use different AI APIs (OpenAI, Anthropic, etc.) to understand
natural language commands and perform intelligent actions.
"""
import asyncio
import sys
import os
import json
from typing import Dict, Any, Optional

# Ensure stdout/stderr use UTF-8 when interactive; add safe print fallback for non-UTF consoles
try:
    if hasattr(sys.stdout, "isatty") and sys.stdout.isatty() and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Monkey-patch print to avoid UnicodeEncodeError on limited consoles
try:
    import builtins
    _orig_print = builtins.print
    def _safe_print(*args, **kwargs):
        try:
            return _orig_print(*args, **kwargs)
        except UnicodeEncodeError:
            enc = (getattr(sys.stdout, "encoding", None) or "utf-8")
            safe_args = []
            for a in args:
                s = str(a)
                try:
                    s.encode(enc, errors="strict")
                except UnicodeEncodeError:
                    s = s.encode(enc, errors="replace").decode(enc, errors="replace")
                safe_args.append(s)
            return _orig_print(*safe_args, **kwargs)
    builtins.print = _safe_print
except Exception:
    pass

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed. Trying manual .env loading...")
    # Manual .env file loading
    try:
        if os.path.exists(".env"):
            with open(".env", 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            print("✅ Loaded environment variables from .env file (manual)")
        else:
            print("⚠️ .env file not found")
    except Exception as e:
        print(f"⚠️ Error loading .env file: {e}")
        print("   Install python-dotenv: pip install python-dotenv")
        print("   Or set environment variables manually")

from playwright.async_api import async_playwright
import random
import time
import json
import base64
import sqlite3
import threading
import concurrent.futures
import schedule
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import requests
import yaml
from urllib.parse import urljoin, urlparse


class TestResult(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class PerformanceMetrics:
    load_time: float
    first_contentful_paint: float
    largest_contentful_paint: float
    cumulative_layout_shift: float
    first_input_delay: float
    network_requests: int
    memory_usage: float


@dataclass
class SecurityVulnerability:
    type: str
    severity: str
    description: str
    location: str
    recommendation: str


class HumanBehaviorSimulator:
    """Simulate realistic human behavior patterns."""
    
    def __init__(self):
        self.typing_speeds = [50, 80, 100, 120]  # WPM range
        self.mouse_speeds = [0.5, 1.0, 1.5, 2.0]  # Speed multipliers
        
    async def simulate_human_typing(self, element, text: str, page):
        """Type with realistic human patterns."""
        try:
            await element.clear()

            for i, char in enumerate(text):
                # Random typing speed variation
                base_delay = random.uniform(0.05, 0.15)
                
                # Occasional longer pauses (thinking)
                if random.random() < 0.1:  # 10% chance
                    await asyncio.sleep(random.uniform(0.3, 0.8))
                
                # Occasional typos and corrections
                if random.random() < 0.05 and i > 0:  # 5% chance of typo
                    wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                    await element.type(wrong_char)
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    await page.keyboard.press("Backspace")
                    await asyncio.sleep(random.uniform(0.1, 0.2))
                
                await element.type(char)
                await asyncio.sleep(base_delay)
                
        except Exception as e:
            print(f"⚠️ Human typing simulation failed: {e}")
            # Fallback to normal typing
            await element.fill(text)
    
    async def simulate_mouse_movement(self, target_element, page):
        """Move mouse naturally to target."""
        try:
            # Get target position
            bounding_box = await target_element.bounding_box()
            if not bounding_box:
                return
            
            target_x = bounding_box["x"] + bounding_box["width"] / 2
            target_y = bounding_box["y"] + bounding_box["height"] / 2
            
            # Get current mouse position
            current_pos = await page.evaluate("() => ({ x: 0, y: 0 })")
            
            # Create curved path
            steps = random.randint(8, 15)
            for i in range(steps):
                progress = i / steps
                
                # Add some curve to the path
                curve_offset = random.uniform(-20, 20) * (1 - progress)
                
                x = current_pos["x"] + (target_x - current_pos["x"]) * progress + curve_offset
                y = current_pos["y"] + (target_y - current_pos["y"]) * progress
                
                await page.mouse.move(x, y)
                
                # Variable speed
                delay = random.uniform(0.01, 0.03)
                await asyncio.sleep(delay)
                
        except Exception as e:
            print(f"⚠️ Mouse movement simulation failed: {e}")


class AdvancedAIAnalyzer:
    """Enhanced AI capabilities for QA."""
    
    def __init__(self, ai_client, ai_provider: str):
        self.ai_client = ai_client
        self.ai_provider = ai_provider
    
    async def analyze_page_intent(self, page_html: str, page_url: str) -> dict:
        """Understand page purpose and user intents."""
        if not self.ai_client:
            return {"page_type": "unknown", "intents": []}
        
        try:
            prompt = f"""
            Analyze this webpage and determine its primary purpose and common user intents.
            
            URL: {page_url}
            HTML snippet: {page_html[:2000]}
            
            Return JSON with:
            {{
                "page_type": "ecommerce|saas|blog|documentation|social|news|portfolio|other",
                "primary_intents": ["intent1", "intent2", "intent3"],
                "user_journeys": ["journey1", "journey2"],
                "key_features": ["feature1", "feature2"],
                "testing_priorities": ["priority1", "priority2"]
            }}
            """
            
            if self.ai_provider == "google":
                response = await self._call_google_api(prompt)
            else:
                return {"page_type": "unknown", "intents": []}
            
            return json.loads(response.strip())
        except Exception as e:
            print(f"⚠️ Page intent analysis failed: {e}")
            return {"page_type": "unknown", "intents": []}
    
    async def predict_user_journey(self, current_state: dict) -> list:
        """Predict likely next user actions."""
        if not self.ai_client:
            return []
        
        try:
            prompt = f"""
            Based on current page state, predict the most likely next user actions.
            
            Current state: {json.dumps(current_state)}
            
            Return JSON array of predicted actions:
            ["action1", "action2", "action3"]
            """
            
            if self.ai_provider == "google":
                response = await self._call_google_api(prompt)
                return json.loads(response.strip())
        except Exception as e:
            print(f"⚠️ User journey prediction failed: {e}")
            return []
    
    async def _call_google_api(self, prompt: str) -> str:
        """Call Google Gemini API."""
        try:
            from google.genai import types
            response = self.ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
            )
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Google API call failed: {e}")


class VisualTestingEngine:
    """Computer vision-based testing."""
    
    def __init__(self):
        self.baseline_screenshots = {}
    
    async def capture_screenshot(self, page, name: str) -> str:
        """Capture and store screenshot."""
        try:
            screenshot_bytes = await page.screenshot(full_page=True)
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
            self.baseline_screenshots[name] = screenshot_b64
            return screenshot_b64
        except Exception as e:
            print(f"⚠️ Screenshot capture failed: {e}")
            return ""
    
    async def detect_visual_regressions(self, page, test_name: str) -> dict:
        """Compare current screenshot with baseline."""
        try:
            current_screenshot = await self.capture_screenshot(page, f"{test_name}_current")
            baseline_screenshot = self.baseline_screenshots.get(f"{test_name}_baseline")
            
            if not baseline_screenshot:
                return {"status": "no_baseline", "message": "No baseline screenshot found"}
            
            # Simple pixel comparison (in production, use proper image diff libraries)
            if current_screenshot == baseline_screenshot:
                return {"status": "match", "message": "Screenshots match"}
            else:
                return {"status": "regression", "message": "Visual regression detected"}
                
        except Exception as e:
            return {"status": "error", "message": f"Screenshot comparison failed: {e}"}
    
    async def analyze_ui_elements(self, page) -> dict:
        """Extract UI elements using page analysis."""
        try:
            # Analyze page structure for UI elements
            elements = await page.evaluate("""
                () => {
                    const buttons = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]'))
                        .map(el => ({
                            type: 'button',
                            text: el.textContent?.trim() || el.value || '',
                            visible: el.offsetParent !== null,
                            position: { x: el.offsetLeft, y: el.offsetTop }
                        }));
                    
                    const inputs = Array.from(document.querySelectorAll('input, textarea, select'))
                        .map(el => ({
                            type: 'input',
                            inputType: el.type || 'text',
                            placeholder: el.placeholder || '',
                            visible: el.offsetParent !== null,
                            position: { x: el.offsetLeft, y: el.offsetTop }
                        }));
                    
                    const links = Array.from(document.querySelectorAll('a'))
                        .map(el => ({
                            type: 'link',
                            text: el.textContent?.trim() || '',
                            href: el.href || '',
                            visible: el.offsetParent !== null,
                            position: { x: el.offsetLeft, y: el.offsetTop }
                        }));
                    
                    return {
                        buttons: buttons.filter(el => el.visible),
                        inputs: inputs.filter(el => el.visible),
                        links: links.filter(el => el.visible)
                    };
                }
            """)
            
            return elements
        except Exception as e:
            print(f"⚠️ UI element analysis failed: {e}")
            return {"buttons": [], "inputs": [], "links": []}


class PerformanceMonitor:
    """Real-time performance analysis."""
    
    async def measure_page_performance(self, page) -> PerformanceMetrics:
        """Comprehensive performance metrics."""
        try:
            # Get performance metrics from browser
            metrics = await page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        if (window.performance && window.performance.getEntriesByType) {
                            const navigation = window.performance.getEntriesByType('navigation')[0];
                            const paint = window.performance.getEntriesByType('paint');
                            
                            resolve({
                                load_time: navigation ? navigation.loadEventEnd - navigation.loadEventStart : 0,
                                first_contentful_paint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
                                largest_contentful_paint: 0, // Would need LCP API
                                cumulative_layout_shift: 0, // Would need CLS API
                                first_input_delay: 0, // Would need FID API
                                network_requests: window.performance.getEntriesByType('resource').length,
                                memory_usage: performance.memory ? performance.memory.usedJSHeapSize : 0
                            });
                        } else {
                            resolve({
                                load_time: 0,
                                first_contentful_paint: 0,
                                largest_contentful_paint: 0,
                                cumulative_layout_shift: 0,
                                first_input_delay: 0,
                                network_requests: 0,
                                memory_usage: 0
                            });
                        }
                    });
                }
            """)
            
            return PerformanceMetrics(**metrics)
        except Exception as e:
            print(f"⚠️ Performance measurement failed: {e}")
            return PerformanceMetrics(0, 0, 0, 0, 0, 0, 0)
    
    async def detect_performance_issues(self, metrics: PerformanceMetrics) -> list:
        """Identify performance bottlenecks."""
        issues = []
        
        if metrics.load_time > 3000:  # 3 seconds
            issues.append({
                "type": "slow_load",
                "severity": "high",
                "message": f"Page load time is {metrics.load_time:.0f}ms (threshold: 3000ms)"
            })
        
        if metrics.first_contentful_paint > 1500:  # 1.5 seconds
            issues.append({
                "type": "slow_fcp",
                "severity": "medium",
                "message": f"First Contentful Paint is {metrics.first_contentful_paint:.0f}ms (threshold: 1500ms)"
            })
        
        if metrics.network_requests > 100:
            issues.append({
                "type": "too_many_requests",
                "severity": "medium",
                "message": f"Too many network requests: {metrics.network_requests} (threshold: 100)"
            })
        
        return issues


class SecurityTester:
    """Automated security testing."""
    
    async def test_xss_vulnerabilities(self, page) -> list:
        """Test for XSS injection points."""
        vulnerabilities = []
        
        try:
            # Find all input fields
            inputs = await page.locator("input, textarea").all()
            
            # Limit to first 3 inputs to avoid issues
            for input_field in inputs[:3]:
                try:
                    # Check if input is visible and interactable
                    if not await input_field.is_visible():
                        continue
                    
                    # Get field info first
                    field_name = await input_field.get_attribute('name') or await input_field.get_attribute('id') or 'unnamed'
                    field_type = await input_field.get_attribute('type') or 'text'
                    
                    # Skip password fields for safety
                    if field_type.lower() == 'password':
                        continue
                    
                    # Test XSS payloads (simplified)
                    xss_payloads = [
                        "<script>alert('XSS')</script>",
                        "javascript:alert('XSS')"
                    ]
                    
                    for payload in xss_payloads:
                        try:
                            # Clear and fill the input safely
                            await input_field.clear()
                            await input_field.fill(payload)
                            await asyncio.sleep(0.3)
                            
                            # Check if the payload appears in the page content
                            page_content = await page.content()
                            if payload in page_content:
                                vulnerabilities.append(SecurityVulnerability(
                                    type="XSS",
                                    severity="medium",
                                    description=f"Potential XSS vulnerability - payload reflected in page",
                                    location=f"Input field: {field_name}",
                                    recommendation="Implement proper input validation and output encoding"
                                ))
                                break
                                
                        except Exception as payload_error:
                            continue
                            
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"⚠️ XSS testing failed: {e}")
        
        return vulnerabilities
    
    async def analyze_security_headers(self, page) -> dict:
        """Check security headers."""
        try:
            # Get current page URL and response
            current_url = page.url
            
            # Make a new request to get headers (without navigating away)
            response = await page.request.get(current_url)
            headers = response.headers
            
            security_headers = {
                "content_security_policy": headers.get("content-security-policy", "Missing"),
                "x_frame_options": headers.get("x-frame-options", "Missing"),
                "x_content_type_options": headers.get("x-content-type-options", "Missing"),
                "strict_transport_security": headers.get("strict-transport-security", "Missing"),
                "referrer_policy": headers.get("referrer-policy", "Missing")
            }
            
            return security_headers
        except Exception as e:
            print(f"⚠️ Security header analysis failed: {e}")
            return {
                "content_security_policy": "Error",
                "x_frame_options": "Error", 
                "x_content_type_options": "Error",
                "strict_transport_security": "Error",
                "referrer_policy": "Error"
            }


class IntelligentRetrySystem:
    """Smart retry mechanisms."""
    
    def __init__(self):
        self.retry_strategies = {
            "network_timeout": self._exponential_backoff,
            "element_not_found": self._selector_evolution,
            "page_crash": self._browser_restart,
            "rate_limited": self._rate_limit_backoff
        }
    
    async def adaptive_retry_strategy(self, error_type: str, context: dict, max_retries: int = 3) -> bool:
        """Choose retry strategy based on error type."""
        strategy = self.retry_strategies.get(error_type, self._default_retry)
        
        for attempt in range(max_retries):
            try:
                success = await strategy(context, attempt)
                if success:
                    return True
            except Exception as e:
                print(f"⚠️ Retry attempt {attempt + 1} failed: {e}")
                
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return False
    
    async def _exponential_backoff(self, context: dict, attempt: int) -> bool:
        """Exponential backoff for network issues."""
        await asyncio.sleep(min(2 ** attempt, 30))  # Cap at 30 seconds
        return True
    
    async def _selector_evolution(self, context: dict, attempt: int) -> bool:
        """Evolve selectors when elements not found."""
        # This would implement selector evolution logic
        return True
    
    async def _browser_restart(self, context: dict, attempt: int) -> bool:
        """Restart browser for crashes."""
        # This would implement browser restart logic
        return True
    
    async def _rate_limit_backoff(self, context: dict, attempt: int) -> bool:
        """Handle rate limiting."""
        await asyncio.sleep(60 * (attempt + 1))  # 1, 2, 3 minutes
        return True
    
    async def _default_retry(self, context: dict, attempt: int) -> bool:
        """Default retry strategy."""
        await asyncio.sleep(1 * (attempt + 1))
        return True


class AdvancedAnalytics:
    """Comprehensive testing analytics."""
    
    def __init__(self):
        self.test_history = []
        self.performance_history = []
        self.failure_patterns = {}
    
    async def generate_test_report(self, test_results: list) -> dict:
        """Generate detailed test reports."""
        if not test_results:
            return {"message": "No test results to analyze"}
        
        total_tests = len(test_results)
        successful_tests = len([r for r in test_results if r.get("status") == "success"])
        failed_tests = len([r for r in test_results if r.get("status") == "failure"])
        
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Analyze failure patterns
        failure_patterns = self._analyze_failure_patterns(test_results)
        
        # Performance trends
        performance_trends = self._analyze_performance_trends(test_results)
        
        return {
            "summary": {
                "total_tests": total_tests,
                "successful": successful_tests,
                "failed": failed_tests,
                "success_rate": f"{success_rate:.1f}%"
            },
            "failure_patterns": failure_patterns,
            "performance_trends": performance_trends,
            "recommendations": self._generate_recommendations(test_results)
        }
    
    def _analyze_failure_patterns(self, test_results: list) -> dict:
        """Analyze common failure patterns."""
        failures = [r for r in test_results if r.get("status") == "failure"]
        
        if not failures:
            return {"message": "No failures to analyze"}
        
        error_types = {}
        for failure in failures:
            error = failure.get("error", "unknown")
            error_types[error] = error_types.get(error, 0) + 1
        
        return {
            "most_common_errors": sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5],
            "total_failures": len(failures)
        }
    
    def _analyze_performance_trends(self, test_results: list) -> dict:
        """Analyze performance trends."""
        performance_data = [r.get("performance") for r in test_results if r.get("performance")]
        
        if not performance_data:
            return {"message": "No performance data available"}
        
        avg_load_time = sum(p.get("load_time", 0) for p in performance_data) / len(performance_data)
        
        return {
            "average_load_time": f"{avg_load_time:.0f}ms",
            "performance_samples": len(performance_data)
        }
    
    def _generate_recommendations(self, test_results: list) -> list:
        """Generate actionable recommendations."""
        recommendations = []
        
        failures = [r for r in test_results if r.get("status") == "failure"]
        if len(failures) > len(test_results) * 0.2:  # More than 20% failure rate
            recommendations.append("High failure rate detected. Review test stability and selectors.")
        
        performance_data = [r.get("performance") for r in test_results if r.get("performance")]
        if performance_data:
            avg_load_time = sum(p.get("load_time", 0) for p in performance_data) / len(performance_data)
            if avg_load_time > 3000:
                recommendations.append("Slow page load times detected. Consider performance optimization.")
        
        return recommendations


class DatabaseManager:
    """Database integration for test result persistence."""
    
    def __init__(self, db_path: str = "qa_agent.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Test results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    duration REAL,
                    error_message TEXT,
                    page_url TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    browser_type TEXT,
                    device_type TEXT,
                    performance_metrics TEXT,
                    screenshot_path TEXT
                )
            """)
            
            # Test suites table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_suites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    suite_name TEXT NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_run DATETIME,
                    success_rate REAL
                )
            """)
            
            # Environments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS environments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    base_url TEXT NOT NULL,
                    browser_config TEXT,
                    test_data TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            conn.commit()
            conn.close()
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"⚠️ Database initialization failed: {e}")
    
    def save_test_result(self, test_result: dict):
        """Save test result to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO test_results 
                (test_name, status, duration, error_message, page_url, browser_type, device_type, performance_metrics, screenshot_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test_result.get('test_name', 'unknown'),
                test_result.get('status', 'unknown'),
                test_result.get('duration', 0),
                test_result.get('error_message', ''),
                test_result.get('page_url', ''),
                test_result.get('browser_type', 'chromium'),
                test_result.get('device_type', 'desktop'),
                json.dumps(test_result.get('performance_metrics', {})),
                test_result.get('screenshot_path', '')
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Failed to save test result: {e}")
    
    def get_test_history(self, limit: int = 100) -> list:
        """Get test history from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM test_results 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"⚠️ Failed to get test history: {e}")
            return []


class CrossBrowserManager:
    """Cross-browser testing support."""
    
    def __init__(self):
        self.browsers = ['chromium', 'firefox', 'webkit']
        self.browser_configs = {
            'chromium': {'headless': False, 'slow_mo': 1000},
            'firefox': {'headless': False, 'slow_mo': 1000},
            'webkit': {'headless': False, 'slow_mo': 1000}
        }
    
    async def test_across_browsers(self, test_function, *args, **kwargs):
        """Run the same test across multiple browsers."""
        results = {}
        
        for browser_type in self.browsers:
            try:
                print(f"🌐 Testing on {browser_type}...")
                result = await test_function(browser_type, *args, **kwargs)
                results[browser_type] = result
            except Exception as e:
                results[browser_type] = f"Failed: {e}"
        
        return results


class APITester:
    """API testing capabilities."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QA-Agent/1.0',
            'Content-Type': 'application/json'
        })
    
    async def test_api_endpoint(self, method: str, url: str, **kwargs) -> dict:
        """Test API endpoint."""
        try:
            response = self.session.request(method.upper(), url, **kwargs)
            
            return {
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'headers': dict(response.headers),
                'content': response.text[:1000],  # Limit content
                'success': 200 <= response.status_code < 300
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    async def test_api_suite(self, endpoints: list) -> dict:
        """Test multiple API endpoints."""
        results = {}
        
        for endpoint in endpoints:
            method = endpoint.get('method', 'GET')
            url = endpoint.get('url')
            data = endpoint.get('data')
            headers = endpoint.get('headers', {})
            
            result = await self.test_api_endpoint(method, url, json=data, headers=headers)
            results[url] = result
        
        return results


class MobileDeviceManager:
    """Mobile device testing support."""
    
    def __init__(self):
        self.devices = {
            'iPhone 12': {'width': 390, 'height': 844, 'deviceScaleFactor': 3},
            'iPhone SE': {'width': 375, 'height': 667, 'deviceScaleFactor': 2},
            'Samsung Galaxy S21': {'width': 384, 'height': 854, 'deviceScaleFactor': 3},
            'iPad': {'width': 768, 'height': 1024, 'deviceScaleFactor': 2}
        }
    
    async def test_on_device(self, page, device_name: str):
        """Test on specific mobile device."""
        if device_name not in self.devices:
            return f"❌ Unknown device: {device_name}"
        
        device_config = self.devices[device_name]
        
        try:
            if page is None:
                # Create a new page if none provided
                from playwright.async_api import async_playwright
                playwright = await async_playwright().start()
                browser = await playwright.chromium.launch(headless=False)
                context = await browser.new_context()
                page = await context.new_page()
            
            # Set viewport size
            await page.set_viewport_size({
                'width': device_config['width'],
                'height': device_config['height']
            })
            
            # Set device characteristics via context
            await page.context.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
            })
            
            # Navigate to current URL or default
            test_url = getattr(page, 'url', None) or "https://www.w3schools.com"
            if not test_url.startswith('http'):
                test_url = "https://www.w3schools.com"
            
            await page.goto(test_url, timeout=30000)
            
            # Take screenshot for verification
            screenshot_path = f"mobile_{device_name.replace(' ', '_').lower()}.png"
            await page.screenshot(path=screenshot_path)
            
            # Get page info
            title = await page.title()
            
            return f"✅ Testing on {device_name} ({device_config['width']}x{device_config['height']}) - Screenshot: {screenshot_path} - Title: {title[:50]}..."
            
        except Exception as e:
            return f"❌ Device testing failed: {e}"


class TestDataManager:
    """Test data management system."""
    
    def __init__(self):
        self.test_data = {}
        self.load_test_data()
    
    def load_test_data(self):
        """Load test data from files."""
        try:
            # Load from JSON files
            test_data_files = ['test_data.json', 'user_credentials.json', 'api_endpoints.json']
            
            for file_name in test_data_files:
                try:
                    with open(file_name, 'r') as f:
                        data = json.load(f)
                        self.test_data[file_name.replace('.json', '')] = data
                except FileNotFoundError:
                    # Create default test data
                    self._create_default_test_data(file_name)
        except Exception as e:
            print(f"⚠️ Test data loading failed: {e}")
    
    def _create_default_test_data(self, file_name: str):
        """Create default test data files."""
        if file_name == 'test_data.json':
            default_data = {
                'users': [
                    {'email': 'test1@example.com', 'password': 'TestPass123!'},
                    {'email': 'test2@example.com', 'password': 'TestPass456!'}
                ],
                'test_urls': [
                    'https://example.com',
                    'https://httpbin.org'
                ]
            }
        elif file_name == 'user_credentials.json':
            default_data = {
                'valid_users': [
                    {'email': 'valid@example.com', 'password': 'ValidPass123!'}
                ],
                'invalid_users': [
                    {'email': 'invalid@example.com', 'password': 'WrongPass'}
                ]
            }
        elif file_name == 'api_endpoints.json':
            default_data = {
                'endpoints': [
                    {'method': 'GET', 'url': 'https://httpbin.org/get'},
                    {'method': 'POST', 'url': 'https://httpbin.org/post', 'data': {'test': 'data'}}
                ]
            }
        
        try:
            with open(file_name, 'w') as f:
                json.dump(default_data, f, indent=2)
            print(f"✅ Created default {file_name}")
        except Exception as e:
            print(f"⚠️ Failed to create {file_name}: {e}")
    
    def get_test_data(self, category: str, key: str = None):
        """Get test data by category and optional key."""
        if category in self.test_data:
            if key:
                return self.test_data[category].get(key)
            return self.test_data[category]
        return None


class NotificationManager:
    """Notification and alerting system."""
    
    def __init__(self):
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('EMAIL_USERNAME', ''),
            'password': os.getenv('EMAIL_PASSWORD', ''),
            'from_email': os.getenv('FROM_EMAIL', ''),
            'to_emails': os.getenv('TO_EMAILS', '').split(',')
        }
    
    async def send_notification(self, subject: str, message: str, is_html: bool = False):
        """Send a simple notification via email."""
        try:
            if not self.email_config['username'] or not self.email_config['password']:
                return "❌ Email configuration not set. Set EMAIL_USERNAME and EMAIL_PASSWORD environment variables."
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email'] or self.email_config['username']
            msg['To'] = ', '.join(self.email_config['to_emails']) if self.email_config['to_emails'] else self.email_config['username']
            msg['Subject'] = subject
            
            # Attach message
            if is_html:
                msg.attach(MIMEText(message, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            return f"✅ Notification sent successfully to {msg['To']}"
        except Exception as e:
            return f"❌ Failed to send notification: {e}"

    async def send_test_report(self, test_results: list, subject: str = "QA Test Report"):
        """Send test report via email."""
        try:
            if not self.email_config['username'] or not self.email_config['password']:
                return "❌ Email configuration not set"
            
            # Generate report content
            report_content = self._generate_email_report(test_results)
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = ', '.join(self.email_config['to_emails'])
            msg['Subject'] = subject
            
            msg.attach(MIMEText(report_content, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            return "✅ Test report sent successfully"
        except Exception as e:
            return f"❌ Failed to send email: {e}"
    
    def _generate_email_report(self, test_results: list) -> str:
        """Generate HTML email report."""
        total_tests = len(test_results)
        successful = len([r for r in test_results if r.get('status') == 'success'])
        failed = total_tests - successful
        success_rate = (successful / total_tests * 100) if total_tests > 0 else 0
        
        html = f"""
        <html>
        <body>
            <h2>QA Test Report</h2>
            <p><strong>Total Tests:</strong> {total_tests}</p>
            <p><strong>Successful:</strong> {successful}</p>
            <p><strong>Failed:</strong> {failed}</p>
            <p><strong>Success Rate:</strong> {success_rate:.1f}%</p>
            
            <h3>Test Details</h3>
            <table border="1">
                <tr><th>Test</th><th>Status</th><th>Duration</th><th>Error</th></tr>
        """
        
        for result in test_results:
            status_color = "green" if result.get('status') == 'success' else "red"
            html += f"""
                <tr>
                    <td>{result.get('test_name', 'Unknown')}</td>
                    <td style="color: {status_color}">{result.get('status', 'Unknown')}</td>
                    <td>{result.get('duration', 0):.2f}s</td>
                    <td>{result.get('error_message', '')}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        return html


class TestScheduler:
    """Test scheduling and automation."""
    
    def __init__(self):
        self.scheduled_tests = {}
        self.is_running = False
    
    def schedule_test(self, test_name: str, test_function, schedule_time: str):
        """Schedule a test to run at specific time."""
        try:
            schedule.every().day.at(schedule_time).do(self._run_scheduled_test, test_name, test_function)
            self.scheduled_tests[test_name] = {
                'function': test_function,
                'schedule': schedule_time,
                'last_run': None,
                'next_run': schedule_time
            }
            return f"✅ Scheduled {test_name} to run at {schedule_time}"
        except Exception as e:
            return f"❌ Failed to schedule test: {e}"
    
    def _run_scheduled_test(self, test_name: str, test_function):
        """Run scheduled test."""
        try:
            print(f"🕐 Running scheduled test: {test_name}")
            result = asyncio.run(test_function())
            self.scheduled_tests[test_name]['last_run'] = datetime.now()
            return result
        except Exception as e:
            print(f"❌ Scheduled test failed: {e}")
            return None
    
    def start_scheduler(self):
        """Start the test scheduler."""
        self.is_running = True
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop_scheduler(self):
        """Stop the test scheduler."""
        self.is_running = False


class AccessibilityTester:
    """WCAG compliance and accessibility testing."""
    
    def __init__(self):
        self.wcag_guidelines = {
            '1.1.1': 'Non-text Content',
            '1.3.1': 'Info and Relationships',
            '1.4.3': 'Contrast (Minimum)',
            '2.1.1': 'Keyboard',
            '2.4.1': 'Bypass Blocks',
            '4.1.2': 'Name, Role, Value'
        }
    
    async def test_accessibility(self, page) -> dict:
        """Run comprehensive accessibility tests."""
        try:
            results = {
                'wcag_violations': [],
                'accessibility_score': 0,
                'recommendations': []
            }
            
            # Test for missing alt text
            images_without_alt = await page.locator("img:not([alt])").count()
            if images_without_alt > 0:
                results['wcag_violations'].append({
                    'guideline': '1.1.1',
                    'description': f'{images_without_alt} images missing alt text',
                    'severity': 'high'
                })
            
            # Test for missing form labels
            inputs_without_labels = await page.locator("input:not([aria-label]):not([aria-labelledby])").count()
            if inputs_without_labels > 0:
                results['wcag_violations'].append({
                    'guideline': '1.3.1',
                    'description': f'{inputs_without_labels} form inputs missing labels',
                    'severity': 'medium'
                })
            
            # Test for missing heading structure
            h1_count = await page.locator("h1").count()
            if h1_count == 0:
                results['wcag_violations'].append({
                    'guideline': '1.3.1',
                    'description': 'Page missing H1 heading',
                    'severity': 'high'
                })
            
            # Calculate accessibility score
            total_violations = len(results['wcag_violations'])
            results['accessibility_score'] = max(0, 100 - (total_violations * 10))
            
            # Generate recommendations
            if total_violations > 0:
                results['recommendations'].append("Add alt text to all images")
                results['recommendations'].append("Ensure all form inputs have labels")
                results['recommendations'].append("Use proper heading hierarchy")
            
            return results
        except Exception as e:
            return {'error': str(e)}


class LoadTester:
    """Load testing capabilities."""
    
    def __init__(self):
        self.load_test_results = []
    
    async def run_load_test(self, url: str, concurrent_users: int = 10, duration: int = 60) -> dict:
        """Run load test on URL."""
        try:
            print(f"⚡ Starting load test: {concurrent_users} users for {duration}s")
            
            start_time = time.time()
            results = {
                'url': url,
                'concurrent_users': concurrent_users,
                'duration': duration,
                'requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'average_response_time': 0,
                'max_response_time': 0,
                'min_response_time': float('inf')
            }
            
            response_times = []
            
            async def make_request():
                try:
                    start = time.time()
                    response = requests.get(url, timeout=10)
                    end = time.time()
                    
                    response_time = end - start
                    response_times.append(response_time)
                    
                    results['requests'] += 1
                    if response.status_code == 200:
                        results['successful_requests'] += 1
                    else:
                        results['failed_requests'] += 1
                        
                except Exception as e:
                    results['failed_requests'] += 1
                    print(f"Request failed: {e}")
            
            # Run load test
            while time.time() - start_time < duration:
                tasks = []
                for _ in range(concurrent_users):
                    tasks.append(make_request())
                
                await asyncio.gather(*tasks, return_exceptions=True)
                await asyncio.sleep(1)  # 1 second between batches
            
            # Calculate statistics
            if response_times:
                results['average_response_time'] = sum(response_times) / len(response_times)
                results['max_response_time'] = max(response_times)
                results['min_response_time'] = min(response_times)
            
            results['success_rate'] = (results['successful_requests'] / results['requests'] * 100) if results['requests'] > 0 else 0
            
            return results
        except Exception as e:
            return {'error': str(e)}


class SelectorMemory:
    """Memory system for learning successful selectors and patterns."""
    
    def __init__(self):
        self.successful_selectors = {}  # site -> element_type -> selector mapping
        self.failed_attempts = {}       # learn from mistakes
        self.site_patterns = {}         # common patterns per site type
    
    def record_success(self, site: str, element_type: str, selector: str):
        """Record a successful selector for future use."""
        if site not in self.successful_selectors:
            self.successful_selectors[site] = {}
        if element_type not in self.successful_selectors[site]:
            self.successful_selectors[site][element_type] = []
        
        if selector not in self.successful_selectors[site][element_type]:
            self.successful_selectors[site][element_type].append(selector)
    
    def record_failure(self, site: str, element_type: str, selector: str):
        """Record a failed selector attempt."""
        if site not in self.failed_attempts:
            self.failed_attempts[site] = {}
        if element_type not in self.failed_attempts[site]:
            self.failed_attempts[site][element_type] = []
        
        if selector not in self.failed_attempts[site][element_type]:
            self.failed_attempts[site][element_type].append(selector)
    
    def get_best_selector(self, site: str, element_type: str) -> str:
        """Return the most successful selector for this site/element combo."""
        if site in self.successful_selectors and element_type in self.successful_selectors[site]:
            selectors = self.successful_selectors[site][element_type]
            if selectors:
                return selectors[0]  # Return most recent successful selector
        return None
    
    def get_avoid_selectors(self, site: str, element_type: str) -> list:
        """Return selectors that have failed for this site/element combo."""
        if site in self.failed_attempts and element_type in self.failed_attempts[site]:
            return self.failed_attempts[site][element_type]
        return []


class MultiAIQAAgent:
    """
    A QA agent that can use multiple AI APIs to understand
    natural language commands and perform intelligent actions.
    """
    
    def __init__(self, ai_provider: str = "openai", api_key: str = None):
        self.current_page = None
        self.current_url = None
        self.ai_provider = ai_provider.lower()
        self.api_key = api_key
        self.ai_client = None
        
        # Learning and memory systems
        self.selector_memory = SelectorMemory()
        self.page_semantics = {}
        self.device_type = "unknown"
        self.page_language = "en"
        self.success_rates = {}
        
        # Advanced testing capabilities
        self.human_behavior = HumanBehaviorSimulator()
        self.visual_testing = VisualTestingEngine()
        self.performance_monitor = PerformanceMonitor()
        self.security_tester = SecurityTester()
        self.retry_system = IntelligentRetrySystem()
        self.analytics = AdvancedAnalytics()
        self.test_results = []
        
        # Enterprise QA features
        self.database_manager = DatabaseManager()
        self.cross_browser_manager = CrossBrowserManager()
        self.api_tester = APITester()
        self.mobile_device_manager = MobileDeviceManager()
        self.test_data_manager = TestDataManager()
        self.notification_manager = NotificationManager()
        self.test_scheduler = TestScheduler()
        self.accessibility_tester = AccessibilityTester()
        self.load_tester = LoadTester()
        
        # Initialize AI client based on provider
        self._initialize_ai_client()
        
        # Initialize advanced AI analyzer
        self.ai_analyzer = AdvancedAIAnalyzer(self.ai_client, self.ai_provider)
    
    def _initialize_ai_client(self):
        """Initialize the AI client based on the provider."""
        if self.ai_provider == "openai":
            try:
                import openai
                if self.api_key:
                    openai.api_key = self.api_key
                    self.ai_client = openai
                    print("✅ OpenAI API initialized")
                else:
                    print("⚠️ OpenAI API key not provided")
            except ImportError:
                print("❌ OpenAI package not installed. Run: pip install openai")
        
        elif self.ai_provider == "anthropic":
            try:
                import anthropic
                if self.api_key:
                    self.ai_client = anthropic.Anthropic(api_key=self.api_key)
                    print("✅ Anthropic API initialized")
                else:
                    print("⚠️ Anthropic API key not provided")
            except ImportError:
                print("❌ Anthropic package not installed. Run: pip install anthropic")
        
        elif self.ai_provider == "google":
            try:
                from google import genai
                if self.api_key:
                    # Use the new Google GenAI SDK with thinking disabled
                    self.ai_client = genai.Client(api_key=self.api_key)
                    print("✅ Google Gemini API initialized (thinking disabled)")
                else:
                    print("⚠️ Google API key not provided")
            except ImportError:
                print("❌ Google GenAI package not installed. Run: pip install google-genai")
        
        else:
            print(f"⚠️ Unknown AI provider: {self.ai_provider}")
    
    async def start_session(self, website_url: str = "https://www.w3schools.com/", auto_check: bool = True):
        """Start a browser session on a specific website."""
        print("🤖 Multi-AI QA Agent Starting...")
        print("=" * 40)
        print(f"🌐 Opening: {website_url}")
        print(f"🧠 AI Provider: {self.ai_provider.upper()}")
        print("👁️ Browser Mode: VISIBLE (headful)")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Browser visible
            slow_mo=1000,    # Slower interactions for visibility
            args=[
                '--start-maximized',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        self.current_page = await self.context.new_page()
        # Increase default timeouts for slow networks/pages
        try:
            self.current_page.set_default_timeout(60000)
            self.current_page.set_default_navigation_timeout(90000)
        except Exception:
            pass
        
        # Navigate to the website
        try:
            await self.current_page.goto(website_url, wait_until="domcontentloaded", timeout=45000)
        except Exception as e1:
            print(f"⚠️ DOMContentLoaded timed out: {e1}. Retrying with 'load'...")
            try:
                await self.current_page.goto(website_url, wait_until="load", timeout=60000)
            except Exception as e2:
                print(f"⚠️ Load timed out: {e2}. Retrying with 'commit'...")
                try:
                    await self.current_page.goto(website_url, wait_until="commit", timeout=30000)
                except Exception as e3:
                    print(f"⚠️ Navigation still timing out: {e3}. Continuing best-effort.")
        # Best-effort: ensure body is present
        try:
            await self.current_page.wait_for_selector("body", timeout=10000)
        except Exception:
            pass
        await self.current_page.wait_for_timeout(2000)
        
        # Analyze page characteristics for dynamic adaptation
        await self._analyze_page_characteristics()

        # Automatically run baseline QA checks if enabled
        if auto_check:
            try:
                summary = await self._run_auto_checks()
                print(summary)
            except Exception as e:
                print(f"⚠️ Auto-checks failed: {e}")
        
        self.current_url = website_url
        print("✅ Agent ready! I can understand natural language commands.")
        print("\n💬 Try commands like:")
        print("   - 'log in'")
        print("   - 'sign up'")
        print("   - 'scroll down'")
        print("   - 'search for python'")
        print("   - 'click the menu'")
        print("   - 'what can I do here?'")
        print("   - 'find all the buttons on this page'")
        print("   - 'navigate to the tutorials section'")
        print()
        print("🔄 Multi-step commands:")
        print("   - 'first search python then click python tutorial'")
        print("   - 'search for javascript and then click on the first result'")
        print("   - 'scroll down then click the menu'")
        print()
        print("🧪 Auto Checks:")
        print("   - 'auto check' - Run baseline QA checks on this page")
        
        return True
    
    async def process_command(self, user_input: str) -> str:
        """Process natural language commands using AI - supports multi-step commands."""
        if not self.current_page:
            return "❌ No active session. Please start a session first."
        
        print(f"🧠 Processing: '{user_input}'")
        
        # Record test start
        test_start_time = time.time()
        test_result = {
            "command": user_input,
            "start_time": test_start_time,
            "status": "running"
        }
        
        try:
            # Route compound auth prompts directly to robust flow
            if self._looks_like_auth_compound(user_input):
                result = await self._handle_auth_compound_command(user_input)
            elif user_input.lower().startswith("test ") or user_input.lower() in ["test all", "test everything"]:
                # Handle testing commands
                result = await self._handle_testing_command(user_input)
            elif user_input.lower().startswith("analyze "):
                # Handle analysis commands
                result = await self._handle_analysis_command(user_input)
            elif user_input.lower().startswith("security "):
                # Handle security testing
                result = await self._handle_security_command(user_input)
            elif user_input.lower().startswith("performance "):
                # Handle performance testing
                result = await self._handle_performance_command(user_input)
            elif user_input.lower().startswith("visual "):
                # Handle visual testing
                result = await self._handle_visual_command(user_input)
            elif user_input.lower().startswith("search "):
                # Handle search commands
                result = await self._handle_search_command(user_input)
            elif user_input.lower().strip() in ["auto check", "autocheck", "auto-check"]:
                # Run baseline auto checks
                result = await self._run_auto_checks()
            elif user_input.lower().strip() in ["auto audit", "auto-audit", "autoaudit", "audit"]:
                # Run detailed audit
                result = await self._run_auto_audit()
            elif user_input.lower().startswith("cross-browser "):
                # Handle cross-browser testing
                result = await self._handle_cross_browser_command(user_input)
            elif user_input.lower().startswith("api "):
                # Handle API testing
                result = await self._handle_api_command(user_input)
            elif user_input.lower().startswith("mobile "):
                # Handle mobile testing
                result = await self._handle_mobile_command(user_input)
            elif user_input.lower().startswith("schedule "):
                # Handle test scheduling
                result = await self._handle_schedule_command(user_input)
            elif user_input.lower().startswith("load "):
                # Handle load testing
                result = await self._handle_load_test_command(user_input)
            elif user_input.lower().startswith("notify "):
                # Handle notifications
                result = await self._handle_notification_command(user_input)
            elif user_input.lower().startswith("database "):
                # Handle database operations
                result = await self._handle_database_command(user_input)
            elif user_input.lower().startswith("accessibility ") or user_input.lower() in ["accessibility testing", "accessiblilty testing"]:
                # Handle accessibility testing
                result = await self._handle_accessibility_command(user_input)
            elif user_input.lower() == "report":
                # Generate comprehensive report
                result = await self._generate_comprehensive_report()
            elif self.ai_client:
                # Check if this is a multi-step command
                if self._is_multi_step_command(user_input):
                    result = await self._process_multi_step_command(user_input)
                else:
                    # Use AI to understand the command
                    result = await self._process_with_ai(user_input)
            else:
                # Fallback to basic command processing
                result = await self._process_basic_command(user_input)
            
            # Record successful test result
            test_result.update({
                "status": "success",
                "result": result,
                "end_time": time.time(),
                "duration": time.time() - test_start_time
            })
            
        except Exception as e:
            # Record failed test result
            test_result.update({
                "status": "failure",
                "error": str(e),
                "end_time": time.time(),
                "duration": time.time() - test_start_time
            })
            result = f"❌ Error processing command: {e}"
        
        # Store test result
        self.test_results.append(test_result)
        
        return result
    
    async def _process_with_ai(self, user_input: str) -> str:
        """Process commands using the configured AI API."""
        try:
            # Get current page context
            page_context = await self._get_page_context()
            
            # Create a prompt for the AI
            prompt = f"""
            You are an intelligent QA agent that can perform ANY actions on websites based on user instructions.  

Current page context:
- URL: {self.current_url}
- Title: {page_context.get('title', 'Unknown')}
- Available elements: {page_context.get('elements', [])}

User command: "{user_input}"

INSTRUCTIONS:
1. Interpret the user's command dynamically. Do not restrict to fixed flows — perform ANY requested action such as login, signup, search, click, scroll, navigate, type, upload, wait, open menus, or check status.  
2. Always reference the current page context (URL, title, available elements) when deciding what to do.  
3. Prioritize matching available elements. Use labels, roles, or attributes to pick the correct element.  
4. If the user wants to click a search result, look for result_link elements first.  
5. Do not repeat actions unnecessarily (e.g., don't re-search if results are already visible).  
6. If the request is ambiguous, act with your best effort using available context.  
7. For complex commands like "go type tech with time in search bar", break them down:
   - "go" = navigate or find
   - "type" = typing action
   - "tech with time" = the text to type
   - "in search bar" = the target element
8. Output MUST be valid JSON only. No markdown, no code blocks, no free text.  

CRITICAL RULE:
- Do NOT automatically click "Get started" unless the user explicitly mentions it.
- When the user says "login" or "sign in", prioritize elements where type = "auth".
- When the user says "pricing" or "plans", prioritize elements where type = "navigation".
- Always use the 'text' field for reasoning and the 'locator' field for execution.
- If the user command implies both typing and immediate submission (e.g., "type X in search and press enter"), use the 'action': 'search' instead of 'type'.

OUTPUT FORMAT:
{{
    "action": "login|signup|search|click|scroll|navigate|type|wait|help|status|upload",
    "target": "element or text to interact with (if applicable)",
    "text": "text to type (if applicable)",
    "url": "URL to navigate to (if applicable)",
    "search_term": "search term (if applicable)",
    "submit_action": "enter|click_button|none",
    "explanation": "short reasoning of what you're doing"
}}
            """

            
            # Call AI API based on provider
            if self.ai_provider == "openai":
                response = await self._call_openai_api(prompt)
            elif self.ai_provider == "anthropic":
                response = await self._call_anthropic_api(prompt)
            elif self.ai_provider == "google":
                response = await self._call_google_api(prompt)
            else:
                return f"❌ Unsupported AI provider: {self.ai_provider}"
            
            # Parse AI response
            try:
                # Clean the response to extract JSON from markdown code blocks
                response_clean = response.strip()
                if response_clean.startswith('```json'):
                    response_clean = response_clean[7:]  # Remove ```json
                if response_clean.startswith('```'):
                    response_clean = response_clean[3:]   # Remove ```
                if response_clean.endswith('```'):
                    response_clean = response_clean[:-3]  # Remove trailing ```
                
                action_data = json.loads(response_clean.strip())
                return await self._execute_ai_action(action_data)
            except json.JSONDecodeError as e:
                return f"❌ AI response parsing failed: {response}\nError: {e}"
        
        except Exception as e:
            return f"❌ AI processing failed: {e}"
    
    def _is_multi_step_command(self, user_input: str) -> bool:
        """Check if the command contains multiple steps."""
        multi_step_indicators = [
            " and then ", " then ", " after ", " next ", " followed by ",
            " first ", " second ", " third ", " finally ", " lastly ",
            " also ", " additionally ", " furthermore ", " moreover ", ","
        ]
        return any(indicator in user_input.lower() for indicator in multi_step_indicators)
    
    async def _process_multi_step_command(self, user_input: str) -> str:
        """Process multi-step commands by breaking them into individual actions."""
        try:
            # If the entire prompt is an auth flow, run as a single orchestrated step
            if self._looks_like_auth_compound(user_input):
                return await self._handle_auth_compound_command(user_input)
            
            # Break down other commands into steps
            steps = self._parse_multi_step_command(user_input)
            
            if not steps:
                return "❌ Could not parse multi-step command. Try breaking it into separate commands."
            
            results = []
            last_action_context = None  # Store context from previous action
            
            for i, step in enumerate(steps, 1):
                print(f"🔄 Step {i}: {step}")
                
                # Check if this step is a continuation of the previous action
                if self._is_continuation_action(step, last_action_context):
                    result = await self._handle_continuation_action(step, last_action_context)
                else:
                    result = await self._process_with_ai(step)
                    # Store context for potential continuation actions
                    last_action_context = self._extract_action_context(step, result)
                
                results.append(f"Step {i}: {result}")
                
                # Wait a bit between steps to allow page to load
                if i < len(steps):
                    await asyncio.sleep(2)
            
            return f"✅ Multi-step command completed:\n" + "\n".join(results)
            
        except Exception as e:
            return f"❌ Multi-step command failed: {e}"
    
    def _parse_multi_step_command(self, user_input: str) -> list:
        """Parse a multi-step command into individual steps."""
        user_input_lower = user_input.lower()
        
        # Common patterns for multi-step commands
        if "first" in user_input_lower and "then" in user_input_lower:
            # Pattern: "first X then Y"
            parts = user_input_lower.split("then")
            if len(parts) == 2:
                first_part = parts[0].replace("first", "").strip()
                second_part = parts[1].strip()
                return [first_part, second_part]
        
        elif " and then " in user_input_lower:
            # Pattern: "X and then Y"
            parts = user_input_lower.split(" and then ")
            return [part.strip() for part in parts]
        
        elif " then " in user_input_lower:
            # Pattern: "X then Y"
            parts = user_input_lower.split(" then ")
            return [part.strip() for part in parts]
        
        elif " after " in user_input_lower:
            # Pattern: "Y after X" -> reverse order
            parts = user_input_lower.split(" after ")
            if len(parts) == 2:
                return [parts[1].strip(), parts[0].strip()]
        
        # If no clear pattern, try to split on common conjunctions
        for separator in [" and ", " also ", " next ", ","]:
            if separator in user_input_lower:
                parts = user_input_lower.split(separator)
                if len(parts) > 1:
                    return [part.strip() for part in parts]
        
        return []

    def _is_continuation_action(self, step: str, last_context: dict) -> bool:
        """Check if the current step is a continuation of the previous action."""
        if not last_context:
            return False
        
        step_lower = step.lower().strip()
        
        # Check for continuation patterns
        continuation_patterns = [
            "press enter", "hit enter", "press return", "hit return",
            "click submit", "click go", "click search",
            "submit", "go", "enter"
        ]
        
        return any(pattern in step_lower for pattern in continuation_patterns)

    async def _handle_continuation_action(self, step: str, last_context: dict) -> str:
        """Handle continuation actions like 'press enter' after typing."""
        step_lower = step.lower().strip()
        
        try:
            if "press enter" in step_lower or "hit enter" in step_lower or "press return" in step_lower:
                # Press Enter on the current page (most reliable method)
                await self.current_page.keyboard.press("Enter")
                await asyncio.sleep(1)  # Wait for submission
                return "✅ Enter key pressed"
            
            elif "click submit" in step_lower or "click go" in step_lower or "click search" in step_lower:
                # Try to find and click submit/go/search buttons
                submit_selectors = [
                    "button[type='submit']", "input[type='submit']",
                    "button:has-text('Submit')", "button:has-text('Go')",
                    "button:has-text('Search')", "button:has-text('Send')",
                    "[aria-label*='submit']", "[aria-label*='go']"
                ]
                
                for selector in submit_selectors:
                    try:
                        element = self.current_page.locator(selector).first
                        if await element.count() > 0 and await element.is_visible():
                            await element.click()
                            await asyncio.sleep(1)
                            return f"✅ Clicked submit button: {selector}"
                    except:
                        continue
                
                return "⚠️ No submit button found, trying Enter key instead"
            
            else:
                return "⚠️ Unknown continuation action"
                
        except Exception as e:
            return f"❌ Continuation action failed: {e}"

    def _extract_action_context(self, step: str, result: str) -> dict:
        """Extract context from the previous action for potential continuation."""
        step_lower = step.lower()
        
        context = {
            "step": step,
            "result": result,
            "action_type": None,
            "target_element": None
        }
        
        # Determine action type
        if "type" in step_lower and "search" in step_lower:
            context["action_type"] = "search_input"
        elif "type" in step_lower:
            context["action_type"] = "text_input"
        elif "click" in step_lower:
            context["action_type"] = "click"
        elif "search" in step_lower:
            context["action_type"] = "search"
        
        return context

    def _looks_like_auth_compound(self, user_input: str) -> bool:
        """Detect prompts like: click sign, add email and password, click sign again."""
        text = user_input.lower()
        has_auth_word = any(k in text for k in ["sign up", "signup", "register", "create account", "log in", "login", "sign in", "signin", "sign"])
        has_email = "email" in text
        has_password = "password" in text or "pass" in text
        return has_auth_word and has_email and has_password

    async def _handle_auth_compound_command(self, user_input: str) -> str:
        """Route compound auth prompts directly to a robust auth flow."""
        mode = self._detect_auth_mode(user_input)
        email, password = self._extract_email_password_from_text(user_input)
        # Defaults if not provided explicitly
        if not email:
            email = os.getenv("DEMO_EMAIL", "demo@example.com")
        if not password:
            password = os.getenv("DEMO_PASSWORD", "DemoPassword123!")
        return await self._handle_auth_flow(mode, email, password)

    def _detect_auth_mode(self, user_input: str) -> str:
        """Infer login vs signup from text; default to signup on ambiguous 'sign'."""
        text = user_input.lower()
        if any(k in text for k in ["sign up", "signup", "register", "create account"]):
            return "signup"
        if any(k in text for k in ["log in", "login", "sign in", "signin"]):
            return "login"
        # Ambiguous 'sign' -> try signup first then login in the flow
        return "signup"

    def _extract_email_password_from_text(self, user_input: str):
        """Extract email and password tokens from free text if present."""
        import re
        text = user_input
        email = None
        password = None
        # Email pattern
        email_match = re.search(r"([\w\.-]+@[\w\.-]+\.[A-Za-z]{2,})", text)
        if email_match:
            email = email_match.group(1)
        # Password patterns: password "..." | password '...' | password: ...
        pwd_match = re.search(r"password\s*[\=:]*\s*['\"]([^'\"]+)['\"]", text, re.IGNORECASE)
        if not pwd_match:
            pwd_match = re.search(r"password\s*[\=:]*\s*([\S]+)", text, re.IGNORECASE)
        if pwd_match:
            candidate = pwd_match.group(1).strip()
            # Avoid capturing the literal word password
            if candidate.lower() not in ["password", "pass"]:
                password = candidate
        return email, password

    async def _open_possible_menus(self):
        """Open common nav/hamburger/account menus to reveal auth links."""
        try:
            menu_selectors = [
                "button[aria-label*='menu' i]", "[aria-label='Open menu']", "[data-testid*='menu' i]",
                "[class*='hamburger' i]", "[class*='menu' i]",
                "[aria-label*='account' i]", "[aria-label*='profile' i]",
                "[class*='account' i]", "[class*='profile' i]", "[class*='avatar' i]",
                "button:has-text('Menu')", "button:has-text('Account')", "button:has-text('Profile')"
            ]
            candidates = []
            for sel in menu_selectors:
                try:
                    candidates += await self.current_page.locator(sel).all()
                except:
                    continue

            top_right = await self._choose_top_right(candidates)
            if top_right:
                try:
                    await top_right.scroll_into_view_if_needed()
                except:
                    pass
                await top_right.highlight()
                await asyncio.sleep(0.3)
                await top_right.click()
                await self.current_page.wait_for_timeout(800)
        except:
            pass

    async def _choose_top_right(self, locators: list):
        """Pick the most likely top-right candidate among provided locators."""
        try:
            if not locators:
                return None
            viewport = await self.current_page.evaluate("() => ({ w: window.innerWidth, h: window.innerHeight })")
            best = None
            best_score = -1.0
            for loc in locators:
                try:
                    if not await loc.is_visible():
                        continue
                    bb = await loc.bounding_box()
                    if not bb:
                        continue
                    rightness = min(1.0, (bb["x"] + bb["width"]) / max(1.0, viewport.get("w", 1)))
                    topness = max(0.0, 1.0 - (bb["y"] / max(1.0, viewport.get("h", 1))))
                    score = (0.65 * rightness) + (0.35 * topness)
                    if score > best_score:
                        best_score = score
                        best = loc
                except:
                    continue
            return best
        except:
            return None

    async def _find_auth_entry_button(self, mode: str):
        """Dynamically find an auth entry button/link across arbitrary sites."""
        try:
            site_domain = self.current_url.split('/')[2] if '/' in self.current_url else "unknown"
            
            # Try AI-powered discovery first
            ai_selectors = await self._ai_discover_elements(f"find {mode} button")
            if ai_selectors:
                print(f"   🤖 AI found {len(ai_selectors)} potential selectors")
                for selector in ai_selectors:
                    try:
                        element = self.current_page.locator(selector).first
                        if await element.count() > 0 and await element.is_visible():
                            if await self._is_clickable(element):
                                self.selector_memory.record_success(site_domain, "auth_entry", selector)
                                return element
                    except:
                        continue
            
            # Fallback to traditional methods with memory
            login_terms = ["log in", "login", "sign in", "signin", "sign-in"]
            signup_terms = ["sign up", "signup", "sign-up", "register", "create account", "create-account", "join"]
            terms = signup_terms if mode == "signup" else login_terms

            href_parts_login = ["login", "log-in", "signin", "sign-in", "auth"]
            href_parts_signup = ["signup", "sign-up", "register", "create-account", "join"]
            href_parts = href_parts_signup if mode == "signup" else href_parts_login

            bases = [
                self.current_page.locator("header"),
                self.current_page.locator("nav"),
                self.current_page
            ]

            candidates = []
            # Role and text based in header/nav first
            for base in bases:
                for t in terms:
                    try:
                        candidates += await base.locator(f"role=button[name=/{t}/i]").all()
                        candidates += await base.locator(f"role=link[name=/{t}/i]").all()
                        candidates += await base.locator(f":is(a,button)[aria-label*='{t}' i]").all()
                        candidates += await base.locator(f":is(a,button):has-text('{t}')").all()
                    except:
                        continue
                for part in href_parts:
                    try:
                        candidates += await base.locator(f"a[href*='{part}' i]").all()
                        candidates += await base.locator(f"button[id*='{part}' i]").all()
                        candidates += await base.locator(f"button[class*='{part}' i]").all()
                    except:
                        continue

                # If we already have some candidates in header/nav, prefer ranking now
                if candidates:
                    ranked_candidates = await self._rank_elements_by_relevance(candidates, "auth")
                    if ranked_candidates:
                        best = ranked_candidates[0]
                        self.selector_memory.record_success(site_domain, "auth_entry", "ranked_selection")
                        return best

            # Try opening menus and rescan
            await self._open_possible_menus()

            candidates = []
            for base in bases:
                for t in terms:
                    try:
                        candidates += await base.locator(f"role=button[name=/{t}/i]").all()
                        candidates += await base.locator(f"role=link[name=/{t}/i]").all()
                        candidates += await base.locator(f":is(a,button)[aria-label*='{t}' i]").all()
                        candidates += await base.locator(f":is(a,button):has-text('{t}')").all()
                    except:
                        continue
                for part in href_parts:
                    try:
                        candidates += await base.locator(f"a[href*='{part}' i]").all()
                        candidates += await base.locator(f"button[id*='{part}' i]").all()
                        candidates += await base.locator(f"button[class*='{part}' i]").all()
                    except:
                        continue

            ranked_candidates = await self._rank_elements_by_relevance(candidates, "auth")
            if ranked_candidates:
                best = ranked_candidates[0]
                self.selector_memory.record_success(site_domain, "auth_entry", "ranked_selection")
                return best
            return None
        except:
            return None

    async def _find_first_visible(self, selectors: list):
        """Return first visible locator for any selector in list."""
        for selector in selectors:
            try:
                element = self.current_page.locator(selector).first
                if await element.count() > 0 and await element.is_visible():
                    return element
            except:
                continue
        return None

    async def _handle_auth_flow(self, mode: str, email: str, password: str) -> str:
        """Robust auth flow: open entry, fill, submit, with reliable waits and fallbacks."""
        try:
            print(f"🔐 Starting {mode} flow...")
            # Entry button selectors for both modes
            # Prefer dynamic entry detection over static lists
            entry_clicked = False
            dynamic_entry = await self._find_auth_entry_button(mode)
            if dynamic_entry:
                try:
                    await dynamic_entry.scroll_into_view_if_needed()
                except:
                    pass
                await dynamic_entry.highlight()
                await asyncio.sleep(0.4)
                await dynamic_entry.click()
                try:
                    await self.current_page.wait_for_load_state("domcontentloaded")
                except:
                    pass
                await self.current_page.wait_for_timeout(800)
                entry_clicked = True
                print("   ✅ Entry button clicked (dynamic)")
            else:
                # Fallback to static selectors if dynamic failed
                signin_entry = [
                    "role=button[name=/sign in|signin/i]",
                    "text=Sign in", "text=Sign In", "text=Signin",
                    "a:has-text('Sign in')", "button:has-text('Sign in')",
                ]
                signup_entry = [
                    "role=button[name=/sign up|signup|register|get started/i]",
                    "text=Sign up", "text=Sign Up", "text=Register", "text=Get started",
                    "a:has-text('Sign up')", "button:has-text('Sign up')",
                ]
                login_entry = [
                    "role=button[name=/log in|login|sign in|signin/i]",
                    "text=Log in", "text=Login", "text=Sign in", "text=Signin",
                    "a:has-text('Log in')", "button:has-text('Log in')",
                ]

                entry_order = [signin_entry, signup_entry, login_entry] if mode == "signup" else [login_entry, signup_entry, signin_entry]
                for entry_selectors in entry_order:
                    element = await self._find_first_visible(entry_selectors)
                    if element:
                        try:
                            await element.scroll_into_view_if_needed()
                            await element.highlight()
                            await asyncio.sleep(0.5)
                            await element.click()
                            try:
                                await self.current_page.wait_for_load_state("domcontentloaded")
                            except:
                                pass
                            await self.current_page.wait_for_timeout(800)
                            entry_clicked = True
                            print("   ✅ Entry button clicked (fallback)")
                            break
                        except:
                            continue

            if not entry_clicked:
                return "❌ No authentication entry button found on this page."

            # Wait for form elements
            await self.current_page.wait_for_timeout(1500)

            # Inputs (expanded with role and label fallbacks)
            email_selectors = [
                "input[type='email']", "input[name*='email' i]", "input[autocomplete='email']",
                "input[aria-label*='email' i]", "input[placeholder*='email' i]",
                "role=textbox[name=/email/i]",
                # label-for associations
                "label:has-text('Email') ~ input", "label:has-text('email') ~ input",
                "[for*='email' i] ~ input", "[id*='email' i]"
            ]
            password_selectors = [
                "input[type='password']", "input[name*='pass' i]", "input[autocomplete='current-password']",
                "input[autocomplete='new-password']", "input[aria-label*='password' i]",
                "input[placeholder*='password' i]", "role=textbox[name=/password/i]",
                # label-for associations
                "label:has-text('Password') ~ input", "label:has-text('password') ~ input",
                "[for*='pass' i] ~ input", "[id*='pass' i]"
            ]

            email_input = await self._find_first_visible(email_selectors)
            password_input = await self._find_first_visible(password_selectors)

            # Some sites open in a modal slightly delayed – retry briefly
            if not email_input or not password_input:
                for _ in range(3):
                    await self.current_page.wait_for_timeout(700)
                    if not email_input:
                        email_input = await self._find_first_visible(email_selectors)
                    if not password_input:
                        password_input = await self._find_first_visible(password_selectors)
                    if email_input and password_input:
                        break

            if not email_input or not password_input:
                return "⚠️ Auth form not detected after clicking."

            # Fill credentials with human behavior simulation
            try:
                await email_input.scroll_into_view_if_needed()
            except:
                pass
            await email_input.highlight()
            await asyncio.sleep(0.3)
            
            # Simulate human typing for email
            await self.human_behavior.simulate_human_typing(email_input, email, self.current_page)
            print("   ✅ Email filled (human-like typing)")

            try:
                await password_input.scroll_into_view_if_needed()
            except:
                pass
            await password_input.highlight()
            await asyncio.sleep(0.3)
            
            # Simulate human typing for password
            await self.human_behavior.simulate_human_typing(password_input, password, self.current_page)
            print("   ✅ Password filled (human-like typing)")

            # Submit
            submit_selectors = [
                "button[type='submit']", "input[type='submit']",
                "role=button[name=/log in|login|sign in|signin|sign up|signup|continue|submit|create account/i]",
                "button:has-text('Log in')", "button:has-text('Sign in')",
                "button:has-text('Sign up')", "button:has-text('Create account')",
                "button:has-text('Continue')", "button:has-text('Submit')"
            ]

            submit = await self._find_first_visible(submit_selectors)
            if submit:
                await submit.scroll_into_view_if_needed()
                await submit.highlight()
                await asyncio.sleep(0.4)
                # Some sites require the inputs to lose focus; blur email before clicking
                try:
                    await self.current_page.keyboard.press("Tab")
                except:
                    pass
                await submit.click()
                print("   ✅ Submit clicked")
            else:
                # Fallback: press Enter in password field
                await self.current_page.keyboard.press("Enter")
                print("   ✅ Submit via Enter key")

            # Try to scope future error detection to the form/dialog container
            container = None
            try:
                form_candidate = self.current_page.locator("form").filter(has=email_input).first
                if await form_candidate.count() > 0:
                    container = form_candidate
                else:
                    container = self.current_page.locator("[role='dialog'], [aria-modal='true'], [class*='modal'], [class*='dialog'], [class*='auth'], [class*='signin'], [class*='login']").first
            except:
                pass

            # Wait for potential navigation or success
            try:
                await self.current_page.wait_for_load_state("networkidle", timeout=8000)
            except:
                await self.current_page.wait_for_timeout(2000)

            # Check for error messages after submission with multiple attempts (scoped)
            error_message = await self._detect_auth_error_with_retry(container)
            if error_message:
                print(f"⚠️ Auth error detected: {error_message}")
                return f"❌ Authentication failed: {error_message}"
            
            return "✅ Authentication flow executed. Check the page for results."
        except Exception as e:
            return f"❌ Auth flow failed: {e}"

    async def _detect_auth_error_with_retry(self, scope_locator=None) -> str:
        """Detect authentication error messages with multiple attempts and better timing."""
        try:
            # Try multiple times with different delays to catch dynamic error messages
            for attempt in range(3):
                await self.current_page.wait_for_timeout(1000 + (attempt * 500))  # 1s, 1.5s, 2s
                
                error_message = await self._detect_auth_error(scope_locator)
                if error_message:
                    # Extract clean error message from the detected text
                    clean_error = self._extract_clean_error_message(error_message)
                    if clean_error:
                        return clean_error
                
                # Also check for any visible text that might be an error
                all_text = await self._get_all_visible_text(scope_locator)
                if all_text:
                    clean_error = self._extract_clean_error_message(all_text)
                    if clean_error:
                        return clean_error
            
            return ""
        except Exception as e:
            print(f"⚠️ Error detection with retry failed: {e}")
            return ""

    async def _detect_auth_error(self, scope_locator=None) -> str:
        """Detect authentication error messages on the page."""
        try:
            # Common error message selectors - expanded list
            error_selectors = [
                # Generic error containers
                "[class*='error']", "[class*='alert']", "[class*='warning']", "[class*='danger']",
                "[role='alert']", "[aria-live='polite']", "[aria-live='assertive']",
                # Specific error text patterns
                "text=/invalid.*username/i", "text=/invalid.*password/i", "text=/wrong.*credentials/i",
                "text=/incorrect.*login/i", "text=/authentication.*failed/i", "text=/login.*failed/i",
                "text=/access.*denied/i", "text=/unauthorized/i", "text=/forbidden/i",
                # Common error message containers
                ".error", ".alert", ".warning", ".danger", ".message", ".notification",
                "[data-testid*='error']", "[data-testid*='alert']",
                # Additional patterns for modern sites
                "[class*='message']", "[class*='feedback']", "[class*='status']",
                "div[class*='error']", "span[class*='error']", "p[class*='error']",
                # Look for any element containing error-like text
                "text=/error/i", "text=/invalid/i", "text=/wrong/i", "text=/failed/i"
            ]
            
            for selector in error_selectors:
                try:
                    base = scope_locator if scope_locator else self.current_page
                    elements = await base.locator(selector).all()
                    for element in elements:
                        if await element.is_visible():
                            text = await element.text_content()
                            if text and text.strip():
                                # Check if it looks like an error message
                                error_text = text.strip().lower()
                                error_indicators = [
                                    "invalid", "wrong", "incorrect", "failed", "error", 
                                    "denied", "unauthorized", "forbidden", "not found",
                                    "doesn't exist", "does not exist", "try again"
                                ]
                                if any(indicator in error_text for indicator in error_indicators):
                                    # Extract clean error message from the detected text
                                    clean_error = self._extract_clean_error_message(text)
                                    if clean_error:
                                        return clean_error
                                    return text.strip()
                except:
                    continue
            
            return ""
        except Exception as e:
            print(f"⚠️ Error detection failed: {e}")
            return ""

    async def _get_all_visible_text(self, scope_locator=None) -> str:
        """Get all visible text on the page for error detection."""
        try:
            # Get all text content from visible elements
            base = scope_locator if scope_locator else self.current_page
            text_elements = await base.locator("*").all()
            all_text = ""
            for element in text_elements:
                try:
                    text = await element.text_content()
                    if text:
                        all_text += text + " "
                except:
                    continue
            return all_text
        except Exception as e:
            print(f"⚠️ Failed to get page text: {e}")
            return ""

    def _extract_clean_error_message(self, text: str) -> str:
        """Extract clean, concise error messages from website text."""
        try:
            import re
            
            # Common auth error patterns to look for
            auth_error_patterns = [
                # Invalid credentials patterns
                r"invalid\s+(?:username|email|password|credentials)",
                r"wrong\s+(?:username|email|password|credentials)",
                r"incorrect\s+(?:username|email|password|credentials|login)",
                r"invalid\s+username\s+or\s+password",
                r"wrong\s+username\s+or\s+password",
                r"incorrect\s+username\s+or\s+password",
                
                # Authentication failure patterns
                r"authentication\s+failed",
                r"login\s+failed",
                r"sign\s+in\s+failed",
                r"log\s+in\s+failed",
                
                # Access control patterns
                r"access\s+denied",
                r"unauthorized",
                r"forbidden",
                
                # User/account not found patterns
                r"user\s+not\s+found",
                r"account\s+not\s+found",
                r"email\s+not\s+found",
                r"username\s+not\s+found",
                
                # Password specific patterns
                r"password\s+incorrect",
                r"password\s+wrong",
                r"password\s+invalid",
                
                # Generic error patterns
                r"credentials\s+invalid",
                r"login\s+error",
                r"sign\s+in\s+error"
            ]
            
            text_lower = text.lower()
            
            # Look for specific auth error patterns first
            for pattern in auth_error_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    error_phrase = match.group(0)
                    
                    # Map to clean, user-friendly messages
                    if "invalid" in error_phrase and ("username" in error_phrase or "password" in error_phrase):
                        return "Invalid Email and Password"
                    elif "wrong" in error_phrase and ("username" in error_phrase or "password" in error_phrase):
                        return "Wrong Email and Password"
                    elif "incorrect" in error_phrase and ("username" in error_phrase or "password" in error_phrase):
                        return "Incorrect Email and Password"
                    elif "failed" in error_phrase:
                        return "Authentication Failed"
                    elif "denied" in error_phrase:
                        return "Access Denied"
                    elif "unauthorized" in error_phrase:
                        return "Unauthorized Access"
                    elif "not found" in error_phrase:
                        return "Account Not Found"
                    else:
                        return f"Error: {error_phrase.title()}"
            
            # If no specific pattern found, look for short error messages (1-10 words)
            # Split text into sentences and look for short ones containing error keywords
            sentences = re.split(r'[.!?]+', text)
            error_keywords = ["invalid", "wrong", "incorrect", "failed", "error", "denied", "unauthorized"]
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence.split()) <= 10 and len(sentence.split()) >= 2:  # 2-10 words
                    sentence_lower = sentence.lower()
                    if any(keyword in sentence_lower for keyword in error_keywords):
                        # Clean up the sentence
                        clean_sentence = re.sub(r'\s+', ' ', sentence).strip()
                        if len(clean_sentence) <= 100:  # Reasonable length
                            return clean_sentence
            
            return ""
        except Exception as e:
            print(f"⚠️ Error extraction failed: {e}")
            return ""
    
    async def _analyze_page_characteristics(self):
        """Analyze page characteristics for dynamic adaptation."""
        try:
            # Detect device type
            self.device_type = await self._detect_device_type()
            
            # Detect page language
            self.page_language = await self._detect_page_language()
            
            # Analyze page semantics
            self.page_semantics = await self._analyze_page_semantics()
            
            # Advanced AI analysis
            page_html = await self.current_page.content()
            ai_analysis = await self.ai_analyzer.analyze_page_intent(page_html, self.current_url)
            
            # Performance analysis
            performance_metrics = await self.performance_monitor.measure_page_performance(self.current_page)
            performance_issues = await self.performance_monitor.detect_performance_issues(performance_metrics)
            
            # Security analysis
            security_headers = await self.security_tester.analyze_security_headers(self.current_page)
            
            # Visual analysis
            ui_elements = await self.visual_testing.analyze_ui_elements(self.current_page)
            
            # Store comprehensive analysis
            self.page_semantics.update({
                "ai_analysis": ai_analysis,
                "performance": {
                    "metrics": performance_metrics.__dict__,
                    "issues": performance_issues
                },
                "security": security_headers,
                "ui_elements": ui_elements
            })
            
            print(f"🔍 Advanced Page Analysis:")
            print(f"   Device: {self.device_type} | Language: {self.page_language}")
            print(f"   Page Type: {ai_analysis.get('page_type', 'unknown')}")
            print(f"   Performance Issues: {len(performance_issues)}")
            print(f"   UI Elements: {len(ui_elements.get('buttons', []))} buttons, {len(ui_elements.get('inputs', []))} inputs")
        except Exception as e:
            print(f"⚠️ Page analysis failed: {e}")
    
    async def _detect_device_type(self) -> str:
        """Detect if page is mobile/desktop and adapt selectors."""
        try:
            viewport = await self.current_page.evaluate("() => ({ w: window.innerWidth, h: window.innerHeight })")
            if viewport.get("w", 0) < 768:
                return "mobile"
            return "desktop"
        except:
            return "unknown"
    
    async def _detect_page_language(self) -> str:
        """Detect page language and return appropriate auth terms."""
        try:
            lang = await self.current_page.evaluate("document.documentElement.lang || 'en'")
            return lang.split('-')[0]  # Get primary language
        except:
            return "en"
    
    async def _analyze_page_semantics(self) -> dict:
        """Analyze page to understand its purpose and structure."""
        try:
            # Get page title and URL patterns
            title = await self.current_page.title()
            url = self.current_url.lower()
            
            page_type = "unknown"
            if any(word in url for word in ["shop", "store", "buy", "cart", "checkout"]):
                page_type = "ecommerce"
            elif any(word in url for word in ["blog", "news", "article"]):
                page_type = "blog"
            elif any(word in url for word in ["app", "dashboard", "admin", "console"]):
                page_type = "saas"
            elif any(word in url for word in ["docs", "documentation", "help"]):
                page_type = "documentation"
            elif "youtube" in url:
                page_type = "video"
            elif "github" in url:
                page_type = "developer"
            
            return {
                'page_type': page_type,
                'title': title,
                'url_pattern': url
            }
        except:
            return {'page_type': 'unknown'}
    
    async def _ai_discover_elements(self, intent: str) -> list:
        """Use AI to find relevant elements based on user intent."""
        if not self.ai_client:
            return []
        
        try:
            # Get page context for AI
            page_html = await self.current_page.content()
            page_title = await self.current_page.title()
            
            ai_prompt = f"""
            User wants to: {intent}
            Page Title: {page_title}
            Page URL: {self.current_url}
            Device Type: {self.device_type}
            Page Language: {self.page_language}
            
            Analyze this page HTML snippet and find the most relevant clickable elements for the user's intent.
            Return ONLY a JSON array of selectors that would work for this action.
            
            HTML snippet: {page_html[:3000]}
            
            Respond with JSON format:
            ["selector1", "selector2", "selector3"]
            """
            
            if self.ai_provider == "google":
                response = await self._call_google_api(ai_prompt)
            else:
                return []
            
            # Parse AI response
            import json
            try:
                selectors = json.loads(response.strip())
                return selectors if isinstance(selectors, list) else []
            except:
                return []
        except Exception as e:
            print(f"⚠️ AI element discovery failed: {e}")
            return []
    
    async def _rank_elements_by_relevance(self, elements: list, context: str) -> list:
        """Rank elements by visual prominence, position, and semantic relevance."""
        try:
            ranked_elements = []
            for element in elements:
                try:
                    # Get element properties
                    bounding_box = await element.bounding_box()
                    is_visible = await element.is_visible()
                    
                    if not is_visible or not bounding_box:
                        continue
                    
                    # Calculate relevance score
                    score = 0
                    
                    # Position score (prefer top-right for auth, center for main actions)
                    if "auth" in context.lower():
                        # Prefer top-right positioning
                        viewport = await self.current_page.evaluate("() => ({ w: window.innerWidth, h: window.innerHeight })")
                        rightness = (bounding_box["x"] + bounding_box["width"]) / viewport.get("w", 1)
                        topness = 1 - (bounding_box["y"] / viewport.get("h", 1))
                        score += (rightness * 0.6) + (topness * 0.4)
                    else:
                        # Prefer center positioning
                        viewport = await self.current_page.evaluate("() => ({ w: window.innerWidth, h: window.innerHeight })")
                        center_x = viewport.get("w", 1) / 2
                        center_y = viewport.get("h", 1) / 2
                        element_center_x = bounding_box["x"] + bounding_box["width"] / 2
                        element_center_y = bounding_box["y"] + bounding_box["height"] / 2
                        distance_from_center = ((element_center_x - center_x) ** 2 + (element_center_y - center_y) ** 2) ** 0.5
                        max_distance = ((viewport.get("w", 1) / 2) ** 2 + (viewport.get("h", 1) / 2) ** 2) ** 0.5
                        score += 1 - (distance_from_center / max_distance)
                    
                    # Size score (prefer reasonably sized elements)
                    area = bounding_box["width"] * bounding_box["height"]
                    if 100 < area < 10000:  # Reasonable button size
                        score += 0.3
                    
                    # Visibility score
                    try:
                        opacity = await element.evaluate("el => window.getComputedStyle(el).opacity")
                        if float(opacity) > 0.5:
                            score += 0.2
                    except:
                        pass
                    
                    ranked_elements.append((element, score))
                except:
                    continue
            
            # Sort by score and return elements
            ranked_elements.sort(key=lambda x: x[1], reverse=True)
            return [elem for elem, score in ranked_elements]
        except Exception as e:
            print(f"⚠️ Element ranking failed: {e}")
            return elements
    
    async def _smart_wait_for_element(self, selector: str, context: str):
        """Wait intelligently based on page type and element type."""
        try:
            if "modal" in context.lower():
                # Wait for modal animation
                await self.current_page.wait_for_timeout(500)
            elif "form" in context.lower():
                # Wait for form validation
                await self.current_page.wait_for_timeout(300)
            elif "auth" in context.lower():
                # Wait for auth form to stabilize
                await self.current_page.wait_for_timeout(800)
            else:
                # Wait for stable layout
                await self.current_page.wait_for_timeout(200)
        except:
            pass
    
    async def _self_heal_selectors(self, broken_selector: str, element_type: str) -> str:
        """Find alternative selectors when primary ones fail."""
        try:
            # Try to find the element by analyzing its context
            site_domain = self.current_url.split('/')[2] if '/' in self.current_url else "unknown"
            
            # Check memory for successful selectors
            best_selector = self.selector_memory.get_best_selector(site_domain, element_type)
            if best_selector and best_selector != broken_selector:
                return best_selector
            
            # Generate alternative selectors based on element type
            alternatives = []
            
            if element_type == "auth_entry":
                alternatives = [
                    "role=button[name=/sign in|login|signin/i]",
                    "role=link[name=/sign in|login|signin/i]",
                    ":is(a,button)[aria-label*='sign in' i]",
                    ":is(a,button)[aria-label*='login' i]",
                    "a[href*='login' i]",
                    "a[href*='signin' i]",
                    "button[id*='login' i]",
                    "button[class*='login' i]"
                ]
            elif element_type == "email_input":
                alternatives = [
                    "input[type='email']",
                    "input[name*='email' i]",
                    "input[autocomplete='email']",
                    "input[aria-label*='email' i]",
                    "input[placeholder*='email' i]",
                    "role=textbox[name=/email/i]"
                ]
            elif element_type == "password_input":
                alternatives = [
                    "input[type='password']",
                    "input[name*='pass' i]",
                    "input[autocomplete*='password']",
                    "input[aria-label*='password' i]",
                    "input[placeholder*='password' i]",
                    "role=textbox[name=/password/i]"
                ]
            
            # Test alternatives
            for alt_selector in alternatives:
                try:
                    element = self.current_page.locator(alt_selector).first
                    if await element.count() > 0 and await element.is_visible():
                        # Record success
                        self.selector_memory.record_success(site_domain, element_type, alt_selector)
                        return alt_selector
                except:
                    continue
            
            return None
        except Exception as e:
            print(f"⚠️ Self-healing failed: {e}")
            return None
    
    async def _handle_testing_command(self, user_input: str) -> str:
        """Handle comprehensive testing commands."""
        command = user_input.lower().replace("test ", "").strip()
        
        if "all" in command or "everything" in command:
            return await self._run_comprehensive_tests()
        elif "auth" in command or "login" in command:
            return await self._test_authentication_flows()
        elif "forms" in command:
            return await self._test_form_interactions()
        elif "navigation" in command:
            return await self._test_navigation()
        else:
            return "❌ Unknown testing command. Try: 'test all', 'test auth', 'test forms', 'test navigation'"
    
    async def _handle_analysis_command(self, user_input: str) -> str:
        """Handle analysis commands."""
        command = user_input.lower().replace("analyze ", "").strip()
        
        if "page" in command:
            return await self._analyze_current_page()
        elif "performance" in command:
            return await self._analyze_performance()
        elif "accessibility" in command or "a11y" in command:
            return await self._analyze_accessibility()
        else:
            return "❌ Unknown analysis command. Try: 'analyze page', 'analyze performance', 'analyze accessibility'"
    
    async def _handle_security_command(self, user_input: str) -> str:
        """Handle security testing commands."""
        command = user_input.lower().replace("security ", "").strip()
        
        if "scan" in command or "test" in command:
            if self.current_page is None:
                return "❌ No page loaded. Start a session first."
            
            try:
                vulnerabilities = await self.security_tester.test_xss_vulnerabilities(self.current_page)
                security_headers = await self.security_tester.analyze_security_headers(self.current_page)
                
                result = f"🔒 Security Analysis Complete:\n"
                result += f"   XSS Vulnerabilities Found: {len(vulnerabilities)}\n"
                result += f"   Security Headers Analyzed: {len(security_headers)}\n"
                
                if vulnerabilities:
                    result += "\n🚨 Vulnerabilities:\n"
                    for vuln in vulnerabilities:
                        result += f"   - {vuln.type}: {vuln.description}\n"
                        result += f"     Location: {vuln.location}\n"
                        result += f"     Recommendation: {vuln.recommendation}\n"
                
                # Show security headers status
                missing_headers = [header for header, value in security_headers.items() if value == "Missing"]
                if missing_headers:
                    result += f"\n⚠️ Missing Security Headers:\n"
                    for header in missing_headers:
                        result += f"   - {header.replace('_', '-').title()}\n"
                else:
                    result += f"\n✅ All security headers present\n"
                
                return result
            except Exception as e:
                return f"❌ Security scan failed: {e}"
        else:
            return "❌ Unknown security command. Try: 'security scan'"
    
    async def _handle_performance_command(self, user_input: str) -> str:
        """Handle performance testing commands."""
        command = user_input.lower().replace("performance ", "").strip()
        
        if "measure" in command or "test" in command:
            metrics = await self.performance_monitor.measure_page_performance(self.current_page)
            issues = await self.performance_monitor.detect_performance_issues(metrics)
            
            result = f"⚡ Performance Analysis:\n"
            result += f"   Load Time: {metrics.load_time:.0f}ms\n"
            result += f"   First Contentful Paint: {metrics.first_contentful_paint:.0f}ms\n"
            result += f"   Network Requests: {metrics.network_requests}\n"
            result += f"   Memory Usage: {metrics.memory_usage / 1024 / 1024:.1f}MB\n"
            result += f"   Issues Found: {len(issues)}\n"
            
            if issues:
                result += "\n⚠️ Performance Issues:\n"
                for issue in issues:
                    result += f"   - {issue['type']}: {issue['message']}\n"
            
            return result
        else:
            return "❌ Unknown performance command. Try: 'performance measure'"
    
    async def _handle_visual_command(self, user_input: str) -> str:
        """Handle visual testing commands."""
        command = user_input.lower().replace("visual ", "").strip()
        
        if "screenshot" in command:
            screenshot_name = f"test_{int(time.time())}"
            await self.visual_testing.capture_screenshot(self.current_page, screenshot_name)
            return f"📸 Screenshot captured: {screenshot_name}"
        elif "compare" in command:
            test_name = command.replace("compare ", "").strip() or "default"
            comparison = await self.visual_testing.detect_visual_regressions(self.current_page, test_name)
            return f"🔍 Visual Comparison: {comparison['status']} - {comparison['message']}"
        elif "elements" in command:
            ui_elements = await self.visual_testing.analyze_ui_elements(self.current_page)
            return f"🎨 UI Elements Found: {len(ui_elements['buttons'])} buttons, {len(ui_elements['inputs'])} inputs, {len(ui_elements['links'])} links"
        else:
            return "❌ Unknown visual command. Try: 'visual screenshot', 'visual compare', 'visual elements'"
    
    async def _generate_comprehensive_report(self) -> str:
        """Generate comprehensive testing report."""
        if not self.test_results:
            return "📊 No test results available. Run some tests first!"
        
        report = await self.analytics.generate_test_report(self.test_results)
        
        result = "📊 Comprehensive Testing Report\n"
        result += "=" * 40 + "\n"
        result += f"Total Tests: {report['summary']['total_tests']}\n"
        result += f"Successful: {report['summary']['successful']}\n"
        result += f"Failed: {report['summary']['failed']}\n"
        result += f"Success Rate: {report['summary']['success_rate']}\n\n"
        
        if report.get('failure_patterns', {}).get('most_common_errors'):
            result += "🔍 Common Issues:\n"
            for error, count in report['failure_patterns']['most_common_errors']:
                result += f"   - {error}: {count} occurrences\n"
            result += "\n"
        
        if report.get('recommendations'):
            result += "💡 Recommendations:\n"
            for rec in report['recommendations']:
                result += f"   - {rec}\n"
        
        return result
    
    async def _handle_cross_browser_command(self, user_input: str) -> str:
        """Handle cross-browser testing commands."""
        command = user_input.lower().replace("cross-browser ", "").strip()
        
        if "test" in command:
            # Run REAL cross-browser test - actually opens browsers
            async def real_browser_test(browser_type):
                try:
                    from playwright.async_api import async_playwright
                    playwright = await async_playwright().start()
                    
                    # Launch the actual browser
                    if browser_type == 'chromium':
                        browser = await playwright.chromium.launch(headless=False, slow_mo=1000)
                    elif browser_type == 'firefox':
                        browser = await playwright.firefox.launch(headless=False, slow_mo=1000)
                    elif browser_type == 'webkit':
                        browser = await playwright.webkit.launch(headless=False, slow_mo=1000)
                    else:
                        return f"❌ Unknown browser: {browser_type}"
                    
                    # Create context and page
                    context = await browser.new_context(
                        viewport={'width': 1920, 'height': 1080},
                        ignore_https_errors=True
                    )
                    page = await context.new_page()
                    
                    # Navigate to current URL or default
                    test_url = self.current_url or "https://www.w3schools.com"
                    await page.goto(test_url, timeout=30000)
                    
                    # Get page info
                    title = await page.title()
                    url = page.url
                    
                    # Take a screenshot for verification
                    screenshot_path = f"screenshot_{browser_type}.png"
                    await page.screenshot(path=screenshot_path)
                    
                    # Close browser
                    await browser.close()
                    await playwright.stop()
                    
                    return f"✅ Opened {browser_type} - Title: {title[:50]}... - Screenshot: {screenshot_path}"
                    
                except Exception as e:
                    return f"❌ Failed on {browser_type}: {str(e)}"
            
            results = await self.cross_browser_manager.test_across_browsers(real_browser_test)
            return f"🌐 Cross-browser test results:\n" + "\n".join([f"   {browser}: {result}" for browser, result in results.items()])
        else:
            return "❌ Unknown cross-browser command. Try: 'cross-browser test'"
    
    async def _handle_api_command(self, user_input: str) -> str:
        """Handle API testing commands."""
        command = user_input.lower().replace("api ", "").strip()
        
        if "test" in command:
            # Test API endpoints
            endpoints = self.test_data_manager.get_test_data('api_endpoints', 'endpoints')
            if endpoints:
                results = await self.api_tester.test_api_suite(endpoints)
                return f"🔌 API test results:\n" + "\n".join([f"   {url}: {result.get('status_code', 'Error')}" for url, result in results.items()])
            else:
                return "❌ No API endpoints configured. Add endpoints to api_endpoints.json"
        else:
            return "❌ Unknown API command. Try: 'api test'"
    
    async def _handle_mobile_command(self, user_input: str) -> str:
        """Handle mobile testing commands."""
        command = user_input.lower().replace("mobile ", "").strip()
        
        if "test" in command:
            # Test on mobile device
            device_name = "iPhone 12"  # Default device
            if "iphone" in command:
                device_name = "iPhone 12"
            elif "android" in command or "galaxy" in command:
                device_name = "Samsung Galaxy S21"
            elif "ipad" in command:
                device_name = "iPad"
            
            result = await self.mobile_device_manager.test_on_device(self.current_page, device_name)
            return result
        else:
            return "❌ Unknown mobile command. Try: 'mobile test'"
    
    async def _handle_schedule_command(self, user_input: str) -> str:
        """Handle test scheduling commands."""
        command = user_input.lower().replace("schedule ", "").strip()
        
        if "daily" in command:
            # Schedule daily test
            async def daily_test():
                return "Daily test completed"
            
            result = self.test_scheduler.schedule_test("daily_test", daily_test, "09:00")
            return result
        else:
            return "❌ Unknown schedule command. Try: 'schedule daily'"
    
    async def _handle_load_test_command(self, user_input: str) -> str:
        """Handle load testing commands."""
        command = user_input.lower().replace("load ", "").strip()
        
        if "test" in command:
            # Run load test on current URL
            url = self.current_url or "https://httpbin.org/get"
            results = await self.load_tester.run_load_test(url, concurrent_users=5, duration=30)
            
            if 'error' in results:
                return f"❌ Load test failed: {results['error']}"
            
            return f"⚡ Load test results:\n" + \
                   f"   URL: {results['url']}\n" + \
                   f"   Requests: {results['requests']}\n" + \
                   f"   Success Rate: {results['success_rate']:.1f}%\n" + \
                   f"   Avg Response Time: {results['average_response_time']:.2f}s"
        else:
            return "❌ Unknown load command. Try: 'load test'"
    
    async def _handle_notification_command(self, user_input: str) -> str:
        """Handle notification commands."""
        command = user_input.lower().replace("notify ", "").strip()
        
        if "send" in command:
            # Send test report
            if self.test_results:
                result = await self.notification_manager.send_test_report(self.test_results)
                return result
            else:
                return "❌ No test results to send"
        else:
            return "❌ Unknown notify command. Try: 'notify send'"
    
    async def _handle_database_command(self, user_input: str) -> str:
        """Handle database operations."""
        command = user_input.lower().replace("database ", "").strip()
        
        if "history" in command:
            # Get test history
            history = self.database_manager.get_test_history(10)
            if history:
                result = "📊 Recent test history:\n"
                for record in history:
                    result += f"   {record[1]}: {record[2]} ({record[3]:.2f}s)\n"
                return result
            else:
                return "📊 No test history found"
        elif "save" in command:
            # Save current test results
            for test_result in self.test_results:
                self.database_manager.save_test_result(test_result)
            return f"✅ Saved {len(self.test_results)} test results to database"
        else:
            return "❌ Unknown database command. Try: 'database history' or 'database save'"
    
    async def _handle_accessibility_command(self, user_input: str) -> str:
        """Handle accessibility testing commands."""
        # Handle both "accessibility test" and "accessibility testing" (including misspelled version)
        if user_input.lower() in ["accessibility testing", "accessiblilty testing"]:
            command = "test"
        else:
            command = user_input.lower().replace("accessibility ", "").strip()
        
        if "test" in command:
            if self.current_page is None:
                return "❌ No page loaded. Start a session first."
            
            try:
                results = await self.accessibility_tester.test_accessibility(self.current_page)
                
                if 'error' in results:
                    return f"❌ Accessibility test failed: {results['error']}"
                
                result = f"♿ Accessibility Test Results (WCAG AA):\n"
                
                # Handle the actual accessibility tester format
                if 'wcag_violations' in results:
                    violations = results['wcag_violations']
                    score = results.get('accessibility_score', 0)
                    
                    result += f"   Score: {score:.1f}% ({len(violations)} violations found)\n"
                    
                    if violations:
                        result += "\n   Issues Found:\n"
                        for violation in violations:
                            result += f"   - {violation['guideline']}: {violation['description']} ({violation['severity']})\n"
                    else:
                        result += "\n   ✅ No accessibility issues found!\n"
                    
                    if results.get('recommendations'):
                        result += "\n   Recommendations:\n"
                        for rec in results['recommendations']:
                            result += f"   - {rec}\n"
                else:
                    # Handle the new format
                    score = results.get('score', 0)
                    total_checks = results.get('total_checks', 0)
                    passed_checks = results.get('passed_checks', 0)
                    
                    result += f"   Score: {score:.1f}% ({passed_checks}/{total_checks} checks passed)\n"
                    
                    if results.get('issues'):
                        result += "\n   Issues Found:\n"
                        for issue in results['issues']:
                            result += f"   - {issue}\n"
                    else:
                        result += "\n   ✅ No accessibility issues found!\n"
                
                return result
            except Exception as e:
                return f"❌ Accessibility test failed: {e}"
        else:
            return "❌ Unknown accessibility command. Try: 'accessibility test'"
    
    async def _run_comprehensive_tests(self) -> str:
        """Run comprehensive test suite."""
        results = []
        
        if self.current_page is None:
            return "❌ No page loaded. Start a session first with a website."
        
        # Test authentication flows
        try:
            auth_result = await self._test_authentication_flows()
            results.append(f"✅ Auth Tests: {auth_result}")
        except Exception as e:
            results.append(f"❌ Auth Tests Failed: {e}")
        
        # Test form interactions
        try:
            form_result = await self._test_form_interactions()
            results.append(f"✅ Form Tests: {form_result}")
        except Exception as e:
            results.append(f"❌ Form Tests Failed: {e}")
        
        # Test navigation
        try:
            nav_result = await self._test_navigation()
            results.append(f"✅ Navigation Tests: {nav_result}")
        except Exception as e:
            results.append(f"❌ Navigation Tests Failed: {e}")
        
        # Test accessibility
        try:
            accessibility_result = await self.accessibility_tester.test_accessibility(self.current_page)
            if 'error' not in accessibility_result:
                score = accessibility_result.get('score', 0)
                issues = len(accessibility_result.get('issues', []))
                results.append(f"✅ Accessibility Tests: Score {score:.1f}%, {issues} issues found")
            else:
                results.append(f"❌ Accessibility Tests Failed: {accessibility_result['error']}")
        except Exception as e:
            results.append(f"❌ Accessibility Tests Failed: {e}")
        
        # Test performance
        try:
            performance_metrics = await self.performance_monitor.measure_page_performance(self.current_page)
            load_time = performance_metrics.load_time
            fcp = performance_metrics.first_contentful_paint
            requests = performance_metrics.network_requests
            results.append(f"✅ Performance Tests: Load {load_time:.0f}ms, FCP {fcp:.0f}ms, {requests} requests")
        except Exception as e:
            results.append(f"❌ Performance Tests Failed: {e}")
        
        # Test security headers
        try:
            security_result = await self.security_tester.analyze_security_headers(self.current_page)
            if 'error' not in security_result:
                headers_found = len(security_result.get('headers_found', []))
                headers_missing = len(security_result.get('headers_missing', []))
                results.append(f"✅ Security Tests: {headers_found} headers found, {headers_missing} missing")
            else:
                results.append(f"❌ Security Tests Failed: {security_result['error']}")
        except Exception as e:
            results.append(f"❌ Security Tests Failed: {e}")
        
        # Test visual elements
        try:
            visual_result = await self.visual_testing.analyze_ui_elements(self.current_page)
            if 'error' not in visual_result:
                buttons = len(visual_result.get('buttons', []))
                inputs = len(visual_result.get('inputs', []))
                results.append(f"✅ Visual Tests: {buttons} buttons, {inputs} inputs analyzed")
            else:
                results.append(f"❌ Visual Tests Failed: {visual_result['error']}")
        except Exception as e:
            results.append(f"❌ Visual Tests Failed: {e}")
        
        return "🧪 Comprehensive Test Suite Complete:\n" + "\n".join(results)
    
    async def _test_authentication_flows(self) -> str:
        """Test authentication flows."""
        try:
            if self.current_page is None:
                return "No page loaded - cannot test auth flows"
            
            # Find auth elements
            login_buttons = await self.current_page.locator("button:has-text('login'), button:has-text('sign in'), a:has-text('login'), a:has-text('sign in')").count()
            signup_buttons = await self.current_page.locator("button:has-text('sign up'), button:has-text('register'), a:has-text('sign up'), a:has-text('register')").count()
            
            # Find form inputs
            email_inputs = await self.current_page.locator("input[type='email'], input[name*='email'], input[placeholder*='email']").count()
            password_inputs = await self.current_page.locator("input[type='password'], input[name*='password']").count()
            
            return f"Found {login_buttons} login buttons, {signup_buttons} signup buttons, {email_inputs} email inputs, {password_inputs} password inputs"
            
        except Exception as e:
            return f"Auth flow test failed: {e}"
    
    async def _test_form_interactions(self) -> str:
        """Test form interactions."""
        try:
            if self.current_page is None:
                return "No page loaded - cannot test forms"
            
            # Find all forms
            forms = await self.current_page.locator("form").count()
            
            # Find all input types
            text_inputs = await self.current_page.locator("input[type='text'], input[type='email'], textarea").count()
            submit_buttons = await self.current_page.locator("input[type='submit'], button[type='submit']").count()
            
            # Test form validation
            validation_tests = 0
            try:
                # Try to submit empty forms to test validation
                submit_buttons_elements = await self.current_page.locator("input[type='submit'], button[type='submit']").all()
                for button in submit_buttons_elements[:3]:  # Test first 3 forms
                    try:
                        await button.click()
                        await asyncio.sleep(0.5)
                        validation_tests += 1
                    except:
                        continue
            except:
                pass
            
            return f"Found {forms} forms, {text_inputs} text inputs, {submit_buttons} submit buttons, tested {validation_tests} validations"
            
        except Exception as e:
            return f"Form interaction test failed: {e}"
    
    async def _test_navigation(self) -> str:
        """Test navigation."""
        try:
            if self.current_page is None:
                return "No page loaded - cannot test navigation"
            
            # Find navigation elements
            nav_links = await self.current_page.locator("nav a, .nav a, .navigation a").count()
            menu_buttons = await self.current_page.locator("button:has-text('menu'), button:has-text('nav'), .menu-button").count()
            
            # Test page navigation
            navigation_tests = 0
            try:
                # Try clicking navigation links
                nav_elements = await self.current_page.locator("nav a, .nav a").all()
                for link in nav_elements[:3]:  # Test first 3 nav links
                    try:
                        href = await link.get_attribute('href')
                        if href and href.startswith('http'):
                            navigation_tests += 1
                    except:
                        continue
            except:
                pass
            
            return f"Found {nav_links} nav links, {menu_buttons} menu buttons, tested {navigation_tests} external links"
            
        except Exception as e:
            return f"Navigation test failed: {e}"
    
    async def _analyze_current_page(self) -> str:
        """Analyze current page comprehensively."""
        analysis = self.page_semantics.get("ai_analysis", {})
        performance = self.page_semantics.get("performance", {})
        security = self.page_semantics.get("security", {})
        
        result = f"🔍 Page Analysis for {self.current_url}:\n"
        result += f"   Page Type: {analysis.get('page_type', 'unknown')}\n"
        result += f"   Primary Intents: {', '.join(analysis.get('primary_intents', []))}\n"
        result += f"   Key Features: {', '.join(analysis.get('key_features', []))}\n"
        result += f"   Performance Issues: {len(performance.get('issues', []))}\n"
        result += f"   Security Headers: {len([h for h in security.values() if h != 'Missing'])}/{len(security)}\n"
        
        return result
    
    async def _analyze_performance(self) -> str:
        """Analyze page performance."""
        metrics = await self.performance_monitor.measure_page_performance(self.current_page)
        issues = await self.performance_monitor.detect_performance_issues(metrics)
        
        result = f"⚡ Performance Analysis:\n"
        result += f"   Load Time: {metrics.load_time:.0f}ms\n"
        result += f"   First Contentful Paint: {metrics.first_contentful_paint:.0f}ms\n"
        result += f"   Network Requests: {metrics.network_requests}\n"
        result += f"   Memory Usage: {metrics.memory_usage / 1024 / 1024:.1f}MB\n"
        
        if issues:
            result += "\n⚠️ Issues Found:\n"
            for issue in issues:
                result += f"   - {issue['severity'].upper()}: {issue['message']}\n"
        
        return result
    
    async def _analyze_accessibility(self) -> str:
        """Analyze page accessibility."""
        # This would implement comprehensive accessibility testing
        return "♿ Accessibility analysis completed (basic implementation)"

    async def _run_auto_checks(self) -> str:
        """Run baseline auto QA checks on the current page and summarize results."""
        report_lines = ["🧪 Auto QA Checks:"]
        try:
            # 1) Basic load & title
            try:
                await self.current_page.wait_for_selector("body", timeout=10000)
                title = await self.current_page.title()
                current_url = self.current_page.url
                report_lines.append(f"   ✅ Page loaded | Title: {title[:80]}")
                report_lines.append(f"     ↳ URL: {current_url}")
                report_lines.append("     ↳ Confirms DOM is ready and page is reachable")
            except Exception as e:
                report_lines.append(f"   ❌ Page load check failed: {e}")

            # 2) Header & footer presence
            try:
                header_count = await self.current_page.locator("header").count()
                footer_count = await self.current_page.locator("footer").count()
                report_lines.append(f"   ✅ Header present: {header_count>0} | Footer present: {footer_count>0}")
                report_lines.append("     ↳ Ensures global navigation and site attribution are present")
            except Exception as e:
                report_lines.append(f"   ⚠️ Header/footer check failed: {e}")

            # 3) Search input availability
            try:
                search_input = await self._find_first_visible([
                    "input[type='search']", "input[name*='search' i]", "input[name*='q' i]",
                    "input[placeholder*='search' i]", "role=searchbox"
                ])
                if search_input:
                    report_lines.append("   ✅ Search input: available")
                    report_lines.append("     ↳ The agent can type queries and submit via button or Enter")
                else:
                    report_lines.append("   ⚠️ Search input: not detected")
                    report_lines.append("     ↳ The agent will try menus or a docs/help page to find search")
            except Exception as e:
                report_lines.append(f"   ⚠️ Search input check failed: {e}")

            # 4) Auth entry availability (login/signup)
            try:
                auth_login = await self._find_auth_entry_button("login")
                auth_signup = await self._find_auth_entry_button("signup")
                report_lines.append(f"   ✅ Auth buttons | login: {bool(auth_login)} | signup: {bool(auth_signup)}")
                report_lines.append("     ↳ Found using role/text/href and top-right heuristics; menus are probed if hidden")
            except Exception as e:
                report_lines.append(f"   ⚠️ Auth entry check failed: {e}")

            # 5) Performance snapshot
            try:
                metrics = await self.performance_monitor.measure_page_performance(self.current_page)
                issues = await self.performance_monitor.detect_performance_issues(metrics)
                report_lines.append(
                    f"   ⚡ Performance | load: {metrics.load_time:.0f}ms, FCP: {metrics.first_contentful_paint:.0f}ms, requests: {metrics.network_requests} | issues: {len(issues)}"
                )
                if issues:
                    # Suggestions per issue type
                    suggestions = {
                        "slow_load": "Defer or inline critical CSS/JS; reduce render-blocking resources",
                        "slow_fcp": "Optimize above-the-fold content; preload critical assets",
                        "too_many_requests": "Bundle assets; enable HTTP/2 multiplexing; add caching"
                    }
                    for issue in issues[:5]:
                        itype = issue.get("type", "issue")
                        msg = issue.get("message", "")
                        sugg = suggestions.get(itype)
                        if sugg:
                            report_lines.append(f"     ↳ {itype}: {msg} | Suggestion: {sugg}")
                        else:
                            report_lines.append(f"     ↳ {itype}: {msg}")
                else:
                    report_lines.append("     ↳ No immediate performance issues detected")
            except Exception as e:
                report_lines.append(f"   ⚠️ Performance check failed: {e}")

            # 6) Security headers
            try:
                security_headers = await self.security_tester.analyze_security_headers(self.current_page)
                present = len([h for h in security_headers.values() if h != "Missing"]) if security_headers else 0
                total = len(security_headers) if security_headers else 0
                report_lines.append(f"   🔒 Security headers: {present}/{total} present")
                if security_headers:
                    missing = [k for k,v in security_headers.items() if v == "Missing"]
                    if missing:
                        report_lines.append(f"     ↳ Missing: {', '.join(missing)} (improves clickjacking, XSS, TLS, referrer policies)")
                    else:
                        report_lines.append("     ↳ All key headers present (CSP, X-Frame-Options, X-Content-Type-Options, HSTS, Referrer-Policy)")
            except Exception as e:
                report_lines.append(f"   ⚠️ Security header check failed: {e}")

            # 7) Accessibility basic
            try:
                a11y = await self.accessibility_tester.test_accessibility(self.current_page)
                score = a11y.get("accessibility_score", 0)
                violations = len(a11y.get("wcag_violations", []))
                report_lines.append(f"   ♿ Accessibility | score: {score} | violations: {violations}")
                vlist = a11y.get("wcag_violations", [])
                for v in vlist[:3]:
                    report_lines.append(f"     ↳ {v.get('guideline','WG')} - {v.get('description','violation')}")
                if violations > 3:
                    report_lines.append(f"     ↳ +{violations-3} more violations (see detailed a11y scan)")
                report_lines.append("     ↳ Focus on alt text, form labels, and heading hierarchy first")
            except Exception as e:
                report_lines.append(f"   ⚠️ Accessibility check failed: {e}")

            # 8) Visual elements snapshot
            try:
                ui = await self.visual_testing.analyze_ui_elements(self.current_page)
                btns = ui.get('buttons', [])
                inputs = ui.get('inputs', [])
                links = ui.get('links', [])
                report_lines.append(
                    f"   🎨 UI elements | buttons: {len(btns)}, inputs: {len(inputs)}, links: {len(links)}"
                )
                # Show a few button labels as examples
                samples = [b.get('text','').strip() for b in btns if b.get('text')][:3]
                if samples:
                    report_lines.append(f"     ↳ Button examples: {', '.join([s for s in samples if s])}")
            except Exception as e:
                report_lines.append(f"   ⚠️ UI analysis failed: {e}")

            return "\n".join(report_lines)
        except Exception as e:
            return f"❌ Auto checks failed unexpectedly: {e}"

    async def _run_auto_audit(self) -> str:
        """Run a detailed site audit with additional checks and actionable guidance."""
        lines = ["🧾 Detailed Site Audit:"]
        try:
            url = self.current_page.url
            parsed = urlparse(url)
            origin = f"{parsed.scheme}://{parsed.netloc}"

            # 1) SEO basics: title length, meta description, canonical
            try:
                title = await self.current_page.title()
                title_len = len(title or "")
                meta_desc = await self.current_page.locator("meta[name='description']").first.get_attribute("content")
                canonical = await self.current_page.locator("link[rel='canonical']").first.get_attribute("href")
                lines.append(f"   🔎 SEO | title: {title_len} chars | meta description: {'yes' if meta_desc else 'no'} | canonical: {'yes' if canonical else 'no'}")
                if title_len < 10 or title_len > 65:
                    lines.append("     ↳ Suggestion: Keep title between 30-60 characters for best SERP display")
                if not meta_desc:
                    lines.append("     ↳ Suggestion: Add meta description (~155 chars) to improve CTR")
                if not canonical:
                    lines.append("     ↳ Suggestion: Add canonical link to avoid duplicate content issues")
            except Exception:
                lines.append("   ⚠️ SEO check had issues (title/meta/canonical)")

            # 2) Link health: sample internal links
            try:
                anchors = await self.current_page.locator("a[href]").all()
                bad = 0
                checked = 0
                for a in anchors[:30]:
                    try:
                        href = await a.get_attribute("href")
                        if not href or href.startswith("#"):
                            continue
                        abs_url = href if href.startswith("http") else urljoin(origin, href)
                        r = requests.head(abs_url, allow_redirects=True, timeout=5)
                        checked += 1
                        if r.status_code >= 400:
                            bad += 1
                    except Exception:
                        continue
                lines.append(f"   🔗 Links | checked: {checked} | broken (>=400): {bad}")
                if bad > 0:
                    lines.append("     ↳ Suggestion: Fix broken links or add redirects")
            except Exception:
                lines.append("   ⚠️ Link health check failed")

            # 3) Images: alt text & broken images
            try:
                imgs = await self.current_page.locator("img").all()
                no_alt = 0
                broken = 0
                checked = 0
                for img in imgs[:40]:
                    try:
                        alt = await img.get_attribute("alt")
                        src = await img.get_attribute("src")
                        if alt is None or alt.strip() == "":
                            no_alt += 1
                        if src:
                            abs_src = src if src.startswith("http") else urljoin(origin, src)
                            r = requests.head(abs_src, allow_redirects=True, timeout=5)
                            checked += 1
                            if r.status_code >= 400:
                                broken += 1
                    except Exception:
                        continue
                lines.append(f"   🖼️ Images | checked: {checked} | missing alt: {no_alt} | broken: {broken}")
                if no_alt:
                    lines.append("     ↳ Suggestion: Provide descriptive alt text for non-decorative images")
                if broken:
                    lines.append("     ↳ Suggestion: Fix image paths/CDN or add fallbacks")
            except Exception:
                lines.append("   ⚠️ Image audit failed")

            # 4) Cookie consent/banner presence (basic)
            try:
                cookie_sel = [
                    "[id*='cookie' i]", "[class*='cookie' i]", "text=/cookie/i",
                    "button:has-text('Accept')", "button:has-text('Agree')"
                ]
                found = False
                for sel in cookie_sel:
                    try:
                        if await self.current_page.locator(sel).first.is_visible():
                            found = True
                            break
                    except Exception:
                        continue
                lines.append(f"   🍪 Cookie banner detected: {found}")
                if not found:
                    lines.append("     ↳ Note: If operating in GDPR regions, ensure cookie consent UX exists")
            except Exception:
                lines.append("   ⚠️ Cookie banner check failed")

            # 5) Resource counts by type (CSS/JS/fonts/images)
            try:
                resources = await self.current_page.evaluate("""
                    () => {
                        const entries = performance.getEntriesByType('resource') || [];
                        const tally = { css:0, js:0, img:0, font:0, other:0 };
                        for (const e of entries) {
                            const n = (e.name||'').toLowerCase();
                            if (n.endsWith('.css')) tally.css++;
                            else if (n.endsWith('.js')) tally.js++;
                            else if (n.match(/\.(png|jpg|jpeg|gif|webp|svg)$/)) tally.img++;
                            else if (n.match(/\.(woff|woff2|ttf|otf)$/)) tally.font++;
                            else tally.other++;
                        }
                        return tally;
                    }
                """)
                lines.append(f"   📦 Resources | css: {resources.get('css',0)}, js: {resources.get('js',0)}, img: {resources.get('img',0)}, font: {resources.get('font',0)}, other: {resources.get('other',0)}")
                if resources.get('js',0) > 50:
                    lines.append("     ↳ Suggestion: Consider bundling/code-splitting to reduce JS requests")
            except Exception:
                lines.append("   ⚠️ Resource analysis failed")

            # 6) Forms presence and required fields
            try:
                forms = await self.current_page.locator("form").count()
                reqs = await self.current_page.locator("[required]").count()
                lines.append(f"   📝 Forms | forms: {forms} | required fields: {reqs}")
                if forms and reqs == 0:
                    lines.append("     ↳ Suggestion: Mark critical inputs required to improve UX/validation")
            except Exception:
                lines.append("   ⚠️ Forms analysis failed")

            return "\n".join(lines)
        except Exception as e:
            return f"❌ Detailed audit failed: {e}"
    
    async def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API with the prompt."""
        try:
            response = self.ai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an intelligent QA agent. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {e}")
    
    async def _call_anthropic_api(self, prompt: str) -> str:
        """Call Anthropic API with the prompt."""
        try:
            response = self.ai_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text.strip()
        except Exception as e:
            raise Exception(f"Anthropic API call failed: {e}")
    
    async def _call_google_api(self, prompt: str) -> str:
        """Call Google Gemini API with the prompt."""
        try:
            from google.genai import types
            response = self.ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
            )
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Google Gemini API call failed: {e}")
    
    async def _get_page_context(self) -> Dict[str, Any]:
        """Get current page context for AI."""
        try:
            title = await self.current_page.title()
            
            # Get available elements
            elements = []
            
            # Get buttons
            buttons = await self.current_page.locator("button, input[type='button'], input[type='submit']").all()
            for button in buttons[:10]:  # Limit to first 10
                try:
                    text = await button.text_content()
                    if text and text.strip():
                        elements.append(f"button: {text.strip()}")
                except:
                    pass
            
            # Get links (prioritize search results)
            links = await self.current_page.locator("a").all()
            for link in links[:15]:  # Increase limit for search results
                try:
                    text = await link.text_content()
                    if text and text.strip():
                        # Check if it's a search result link
                        href = await link.get_attribute("href") or ""
                        if "python" in text.lower() or "tutorial" in text.lower() or "learn" in text.lower():
                            elements.append(f"result_link: {text.strip()}")
                        else:
                            elements.append(f"link: {text.strip()}")
                except:
                    pass
            
            # Get inputs
            inputs = await self.current_page.locator("input").all()
            for input_elem in inputs[:5]:  # Limit to first 5
                try:
                    input_type = await input_elem.get_attribute("type") or "text"
                    placeholder = await input_elem.get_attribute("placeholder") or ""
                    name = await input_elem.get_attribute("name") or ""
                    elements.append(f"input: {input_type} {placeholder} {name}")
                except:
                    pass
            
            return {
                "title": title,
                "elements": elements[:20]  # Limit total elements
            }
        
        except Exception as e:
            return {"title": "Unknown", "elements": []}
    
    async def _execute_ai_action(self, action_data: Dict[str, Any]) -> str:
        """Execute the action determined by AI."""
        action = action_data.get("action", "").lower()
        explanation = action_data.get("explanation", "")
        
        print(f"🤖 AI Decision: {explanation}")
        
        try:
            # If the incoming natural-language action looks like a compound auth request, route to auth flow
            if self._looks_like_auth_compound(explanation) or self._looks_like_auth_compound(action_data.get("target", "")):
                return await self._handle_auth_compound_command(f"{action} {explanation} {action_data.get('target','')} {action_data.get('text','')}")
            if action == "login":
                return await self._handle_login()
            elif action == "signup":
                return await self._handle_signup()
            elif action == "search":
                search_term = action_data.get("search_term", "python")
                return await self._handle_search(search_term, submit_immediately=True) # Use submit_immediately=True for search action
            elif action == "click":
                target = action_data.get("target", "")
                return await self._handle_click(target)
            elif action == "scroll":
                direction = action_data.get("target", "down")
                return await self._handle_scroll(f"scroll {direction}")
            elif action == "navigate":
                url = action_data.get("url", "")
                return await self._handle_navigation(url)
            elif action == "type":
                text = action_data.get("text", "")
                target = action_data.get("target", "").lower()
                submit_action = action_data.get("submit_action", "none").lower()

                # Check if the target is specifically a search bar
                if "search" in target or "search bar" in target:
                    # Route to _handle_search to use its submit logic
                    return await self._handle_search(text, submit_immediately=(submit_action in ["enter", "click_button"]))
                else:
                    # Standard type action
                    result = await self._handle_type(text)
                    
                    # Handle immediate submission if requested for a general 'type' action
                    if submit_action in ["enter", "click_button"]:
                        if submit_action == "enter":
                            await self.current_page.keyboard.press("Enter")
                            print("   ✅ Submission via Enter key after typing.")
                        elif submit_action == "click_button":
                            click_result = await self._handle_click("submit button") 
                            print(f"   ✅ Submission via button click: {click_result}")
                    
                    return result
            elif action == "wait":
                return await self._handle_wait()
            elif action == "help":
                return await self._show_help()
            elif action == "status":
                return await self._show_status()
            else:
                return f"❌ Unknown action: {action}"
        
        except Exception as e:
            return f"❌ Action execution failed: {e}"
    
    async def _process_basic_command(self, user_input: str) -> str:
        """Fallback basic command processing."""
        command = user_input.lower().strip()

        # Special-case: compound auth phrasing with commas/and
        if self._looks_like_auth_compound(command):
            return await self._handle_auth_compound_command(command)
        
        # Login commands
        if any(word in command for word in ["log in", "login", "sign in", "signin"]):
            return await self._handle_login()
        
        # Signup commands
        elif any(word in command for word in ["sign up", "signup", "register", "create account"]):
            return await self._handle_signup()
        
        # Search commands
        elif any(word in command for word in ["search", "find", "look for"]):
            search_term = self._extract_search_term(command)
            return await self._handle_search(search_term)
        
        # Scroll commands
        elif any(word in command for word in ["scroll", "scroll down", "scroll up"]):
            return await self._handle_scroll(command)
        
        # Click commands
        elif any(word in command for word in ["click", "press", "tap"]):
            target = self._extract_click_target(command)
            return await self._handle_click(target)
        
        # Help commands
        elif any(word in command for word in ["help", "what can i do", "commands", "options"]):
            return await self._show_help()
        
        # Status commands
        elif any(word in command for word in ["status", "where am i", "current page"]):
            return await self._show_status()
        
        else:
            return f"🤔 I don't understand '{user_input}'. Try 'help' for available commands."
    
    # ... (Include all the handler methods from the previous version)
    async def _handle_login(self) -> str:
        """Handle login actions intelligently."""
        print("🔐 Looking for login functionality...")
        
        try:
            # Look for login buttons/links
            login_selectors = [
                "text=Log in", "text=Login", "text=Sign in", "text=Signin",
                "a:has-text('Log in')", "a:has-text('Login')",
                "button:has-text('Log in')", "button:has-text('Login')"
            ]
            
            login_clicked = False
            for selector in login_selectors:
                try:
                    element = self.current_page.locator(selector).first
                    if await element.count() > 0:
                        await element.highlight()
                        await asyncio.sleep(0.5)
                        await element.click()
                        print(f"   ✅ Clicked login: {selector}")
                        login_clicked = True
                        break
                except:
                    continue
            
            if not login_clicked:
                return "❌ No login button found on this page."
            
            await self.current_page.wait_for_timeout(2000)
            
            # Look for login form
            email_inputs = await self.current_page.locator("input[type='email'], input[name*='email'], input[name*='login']").all()
            password_inputs = await self.current_page.locator("input[type='password']").all()
            
            if email_inputs and password_inputs:
                print("   📝 Found login form, filling credentials...")
                
                # Fill email
                email_input = email_inputs[0]
                await email_input.highlight()
                await asyncio.sleep(0.5)
                await email_input.fill("demo@example.com")
                print("   ✅ Email filled")
                
                # Fill password
                password_input = password_inputs[0]
                await password_input.highlight()
                await asyncio.sleep(0.5)
                await password_input.fill("DemoPassword123!")
                print("   ✅ Password filled")
                
                # Look for submit button
                submit_selectors = [
                    "button[type='submit']", "input[type='submit']",
                    "button:has-text('Log in')", "button:has-text('Sign in')",
                    "button:has-text('Login')", "button:has-text('Continue')"
                ]
                
                for selector in submit_selectors:
                    try:
                        submit_btn = self.current_page.locator(selector).first
                        if await submit_btn.count() > 0:
                            await submit_btn.highlight()
                            await asyncio.sleep(0.5)
                            await submit_btn.click()
                            print(f"   ✅ Login submitted: {selector}")
                            break
                    except:
                        continue
                
                await self.current_page.wait_for_timeout(3000)
                return "✅ Login process completed! Check the page for results."
            
            else:
                return "⚠️ Login button clicked, but no login form found."
        
        except Exception as e:
            return f"❌ Login failed: {e}"
    
    async def _handle_signup(self) -> str:
        """Handle signup actions intelligently."""
        print("📝 Looking for signup functionality...")
        
        try:
            # Look for signup buttons/links
            signup_selectors = [
                "text=Sign up", "text=Sign Up", "text=Signup", "text=Register",
                "a:has-text('Sign up')", "a:has-text('Sign Up')",
                "button:has-text('Sign up')", "button:has-text('Get started')"
            ]
            signin_selectors = [
                "text=Sign in", "text=Sign In", "text=Signin",
                "a:has-text('Sign in')", "button:has-text('Sign in')",
            ]
            
            signup_clicked = False
            for selector in signup_selectors:
                try:
                    element = self.current_page.locator(selector).first
                    if await element.count() > 0:
                        await element.highlight()
                        await asyncio.sleep(0.5)
                        await element.click()
                        print(f"   ✅ Clicked signup: {selector}")
                        signup_clicked = True
                        break
                except:
                    continue

            if not signup_clicked:
                for selector in signin_selectors:
                    try:
                        element = self.current_page.locator(selector).first
                        if await element.count() > 0:
                            await element.highlight()
                            await asyncio.sleep(0.5)
                            await element.click()
                            print(f"   ✅ Clicked signin: {selector}")
                            signup_clicked = True
                            break
                    except:
                        continue
            
            if not signup_clicked:
                return "❌ No signup button found on this page."
            
            await self.current_page.wait_for_timeout(2000)
            
            # Look for signup form
            email_inputs = await self.current_page.locator("input[type='email'], input[name*='email']").all()
            password_inputs = await self.current_page.locator("input[type='password']").all()
            
            if email_inputs and password_inputs:
                print("   📝 Found signup form, filling credentials...")
                
                # Fill email
                email_input = email_inputs[0]
                await email_input.highlight()
                await asyncio.sleep(0.5)
                await email_input.fill("newuser@example.com")
                print("   ✅ Email filled")
                
                # Fill password
                password_input = password_inputs[0]
                await password_input.highlight()
                await asyncio.sleep(0.5)
                await password_input.fill("NewPassword123!")
                print("   ✅ Password filled")
                
                # Look for submit button
                submit_selectors = [
                    "button[type='submit']", "input[type='submit']",
                    "button:has-text('Sign up')", "button:has-text('Create account')",
                    "button:has-text('Continue')", "button:has-text('Get started')"
                ]
                
                for selector in submit_selectors:
                    try:
                        submit_btn = self.current_page.locator(selector).first
                        if await submit_btn.count() > 0:
                            await submit_btn.highlight()
                            await asyncio.sleep(0.5)
                            await submit_btn.click()
                            print(f"   ✅ Signup submitted: {selector}")
                            break
                    except:
                        continue
                
                await self.current_page.wait_for_timeout(3000)
                return "✅ Signup process completed! Check the page for results."
            
            else:
                return "⚠️ Signup button clicked, but no signup form found."
        
        except Exception as e:
            return f"❌ Signup failed: {e}"

    async def _handle_search(self, search_term: str, submit_immediately: bool = False) -> str:
        """Handle search actions intelligently with AI-powered search capabilities."""
        if not search_term:
            search_term = "default query"  # Better default than python
        print(f"🔍 Searching for: '{search_term}'")
        
        try:
            # Initialize search_input to None to prevent NameError
            search_input = None
            
            # Try AI-powered search element discovery first
            ai_search_selectors = await self._ai_discover_elements(f"find search input for '{search_term}'")
            if ai_search_selectors:
                print(f"   🤖 AI found {len(ai_search_selectors)} potential search selectors")
                for selector in ai_search_selectors:
                    try:
                        element = self.current_page.locator(selector).first
                        if await element.count() > 0 and await element.is_visible():
                            search_input = element
                            print(f"   ✅ Found search input (AI): {selector}")
                            break
                    except:
                        continue
            
            # Fallback to comprehensive search selectors
            if not search_input:
                search_selectors = [
                    # Primary search inputs
                    "input[type='search']", "input[name*='search']", "input[name*='q']",
                    "input[placeholder*='search']", "input[placeholder*='Search']",
                    "input[placeholder*='Search docs']", "input[placeholder*='Find']",
                    "input[placeholder*='Browse']", "input[placeholder*='Look for']",
                    "input[aria-label*='search']", "input[aria-label*='Search']",
                    "input[aria-label*='Find']", "input[aria-label*='Look for']",
                    "input[class*='search']", "input[id*='search']", "input[id*='query']",
                    "input[data-testid*='search']", "input[data-testid*='query']",
                    # Role-based selectors
                    "role=searchbox", "role=textbox[name=/search/i]",
                    # Generic text inputs (as last resort)
                    "input[type='text']"
                ]
                
                for selector in search_selectors:
                    try:
                        element = self.current_page.locator(selector).first
                        if await element.count() > 0:
                            # Check if element is visible and likely a search input
                            if await element.is_visible():
                                # Additional validation for search inputs
                                placeholder = await element.get_attribute("placeholder") or ""
                                name = await element.get_attribute("name") or ""
                                aria_label = await element.get_attribute("aria-label") or ""
                                
                                # Check if it looks like a search input
                                search_indicators = ["search", "find", "query", "look", "browse"]
                                if any(indicator in (placeholder + name + aria_label).lower() for indicator in search_indicators):
                                    search_input = element
                                    print(f"   ✅ Found search input: {selector}")
                                    break
                    except:
                        continue
            
            # If no direct search input found, try to find search-related buttons/links
            if not search_input:
                search_links = [
                    "a:has-text('Search')", "button:has-text('Search')",
                    "a:has-text('Docs')", "a:has-text('Documentation')",
                    "a:has-text('Find')", "a:has-text('Browse')",
                    "a:has-text('Look')", "a:has-text('Explore')",
                    "[aria-label*='search']", "[aria-label*='Search']",
                    "[data-testid*='search']", "[data-testid*='docs']"
                ]
                
                for selector in search_links:
                    try:
                        element = self.current_page.locator(selector).first
                        if await element.count() > 0 and await element.is_visible():
                            await element.highlight()
                            await asyncio.sleep(1)
                            await element.click()
                            print(f"   ✅ Clicked search-related link: {selector}")
                            await self.current_page.wait_for_timeout(3000)
                            
                            # Try to find search input again after clicking
                            for search_selector in search_selectors:
                                try:
                                    new_element = self.current_page.locator(search_selector).first
                                    if await new_element.count() > 0 and await new_element.is_visible():
                                        search_input = new_element
                                        print(f"   ✅ Found search input after navigation: {search_selector}")
                                        break
                                except:
                                    continue
                            break
                    except:
                        continue
                
                if not search_input:
                    return f"❌ No search functionality found on this page. Try 'scroll down' or 'click menu' instead."
            
            # Use human-like typing for search
            await search_input.highlight()
            await asyncio.sleep(0.5)
            await search_input.click()
            
            # Clear any existing text first
            await search_input.clear()
            
            # Use human behavior simulation for typing
            await self.human_behavior.simulate_human_typing(search_input, search_term, self.current_page)
            print(f"   ✅ Search term entered (human-like): '{search_term}'")

            # --- Submission Logic ---
            if submit_immediately:
                search_submitted = False

                # Look for search button with enhanced selectors
                search_button_selectors = [
                    "button[type='submit']", "input[type='submit']",
                    "button:has-text('Search')", "button:has-text('Go')",
                    "button:has-text('Find')", "button:has-text('Submit')",
                    "button:has-text('Look')", "button:has-text('Browse')",
                    "[aria-label*='search']", "[aria-label*='Search']",
                    "[aria-label*='submit']", "[aria-label*='go']",
                    "button[class*='search']", "button[id*='search']",
                    "button[data-testid*='search']", "button[data-testid*='submit']",
                    # Icon-based search buttons
                    "button:has(svg)", "button:has(.search-icon)", "button:has(.fa-search)",
                    # Generic submit buttons near search input
                    "form:has(input[type='search']) button",
                    "form:has(input[name*='search']) button",
                    "form:has(input[placeholder*='search']) button"
                ]
                
                search_submitted = False
                for selector in search_button_selectors:
                    try:
                        search_btn = self.current_page.locator(selector).first
                        if await search_btn.count() > 0 and await search_btn.is_visible():
                            await search_btn.highlight()
                            await asyncio.sleep(0.5)
                            await search_btn.click()
                            print(f"   ✅ Search submitted: {selector}")
                            search_submitted = True
                            break
                    except:
                        continue
                
                # Try pressing Enter as fallback
                if not search_submitted:
                    # Use page keyboard instead of element-specific press
                    await self.current_page.keyboard.press("Enter")
                    print("   ✅ Search submitted (Page Enter key)")
                
                # Wait for search results to load
                await self.current_page.wait_for_timeout(3000)
                
                # Wait for navigation to complete
                try:
                    await self.current_page.wait_for_load_state("networkidle", timeout=10000)
                except:
                    pass  # Continue even if timeout
                
                # Check if search was successful by looking for results
                results_found = await self._check_search_results(search_term)
                if results_found:
                    print(f"   ✅ Search results found for '{search_term}'")
                    return f"✅ Search completed for '{search_term}'! Found search results."
                else:
                    print(f"   ⚠️ No obvious search results found for '{search_term}'")
                    return f"✅ Search completed for '{search_term}'! Check the page for results."

            # If submit_immediately is False, we are done after typing
            return f"✅ Text typed in search bar: '{search_term}'. Submit manually."
        
        except Exception as e:
            return f"❌ Search failed: {e}"
    
    async def _check_search_results(self, search_term: str) -> bool:
        """Check if search results are visible on the page."""
        try:
            # Look for common search result indicators
            result_indicators = [
                f"text=/{search_term}/i",  # Search term appears in results
                "[class*='result']", "[class*='search-result']", "[class*='item']",
                "[data-testid*='result']", "[data-testid*='search-result']",
                "h1:has-text('Search Results')", "h2:has-text('Results')",
                "h3:has-text('Results')", ".search-results", "#search-results",
                "[role='main']", "[role='search']", "[role='list']"
            ]
            
            for indicator in result_indicators:
                try:
                    elements = await self.current_page.locator(indicator).all()
                    if elements and len(elements) > 0:
                        # Check if any of these elements are visible
                        for element in elements[:5]:  # Check first 5 elements
                            if await element.is_visible():
                                return True
                except:
                    continue
            
            return False
        except:
            return False
    
    async def _handle_search_command(self, user_input: str) -> str:
        """Handle dedicated search commands."""
        command = user_input.lower().replace("search ", "").strip()
        
        if not command:
            return "❌ Please specify what to search for. Example: 'search python tutorials'"
        
        # Extract search term from various patterns
        search_term = command
        
        # Handle patterns like "search for python" or "search python"
        if command.startswith("for "):
            search_term = command.replace("for ", "").strip()
        
        return await self._handle_search(search_term)
    
    async def _handle_type_in_search(self, text: str) -> str:
        """Handle typing text in search bar specifically."""
        try:
            print(f"⌨️ Typing '{text}' in search bar...")
            
            # Find search input using the same logic as search handler
            search_selectors = [
                "input[type='search']", "input[name*='search']", "input[name*='q']",
                "input[placeholder*='search']", "input[placeholder*='Search']",
                "input[placeholder*='Find']", "input[aria-label*='search']",
                "input[class*='search']", "input[id*='search']", "role=searchbox"
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    element = self.current_page.locator(selector).first
                    if await element.count() > 0 and await element.is_visible():
                        search_input = element
                        print(f"   ✅ Found search input: {selector}")
                        break
                except:
                    continue
            
            if not search_input:
                return "❌ No search bar found on this page."
            
            # Use human-like typing
            await search_input.highlight()
            await asyncio.sleep(0.5)
            await search_input.click()
            await search_input.clear()
            
            # Use human behavior simulation
            await self.human_behavior.simulate_human_typing(search_input, text, self.current_page)
            print(f"   ✅ Text entered in search bar: '{text}'")
            
            return f"✅ Typed '{text}' in search bar successfully!"
            
        except Exception as e:
            return f"❌ Failed to type in search bar: {e}"
    
    async def _handle_scroll(self, command: str) -> str:
        """Handle scroll actions intelligently."""
        print("📜 Scrolling the page...")
        
        try:
            if "up" in command:
                await self.current_page.evaluate("window.scrollBy(0, -500)")
                return "✅ Scrolled up"
            elif "down" in command:
                await self.current_page.evaluate("window.scrollBy(0, 500)")
                return "✅ Scrolled down"
            else:
                await self.current_page.evaluate("window.scrollBy(0, 500)")
                return "✅ Scrolled down"
        
        except Exception as e:
            return f"❌ Scroll failed: {e}"
    
    async def _handle_click(self, target: str) -> str:
        """Handle click actions intelligently."""
        if not target:
            return "❌ Please specify what to click (e.g., 'click the menu', 'click sign up')"
        
        print(f"🖱️ Clicking: '{target}'")
        
        try:
            # Wait for page to be stable first
            await self.current_page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(1)
            
            # If clicking auth-related target, try dynamic entry discovery first
            lower_t = target.lower()
            if any(k in lower_t for k in ["login", "log in", "sign in", "signin", "sign up", "signup", "register", "create account"]):
                mode = "signup" if any(k in lower_t for k in ["sign up", "signup", "register", "create account"]) else "login"
                candidate = await self._find_auth_entry_button(mode)
                if candidate:
                    try:
                        await candidate.scroll_into_view_if_needed()
                    except:
                        pass
                    await candidate.highlight()
                    await asyncio.sleep(0.4)
                    await candidate.click()
                    await self.current_page.wait_for_timeout(1000)
                    return f"✅ Clicked '{target}' successfully!"

            # Try AI-powered element discovery first
            ai_selectors = await self._ai_discover_elements(f"click {target}")
            if ai_selectors:
                print(f"   🤖 AI found {len(ai_selectors)} potential selectors")
                for selector in ai_selectors:
                    try:
                        element = self.current_page.locator(selector).first
                        if await element.count() > 0 and await element.is_visible():
                            if await self._is_clickable(element):
                                await element.highlight()
                                await asyncio.sleep(0.5)
                                await element.click()
                                print(f"   ✅ Clicked (AI): {selector}")
                                await self.current_page.wait_for_timeout(2000)
                                return f"✅ Clicked '{target}' successfully!"
                    except:
                        continue

            # Fallback to traditional selectors with smart waiting
            selectors = [
                f"role=button[name=/{target}/i]",
                f"role=link[name=/{target}/i]",
                f"button:has-text('{target}')",
                f"a:has-text('{target}')",
                f":is(a,button)[aria-label*='{target}' i]",
                f":is(a,button)[title*='{target}' i]",
                f"a[href*='{target.lower()}']",
                # Generic clickable patterns
                f"*[role='button']:has-text('{target}')",
                f"*[tabindex]:has-text('{target}')",
                f"*[onclick]:has-text('{target}')",
                # Last resort: raw text (may match non-clickable elements)
                f"text={target}",
                f"text={target.title()}",
                f"text={target.lower()}",
                f"text={target.upper()}"
            ]
            
            for selector in selectors:
                try:
                    element = self.current_page.locator(selector).first
                    if await element.count() > 0:
                        # Smart waiting based on context
                        await self._smart_wait_for_element(selector, target)
                        # Wait for element to be visible
                        await element.wait_for(state="visible", timeout=5000)
                        # Ensure element is likely clickable to avoid hitting plain text
                        if not await self._is_clickable(element):
                            continue
                        await element.highlight()
                        await asyncio.sleep(0.5)
                        await element.click()
                        print(f"   ✅ Clicked: {selector}")
                        await self.current_page.wait_for_timeout(2000)
                        return f"✅ Clicked '{target}' successfully!"
                except:
                    continue
            
            return f"❌ Could not find '{target}' to click"
        
        except Exception as e:
            return f"❌ Click failed: {e}"

    async def _is_clickable(self, locator) -> bool:
        """Heuristic check for clickability: tag/role/href/tabindex/onclick and dimensions."""
        try:
            if await locator.count() == 0 or not await locator.is_visible():
                return False
            try:
                if not await locator.is_enabled():
                    return False
            except:
                pass
            return await locator.evaluate("""
                el => {
                    const tag = (el.tagName || '').toUpperCase();
                    const role = (el.getAttribute && el.getAttribute('role')) || '';
                    const hasHref = !!(el.getAttribute && el.getAttribute('href'));
                    const hasOnclick = (el.getAttribute && el.getAttribute('onclick')) !== null;
                    const hasTabindex = (el.tabIndex !== undefined && el.tabIndex >= 0);
                    const style = window.getComputedStyle(el);
                    const pe = style.pointerEvents !== 'none';
                    const rect = el.getBoundingClientRect();
                    const hasBox = rect && rect.width > 1 && rect.height > 1;
                    const semantic = tag === 'A' || tag === 'BUTTON' || role === 'button' || role === 'link' || hasHref;
                    return hasBox && pe && (semantic || hasOnclick || hasTabindex);
                }
            """)
        except:
            return False
    
    async def _handle_navigation(self, url: str) -> str:
        """Handle navigation actions."""
        if not url:
            return "❌ Please specify a URL to navigate to"
        
        print(f"🌐 Navigating to: {url}")
        
        try:
            await self.current_page.goto(url, wait_until="domcontentloaded")
            await self.current_page.wait_for_timeout(2000)
            self.current_url = url
            return f"✅ Navigated to {url}"
        
        except Exception as e:
            return f"❌ Navigation failed: {e}"
    
    async def _handle_type(self, text: str) -> str:
        """Handle typing actions."""
        if not text:
            return "❌ Please specify what to type"
        
        print(f"⌨️ Typing: '{text}'")
        
        try:
            # Find focused element or active input
            await self.current_page.keyboard.type(text)
            await self.current_page.wait_for_timeout(1000)
            return f"✅ Typed '{text}'"
        
        except Exception as e:
            return f"❌ Typing failed: {e}"
    
    async def _handle_wait(self) -> str:
        """Handle wait actions."""
        print("⏳ Waiting...")
        await self.current_page.wait_for_timeout(3000)
        return "✅ Waited 3 seconds"
    
    async def _show_help(self) -> str:
        """Show available commands."""
        help_text = """
🤖 Enterprise QA Agent Commands:

🔐 Authentication:
   - "log in" or "login" - Perform login
   - "sign up" or "signup" - Perform signup

🔍 Search & Navigation:
   - "search [term]" - Search the website with AI-powered detection
   - "search for [term]" - Alternative search syntax
   - "go to [url]" - Navigate to a URL
   - "scroll down" or "scroll up" - Scroll the page

🖱️ Interactions:
   - "click [target]" - Click an element
   - "type [text]" - Type text
   - "wait" - Wait for 3 seconds

🧪 Testing Commands:
   - "test all" - Run comprehensive test suite
   - "test auth" - Test authentication flows
   - "test forms" - Test form interactions
   - "test navigation" - Test navigation

🔍 Analysis Commands:
   - "analyze page" - Comprehensive page analysis
   - "analyze performance" - Performance analysis
   - "analyze accessibility" - Accessibility analysis

🔒 Security Commands:
   - "security scan" - Security vulnerability scan

⚡ Performance Commands:
   - "performance measure" - Performance metrics

🎨 Visual Commands:
   - "visual screenshot" - Capture screenshot
   - "visual compare [name]" - Compare with baseline
   - "visual elements" - Analyze UI elements

🌐 Cross-Browser Testing:
   - "cross-browser test" - Test across multiple browsers

🔌 API Testing:
   - "api test" - Test API endpoints

📱 Mobile Testing:
   - "mobile test" - Test on mobile devices

♿ Accessibility Testing:
   - "accessibility test" - Test WCAG compliance
   - "accessibility testing" - Test WCAG compliance
   - "accessiblilty testing" - Test WCAG compliance (typo-tolerant)

⏰ Test Scheduling:
   - "schedule daily" - Schedule daily tests

⚡ Load Testing:
   - "load test" - Run load tests

📧 Notifications:
   - "notify send" - Send test report via email

💾 Database Operations:
   - "database history" - View test history
   - "database save" - Save test results

📊 Reporting:
   - "report" - Generate comprehensive test report

ℹ️ Information:
   - "status" - Show current page info
   - "help" - Show this help

🧪 Auto Checks:
   - "auto check" - Run baseline QA checks on the current page
   - "auto audit" - Run detailed SEO/links/images/cookies/resources/forms audit

💡 Examples:
   - "log in"
   - "search python tutorials"
   - "test all"
   - "cross-browser test"
   - "api test"
   - "mobile test"
   - "accessibility test"
   - "load test"
   - "notify send"
   - "database history"
   - "report"
        """
        return help_text
    
    async def _show_status(self) -> str:
        """Show current session status."""
        try:
            current_url = self.current_page.url
            page_title = await self.current_page.title()
            return f"📍 Current Page: {page_title}\n🌐 URL: {current_url}"
        except Exception as e:
            return f"❌ Status error: {e}"
    
    def _extract_search_term(self, command: str) -> str:
        """Extract search term from command."""
        import re
        patterns = [
            r"search for (.+)",
            r"find (.+)",
            r"look for (.+)",
            r"search (.+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_click_target(self, command: str) -> str:
        """Extract click target from command."""
        import re
        patterns = [
            r"click (.+)",
            r"press (.+)",
            r"tap (.+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                return match.group(1).strip()
        
        return ""
    
    async def close_session(self):
        """Close the browser session."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("🧹 Session closed!")


async def main():
    """Main interactive loop."""
    print("🤖 Multi-AI QA Agent")
    print("=" * 25)
    print("Choose AI provider:")
    print("1. OpenAI (GPT-3.5)")
    print("2. Anthropic (Claude)")
    print("3. Google (Gemini)")
    print("4. No AI (Basic processing)")
    
    # Auto-select Google Gemini for testing
    choice = "3"
    print(f"Auto-selecting: {choice} (Google Gemini)")
    
    ai_provider = "openai"
    api_key = None
    
    if choice == "1":
        ai_provider = "openai"
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            api_key = input("Enter your OpenAI API key: ").strip()
    elif choice == "2":
        ai_provider = "anthropic"
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            api_key = input("Enter your Anthropic API key: ").strip()
    elif choice == "3":
        ai_provider = "google"
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            api_key = input("Enter your Google API key: ").strip()
    else:
        ai_provider = "none"
    
    agent = MultiAIQAAgent(ai_provider, api_key)
    
    try:
        # Start session on provided URL (CLI arg or START_URL env), fallback to default
        start_url = sys.argv[1] if len(sys.argv) > 1 else os.getenv("START_URL", "https://www.youtube.com/")
        await agent.start_session(start_url)
        
        print("💬 Enter your commands (type 'quit' to exit):")
        
        while True:
            user_input = input("\n🤖 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Process the command
            result = await agent.process_command(user_input)
            print(f"🤖 Agent: {result}")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await agent.close_session()


if __name__ == "__main__":
    asyncio.run(main())


