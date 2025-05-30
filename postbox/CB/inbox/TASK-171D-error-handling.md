# TASK-171D: Production Error Handling

**Agent**: CB (Testing & Integration Specialist)  
**Priority**: MEDIUM  
**Sprint**: Phase 6.17 - Production MVP Sprint 1  
**Working Directory**: `/Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2`

## Your Specialization Reminder
You are CB, the testing and quality assurance specialist. You own ALL decisions related to testing strategies, error handling patterns, quality standards, and system reliability. Your focus is ensuring production-grade stability.

## Context
The MVP-Lite has basic error handling. We need comprehensive production-grade error handling across the entire stack - frontend error boundaries, API error standardization, logging, monitoring, and user-friendly error messages.

## Branch Setup (MANDATORY)
```bash
cd /Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2
git checkout main
git pull origin main
git checkout -b dev/TASK-171D-error-handling
```

## Acceptance Criteria
1. ✅ Global error boundary for React app
2. ✅ Standardized API error responses
3. ✅ User-friendly error messages (no stack traces)
4. ✅ Comprehensive error logging system
5. ✅ Error recovery mechanisms
6. ✅ Error monitoring integration ready
7. ✅ Network error handling with retry logic
8. ✅ Form validation error display

## Implementation Requirements

### 1. Frontend Error Handling

**Global Error Boundary Component**
```typescript
// /components/ErrorBoundary.tsx
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string;
}
```
- Catch all unhandled React errors
- Display user-friendly error page
- Log errors with context
- Provide "Try Again" and "Go Home" actions
- Include error ID for support reference

**API Error Handler Hook**
```typescript
// /hooks/useApiError.ts
interface ApiError {
  code: string;
  message: string;
  details?: any;
  timestamp: string;
  requestId: string;
}
```
- Standardize all API error handling
- Map error codes to user messages
- Handle network failures with retry
- Show appropriate UI feedback

**Network Retry Logic**
- Exponential backoff: 1s, 2s, 4s
- Max 3 retries for GET requests
- No retry for POST/PUT/DELETE
- User notification after final failure

### 2. Backend Error Standardization

**Error Response Format**
```python
# All API errors should follow this structure
{
    "error": {
        "code": "AUTH_INVALID_CREDENTIALS",
        "message": "Invalid email or password",
        "details": {},  # Optional additional context
        "timestamp": "2024-06-01T10:30:00Z",
        "request_id": "req_abc123"  # For tracing
    }
}
```

**Error Codes to Implement**
```python
# /shared/errors/error_codes.py
ERROR_CODES = {
    # Auth Errors (AUTH_*)
    "AUTH_INVALID_CREDENTIALS": (401, "Invalid email or password"),
    "AUTH_TOKEN_EXPIRED": (401, "Session expired, please login again"),
    "AUTH_TOKEN_INVALID": (401, "Invalid authentication token"),
    "AUTH_UNAUTHORIZED": (403, "You don't have permission to access this resource"),
    
    # Validation Errors (VAL_*)
    "VAL_INVALID_INPUT": (400, "Invalid input data"),
    "VAL_MISSING_FIELD": (400, "Required field missing"),
    "VAL_INVALID_FORMAT": (400, "Invalid data format"),
    
    # Resource Errors (RES_*)
    "RES_NOT_FOUND": (404, "Resource not found"),
    "RES_ALREADY_EXISTS": (409, "Resource already exists"),
    "RES_LIMIT_EXCEEDED": (429, "Rate limit exceeded"),
    
    # Server Errors (SRV_*)
    "SRV_INTERNAL_ERROR": (500, "An unexpected error occurred"),
    "SRV_DATABASE_ERROR": (500, "Database operation failed"),
    "SRV_EXTERNAL_SERVICE": (502, "External service unavailable"),
}
```

**Error Handler Middleware**
```python
# /apps/api/middleware/error_handler.py
- Global exception handler
- Log all errors with context
- Convert exceptions to standard format
- Sanitize error messages for production
- Add request ID for tracing
```

### 3. Error Logging System

**Frontend Logging**
```typescript
// /lib/logger.ts
interface LogEntry {
  level: 'error' | 'warn' | 'info';
  message: string;
  context: any;
  timestamp: string;
  userId?: string;
  sessionId: string;
  errorId?: string;
}
```
- Structured logging format
- Batch send to backend
- Store in localStorage if offline
- Clear sensitive data

**Backend Logging**
```python
# /shared/logging/logger.py
- Structured JSON logging
- Include request context
- Log to file and console
- Rotate logs daily
- Different log levels for dev/prod
```

### 4. User-Friendly Error Messages

**Message Mapping**
```typescript
// /lib/errors/user-messages.ts
const ERROR_MESSAGES = {
  'network_error': 'Unable to connect. Please check your internet connection.',
  'auth_failed': 'Login failed. Please check your email and password.',
  'server_error': 'Something went wrong. Please try again later.',
  'validation_error': 'Please check your input and try again.',
  'not_found': "We couldn't find what you're looking for.",
  'rate_limit': 'Too many requests. Please wait a moment.',
}
```

### 5. Error Recovery Mechanisms

**Auto-Recovery Features**
- Retry failed API calls with backoff
- Reconnect WebSocket automatically
- Save form data before error
- Resume interrupted uploads
- Graceful degradation for features

**Manual Recovery Options**
- "Try Again" buttons where appropriate
- "Report Issue" with pre-filled context
- "Go Back" to last known good state
- Clear error state actions

### 6. Form Validation Errors

**Field-Level Validation Display**
```typescript
// Enhance existing forms with:
- Inline error messages below fields
- Red border on invalid fields
- Error summary at form top
- Scroll to first error
- Clear errors on field change
```

### 7. Error Monitoring Preparation

**Error Tracking Setup**
```typescript
// /lib/monitoring/error-tracker.ts
interface ErrorReport {
  error: Error;
  context: {
    component?: string;
    action?: string;
    userId?: string;
    url: string;
    userAgent: string;
  };
  severity: 'low' | 'medium' | 'high' | 'critical';
}
```
- Prepare for Sentry/Rollbar integration
- Capture error context
- Group similar errors
- Set severity levels

## Testing Requirements

### Test Scenarios to Cover
1. **API Error Responses**
   - All error codes return correct format
   - Error messages are user-friendly
   - Stack traces never exposed

2. **Frontend Error Handling**
   - Error boundary catches component errors
   - Network failures trigger retry
   - Form validation shows inline errors

3. **Recovery Mechanisms**
   - Retry logic works correctly
   - Form data persists through errors
   - WebSocket reconnects automatically

4. **Logging System**
   - Errors logged with full context
   - Sensitive data not logged
   - Log rotation works

## Files to Create/Modify
- `/components/ErrorBoundary.tsx` - Global error boundary
- `/hooks/useApiError.ts` - API error handling hook
- `/lib/errors/user-messages.ts` - Error message mapping
- `/lib/logger.ts` - Frontend logging utility
- `/apps/api/middleware/error_handler.py` - Backend error middleware
- `/shared/errors/error_codes.py` - Standardized error codes
- `/shared/logging/logger.py` - Backend logging setup
- `/tests/test_error_handling.py` - Error handling tests
- `Update all API endpoints` - Use standard error format
- `Update all forms` - Add validation error display

## Definition of Done
- [ ] Error boundary catches all React errors
- [ ] All API errors use standard format
- [ ] User never sees technical error details
- [ ] Comprehensive logging implemented
- [ ] Network retry logic working
- [ ] Form validation errors display properly
- [ ] All test scenarios pass
- [ ] No console errors in production build
- [ ] Branch pushed to origin

## Your Autonomy
You have MAXIMUM autonomy to:
- Design the error handling architecture
- Choose logging format and structure
- Implement additional safety mechanisms
- Add any testing utilities needed
- Create helper functions for common patterns
- Enhance UX around error states

## When Complete
1. Run full test suite: `pytest tests/ -v`
2. Test error scenarios manually
3. Verify no sensitive data in logs
4. Commit with clear messages
5. Push branch: `git push origin dev/TASK-171D-error-handling`
6. Update task status to "ready_for_review"
7. Report completion with error handling guide

CB Reports: Begin implementation of comprehensive production error handling system for AIOS v2.