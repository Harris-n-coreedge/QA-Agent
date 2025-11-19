"""
Combined Test Runner Module
Combines Locust load testing with pytest-benchmark code benchmarking
"""
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from qa_agent.utils.locust_runner import LocustTestRunner
from qa_agent.utils.benchmark_runner import BenchmarkTestRunner

logger = logging.getLogger(__name__)


class CombinedTestRunner:
    """Runner for combined load testing and benchmarking"""
    
    def __init__(self):
        self.locust_runner = LocustTestRunner()
        self.benchmark_runner = BenchmarkTestRunner()
    
    async def run_load_with_benchmark(
        self,
        target_url: str,
        users: int = 50,
        duration: int = 60,
        benchmark_func: Optional[Any] = None,
        benchmark_iterations: int = 100
    ) -> Dict[str, Any]:
        """Run load test while simultaneously benchmarking code"""
        results = {
            "load_test": {},
            "benchmark": {},
            "combined_analysis": {}
        }
        
        try:
            # Run load test and benchmark in parallel
            load_task = asyncio.create_task(
                self.locust_runner.run_load_test(target_url, users, 10, duration)
            )
            
            benchmark_task = None
            if benchmark_func:
                benchmark_task = asyncio.create_task(
                    self.benchmark_runner.benchmark_function(
                        benchmark_func, "combined_benchmark", benchmark_iterations
                    )
                )
            
            # Wait for both to complete
            results["load_test"] = await load_task
            
            if benchmark_task:
                results["benchmark"] = await benchmark_task
            
            # Analyze combined results
            results["combined_analysis"] = self._analyze_combined_results(
                results["load_test"],
                results.get("benchmark", {})
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error in combined test: {str(e)}")
            raise
    
    async def run_performance_regression(
        self,
        target_url: str,
        baseline_results: Optional[Dict[str, Any]] = None,
        users: int = 50,
        duration: int = 60
    ) -> Dict[str, Any]:
        """Compare current performance with historical baseline"""
        # Run current test
        current_results = await self.locust_runner.run_load_test(
            target_url, users, 10, duration
        )
        
        regression_analysis = {
            "current": current_results,
            "baseline": baseline_results,
            "regression_detected": False,
            "changes": {}
        }
        
        if baseline_results:
            # Compare metrics
            changes = {}
            
            # Compare response times
            if "avg_response_time" in current_results and "avg_response_time" in baseline_results:
                current_avg = current_results["avg_response_time"]
                baseline_avg = baseline_results["avg_response_time"]
                change_pct = ((current_avg - baseline_avg) / baseline_avg) * 100
                changes["avg_response_time_change_pct"] = change_pct
                
                if change_pct > 20:  # 20% degradation threshold
                    regression_analysis["regression_detected"] = True
            
            # Compare throughput
            if "requests_per_second" in current_results and "requests_per_second" in baseline_results:
                current_rps = current_results["requests_per_second"]
                baseline_rps = baseline_results["requests_per_second"]
                change_pct = ((current_rps - baseline_rps) / baseline_rps) * 100
                changes["throughput_change_pct"] = change_pct
            
            # Compare error rate
            if "failed_requests" in current_results and "failed_requests" in baseline_results:
                current_errors = current_results["failed_requests"]
                baseline_errors = baseline_results["failed_requests"]
                changes["error_rate_change"] = current_errors - baseline_errors
            
            regression_analysis["changes"] = changes
        
        return regression_analysis
    
    async def run_optimization_validation(
        self,
        target_url: str,
        before_func: Optional[Any] = None,
        after_func: Optional[Any] = None,
        users: int = 50,
        duration: int = 60
    ) -> Dict[str, Any]:
        """Validate performance improvements from optimizations"""
        results = {
            "before": {},
            "after": {},
            "improvement": {}
        }
        
        try:
            # Run load test before optimization
            results["before"] = await self.locust_runner.run_load_test(
                target_url, users, 10, duration
            )
            
            # If benchmark functions provided, benchmark them
            if before_func and after_func:
                before_bench = await self.benchmark_runner.benchmark_function(
                    before_func, "before_optimization", 100
                )
                after_bench = await self.benchmark_runner.benchmark_function(
                    after_func, "after_optimization", 100
                )
                
                results["before"]["benchmark"] = before_bench
                results["after"]["benchmark"] = after_bench
            
            # Run load test after optimization (simulated - in real scenario, 
            # optimization would be applied between tests)
            results["after"] = await self.locust_runner.run_load_test(
                target_url, users, 10, duration
            )
            
            # Calculate improvements
            if "avg_response_time" in results["before"] and "avg_response_time" in results["after"]:
                before_avg = results["before"]["avg_response_time"]
                after_avg = results["after"]["avg_response_time"]
                improvement_pct = ((before_avg - after_avg) / before_avg) * 100
                results["improvement"]["response_time_improvement_pct"] = improvement_pct
            
            if "requests_per_second" in results["before"] and "requests_per_second" in results["after"]:
                before_rps = results["before"]["requests_per_second"]
                after_rps = results["after"]["requests_per_second"]
                improvement_pct = ((after_rps - before_rps) / before_rps) * 100
                results["improvement"]["throughput_improvement_pct"] = improvement_pct
            
            return results
            
        except Exception as e:
            logger.error(f"Error in optimization validation: {str(e)}")
            raise
    
    def _analyze_combined_results(
        self,
        load_results: Dict[str, Any],
        benchmark_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze combined load test and benchmark results"""
        analysis = {
            "correlation": {},
            "bottlenecks": [],
            "recommendations": []
        }
        
        # Simple correlation analysis
        if load_results and benchmark_results:
            # If load test shows high response times and benchmark shows slow code,
            # there might be a correlation
            if load_results.get("avg_response_time", 0) > 1000:  # > 1 second
                if benchmark_results.get("avg_time_ms", 0) > 500:  # > 500ms
                    analysis["correlation"]["code_performance_impact"] = "high"
                    analysis["bottlenecks"].append("Code execution time may be impacting load test results")
                    analysis["recommendations"].append("Consider optimizing code performance")
        
        return analysis


