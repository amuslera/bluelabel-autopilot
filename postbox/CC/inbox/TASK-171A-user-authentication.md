# TASK-171A: User Authentication System

**Agent**: CC (Backend Specialist)  
**Priority**: HIGH  
**Sprint**: Phase 6.17 - Production MVP Sprint 1  
**Working Directory**: `/Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2`

## Your Specialization Reminder
You are CC, the backend specialist. You own ALL decisions related to APIs, databases, authentication, and server-side architecture. Make technical decisions autonomously - do not ask for approval on implementation details.

## Context
We're transforming the MVP-Lite into a production-ready system. Currently, we have session-based auth using UUIDs. Now we need proper user authentication with JWT tokens, user registration, and secure password handling.

## Branch Setup (MANDATORY)
```bash
cd /Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2
git checkout main
git pull origin main
git checkout -b dev/TASK-171A-user-authentication
```

## Acceptance Criteria
1. ✅ User registration endpoint with email/password validation
2. ✅ JWT-based login/logout endpoints  
3. ✅ Refresh token mechanism for session management
4. ✅ Password reset functionality with token-based flow
5. ✅ User profile endpoints (GET/UPDATE)
6. ✅ Secure password hashing (bcrypt or similar)
7. ✅ Protected route middleware for API endpoints
8. ✅ Database schema for users table

## Technical Requirements

### Database Schema
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    email_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Refresh tokens table
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Password reset tokens
CREATE TABLE password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### API Endpoints to Implement

1. **POST /api/auth/register**
   - Body: `{ email, password, name }`
   - Validation: email format, password strength (min 8 chars)
   - Response: `{ user: { id, email, name }, access_token, refresh_token }`

2. **POST /api/auth/login**
   - Body: `{ email, password }`
   - Response: `{ user: { id, email, name }, access_token, refresh_token }`
   - Set refresh token as httpOnly cookie

3. **POST /api/auth/logout**
   - Requires: Valid JWT in Authorization header
   - Action: Invalidate refresh token
   - Response: `{ message: "Logged out successfully" }`

4. **POST /api/auth/refresh**
   - Body: `{ refresh_token }` or from httpOnly cookie
   - Response: `{ access_token, refresh_token }`

5. **POST /api/auth/forgot-password**
   - Body: `{ email }`
   - Action: Generate reset token, store in DB (would send email in production)
   - Response: `{ message: "Reset instructions sent", reset_token }` (include token for testing)

6. **POST /api/auth/reset-password**
   - Body: `{ token, new_password }`
   - Response: `{ message: "Password reset successfully" }`

7. **GET /api/users/profile**
   - Requires: Valid JWT
   - Response: `{ id, email, name, created_at, last_login }`

8. **PUT /api/users/profile**
   - Requires: Valid JWT
   - Body: `{ name }` (email changes not allowed in MVP)
   - Response: Updated user object

### JWT Configuration
- Access token expiry: 15 minutes
- Refresh token expiry: 7 days
- Include user id and email in JWT payload
- Use RS256 algorithm (generate keys) or HS256 with strong secret

### Middleware Implementation
```python
# Example structure (you decide the actual implementation)
@jwt_required
async def protected_endpoint(current_user: User):
    # current_user automatically injected by middleware
    pass
```

### Security Requirements
- Bcrypt for password hashing (or argon2)
- Rate limiting on auth endpoints (5 attempts per minute)
- Proper error messages (don't reveal if email exists)
- CORS configuration for frontend access
- Validate all inputs with Pydantic models

## Integration Points
- Update existing job-related endpoints to associate jobs with users
- Modify session management to work with JWT
- Ensure backward compatibility during transition

## Files to Create/Modify
- `apps/api/auth.py` - New auth endpoints
- `apps/api/middleware/auth.py` - JWT validation middleware  
- `shared/models/user.py` - User, RefreshToken, PasswordResetToken models
- `apps/api/main.py` - Register auth routes and middleware
- `alembic/versions/xxx_add_users_tables.py` - Database migration
- `tests/test_auth.py` - Comprehensive auth tests

## Definition of Done
- [ ] All endpoints implemented and working
- [ ] Database migrations created and applied
- [ ] JWT middleware protecting appropriate routes
- [ ] Password hashing implemented securely
- [ ] All inputs validated with Pydantic
- [ ] Rate limiting in place
- [ ] Comprehensive tests written
- [ ] No console.log or print statements
- [ ] Branch pushed to origin

## Testing Checklist
- [ ] User can register with valid email/password
- [ ] Duplicate email registration rejected
- [ ] User can login and receive JWT tokens
- [ ] Access token expires after 15 minutes
- [ ] Refresh token generates new access token
- [ ] Protected endpoints reject invalid/expired tokens
- [ ] Password reset flow works end-to-end
- [ ] Profile endpoints work correctly

## Your Autonomy
You have MAXIMUM autonomy for this task. Make all technical decisions:
- Choose the JWT library (python-jose, PyJWT, etc.)
- Decide on exact error response formats
- Implement any helper utilities needed
- Add any additional security measures you see fit
- Structure the code as you think best

## When Complete
1. Run all tests: `pytest tests/test_auth.py -v`
2. Ensure no linting errors
3. Commit all changes with clear messages
4. Push branch: `git push origin dev/TASK-171A-user-authentication`
5. Update task status to "ready_for_review" in your outbox
6. Report completion with list of files created/modified

CC Reports: Begin implementation of comprehensive user authentication system for AIOS v2 production MVP.