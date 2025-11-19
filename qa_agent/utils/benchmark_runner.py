"""
Pytest-Benchmark Integration Module for Code Performance Testing
Uses latest pytest-benchmark API patterns from documentation
"""
import asyncio
import subprocess
import tempfile
import os
import json
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BenchmarkTestRunner:
    """Runner for executing pytest-benchmark tests programmatically"""
    
    def __init__(self):
        self.temp_dir = None
        self.benchmark_files = []
    
    def _generate_benchmark_test_file(
        self, 
        test_name: str, 
        function_to_benchmark: str,
        iterations: int = 100
    ) -> str:
        """Generate a pytest-benchmark test file dynamically"""
        test_code = f"""
import pytest
import time
import asyncio
from typing import Any

# Import the function to benchmark
{function_to_benchmark}

def test_{test_name}(benchmark):
    \"\"\"Benchmark test for {test_name}\"\"\"
    # Use pedantic mode for precise control
    result = benchmark.pedantic(
        {test_name}_function,
        iterations={iterations},
        rounds=10
    )
    return result
"""
        return test_code
    
    async def _run_pytest_benchmark(
        self, 
        test_file: str, 
        output_file: str
    ) -> Dict[str, Any]:
        """Run pytest-benchmark and parse JSON output"""
        try:
            cmd = [
                "pytest",
                test_file,
                "--benchmark-only",
                "--benchmark-json", output_file,
                "-v"
            ]
            
            logger.info(f"Running pytest-benchmark: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.path.dirname(test_file)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"Pytest-benchmark execution failed: {error_msg}")
                # Don't raise - might still have partial results
            
            # Parse JSON results
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    benchmark_data = json.load(f)
                return self._parse_benchmark_json(benchmark_data)
            else:
                raise Exception("Benchmark JSON output file not found")
                
        except Exception as e:
            logger.error(f"Error running pytest-benchmark: {str(e)}")
            raise
    
    def _parse_benchmark_json(self, benchmark_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse pytest-benchmark JSON output"""
        metrics = {
            "avg_time_ms": 0,
            "min_time_ms": 0,
            "max_time_ms": 0,
            "std_dev": 0,
            "iterations": 0,
            "rounds": 0,
            "total_time_ms": 0
        }
        
        try:
            if "benchmarks" in benchmark_data and len(benchmark_data["benchmarks"]) > 0:
                bench = benchmark_data["benchmarks"][0]
                
                # Convert from seconds to milliseconds
                metrics["avg_time_ms"] = bench.get("mean", 0) * 1000
                metrics["min_time_ms"] = bench.get("min", 0) * 1000
                metrics["max_time_ms"] = bench.get("max", 0) * 1000
                metrics["std_dev"] = bench.get("stddev", 0) * 1000
                metrics["iterations"] = bench.get("iterations", 0)
                metrics["rounds"] = bench.get("rounds", 0)
                metrics["total_time_ms"] = bench.get("stats", {}).get("total", 0) * 1000
                
        except Exception as e:
            logger.error(f"Error parsing benchmark JSON: {str(e)}")
        
        return metrics
    
    async def benchmark_function(
        self,
        function_to_benchmark: Callable,
        function_name: str,
        iterations: int = 100,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """Benchmark a function directly"""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="benchmark_test_")
        
        try:
            # Create a test file that imports and benchmarks the function
            test_file = os.path.join(self.temp_dir, f"test_{function_name}.py")
            output_file = os.path.join(self.temp_dir, "benchmark_results.json")
            
            # For direct function benchmarking, we'll use a simpler approach
            # Create a wrapper test
            test_code = f"""
import pytest
import sys
import os

# Add path to import function
sys.path.insert(0, r"{os.path.dirname(os.path.abspath(__file__))}")

def test_benchmark_{function_name}(benchmark):
    # Import and call the function
    from {function_to_benchmark.__module__} import {function_to_benchmark.__name__}
    result = benchmark.pedantic(
        {function_to_benchmark.__name__},
        args={args},
        kwargs={kwargs},
        iterations={iterations},
        rounds=10
    )
    return result
"""
            
            with open(test_file, 'w') as f:
                f.write(test_code)
            
            # Run pytest-benchmark
            metrics = await self._run_pytest_benchmark(test_file, output_file)
            
            return metrics
            
        finally:
            self._cleanup()
    
    async def benchmark_command_execution(
        self,
        command_func: Callable,
        iterations: int = 100
    ) -> Dict[str, Any]:
        """Benchmark AI command processing speed"""
        return await self.benchmark_function(
            command_func, "command_execution", iterations
        )
    
    async def benchmark_browser_automation(
        self,
        automation_func: Callable,
        iterations: int = 50
    ) -> Dict[str, Any]:
        """Benchmark browser automation operations"""
        return await self.benchmark_function(
            automation_func, "browser_automation", iterations
        )
    
    async def benchmark_page_navigation(
        self,
        navigation_func: Callable,
        iterations: int = 50
    ) -> Dict[str, Any]:
        """Benchmark page navigation speed"""
        return await self.benchmark_function(
            navigation_func, "page_navigation", iterations
        )
    
    async def benchmark_screenshot_capture(
        self,
        screenshot_func: Callable,
        iterations: int = 20
    ) -> Dict[str, Any]:
        """Benchmark screenshot capture speed"""
        return await self.benchmark_function(
            screenshot_func, "screenshot_capture", iterations
        )
    
    async def benchmark_cross_browser_test(
        self,
        cross_browser_func: Callable,
        iterations: int = 10
    ) -> Dict[str, Any]:
        """Benchmark cross-browser test execution"""
        return await self.benchmark_function(
            cross_browser_func, "cross_browser_test", iterations
        )
    
    async def benchmark_mobile_test(
        self,
        mobile_test_func: Callable,
        iterations: int = 10
    ) -> Dict[str, Any]:
        """Benchmark mobile test speed"""
        return await self.benchmark_function(
            mobile_test_func, "mobile_test", iterations
        )
    
    async def benchmark_auto_check(
        self,
        auto_check_func: Callable,
        iterations: int = 10
    ) -> Dict[str, Any]:
        """Benchmark auto check execution"""
        return await self.benchmark_function(
            auto_check_func, "auto_check", iterations
        )
    
    async def benchmark_auto_audit(
        self,
        auto_audit_func: Callable,
        iterations: int = 10
    ) -> Dict[str, Any]:
        """Benchmark auto audit execution"""
        return await self.benchmark_function(
            auto_audit_func, "auto_audit", iterations
        )
    
    async def benchmark_ai_processing(
        self,
        ai_func: Callable,
        iterations: int = 20
    ) -> Dict[str, Any]:
        """Benchmark AI API response times"""
        return await self.benchmark_function(
            ai_func, "ai_processing", iterations
        )
    
    async def benchmark_test_result_storage(
        self,
        storage_func: Callable,
        iterations: int = 100
    ) -> Dict[str, Any]:
        """Benchmark test result storage speed"""
        return await self.benchmark_function(
            storage_func, "test_result_storage", iterations
        )
    
    async def benchmark_network_request(
        self,
        request_func: Callable,
        iterations: int = 50
    ) -> Dict[str, Any]:
        """Benchmark HTTP request performance"""
        return await self.benchmark_function(
            request_func, "network_request", iterations
        )
    
    async def benchmark_database_query(
        self,
        query_func: Callable,
        iterations: int = 100
    ) -> Dict[str, Any]:
        """Benchmark database query performance"""
        return await self.benchmark_function(
            query_func, "database_query", iterations
        )
    
    def _cleanup(self):
        """Clean up temporary files and directories"""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
        except Exception as e:
            logger.warning(f"Error cleaning up temp files: {str(e)}")


