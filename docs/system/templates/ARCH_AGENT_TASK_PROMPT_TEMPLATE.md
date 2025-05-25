# ARCH-AI Task Prompt Structure Reference

This document provides a standardized template for creating task prompts for ARCH-AI agents. Following this structure ensures consistency and clarity in task assignments.

## Basic Structure

```
TASK-XXXXX — [Clear, Concise Title]

🎯 Objective:
[1-2 sentences describing the task goal]

📁 Branch:
dev/TASK-XXXX-agent-name-description

📂 Files to Create/Update:
- /path/to/file1
- /path/to/file2

📄 Content Requirements:
- ✅ Requirement 1
- ✅ Requirement 2
- ✅ Requirement 3

📦 Output Requirements:
- ✅ Deliverable 1
- ✅ Deliverable 2
- ✅ Deliverable 3
```

## Guidelines

1. **Title Format**
   - Always start with `TASK-XXXXX`
   - Use em dash (—) after task number
   - Keep title concise and descriptive

2. **Objective Section**
   - Maximum 1-2 sentences
   - Focus on the end goal
   - Avoid implementation details

3. **Branch Naming**
   - Follow pattern: `dev/TASK-XXXX-agent-name-description`
   - Use lowercase with hyphens
   - Include task number and brief description

4. **File Paths**
   - List absolute paths from project root
   - Clearly indicate if file is new or existing
   - Group by create/update operations

5. **Requirements Format**
   - Use ✅ bullet points
   - One requirement per line
   - Start with action verb
   - Keep requirements specific and measurable

6. **Output Requirements**
   - List all expected deliverables
   - Use ✅ bullet points
   - Include acceptance criteria

## Example

```
TASK-12345 — Implement User Authentication Flow

🎯 Objective:
Create a secure authentication system using OAuth 2.0 for user login and registration.

📁 Branch:
dev/TASK-12345-auth-implementation

📂 Files to Create/Update:
- /src/auth/AuthService.ts
- /src/auth/types.ts
- /docs/auth/README.md

📄 Content Requirements:
- ✅ Implement OAuth 2.0 authentication flow
- ✅ Add user registration endpoint
- ✅ Create login validation middleware
- ✅ Add password hashing with bcrypt

📦 Output Requirements:
- ✅ Working authentication endpoints
- ✅ Updated API documentation
- ✅ Unit tests with 90% coverage
```

## Notes

- Avoid markdown wrapping or nested code fences
- Keep instructions direct and clear
- Use plain text for requirements
- Reference ARCH_CONTINUITY.md and PROMPT.md for additional context 