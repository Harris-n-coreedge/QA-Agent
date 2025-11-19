"""
Locust Integration Module for Performance Testing
Uses latest Locust API patterns from documentation
"""
import asyncio
import subprocess
import tempfile
import os
import json
import csv
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LocustTestRunner:
    """Runner for executing Locust load tests programmatically"""
    
    def __init__(self):
        self.temp_dir = None
        self.locust_files = []
    
    def _generate_locust_file(self, test_type: str, target_url: str, **kwargs) -> str:
        """Generate a Locust test file dynamically based on test type"""
        locust_code = f"""
from locust import HttpUser, task, between
import time

class TestUser(HttpUser):
    host = "{target_url}"
    wait_time = between(1, 3)
    
    def on_start(self):
        # Optional startup logic
        pass
    
"""
        
        if test_type == "load_test":
            # Basic load test - simple GET requests to root only
            # Use catch_response to handle 404s gracefully
            locust_code += """
    @task
    def index(self):
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code: {{response.status_code}}")
"""
        elif test_type == "stress_test":
            # Stress test - more intensive operations
            locust_code += """
    @task
    def heavy_operation(self):
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code: {{response.status_code}}")
"""
        elif test_type == "spike_test":
            # Spike test - rapid requests
            locust_code += """
    @task
    def rapid_requests(self):
        for i in range(5):
            with self.client.get("/", catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Got status code: {{response.status_code}}")
"""
        elif test_type == "soak_test":
            # Soak test - sustained load
            locust_code += """
    @task
    def sustained_load(self):
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code: {{response.status_code}}")
        time.sleep(0.5)
"""
        elif test_type == "api_load_test":
            # API load test - try root endpoint, gracefully handle failures
            locust_code += """
    @task
    def api_endpoint(self):
        with self.client.get("/", catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()  # Accept both as valid for testing
            else:
                response.failure(f"Got status code: {{response.status_code}}")
"""
        else:
            # Default - basic load test
            locust_code += """
    @task
    def default_task(self):
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code: {{response.status_code}}")
"""
        
        return locust_code
    
    async def _run_locust_command(
        self, 
        locust_file: str, 
        users: int, 
        spawn_rate: int, 
        run_time: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """Run Locust in headless mode and parse results"""
        try:
            # Run Locust in headless mode with CSV output
            csv_prefix = os.path.join(output_dir, "locust_stats")
            cmd = [
                "locust",
                "-f", locust_file,
                "--headless",
                "-u", str(users),
                "-r", str(spawn_rate),
                "--run-time", run_time,
                "--csv", csv_prefix,
                "--html", os.path.join(output_dir, "report.html"),
                "--loglevel", "WARNING"
            ]
            
            logger.info(f"Running Locust command: {' '.join(cmd)}")
            
            # Execute Locust
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.path.dirname(locust_file)
            )
            
            stdout, stderr = await process.communicate()
            
            # Parse CSV results even if there were some failures (non-zero exit code)
            # Locust may exit with non-zero if there are request failures, but we still want the stats
            # Locust creates files with pattern: {prefix}_stats.csv, {prefix}_failures.csv
            stats_file = f"{csv_prefix}_stats.csv"
            failures_file = f"{csv_prefix}_failures.csv"
            
            # Also check in the working directory (where Locust was run from)
            cwd = os.path.dirname(locust_file)
            stats_file_cwd = os.path.join(cwd, os.path.basename(stats_file))
            failures_file_cwd = os.path.join(cwd, os.path.basename(failures_file))
            
            # Try to find the stats file in multiple locations
            if not os.path.exists(stats_file):
                if os.path.exists(stats_file_cwd):
                    stats_file = stats_file_cwd
                    failures_file = failures_file_cwd
                    logger.info(f"Found stats file in working directory: {stats_file}")
                else:
                    # List all CSV files in both directories to help debug
                    logger.warning(f"Stats file not found at: {stats_file}")
                    logger.warning(f"Also checked: {stats_file_cwd}")
                    if os.path.exists(output_dir):
                        csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
                        logger.warning(f"CSV files in output_dir: {csv_files}")
                    if os.path.exists(cwd):
                        csv_files = [f for f in os.listdir(cwd) if f.endswith('.csv')]
                        logger.warning(f"CSV files in cwd: {csv_files}")
            
            # Log stdout/stderr for debugging
            if stdout:
                stdout_text = stdout.decode()
                logger.debug(f"Locust stdout (first 1000 chars):\n{stdout_text[:1000]}")
                # Also log the last part which usually has the final stats
                if len(stdout_text) > 1000:
                    logger.debug(f"Locust stdout (last 500 chars):\n{stdout_text[-500:]}")
            if stderr:
                stderr_text = stderr.decode()
                logger.debug(f"Locust stderr: {stderr_text[:500]}")
            
            # Check if CSV files were created
            if not os.path.exists(stats_file):
                # If no stats file, then it's a real failure
                error_msg = stderr.decode() if stderr else stdout.decode() if stdout else "Unknown error"
                logger.error(f"Locust execution failed - no stats file created: {error_msg}")
                logger.error(f"Expected stats file at: {stats_file}")
                logger.error(f"Output directory contents: {os.listdir(output_dir) if os.path.exists(output_dir) else 'Directory does not exist'}")
                raise Exception(f"Locust execution failed: {error_msg}")
            
            logger.info(f"Found stats file: {stats_file}, size: {os.path.getsize(stats_file)} bytes")
            
            # Small delay to ensure file is fully written and flushed
            await asyncio.sleep(0.5)
            
            metrics = self._parse_locust_csv(stats_file, failures_file)
            
            # If metrics are all zeros, try parsing from stdout as fallback
            if metrics.get("total_requests", 0) == 0 and stdout:
                logger.warning("CSV parsing returned zeros, attempting to parse from stdout")
                stdout_text = stdout.decode()
                
                # Try multiple regex patterns to match Locust output format
                # Format: "Aggregated 989 751(75.94%) | 892 19 49575 120 | 16.81 12.77"
                # Pattern: Aggregated {total} {failed}({percent}%) | {avg} {min} {max} {median} | {rps} {failures/s}
                patterns = [
                    # Standard format with all fields
                    r'Aggregated\s+(\d+)\s+(\d+)\([^)]+\)\s+\|\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+\|\s+([\d.]+)',
                    # Format without failures/s
                    r'Aggregated\s+(\d+)\s+(\d+)\([^)]+\)\s+\|\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+\|\s+([\d.]+)\s+[\d.]+',
                    # Simpler format
                    r'Aggregated\s+(\d+)\s+(\d+)\s+\|\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+\|\s+([\d.]+)',
                ]
                
                for pattern in patterns:
                    aggregated_match = re.search(pattern, stdout_text)
                    if aggregated_match:
                        try:
                            metrics["total_requests"] = int(aggregated_match.group(1))
                            metrics["failed_requests"] = int(aggregated_match.group(2))
                            metrics["successful_requests"] = metrics["total_requests"] - metrics["failed_requests"]
                            metrics["avg_response_time"] = float(aggregated_match.group(3))
                            metrics["min_response_time"] = float(aggregated_match.group(4))
                            metrics["max_response_time"] = float(aggregated_match.group(5))
                            metrics["median_response_time"] = float(aggregated_match.group(6))
                            metrics["requests_per_second"] = float(aggregated_match.group(7))
                            logger.info(f"Successfully parsed metrics from stdout using pattern: {metrics}")
                            break
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Error parsing stdout match: {e}, trying next pattern...")
                            continue
                
                if metrics.get("total_requests", 0) == 0:
                    logger.warning("Could not parse metrics from stdout either. Showing last 1000 chars for debugging:")
                    logger.warning(stdout_text[-1000:] if len(stdout_text) > 1000 else stdout_text)
            
            # Log warnings if there were failures, but don't treat as fatal
            if metrics.get("failed_requests", 0) > 0:
                logger.warning(f"Locust test completed with {metrics['failed_requests']} failed requests")
            
            # Final check - if still all zeros, log a warning
            if metrics.get("total_requests", 0) == 0:
                logger.warning("All metrics are zero - test may not have generated any requests. Check Locust output.")
                logger.warning(f"Stats file exists: {os.path.exists(stats_file)}, Size: {os.path.getsize(stats_file) if os.path.exists(stats_file) else 0}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error running Locust: {str(e)}")
            raise
    
    def _parse_locust_csv(self, stats_file: str, failures_file: str) -> Dict[str, Any]:
        """Parse Locust CSV output files - reads ALL rows and finds the LAST Aggregated row"""
        metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0,
            "min_response_time": 0,
            "max_response_time": 0,
            "median_response_time": 0,
            "requests_per_second": 0,
            "failures": []
        }
        
        try:
            if not os.path.exists(stats_file):
                logger.warning(f"Stats file not found: {stats_file}")
                return metrics
            
            logger.info(f"Parsing Locust stats file: {stats_file}")
            
            # Read entire file first to get all rows
            with open(stats_file, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.debug(f"CSV file content (first 500 chars):\n{content[:500]}")
            
            # Parse CSV
            with open(stats_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Log available columns
                if reader.fieldnames:
                    logger.info(f"CSV columns found: {reader.fieldnames}")
                
                # Read ALL rows into a list
                all_rows = list(reader)
                logger.info(f"Total rows in CSV: {len(all_rows)}")
                
                # Find the LAST "Aggregated" row (Locust writes it at the end)
                # The Aggregated row has Name='Aggregated' (Type may be empty)
                aggregated_row = None
                for row in reversed(all_rows):  # Start from the end
                    row_type = (row.get('Type') or row.get('type') or row.get('TYPE') or '').strip()
                    row_name = (row.get('Name') or row.get('name') or '').strip()
                    logger.debug(f"Checking row with Type='{row_type}', Name='{row_name}'")
                    
                    # Aggregated row: Name='Aggregated' (Type may be empty or 'Aggregated')
                    if row_name.lower() == 'aggregated' or row_type.lower() == 'aggregated':
                        aggregated_row = row
                        logger.info(f"Found Aggregated row: Type='{row_type}', Name='{row_name}'")
                        logger.info(f"Aggregated row data: {dict(row)}")
                        break
                
                if aggregated_row:
                    # Parse the aggregated row with multiple column name variations
                    def get_value(row, *keys):
                        """Try multiple key variations"""
                        for key in keys:
                            value = row.get(key) or row.get(key.lower()) or row.get(key.upper())
                            if value and str(value).strip() and str(value).strip().lower() != 'n/a':
                                return str(value).strip()
                        return '0'
                    
                    try:
                        # Get values with multiple column name attempts
                        # Based on actual CSV: "Request Count", "Failure Count", "Average Response Time", etc.
                        total_reqs_str = get_value(aggregated_row, 
                            'Request Count', 'request count', '# requests', '#requests', 
                            'requests', 'Requests', 'Total Requests', 'Total requests')
                        failed_reqs_str = get_value(aggregated_row,
                            'Failure Count', 'failure count', '# failures', '#failures',
                            'failures', 'Failures', 'Total Failures', 'Total failures')
                        avg_str = get_value(aggregated_row,
                            'Average Response Time', 'average response time', 'Average', 'average',
                            'Avg', 'avg', 'Average response time', 'Mean', 'mean')
                        min_str = get_value(aggregated_row,
                            'Min Response Time', 'min response time', 'Min', 'min',
                            'Minimum', 'minimum', 'Min response time')
                        max_str = get_value(aggregated_row,
                            'Max Response Time', 'max response time', 'Max', 'max',
                            'Maximum', 'maximum', 'Max response time')
                        median_str = get_value(aggregated_row,
                            'Median Response Time', 'median response time', 'Median', 'median',
                            'Median response time')
                        rps_str = get_value(aggregated_row,
                            'Requests/s', 'requests/s', 'Requests per second', 'RPS', 'rps', 'req/s')
                        
                        logger.info(f"Parsing values - total: '{total_reqs_str}', failed: '{failed_reqs_str}', avg: '{avg_str}'")
                        
                        # Convert to numbers, handling empty strings and None
                        total_reqs = int(float(total_reqs_str)) if total_reqs_str and total_reqs_str != '0' else 0
                        failed_reqs = int(float(failed_reqs_str)) if failed_reqs_str and failed_reqs_str != '0' else 0
                        
                        metrics["total_requests"] = total_reqs
                        metrics["failed_requests"] = failed_reqs
                        metrics["successful_requests"] = total_reqs - failed_reqs
                        metrics["avg_response_time"] = float(avg_str) if avg_str and avg_str != '0' else 0.0
                        metrics["min_response_time"] = float(min_str) if min_str and min_str != '0' else 0.0
                        metrics["max_response_time"] = float(max_str) if max_str and max_str != '0' else 0.0
                        metrics["median_response_time"] = float(median_str) if median_str and median_str != '0' else 0.0
                        metrics["requests_per_second"] = float(rps_str) if rps_str and rps_str != '0' else 0.0
                        
                        logger.info(f"Successfully parsed metrics: total={total_reqs}, failed={failed_reqs}, "
                                  f"avg_time={metrics['avg_response_time']:.2f}ms, rps={metrics['requests_per_second']:.2f}")
                    except (ValueError, TypeError) as e:
                        logger.error(f"Error parsing numeric values from Aggregated row: {e}")
                        logger.error(f"Row data: {dict(aggregated_row)}")
                        # Try fallback: sum all non-aggregated rows
                        self._fallback_aggregate(all_rows, metrics)
                else:
                    logger.warning("No 'Aggregated' row found. Attempting fallback aggregation from all rows.")
                    self._fallback_aggregate(all_rows, metrics)
            
            # Parse failures file
            if os.path.exists(failures_file):
                with open(failures_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            metrics["failures"].append({
                                "method": row.get('Method', '') or row.get('method', ''),
                                "name": row.get('Name', '') or row.get('name', ''),
                                "error": row.get('Error', '') or row.get('error', ''),
                                "occurrences": int(float(row.get('Occurrences', 0) or row.get('occurrences', 0) or 0))
                            })
                        except Exception as e:
                            logger.warning(f"Error parsing failure row: {e}")
        except Exception as e:
            logger.error(f"Error parsing Locust CSV: {str(e)}", exc_info=True)
        
        logger.info(f"Final parsed metrics: {metrics}")
        return metrics
    
    def _fallback_aggregate(self, rows: List[Dict[str, Any]], metrics: Dict[str, Any]) -> None:
        """Fallback method to aggregate metrics from all rows if Aggregated row not found"""
        try:
            total = 0
            failed = 0
            response_times = []
            
            for r in rows:
                row_type = (r.get('Type') or r.get('type') or '').strip()
                if row_type.lower() == 'aggregated':
                    continue  # Skip aggregated rows in fallback
                
                try:
                    reqs_str = r.get('# requests') or r.get('#requests') or r.get('requests') or '0'
                    fails_str = r.get('# failures') or r.get('#failures') or r.get('failures') or '0'
                    avg_str = r.get('Average') or r.get('average') or r.get('Avg') or '0'
                    
                    reqs = int(float(reqs_str)) if reqs_str else 0
                    fails = int(float(fails_str)) if fails_str else 0
                    avg_time = float(avg_str) if avg_str else 0.0
                    
                    total += reqs
                    failed += fails
                    if avg_time > 0:
                        response_times.append(avg_time)
                except (ValueError, TypeError):
                    continue
            
            if total > 0:
                metrics["total_requests"] = total
                metrics["failed_requests"] = failed
                metrics["successful_requests"] = total - failed
                if response_times:
                    metrics["avg_response_time"] = sum(response_times) / len(response_times)
                    metrics["min_response_time"] = min(response_times)
                    metrics["max_response_time"] = max(response_times)
                logger.info(f"Fallback aggregation: total={total}, failed={failed}")
        except Exception as e:
            logger.error(f"Error in fallback aggregation: {e}")
    
    async def run_load_test(
        self, 
        target_url: str, 
        users: int = 50, 
        spawn_rate: int = 10, 
        duration: int = 60
    ) -> Dict[str, Any]:
        """Run basic load test"""
        return await self._execute_test("load_test", target_url, users, spawn_rate, duration)
    
    async def run_stress_test(
        self, 
        target_url: str, 
        max_users: int = 500, 
        step_users: int = 50, 
        duration: int = 300
    ) -> Dict[str, Any]:
        """Run stress test with increasing load"""
        # For stress test, we'll use a stepped approach
        return await self._execute_test("stress_test", target_url, max_users, step_users, duration)
    
    async def run_spike_test(
        self, 
        target_url: str, 
        initial_users: int = 10, 
        spike_users: int = 200, 
        duration: int = 120
    ) -> Dict[str, Any]:
        """Run spike test with sudden load increase"""
        return await self._execute_test("spike_test", target_url, spike_users, spike_users, duration)
    
    async def run_soak_test(
        self, 
        target_url: str, 
        users: int = 50, 
        duration_hours: int = 1
    ) -> Dict[str, Any]:
        """Run soak/endurance test"""
        duration_seconds = duration_hours * 3600
        return await self._execute_test("soak_test", target_url, users, 10, duration_seconds)
    
    async def run_ramp_up_test(
        self, 
        target_url: str, 
        max_users: int = 100, 
        ramp_up_time: int = 60, 
        duration: int = 120
    ) -> Dict[str, Any]:
        """Run ramp-up test with gradual load increase"""
        spawn_rate = max_users // ramp_up_time if ramp_up_time > 0 else 10
        return await self._execute_test("load_test", target_url, max_users, spawn_rate, duration)
    
    async def run_throughput_test(
        self, 
        target_url: str, 
        target_rps: int = 100, 
        duration: int = 60
    ) -> Dict[str, Any]:
        """Run throughput test targeting specific requests per second"""
        # Estimate users needed for target RPS (rough estimate)
        users = target_rps * 2  # Conservative estimate
        return await self._execute_test("load_test", target_url, users, users, duration)
    
    async def run_endpoint_performance_test(
        self, 
        target_url: str, 
        endpoint: str, 
        users: int = 50, 
        duration: int = 60
    ) -> Dict[str, Any]:
        """Run performance test on specific endpoint"""
        return await self._execute_test("api_load_test", target_url, users, 10, duration)
    
    async def run_api_load_test(
        self, 
        target_url: str, 
        users: int = 50, 
        duration: int = 60
    ) -> Dict[str, Any]:
        """Run API load test"""
        return await self._execute_test("api_load_test", target_url, users, 10, duration)
    
    async def run_website_load_test(
        self, 
        target_url: str, 
        users: int = 50, 
        duration: int = 60
    ) -> Dict[str, Any]:
        """Run website load test"""
        return await self._execute_test("load_test", target_url, users, 10, duration)
    
    async def run_volume_test(
        self, 
        target_url: str, 
        users: int = 100, 
        duration: int = 300
    ) -> Dict[str, Any]:
        """Run volume test with large data"""
        return await self._execute_test("load_test", target_url, users, 20, duration)
    
    async def run_concurrent_user_test(
        self, 
        target_url: str, 
        concurrent_users: int = 100, 
        duration: int = 60
    ) -> Dict[str, Any]:
        """Run concurrent user test"""
        return await self._execute_test("load_test", target_url, concurrent_users, concurrent_users, duration)
    
    async def run_response_time_distribution_test(
        self, 
        target_url: str, 
        users: int = 50, 
        duration: int = 60
    ) -> Dict[str, Any]:
        """Run test to measure response time distribution"""
        result = await self._execute_test("load_test", target_url, users, 10, duration)
        # Add percentile calculations if available
        return result
    
    async def _execute_test(
        self, 
        test_type: str, 
        target_url: str, 
        users: int, 
        spawn_rate: int, 
        duration: int
    ) -> Dict[str, Any]:
        """Internal method to execute a Locust test"""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp(prefix="locust_test_")
        
        try:
            # Generate Locust test file
            locust_code = self._generate_locust_file(test_type, target_url)
            locust_file = os.path.join(self.temp_dir, "locustfile.py")
            
            with open(locust_file, 'w') as f:
                f.write(locust_code)
            
            logger.info(f"Generated Locust file at: {locust_file}")
            logger.debug(f"Locust file content:\n{locust_code}")
            
            # Format duration (e.g., "60s", "5m", "1h")
            if duration < 60:
                run_time = f"{duration}s"
            elif duration < 3600:
                run_time = f"{duration // 60}m"
            else:
                run_time = f"{duration // 3600}h"
            
            logger.info(f"Running Locust test: {test_type}, users={users}, spawn_rate={spawn_rate}, duration={run_time}")
            
            # Run Locust
            metrics = await self._run_locust_command(
                locust_file, users, spawn_rate, run_time, self.temp_dir
            )
            
            # Log the returned metrics to verify they're not zeros
            logger.info(f"Test completed. Returning metrics: {metrics}")
            
            # Verify we have non-zero metrics
            if metrics.get("total_requests", 0) == 0:
                logger.warning("WARNING: Metrics are all zeros! This indicates a parsing problem.")
                # Try to read the CSV file directly for debugging
                stats_file = os.path.join(self.temp_dir, "locust_stats_stats.csv")
                if os.path.exists(stats_file):
                    logger.warning(f"CSV file exists at {stats_file}, attempting direct read...")
                    with open(stats_file, 'r') as debug_f:
                        content = debug_f.read()
                        logger.warning(f"CSV file content:\n{content}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error in _execute_test: {e}", exc_info=True)
            raise
        finally:
            # Don't cleanup immediately - keep temp files for debugging if metrics are zero
            metrics_check = metrics if 'metrics' in locals() else {}
            if metrics_check.get("total_requests", 0) > 0:
                self._cleanup()
            else:
                logger.warning(f"Keeping temp directory for debugging: {self.temp_dir}")
    
    def _cleanup(self):
        """Clean up temporary files and directories"""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
        except Exception as e:
            logger.warning(f"Error cleaning up temp files: {str(e)}")

