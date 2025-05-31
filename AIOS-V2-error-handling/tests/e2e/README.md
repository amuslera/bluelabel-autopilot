# E2E Testing Suite

Comprehensive end-to-end testing suite for the Bluelabel Agent OS platform.

## Overview

This E2E testing suite provides comprehensive coverage for:
- User journey validation
- Cross-browser compatibility
- Mobile responsiveness
- Performance benchmarking
- Security testing

## Test Structure

```
e2e/
├── auth/                    # Authentication flow tests
│   ├── test_registration.py # User registration tests
│   ├── test_login.py       # Login flow tests  
│   └── test_password_reset.py # Password reset tests
├── marketplace/            # Marketplace functionality tests
│   ├── test_browsing.py   # Agent browsing tests
│   ├── test_search.py     # Search functionality tests
│   └── test_installation.py # Agent installation tests
├── performance/           # Performance benchmark tests
│   ├── test_api_response.py # API performance (<200ms target)
│   └── test_page_load.py   # Page load performance (<3s target)
├── security/              # Security testing
│   └── test_security.py   # XSS, CSRF, SQL injection tests
├── compatibility/         # Cross-browser tests
│   └── test_cross_browser.py # Browser compatibility tests
├── run_e2e_tests.py      # Main test runner
├── playwright.config.py   # Playwright configuration
└── README.md             # This file
```

## Prerequisites

### Install Dependencies

```bash
# Install Python dependencies
pip install playwright pytest pytest-playwright pytest-json-report

# Install Playwright browsers
playwright install
```

### Start the Application

Ensure the application is running before executing tests:

```bash
# Start the frontend
cd apps/ui
npm install
npm run dev

# Start the backend (in another terminal)
cd ../../
python -m uvicorn apps.api.main:app --reload
```

## Running Tests

### Run All Tests

```bash
# Run with default settings
python tests/e2e/run_e2e_tests.py

# Run with specific options
python tests/e2e/run_e2e_tests.py --url http://localhost:3000 --browsers chromium firefox webkit

# Run in headed mode (see browser)
python tests/e2e/run_e2e_tests.py --headed
```

### Run Specific Test Suites

```bash
# Authentication tests only
pytest tests/e2e/auth/

# Performance tests only
pytest tests/e2e/performance/

# Security tests only
pytest tests/e2e/security/
```

### Run Individual Tests

```bash
# Run specific test file
pytest tests/e2e/auth/test_login.py

# Run specific test function
pytest tests/e2e/auth/test_login.py::TestLoginFlow::test_successful_login
```

## Test Configuration

### Environment Variables

```bash
# Base URL for testing
export BASE_URL=http://localhost:3000

# Run in CI mode
export CI=true

# Disable headless mode
export HEADLESS=false

# Auto-start server
export START_SERVER=true
```

### Playwright Configuration

Edit `playwright.config.py` to customize:
- Timeouts
- Retries
- Parallel workers
- Browser settings
- Screenshot/video capture

## Test Categories

### 1. Authentication Tests

- User registration flow
- Email validation
- Password strength requirements
- Login functionality
- Remember me feature
- Session management
- Password reset flow
- Token validation

### 2. Marketplace Tests

- Agent browsing
- Category filtering
- Search functionality
- Autocomplete
- Agent details view
- Installation workflow
- Configuration management
- Bulk operations

### 3. Performance Tests

- API response times (<200ms)
- Page load times (<3s)
- First Contentful Paint (FCP)
- Time to Interactive (TTI)
- Cumulative Layout Shift (CLS)
- Bundle size analysis
- Memory usage profiling
- Resource optimization

### 4. Security Tests

- Authentication requirements
- SQL injection prevention
- XSS protection
- CSRF protection
- Password security
- Session security
- Rate limiting
- Input sanitization
- Security headers

### 5. Cross-Browser Tests

- Chrome/Chromium
- Firefox
- Safari/WebKit
- Edge
- Mobile browsers
- Feature compatibility
- CSS rendering
- JavaScript functionality

## Performance Targets

| Metric | Target | Critical |
|--------|--------|----------|
| API Response Time | <200ms | Yes |
| Page Load Time | <3s | Yes |
| First Contentful Paint | <1.8s | No |
| Time to Interactive | <3.8s | No |
| Cumulative Layout Shift | <0.1 | No |
| Total JS Bundle Size | <2MB | No |

## Test Reports

After running tests, reports are generated in the `reports/` directory:

- `e2e_test_report.html` - Interactive HTML report
- `e2e_test_report.json` - Detailed JSON report
- Individual suite reports
- Performance metrics
- Screenshots on failure
- Video recordings (if enabled)

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Install dependencies
  run: |
    pip install -r requirements.txt
    pip install playwright pytest pytest-playwright
    playwright install

- name: Run E2E tests
  run: python tests/e2e/run_e2e_tests.py --browsers chromium
  env:
    CI: true
    BASE_URL: ${{ env.DEPLOY_URL }}

- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v2
  with:
    name: e2e-test-results
    path: reports/
```

## Writing New Tests

### Test Template

```python
import pytest
from playwright.sync_api import Page, expect

class TestNewFeature:
    """Test new feature functionality."""
    
    @pytest.fixture
    def setup(self, page: Page):
        """Setup for tests."""
        # Navigate to feature
        page.goto("/feature")
        yield page
        # Cleanup if needed
    
    def test_feature_works(self, setup: Page):
        """Test feature works correctly."""
        page = setup
        
        # Test implementation
        element = page.locator('[data-testid="element"]')
        expect(element).to_be_visible()
        
        # Interact with element
        element.click()
        
        # Assert results
        expect(page).to_have_url("/expected-url")
```

### Best Practices

1. **Use data-testid attributes** for reliable element selection
2. **Write independent tests** that don't rely on other tests
3. **Use fixtures** for common setup/teardown
4. **Assert specific conditions** rather than generic checks
5. **Handle async operations** with proper waits
6. **Test error conditions** not just happy paths
7. **Keep tests focused** on single functionality
8. **Use descriptive names** for tests and assertions

## Debugging Tests

### Debug Mode

```bash
# Run with Playwright inspector
PWDEBUG=1 pytest tests/e2e/auth/test_login.py

# Pause on failure
pytest tests/e2e/auth/test_login.py --pdb
```

### View Traces

```bash
# After test failure, view trace
playwright show-trace trace.zip
```

### Common Issues

1. **Timeout errors**: Increase timeout in config or use explicit waits
2. **Element not found**: Check selectors, ensure page loaded
3. **Flaky tests**: Add proper waits, check for race conditions
4. **Cross-browser failures**: Check for browser-specific implementations

## Maintenance

### Regular Tasks

- Update selectors when UI changes
- Review and update performance targets
- Add tests for new features
- Remove tests for deprecated features
- Update browser versions
- Review test execution times

### Test Health Metrics

- Test execution time trends
- Flakiness rate
- Coverage metrics
- Performance regression detection

## Contributing

When adding new E2E tests:

1. Follow the existing structure
2. Add appropriate markers (@pytest.mark.e2e)
3. Document test purpose
4. Include in appropriate test suite
5. Update this README if needed
6. Ensure tests pass locally before PR

## Support

For issues or questions:
- Check test logs in `reports/`
- Review screenshots/videos for failures
- Consult Playwright documentation
- Contact the QA team