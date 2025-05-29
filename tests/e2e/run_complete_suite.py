#!/usr/bin/env python3
"""
Complete E2E Testing Suite Runner.

Orchestrates the execution of all E2E testing components and generates
a comprehensive test report.
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import argparse

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class E2ETestSuiteRunner:
    """Orchestrates the complete E2E testing suite."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._load_default_config()
        self.results_dir = PROJECT_ROOT / "tests" / "e2e_results"
        self.results_dir.mkdir(exist_ok=True)
        self.test_results = {}
        self.start_time = None
        self.end_time = None
    
    def run_complete_suite(self, quick_mode: bool = False) -> Dict[str, Any]:
        """Run the complete E2E testing suite."""
        print("🚀 Starting Complete E2E Testing Suite")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Define test execution order and configuration
        if quick_mode:
            test_schedule = self._get_quick_test_schedule()
        else:
            test_schedule = self._get_full_test_schedule()
        
        # Execute tests in order
        for test_category in test_schedule:
            self._execute_test_category(test_category)
        
        self.end_time = time.time()
        
        # Generate comprehensive report
        summary_report = self._generate_summary_report()
        
        print("\n" + "=" * 60)
        print("🏁 E2E Testing Suite Completed")
        print(f"Total Duration: {self.end_time - self.start_time:.1f} seconds")
        print(f"Overall Success Rate: {summary_report['overall_success_rate']:.1%}")
        print(f"Report saved to: {summary_report['report_file']}")
        
        return summary_report
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration for test execution."""
        return {
            "timeouts": {
                "short": 300,    # 5 minutes
                "medium": 900,   # 15 minutes
                "long": 1800,    # 30 minutes
                "extended": 3600 # 1 hour
            },
            "retry_attempts": 2,
            "parallel_execution": True,
            "save_artifacts": True,
            "cleanup_on_success": False
        }
    
    def _get_quick_test_schedule(self) -> List[Dict[str, Any]]:
        """Get quick test schedule for faster execution."""
        return [
            {
                "name": "multi_agent_scenarios",
                "module": "tests.e2e.multi_agent_scenarios",
                "markers": ["e2e"],
                "timeout": self.config["timeouts"]["medium"],
                "priority": "high",
                "tests": [
                    "test_large_scale_task_distribution",
                    "test_concurrent_agent_operations"
                ]
            },
            {
                "name": "failure_scenarios",
                "module": "tests.e2e.failure_scenarios",
                "markers": ["failure"],
                "timeout": self.config["timeouts"]["short"],
                "priority": "high",
                "tests": [
                    "test_agent_crash_recovery",
                    "test_data_corruption_scenarios"
                ]
            },
            {
                "name": "performance_benchmarks",
                "module": "tests.e2e.performance_benchmarks",
                "markers": ["benchmark"],
                "timeout": self.config["timeouts"]["medium"],
                "priority": "medium",
                "tests": [
                    "test_large_scale_throughput"
                ]
            }
        ]
    
    def _get_full_test_schedule(self) -> List[Dict[str, Any]]:
        """Get complete test schedule for comprehensive testing."""
        return [
            {
                "name": "multi_agent_scenarios",
                "module": "tests.e2e.multi_agent_scenarios",
                "markers": ["e2e"],
                "timeout": self.config["timeouts"]["long"],
                "priority": "high",
                "description": "Core multi-agent orchestration scenarios"
            },
            {
                "name": "stress_testing",
                "module": "tests.e2e.stress_testing_suite",
                "markers": ["stress"],
                "timeout": self.config["timeouts"]["long"],
                "priority": "high",
                "description": "Stress testing under extreme conditions"
            },
            {
                "name": "failure_scenarios",
                "module": "tests.e2e.failure_scenarios",
                "markers": ["failure"],
                "timeout": self.config["timeouts"]["medium"],
                "priority": "high",
                "description": "System resilience and failure recovery"
            },
            {
                "name": "performance_benchmarks",
                "module": "tests.e2e.performance_benchmarks",
                "markers": ["benchmark"],
                "timeout": self.config["timeouts"]["long"],
                "priority": "medium",
                "description": "Performance analysis and benchmarking"
            },
            {
                "name": "chaos_testing",
                "module": "tests.e2e.chaos_testing_framework",
                "markers": ["chaos"],
                "timeout": self.config["timeouts"]["long"],
                "priority": "medium",
                "description": "Chaos engineering and resilience testing"
            },
            {
                "name": "ui_regression",
                "module": "tests.e2e.ui_regression_tests",
                "markers": ["ui"],
                "timeout": self.config["timeouts"]["medium"],
                "priority": "low",
                "description": "UI regression and compatibility testing"
            },
            {
                "name": "load_testing",
                "module": "tests.e2e.load_testing_suite",
                "markers": ["load"],
                "timeout": self.config["timeouts"]["extended"],
                "priority": "low",
                "description": "Load testing for dashboard and APIs"
            }
        ]
    
    def _execute_test_category(self, test_category: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific test category."""
        category_name = test_category["name"]
        print(f"\n📋 Executing: {category_name}")
        print(f"   Description: {test_category.get('description', 'No description')}")
        print(f"   Priority: {test_category['priority'].upper()}")
        
        category_start = time.time()
        
        try:
            # Build pytest command
            cmd = self._build_pytest_command(test_category)
            
            # Execute tests
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=test_category["timeout"],
                cwd=PROJECT_ROOT
            )
            
            category_end = time.time()
            duration = category_end - category_start
            
            # Parse results
            category_result = {
                "name": category_name,
                "success": result.returncode == 0,
                "duration": duration,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd),
                "timestamp": datetime.now().isoformat()
            }
            
            # Extract test metrics from output
            category_result.update(self._parse_pytest_output(result.stdout))
            
            self.test_results[category_name] = category_result
            
            # Print results
            status = "✅ PASSED" if category_result["success"] else "❌ FAILED"
            print(f"   Result: {status} ({duration:.1f}s)")
            
            if category_result.get("tests_passed"):
                print(f"   Tests: {category_result['tests_passed']}/{category_result['tests_total']} passed")
            
            if not category_result["success"]:
                print(f"   Error: {result.stderr[:200]}...")
            
        except subprocess.TimeoutExpired:
            category_result = {
                "name": category_name,
                "success": False,
                "duration": test_category["timeout"],
                "error": "Test execution timed out",
                "timestamp": datetime.now().isoformat()
            }
            self.test_results[category_name] = category_result
            print(f"   Result: ⏰ TIMEOUT ({test_category['timeout']}s)")
            
        except Exception as e:
            category_result = {
                "name": category_name,
                "success": False,
                "duration": time.time() - category_start,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.test_results[category_name] = category_result
            print(f"   Result: 💥 ERROR - {e}")
        
        return category_result
    
    def _build_pytest_command(self, test_category: Dict[str, Any]) -> List[str]:
        """Build pytest command for test category."""
        cmd = ["python", "-m", "pytest"]
        
        # Add specific tests or use module
        if "tests" in test_category:
            # Run specific tests
            for test_name in test_category["tests"]:
                test_path = f"{test_category['module'].replace('.', '/')}::{test_name}"
                cmd.append(test_path)
        else:
            # Run entire module
            module_path = test_category["module"].replace(".", "/") + ".py"
            cmd.append(module_path)
        
        # Add markers
        if "markers" in test_category:
            for marker in test_category["markers"]:
                cmd.extend(["-m", marker])
        
        # Add verbosity and output options
        cmd.extend([
            "-v",                    # Verbose output
            "--tb=short",           # Short traceback format
            "--disable-warnings",   # Disable pytest warnings
            "-x"                    # Stop on first failure
        ])
        
        # Add JUnit XML output for CI integration
        junit_file = self.results_dir / f"junit_{test_category['name']}.xml"
        cmd.extend(["--junitxml", str(junit_file)])
        
        return cmd
    
    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """Parse pytest output to extract test metrics."""
        metrics = {}
        
        # Parse test results summary
        lines = output.split('\n')
        for line in lines:
            if '====' in line and ('passed' in line or 'failed' in line):
                # Parse summary line like "=== 5 passed, 2 failed in 10.5s ==="
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed" and i > 0:
                        metrics["tests_passed"] = int(parts[i-1])
                    elif part == "failed" and i > 0:
                        metrics["tests_failed"] = int(parts[i-1])
                    elif part == "error" and i > 0:
                        metrics["tests_error"] = int(parts[i-1])
                    elif part == "skipped" and i > 0:
                        metrics["tests_skipped"] = int(parts[i-1])
        
        # Calculate totals
        metrics["tests_total"] = sum([
            metrics.get("tests_passed", 0),
            metrics.get("tests_failed", 0),
            metrics.get("tests_error", 0),
            metrics.get("tests_skipped", 0)
        ])
        
        return metrics
    
    def _generate_summary_report(self) -> Dict[str, Any]:
        """Generate comprehensive summary report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Calculate overall statistics
        total_categories = len(self.test_results)
        successful_categories = sum(1 for r in self.test_results.values() if r.get("success", False))
        total_duration = self.end_time - self.start_time if self.start_time and self.end_time else 0
        
        # Calculate test statistics
        total_tests = sum(r.get("tests_total", 0) for r in self.test_results.values())
        passed_tests = sum(r.get("tests_passed", 0) for r in self.test_results.values())
        failed_tests = sum(r.get("tests_failed", 0) for r in self.test_results.values())
        error_tests = sum(r.get("tests_error", 0) for r in self.test_results.values())
        
        # Generate summary
        summary = {
            "timestamp": timestamp,
            "execution_time": {
                "start": datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
                "end": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
                "duration_seconds": total_duration
            },
            "categories": {
                "total": total_categories,
                "successful": successful_categories,
                "failed": total_categories - successful_categories,
                "success_rate": successful_categories / total_categories if total_categories > 0 else 0
            },
            "tests": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0
            },
            "overall_success_rate": (successful_categories / total_categories) if total_categories > 0 else 0,
            "category_results": self.test_results,
            "recommendations": self._generate_recommendations()
        }
        
        # Save detailed report
        report_file = self.results_dir / f"e2e_test_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        # Generate human-readable summary
        summary_file = self.results_dir / f"e2e_test_summary_{timestamp}.md"
        self._generate_markdown_summary(summary, summary_file)
        
        summary["report_file"] = str(report_file)
        summary["summary_file"] = str(summary_file)
        
        return summary
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Analyze failed categories
        failed_categories = [
            name for name, result in self.test_results.items()
            if not result.get("success", False)
        ]
        
        if failed_categories:
            recommendations.append(
                f"Investigate failures in: {', '.join(failed_categories)}"
            )
        
        # Analyze performance
        long_running_tests = [
            name for name, result in self.test_results.items()
            if result.get("duration", 0) > 600  # > 10 minutes
        ]
        
        if long_running_tests:
            recommendations.append(
                f"Consider optimizing slow test categories: {', '.join(long_running_tests)}"
            )
        
        # Analyze test coverage
        if len(self.test_results) < 5:
            recommendations.append(
                "Consider running the complete test suite for comprehensive coverage"
            )
        
        # Success recommendations
        if not failed_categories:
            recommendations.append("All test categories passed - system is stable")
            recommendations.append("Consider running extended endurance tests")
        
        return recommendations
    
    def _generate_markdown_summary(self, summary: Dict[str, Any], output_file: Path):
        """Generate human-readable markdown summary."""
        content = f"""# E2E Test Suite Report

## Summary

- **Execution Date**: {summary['timestamp']}
- **Total Duration**: {summary['execution_time']['duration_seconds']:.1f} seconds
- **Overall Success Rate**: {summary['overall_success_rate']:.1%}

## Category Results

| Category | Status | Duration | Tests | Success Rate |
|----------|--------|----------|-------|--------------|
"""
        
        for name, result in summary['category_results'].items():
            status = "✅ PASS" if result.get('success') else "❌ FAIL"
            duration = f"{result.get('duration', 0):.1f}s"
            tests = f"{result.get('tests_passed', 0)}/{result.get('tests_total', 0)}"
            success_rate = ""
            if result.get('tests_total', 0) > 0:
                rate = result.get('tests_passed', 0) / result.get('tests_total')
                success_rate = f"{rate:.1%}"
            
            content += f"| {name} | {status} | {duration} | {tests} | {success_rate} |\n"
        
        content += f"""
## Test Statistics

- **Total Categories**: {summary['categories']['total']}
- **Successful Categories**: {summary['categories']['successful']}
- **Failed Categories**: {summary['categories']['failed']}
- **Total Tests**: {summary['tests']['total']}
- **Passed Tests**: {summary['tests']['passed']}
- **Failed Tests**: {summary['tests']['failed']}

## Recommendations

"""
        
        for recommendation in summary['recommendations']:
            content += f"- {recommendation}\n"
        
        content += f"""
## Failed Categories

"""
        
        failed_results = {k: v for k, v in summary['category_results'].items() 
                         if not v.get('success', False)}
        
        if failed_results:
            for name, result in failed_results.items():
                content += f"### {name}\n"
                content += f"- **Error**: {result.get('error', 'Unknown error')}\n"
                if result.get('stderr'):
                    content += f"- **Details**: {result['stderr'][:500]}...\n"
                content += "\n"
        else:
            content += "No failed categories - all tests passed! 🎉\n"
        
        with open(output_file, 'w') as f:
            f.write(content)


def main():
    """Main entry point for the test suite runner."""
    parser = argparse.ArgumentParser(description="Run complete E2E testing suite")
    parser.add_argument(
        "--quick", 
        action="store_true", 
        help="Run quick test subset instead of full suite"
    )
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to custom configuration file"
    )
    
    args = parser.parse_args()
    
    # Load custom config if provided
    config = None
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
    
    # Create and run test suite
    runner = E2ETestSuiteRunner(config)
    
    try:
        results = runner.run_complete_suite(quick_mode=args.quick)
        
        # Exit with appropriate code
        if results["overall_success_rate"] == 1.0:
            print("\n🎉 All tests passed!")
            sys.exit(0)
        else:
            print(f"\n⚠️  Some tests failed (success rate: {results['overall_success_rate']:.1%})")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()