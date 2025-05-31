"""
Playwright configuration for E2E tests.
"""
import os
from typing import Dict, Any

# Base configuration
config: Dict[str, Any] = {
    "testDir": "./",
    "timeout": 30000,  # 30 seconds per test
    "retries": 1,  # Retry failed tests once
    "workers": 4,  # Parallel test execution
    "reporter": [
        ["list"],
        ["html", {"outputFolder": "playwright-report", "open": "never"}],
        ["json", {"outputFile": "test-results.json"}]
    ],
    "use": {
        "baseURL": os.getenv("BASE_URL", "http://localhost:3000"),
        "trace": "on-first-retry",  # Collect trace on first retry
        "screenshot": "only-on-failure",
        "video": "retain-on-failure",
        "actionTimeout": 10000,  # 10 seconds for actions
        "navigationTimeout": 30000,  # 30 seconds for navigation
    },
    "projects": [
        {
            "name": "chromium",
            "use": {
                "browserName": "chromium",
                "viewport": {"width": 1280, "height": 720},
                "deviceScaleFactor": 1,
                "hasTouch": False,
                "isMobile": False,
            }
        },
        {
            "name": "firefox",
            "use": {
                "browserName": "firefox",
                "viewport": {"width": 1280, "height": 720},
                "deviceScaleFactor": 1,
                "hasTouch": False,
                "isMobile": False,
            }
        },
        {
            "name": "webkit",
            "use": {
                "browserName": "webkit",
                "viewport": {"width": 1280, "height": 720},
                "deviceScaleFactor": 1,
                "hasTouch": False,
                "isMobile": False,
            }
        },
        {
            "name": "mobile-chrome",
            "use": {
                "browserName": "chromium",
                "viewport": {"width": 375, "height": 667},
                "deviceScaleFactor": 2,
                "hasTouch": True,
                "isMobile": True,
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
            }
        },
        {
            "name": "mobile-safari",
            "use": {
                "browserName": "webkit",
                "viewport": {"width": 375, "height": 667},
                "deviceScaleFactor": 2,
                "hasTouch": True,
                "isMobile": True,
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
            }
        }
    ],
    "webServer": {
        "command": "npm run dev" if os.getenv("CI") != "true" else None,
        "port": 3000,
        "timeout": 120000,  # 2 minutes to start
        "reuseExistingServer": not os.getenv("CI"),
    } if os.getenv("START_SERVER") == "true" else None
}

# Environment-specific overrides
if os.getenv("CI") == "true":
    config["workers"] = 2  # Less parallelism in CI
    config["retries"] = 2  # More retries in CI
    config["use"]["trace"] = "on"  # Always collect traces in CI

if os.getenv("HEADLESS") != "false":
    config["use"]["headless"] = True

# Export for pytest-playwright
pytest_plugins = ["pytest_playwright"]

# Pytest configuration
def pytest_configure(config):
    """Configure pytest for E2E tests."""
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "smoke: mark test as smoke test"
    )
    config.addinivalue_line(
        "markers", "critical: mark test as critical"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )