#!/usr/bin/env python3
"""
UI Regression Testing Suite for Multi-Agent Orchestration Dashboard.

Automated UI testing for dashboard components, monitoring systems,
and user interface regression detection.
"""

import os
import sys
import time
import json
import asyncio
import random
import threading
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import pytest
import requests
from unittest.mock import patch, MagicMock
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.e2e.multi_agent_scenarios import E2ETestEnvironment, TestMetrics, Agent, Task


@dataclass
class UITestResult:
    """Result from a UI test."""
    test_name: str
    component: str
    success: bool
    error_message: Optional[str]
    screenshot_path: Optional[str]
    execution_time: float
    assertions_passed: int
    assertions_failed: int
    performance_metrics: Dict[str, float]


class UIRegressionTestSuite:
    """Comprehensive UI regression testing for the orchestration dashboard."""
    
    def __init__(self):
        self.driver = None
        self.base_url = "http://localhost:3000"  # Next.js dev server
        self.screenshots_dir = PROJECT_ROOT / "tests" / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
    
    def setup_method(self):
        """Set up WebDriver for UI testing."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode for CI
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
        except Exception as e:
            pytest.skip(f"Chrome WebDriver not available: {e}")
    
    def teardown_method(self):
        """Clean up WebDriver."""
        if self.driver:
            self.driver.quit()
    
    @pytest.mark.ui
    def test_dashboard_loading_performance(self):
        """Test dashboard loading performance and initial render."""
        start_time = time.time()
        
        try:
            # Navigate to dashboard
            self.driver.get(self.base_url)
            
            # Wait for main dashboard container
            dashboard_container = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "dashboard-container"))
            )
            
            # Measure loading time
            load_time = time.time() - start_time
            
            # Check essential UI elements are present
            essential_elements = [
                (By.ID, "agent-status-panel"),
                (By.ID, "task-queue-display"),
                (By.CLASS_NAME, "navigation-header"),
                (By.CLASS_NAME, "metrics-overview")
            ]
            
            missing_elements = []
            for selector_type, selector_value in essential_elements:
                try:
                    self.driver.find_element(selector_type, selector_value)
                except NoSuchElementException:
                    missing_elements.append(f"{selector_type}:{selector_value}")
            
            # Take screenshot
            screenshot_path = self._take_screenshot("dashboard_loading")
            
            # Performance assertions
            assert load_time < 5.0, f"Dashboard loading too slow: {load_time:.2f}s"
            assert len(missing_elements) == 0, f"Missing UI elements: {missing_elements}"
            
            return UITestResult(
                test_name="dashboard_loading_performance",
                component="main_dashboard",
                success=True,
                error_message=None,
                screenshot_path=screenshot_path,
                execution_time=load_time,
                assertions_passed=2,
                assertions_failed=0,
                performance_metrics={"load_time": load_time}
            )
            
        except Exception as e:
            screenshot_path = self._take_screenshot("dashboard_loading_error")
            return UITestResult(
                test_name="dashboard_loading_performance",
                component="main_dashboard",
                success=False,
                error_message=str(e),
                screenshot_path=screenshot_path,
                execution_time=time.time() - start_time,
                assertions_passed=0,
                assertions_failed=1,
                performance_metrics={}
            )
    
    @pytest.mark.ui
    def test_agent_status_display(self):
        """Test agent status display and real-time updates."""
        start_time = time.time()
        
        try:
            self.driver.get(self.base_url)
            
            # Wait for agent status panel
            agent_panel = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "agent-status-panel"))
            )
            
            # Check for agent status cards
            agent_cards = self.driver.find_elements(By.CLASS_NAME, "agent-status-card")
            
            # Verify agent information is displayed
            agent_info_checks = []
            for card in agent_cards[:3]:  # Check first 3 agents
                # Check for agent ID
                agent_id = card.find_element(By.CLASS_NAME, "agent-id")
                agent_info_checks.append(bool(agent_id.text.strip()))
                
                # Check for status indicator
                status_indicator = card.find_element(By.CLASS_NAME, "status-indicator")
                agent_info_checks.append(bool(status_indicator))
                
                # Check for task count
                task_count = card.find_element(By.CLASS_NAME, "task-count")
                agent_info_checks.append(bool(task_count.text.strip()))
            
            # Test status color coding
            status_elements = self.driver.find_elements(By.CLASS_NAME, "status-indicator")
            status_colors = []
            for element in status_elements:
                color_class = element.get_attribute("class")
                if "status-active" in color_class:
                    status_colors.append("active")
                elif "status-idle" in color_class:
                    status_colors.append("idle")
                elif "status-error" in color_class:
                    status_colors.append("error")
            
            screenshot_path = self._take_screenshot("agent_status_display")
            
            # Assertions
            assert len(agent_cards) >= 3, f"Expected at least 3 agent cards, found {len(agent_cards)}"
            assert all(agent_info_checks), "Some agent information is missing"
            assert len(status_colors) > 0, "No status indicators found"
            
            return UITestResult(
                test_name="agent_status_display",
                component="agent_status_panel",
                success=True,
                error_message=None,
                screenshot_path=screenshot_path,
                execution_time=time.time() - start_time,
                assertions_passed=3,
                assertions_failed=0,
                performance_metrics={"agent_cards_count": len(agent_cards)}
            )
            
        except Exception as e:
            screenshot_path = self._take_screenshot("agent_status_error")
            return UITestResult(
                test_name="agent_status_display",
                component="agent_status_panel",
                success=False,
                error_message=str(e),
                screenshot_path=screenshot_path,
                execution_time=time.time() - start_time,
                assertions_passed=0,
                assertions_failed=1,
                performance_metrics={}
            )
    
    @pytest.mark.ui
    def test_task_queue_visualization(self):
        """Test task queue display and filtering functionality."""
        start_time = time.time()
        
        try:
            self.driver.get(self.base_url)
            
            # Navigate to task queue section
            task_queue_nav = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "task-queue-nav"))
            )
            task_queue_nav.click()
            
            # Wait for task queue to load
            task_queue = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "task-queue-display"))
            )
            
            # Check for task items
            task_items = self.driver.find_elements(By.CLASS_NAME, "task-item")
            
            # Test filtering functionality
            filter_dropdown = self.driver.find_element(By.ID, "task-filter-dropdown")
            filter_dropdown.click()
            
            # Select "High Priority" filter
            high_priority_filter = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//option[@value='HIGH']"))
            )
            high_priority_filter.click()
            
            # Wait for filtered results
            time.sleep(1)
            filtered_tasks = self.driver.find_elements(By.CLASS_NAME, "task-item")
            
            # Verify task information display
            task_details_checks = []
            for task in task_items[:3]:  # Check first 3 tasks
                try:
                    task_id = task.find_element(By.CLASS_NAME, "task-id")
                    task_title = task.find_element(By.CLASS_NAME, "task-title")
                    task_priority = task.find_element(By.CLASS_NAME, "task-priority")
                    task_status = task.find_element(By.CLASS_NAME, "task-status")
                    
                    task_details_checks.extend([
                        bool(task_id.text.strip()),
                        bool(task_title.text.strip()),
                        bool(task_priority.text.strip()),
                        bool(task_status.text.strip())
                    ])
                except NoSuchElementException:
                    task_details_checks.append(False)
            
            screenshot_path = self._take_screenshot("task_queue_visualization")
            
            # Assertions
            assert len(task_items) > 0, "No task items found in queue"
            assert len(filtered_tasks) <= len(task_items), "Filter not working correctly"
            assert all(task_details_checks), "Some task details are missing"
            
            return UITestResult(
                test_name="task_queue_visualization",
                component="task_queue_display",
                success=True,
                error_message=None,
                screenshot_path=screenshot_path,
                execution_time=time.time() - start_time,
                assertions_passed=3,
                assertions_failed=0,
                performance_metrics={
                    "total_tasks": len(task_items),
                    "filtered_tasks": len(filtered_tasks)
                }
            )
            
        except Exception as e:
            screenshot_path = self._take_screenshot("task_queue_error")
            return UITestResult(
                test_name="task_queue_visualization",
                component="task_queue_display",
                success=False,
                error_message=str(e),
                screenshot_path=screenshot_path,
                execution_time=time.time() - start_time,
                assertions_passed=0,
                assertions_failed=1,
                performance_metrics={}
            )
    
    @pytest.mark.ui
    def test_dag_graph_rendering(self):
        """Test DAG graph visualization and interaction."""
        start_time = time.time()
        
        try:
            # Navigate to DAG graph page
            self.driver.get(f"{self.base_url}/dag/test-run-123")
            
            # Wait for DAG graph to load
            dag_graph = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "dag-graph-container"))
            )
            
            # Check for SVG or Canvas element
            graph_elements = self.driver.find_elements(By.TAG_NAME, "svg") or \
                           self.driver.find_elements(By.TAG_NAME, "canvas")
            
            # Check for node elements
            dag_nodes = self.driver.find_elements(By.CLASS_NAME, "dag-node")
            
            # Check for edge elements (connections between nodes)
            dag_edges = self.driver.find_elements(By.CLASS_NAME, "dag-edge")
            
            # Test node interaction
            if dag_nodes:
                first_node = dag_nodes[0]
                first_node.click()
                
                # Check if node details panel appears
                try:
                    node_details = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.ID, "node-details-panel"))
                    )
                    node_interaction_success = True
                except TimeoutException:
                    node_interaction_success = False
            else:
                node_interaction_success = False
            
            # Test zoom and pan functionality
            graph_container = self.driver.find_element(By.ID, "dag-graph-container")
            
            # Simulate mouse wheel for zoom (if supported)
            zoom_controls = self.driver.find_elements(By.CLASS_NAME, "zoom-controls")
            zoom_functionality = len(zoom_controls) > 0
            
            screenshot_path = self._take_screenshot("dag_graph_rendering")
            
            # Assertions
            assert len(graph_elements) > 0, "No graph rendering element found"
            assert len(dag_nodes) > 0, "No DAG nodes found"
            assert node_interaction_success, "Node interaction not working"
            
            return UITestResult(
                test_name="dag_graph_rendering",
                component="dag_graph",
                success=True,
                error_message=None,
                screenshot_path=screenshot_path,
                execution_time=time.time() - start_time,
                assertions_passed=3,
                assertions_failed=0,
                performance_metrics={
                    "nodes_count": len(dag_nodes),
                    "edges_count": len(dag_edges),
                    "zoom_controls": zoom_functionality
                }
            )
            
        except Exception as e:
            screenshot_path = self._take_screenshot("dag_graph_error")
            return UITestResult(
                test_name="dag_graph_rendering",
                component="dag_graph",
                success=False,
                error_message=str(e),
                screenshot_path=screenshot_path,
                execution_time=time.time() - start_time,
                assertions_passed=0,
                assertions_failed=1,
                performance_metrics={}
            )
    
    @pytest.mark.ui
    def test_responsive_design(self):
        """Test responsive design across different screen sizes."""
        start_time = time.time()
        
        screen_sizes = [
            ("desktop", 1920, 1080),
            ("tablet", 768, 1024),
            ("mobile", 375, 667)
        ]
        
        responsive_results = {}
        
        try:
            for size_name, width, height in screen_sizes:
                # Set window size
                self.driver.set_window_size(width, height)
                
                # Navigate to dashboard
                self.driver.get(self.base_url)
                
                # Wait for page to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "dashboard-container"))
                )
                
                # Check if navigation is responsive
                nav_element = self.driver.find_element(By.CLASS_NAME, "navigation-header")
                nav_responsive = nav_element.is_displayed()
                
                # Check if content adapts to screen size
                content_area = self.driver.find_element(By.ID, "main-content")
                content_width = content_area.size["width"]
                
                # Check for mobile menu on small screens
                if width < 768:
                    mobile_menu_buttons = self.driver.find_elements(By.CLASS_NAME, "mobile-menu-toggle")
                    has_mobile_menu = len(mobile_menu_buttons) > 0
                else:
                    has_mobile_menu = True  # Not required for larger screens
                
                # Take screenshot for this screen size
                screenshot_path = self._take_screenshot(f"responsive_{size_name}")
                
                responsive_results[size_name] = {
                    "nav_responsive": nav_responsive,
                    "content_width": content_width,
                    "has_mobile_menu": has_mobile_menu,
                    "screenshot": screenshot_path
                }
            
            # Verify responsive behavior
            desktop_width = responsive_results["desktop"]["content_width"]
            tablet_width = responsive_results["tablet"]["content_width"]
            mobile_width = responsive_results["mobile"]["content_width"]
            
            width_adaptation = (desktop_width > tablet_width > mobile_width)
            
            all_nav_responsive = all(
                result["nav_responsive"] for result in responsive_results.values()
            )
            
            mobile_menu_present = responsive_results["mobile"]["has_mobile_menu"]
            
            # Assertions
            assert width_adaptation, "Content not adapting to screen sizes"
            assert all_nav_responsive, "Navigation not responsive on all screen sizes"
            assert mobile_menu_present, "Mobile menu not present on mobile screen"
            
            return UITestResult(
                test_name="responsive_design",
                component="responsive_layout",
                success=True,
                error_message=None,
                screenshot_path=responsive_results["desktop"]["screenshot"],
                execution_time=time.time() - start_time,
                assertions_passed=3,
                assertions_failed=0,
                performance_metrics={
                    "desktop_width": desktop_width,
                    "tablet_width": tablet_width,
                    "mobile_width": mobile_width
                }
            )
            
        except Exception as e:
            screenshot_path = self._take_screenshot("responsive_error")
            return UITestResult(
                test_name="responsive_design",
                component="responsive_layout",
                success=False,
                error_message=str(e),
                screenshot_path=screenshot_path,
                execution_time=time.time() - start_time,
                assertions_passed=0,
                assertions_failed=1,
                performance_metrics={}
            )
    
    @pytest.mark.ui
    def test_real_time_updates(self):
        """Test real-time data updates in the UI."""
        start_time = time.time()
        
        try:
            self.driver.get(self.base_url)
            
            # Wait for initial load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "dashboard-container"))
            )
            
            # Get initial state of dynamic elements
            initial_agent_count = len(self.driver.find_elements(By.CLASS_NAME, "agent-status-card"))
            initial_task_count = len(self.driver.find_elements(By.CLASS_NAME, "task-item"))
            
            # Look for real-time indicators
            real_time_indicators = self.driver.find_elements(By.CLASS_NAME, "live-indicator")
            websocket_status = self.driver.find_elements(By.ID, "websocket-status")
            
            # Wait for potential updates (simulate real-time behavior)
            time.sleep(5)
            
            # Check if timestamps are updating
            timestamp_elements = self.driver.find_elements(By.CLASS_NAME, "last-updated")
            live_timestamps = []
            
            for element in timestamp_elements:
                timestamp_text = element.text
                if "ago" in timestamp_text or "now" in timestamp_text:
                    live_timestamps.append(True)
                else:
                    live_timestamps.append(False)
            
            # Check for loading states
            loading_elements = self.driver.find_elements(By.CLASS_NAME, "loading-spinner")
            
            # Check for error states
            error_elements = self.driver.find_elements(By.CLASS_NAME, "error-message")
            
            screenshot_path = self._take_screenshot("real_time_updates")
            
            # Assertions
            assert len(real_time_indicators) > 0 or len(websocket_status) > 0, \
                "No real-time indicators found"
            assert len(live_timestamps) > 0, "No live timestamp elements found"
            assert len(error_elements) == 0, "Error messages present in UI"
            
            return UITestResult(
                test_name="real_time_updates",
                component="real_time_data",
                success=True,
                error_message=None,
                screenshot_path=screenshot_path,
                execution_time=time.time() - start_time,
                assertions_passed=3,
                assertions_failed=0,
                performance_metrics={
                    "real_time_indicators": len(real_time_indicators),
                    "live_timestamps": len(live_timestamps),
                    "loading_elements": len(loading_elements)
                }
            )
            
        except Exception as e:
            screenshot_path = self._take_screenshot("real_time_error")
            return UITestResult(
                test_name="real_time_updates",
                component="real_time_data",
                success=False,
                error_message=str(e),
                screenshot_path=screenshot_path,
                execution_time=time.time() - start_time,
                assertions_passed=0,
                assertions_failed=1,
                performance_metrics={}
            )
    
    @pytest.mark.ui
    def test_accessibility_compliance(self):
        """Test accessibility compliance and ARIA attributes."""
        start_time = time.time()
        
        try:
            self.driver.get(self.base_url)
            
            # Wait for page load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "dashboard-container"))
            )
            
            # Check for ARIA labels
            aria_labeled_elements = self.driver.find_elements(
                By.XPATH, "//*[@aria-label or @aria-labelledby]"
            )
            
            # Check for semantic HTML elements
            semantic_elements = []
            semantic_tags = ["header", "nav", "main", "section", "article", "aside", "footer"]
            
            for tag in semantic_tags:
                elements = self.driver.find_elements(By.TAG_NAME, tag)
                semantic_elements.extend(elements)
            
            # Check for keyboard navigation support
            focusable_elements = self.driver.find_elements(
                By.XPATH, "//*[@tabindex or self::button or self::a or self::input or self::select or self::textarea]"
            )
            
            # Check for alt text on images
            images = self.driver.find_elements(By.TAG_NAME, "img")
            images_with_alt = [img for img in images if img.get_attribute("alt")]
            
            # Check color contrast (basic check for text visibility)
            text_elements = self.driver.find_elements(By.XPATH, "//*[text()]")
            visible_text_elements = [elem for elem in text_elements if elem.is_displayed()]
            
            # Check for skip links
            skip_links = self.driver.find_elements(By.CLASS_NAME, "skip-link")
            
            screenshot_path = self._take_screenshot("accessibility_compliance")
            
            # Calculate accessibility score
            accessibility_checks = [
                len(aria_labeled_elements) > 0,
                len(semantic_elements) > 0,
                len(focusable_elements) > 0,
                len(images_with_alt) == len(images) if images else True,
                len(visible_text_elements) > 0
            ]
            
            accessibility_score = sum(accessibility_checks) / len(accessibility_checks)
            
            # Assertions
            assert accessibility_score > 0.6, f"Accessibility score too low: {accessibility_score:.2f}"
            assert len(semantic_elements) > 0, "No semantic HTML elements found"
            assert len(focusable_elements) > 0, "No focusable elements found"
            
            return UITestResult(
                test_name="accessibility_compliance",
                component="accessibility",
                success=True,
                error_message=None,
                screenshot_path=screenshot_path,
                execution_time=time.time() - start_time,
                assertions_passed=3,
                assertions_failed=0,
                performance_metrics={
                    "accessibility_score": accessibility_score,
                    "aria_elements": len(aria_labeled_elements),
                    "semantic_elements": len(semantic_elements),
                    "focusable_elements": len(focusable_elements)
                }
            )
            
        except Exception as e:
            screenshot_path = self._take_screenshot("accessibility_error")
            return UITestResult(
                test_name="accessibility_compliance",
                component="accessibility",
                success=False,
                error_message=str(e),
                screenshot_path=screenshot_path,
                execution_time=time.time() - start_time,
                assertions_passed=0,
                assertions_failed=1,
                performance_metrics={}
            )
    
    def _take_screenshot(self, test_name: str) -> str:
        """Take a screenshot and return the file path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_filename = f"{test_name}_{timestamp}.png"
        screenshot_path = self.screenshots_dir / screenshot_filename
        
        try:
            self.driver.save_screenshot(str(screenshot_path))
            return str(screenshot_path)
        except Exception:
            return None
    
    def run_complete_ui_regression_suite(self) -> Dict[str, UITestResult]:
        """Run the complete UI regression test suite."""
        test_methods = [
            self.test_dashboard_loading_performance,
            self.test_agent_status_display,
            self.test_task_queue_visualization,
            self.test_dag_graph_rendering,
            self.test_responsive_design,
            self.test_real_time_updates,
            self.test_accessibility_compliance
        ]
        
        results = {}
        
        for test_method in test_methods:
            try:
                self.setup_method()
                result = test_method()
                results[result.test_name] = result
                print(f"✓ {result.test_name}: {'PASS' if result.success else 'FAIL'}")
                
                if not result.success:
                    print(f"  Error: {result.error_message}")
                    
            except Exception as e:
                results[test_method.__name__] = UITestResult(
                    test_name=test_method.__name__,
                    component="unknown",
                    success=False,
                    error_message=str(e),
                    screenshot_path=None,
                    execution_time=0,
                    assertions_passed=0,
                    assertions_failed=1,
                    performance_metrics={}
                )
                print(f"✗ {test_method.__name__}: ERROR - {e}")
                
            finally:
                self.teardown_method()
        
        # Generate summary report
        self._generate_ui_test_report(results)
        
        return results
    
    def _generate_ui_test_report(self, results: Dict[str, UITestResult]):
        """Generate a comprehensive UI test report."""
        report_dir = PROJECT_ROOT / "tests" / "ui_reports"
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"ui_regression_report_{timestamp}.json"
        
        # Convert results to serializable format
        serializable_results = {}
        for test_name, result in results.items():
            serializable_results[test_name] = asdict(result)
        
        # Add summary statistics
        total_tests = len(results)
        passed_tests = sum(1 for r in results.values() if r.success)
        failed_tests = total_tests - passed_tests
        
        report_data = {
            "timestamp": timestamp,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0
            },
            "results": serializable_results
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\nUI Regression Test Report:")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {passed_tests/total_tests:.1%}")
        print(f"Report saved to: {report_file}")


if __name__ == "__main__":
    # Run UI regression tests
    suite = UIRegressionTestSuite()
    suite.run_complete_ui_regression_suite()