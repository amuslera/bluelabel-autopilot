#!/usr/bin/env python3
"""
E2E test runner for comprehensive testing.
Orchestrates all E2E test suites and generates reports.
"""
import subprocess
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import argparse


class E2ETestRunner:
    """Orchestrates E2E test execution and reporting."""
    
    def __init__(self, base_url: str = "http://localhost:3000", 
                 headless: bool = True,
                 browsers: List[str] = None):
        self.base_url = base_url
        self.headless = headless
        self.browsers = browsers or ["chromium"]
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def run_test_suite(self, suite_name: str, test_path: str, 
                      extra_args: List[str] = None) -> Dict:
        """Run a specific test suite."""
        print(f"\n{'='*60}")
        print(f"Running {suite_name}...")
        print(f"{'='*60}")
        
        cmd = [
            "pytest",
            test_path,
            "-v",
            "--tb=short",
            f"--base-url={self.base_url}",
        ]
        
        if self.headless:
            cmd.append("--headed")
        
        if extra_args:
            cmd.extend(extra_args)
        
        # Add pytest-json-report for structured output
        report_file = f"reports/{suite_name.lower().replace(' ', '_')}_report.json"
        cmd.extend(["--json-report", f"--json-report-file={report_file}"])
        
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = time.time() - start
        
        # Parse results
        suite_results = {
            "name": suite_name,
            "duration": duration,
            "exit_code": result.exit_code,
            "passed": result.exit_code == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        
        # Try to load detailed results
        try:
            with open(report_file, 'r') as f:
                detailed_results = json.load(f)
                suite_results["tests"] = detailed_results.get("tests", {})
                suite_results["summary"] = detailed_results.get("summary", {})
        except:
            pass
        
        return suite_results
    
    def run_all_tests(self) -> None:
        """Run all E2E test suites."""
        self.start_time = datetime.now()
        
        # Create reports directory
        Path("reports").mkdir(exist_ok=True)
        
        # Define test suites
        test_suites = [
            {
                "name": "Authentication Tests",
                "path": "tests/e2e/auth/",
                "critical": True
            },
            {
                "name": "Marketplace Tests",
                "path": "tests/e2e/marketplace/",
                "critical": True
            },
            {
                "name": "Performance Tests",
                "path": "tests/e2e/performance/",
                "critical": False,
                "extra_args": ["--benchmark-only"]
            },
            {
                "name": "Security Tests",
                "path": "tests/e2e/security/",
                "critical": True
            },
            {
                "name": "Cross-Browser Tests",
                "path": "tests/e2e/compatibility/",
                "critical": False,
                "browsers": ["chromium", "firefox", "webkit"]
            }
        ]
        
        # Run each suite
        for suite in test_suites:
            # Run for each browser if specified
            browsers = suite.get("browsers", self.browsers)
            
            for browser in browsers:
                suite_name = suite["name"]
                if len(browsers) > 1:
                    suite_name += f" ({browser})"
                
                extra_args = suite.get("extra_args", [])
                if browser != "chromium":
                    extra_args.extend(["--browser", browser])
                
                results = self.run_test_suite(
                    suite_name,
                    suite["path"],
                    extra_args
                )
                
                self.results[suite_name] = results
                
                # Stop if critical test fails
                if suite.get("critical") and not results["passed"]:
                    print(f"\n❌ Critical test suite '{suite_name}' failed!")
                    if not self.continue_on_failure:
                        break
        
        self.end_time = datetime.now()
    
    def generate_report(self) -> None:
        """Generate comprehensive test report."""
        print("\n" + "="*60)
        print("E2E TEST EXECUTION SUMMARY")
        print("="*60)
        
        total_duration = (self.end_time - self.start_time).total_seconds()
        
        # Summary statistics
        total_suites = len(self.results)
        passed_suites = sum(1 for r in self.results.values() if r["passed"])
        failed_suites = total_suites - passed_suites
        
        print(f"\nExecution Time: {total_duration:.2f}s")
        print(f"Total Test Suites: {total_suites}")
        print(f"Passed: {passed_suites}")
        print(f"Failed: {failed_suites}")
        
        # Detailed results
        print("\nDETAILED RESULTS:")
        print("-" * 60)
        
        for suite_name, results in self.results.items():
            status = "✅ PASSED" if results["passed"] else "❌ FAILED"
            print(f"\n{suite_name}: {status}")
            print(f"  Duration: {results['duration']:.2f}s")
            
            if "summary" in results:
                summary = results["summary"]
                print(f"  Tests: {summary.get('total', 0)}")
                print(f"  Passed: {summary.get('passed', 0)}")
                print(f"  Failed: {summary.get('failed', 0)}")
                print(f"  Skipped: {summary.get('skipped', 0)}")
        
        # Generate HTML report
        self.generate_html_report()
        
        # Generate JSON report
        self.generate_json_report()
        
        print(f"\n📊 Reports generated in 'reports/' directory")
        print(f"   - HTML Report: reports/e2e_test_report.html")
        print(f"   - JSON Report: reports/e2e_test_report.json")
    
    def generate_html_report(self) -> None:
        """Generate HTML test report."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>E2E Test Report - {self.start_time.strftime('%Y-%m-%d %H:%M')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .suite {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .passed {{ background: #d4edda; }}
        .failed {{ background: #f8d7da; }}
        .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 20px 0; }}
        .metric {{ background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f0f0f0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>E2E Test Execution Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Base URL: {self.base_url}</p>
        <p>Duration: {(self.end_time - self.start_time).total_seconds():.2f}s</p>
    </div>
    
    <div class="metrics">
        <div class="metric">
            <h3>Total Suites</h3>
            <p style="font-size: 24px;">{len(self.results)}</p>
        </div>
        <div class="metric">
            <h3>Passed</h3>
            <p style="font-size: 24px; color: green;">{sum(1 for r in self.results.values() if r['passed'])}</p>
        </div>
        <div class="metric">
            <h3>Failed</h3>
            <p style="font-size: 24px; color: red;">{sum(1 for r in self.results.values() if not r['passed'])}</p>
        </div>
        <div class="metric">
            <h3>Success Rate</h3>
            <p style="font-size: 24px;">{(sum(1 for r in self.results.values() if r['passed']) / len(self.results) * 100):.1f}%</p>
        </div>
    </div>
    
    <h2>Test Suites</h2>
"""
        
        for suite_name, results in self.results.items():
            status_class = "passed" if results["passed"] else "failed"
            html_content += f"""
    <div class="suite {status_class}">
        <h3>{suite_name}</h3>
        <p>Duration: {results['duration']:.2f}s</p>
"""
            
            if "summary" in results:
                summary = results["summary"]
                html_content += f"""
        <table>
            <tr>
                <th>Total Tests</th>
                <th>Passed</th>
                <th>Failed</th>
                <th>Skipped</th>
            </tr>
            <tr>
                <td>{summary.get('total', 0)}</td>
                <td>{summary.get('passed', 0)}</td>
                <td>{summary.get('failed', 0)}</td>
                <td>{summary.get('skipped', 0)}</td>
            </tr>
        </table>
"""
            
            html_content += "    </div>\n"
        
        html_content += """
</body>
</html>
"""
        
        with open("reports/e2e_test_report.html", "w") as f:
            f.write(html_content)
    
    def generate_json_report(self) -> None:
        """Generate JSON test report."""
        report = {
            "metadata": {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "duration": (self.end_time - self.start_time).total_seconds(),
                "base_url": self.base_url,
                "browsers": self.browsers
            },
            "summary": {
                "total_suites": len(self.results),
                "passed_suites": sum(1 for r in self.results.values() if r["passed"]),
                "failed_suites": sum(1 for r in self.results.values() if not r["passed"]),
                "success_rate": sum(1 for r in self.results.values() if r["passed"]) / len(self.results) * 100
            },
            "suites": self.results
        }
        
        with open("reports/e2e_test_report.json", "w") as f:
            json.dump(report, f, indent=2)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run E2E tests")
    parser.add_argument("--url", default="http://localhost:3000", help="Base URL for testing")
    parser.add_argument("--headless", action="store_true", help="Run tests in headless mode")
    parser.add_argument("--browsers", nargs="+", default=["chromium"], 
                       choices=["chromium", "firefox", "webkit"],
                       help="Browsers to test")
    parser.add_argument("--continue-on-failure", action="store_true",
                       help="Continue running tests even if critical tests fail")
    
    args = parser.parse_args()
    
    # Check if server is running
    import requests
    try:
        response = requests.get(args.url, timeout=5)
        print(f"✅ Server is running at {args.url}")
    except:
        print(f"❌ Server is not accessible at {args.url}")
        print("Please start the server before running E2E tests")
        sys.exit(1)
    
    # Run tests
    runner = E2ETestRunner(
        base_url=args.url,
        headless=args.headless,
        browsers=args.browsers
    )
    runner.continue_on_failure = args.continue_on_failure
    
    try:
        runner.run_all_tests()
        runner.generate_report()
        
        # Exit with appropriate code
        failed_count = sum(1 for r in runner.results.values() if not r["passed"])
        sys.exit(1 if failed_count > 0 else 0)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()