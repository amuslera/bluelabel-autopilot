# ARCH Agent Task Prompt Template (v2.0)

This document defines the **standard format** and **structure** of all task prompts created by ARCH-AI. It is designed for **clarity**, **automation-readiness**, and **high-quality agent execution**.

---

## 🧩 Prompt Structure Overview

```markdown
┌─────────────────────────────────────────────┐  
│ TASK ID: <ID>                               │  
│ Agent: <Agent Name>                         │  
│ Branch: <git branch name>                   │  
│ Title: <concise title with emoji>           │  
└─────────────────────────────────────────────┘

🎯 Objective  
📁 File Scope  
📄 Implementation Instructions  
✅ Output Requirements  
⚠️ Constraints & Compliance  
📣 Completion Report Format
```

## 📋 Required Sections

### 1. Task Header
- **TASK ID**: Must match pattern `TASK-XXXXX`
- **Agent**: One of `CA`, `CC`, `WA`
- **Branch**: Follow pattern `dev/TASK-XXXX-agent-name-description`
- **Title**: Concise description with relevant emoji

### 2. Objective
- 1-2 sentences describing the end goal
- Focus on what, not how
- Include success criteria if applicable

### 3. File Scope
- List all files to create/modify
- Use absolute paths from project root
- Group by operation type (create/update)
- Include expected file contents or changes

### 4. Implementation Instructions
- Step-by-step guidance
- Clear acceptance criteria
- Technical requirements
- Dependencies and prerequisites

### 5. Output Requirements
- Expected deliverables
- Console output format
- File update confirmations
- Testing requirements

### 6. Constraints & Compliance
- Technical limitations
- Security requirements
- Performance expectations
- Agent-specific requirements

### 7. Completion Report Format
- Standardized console message
- Required file confirmations
- Summary of changes
- Next steps or follow-ups

## 🔄 Agent-Specific Requirements

### WA Requirements
- Must follow WA_CHECKLIST.md
- UI/UX considerations
- Visual documentation requirements
- Testing and accessibility standards

### CA Requirements
- CLI and tooling focus
- Test coverage expectations
- Documentation standards
- Integration requirements

### CC Requirements
- Core functionality focus
- Performance considerations
- Security requirements
- Error handling standards

## 📝 Example Prompts

### Example 1: Feature Implementation
```markdown
TASK-162L — 🧠 Redesign ARCH Agent Task Prompt Template

🎯 Objective:
Evolve the current task prompt format into a v2 version, incorporating lessons from recent sprints and compliance requirements.

📁 File Scope:
- /docs/system/templates/ARCH_AGENT_TASK_PROMPT_TEMPLATE.md
- /TASK_CARDS.md
- /postbox/CA/outbox.json

📄 Implementation Instructions:
1. Start from v1.0 template
2. Update structure with new requirements
3. Add agent-specific sections
4. Include examples and glossary

✅ Output Requirements:
- Updated template file
- Task card registration
- Completion report
- Console confirmation

⚠️ Constraints & Compliance:
- Markdown only
- No HTML/scripting
- Follow existing conventions
- Include version history

📣 Completion Format:
CA Reports: I have completed TASK-162L.
✅ Created/Updated files
📘 Major changes summary
📦 Next steps
```

### Example 2: Bug Fix
```markdown
TASK-162M — 🐛 Fix DAGRunStatus Type Error

🎯 Objective:
Resolve TypeScript duplicate identifier error in DAGRunStatus component.

📁 File Scope:
- /apps/web/components/DAGRunStatus.tsx
- /apps/web/components/__tests__/DAGRunStatus.test.tsx

📄 Implementation Instructions:
1. Identify duplicate identifier
2. Rename component appropriately
3. Update all references
4. Add test coverage

✅ Output Requirements:
- Fixed component
- Updated tests
- Type checking passing
- Build successful

⚠️ Constraints & Compliance:
- No breaking changes
- Maintain existing API
- Follow React best practices
- 100% test coverage

📣 Completion Format:
CA Reports: I have completed TASK-162M.
✅ Fixed type error
✅ Updated tests
📘 Changes summary
📦 Verification steps
```

## 📚 Glossary

- **Task ID**: Unique identifier for the task (TASK-XXXXX)
- **Agent**: Assigned agent (CA, CC, WA)
- **Branch**: Git branch name following convention
- **Objective**: Clear, concise task goal
- **File Scope**: Files to create or modify
- **Implementation**: Step-by-step instructions
- **Output**: Expected deliverables
- **Constraints**: Limitations and requirements
- **Completion**: Standardized report format

## 🔄 Version History

### v2.0 (2024-03-22)
- Added agent-specific requirements
- Included WA_CHECKLIST.md compliance
- Added comprehensive examples
- Enhanced glossary
- Added version history

### v1.0 (2024-03-21)
- Initial template structure
- Basic section requirements
- Simple examples
- Core guidelines

## ⚠️ Important Notes

1. **Do's**:
   - Use clear, direct language
   - Include all required sections
   - Follow agent-specific requirements
   - Provide detailed examples
   - Update version history

2. **Don'ts**:
   - Use HTML or scripting
   - Skip required sections
   - Use ambiguous language
   - Omit agent-specific requirements
   - Forget completion format

3. **Compliance**:
   - Must follow ARCH_CONTINUITY.md
   - Must update CLAUDE_CONTEXT.md when relevant
   - Must follow WA_CHECKLIST.md for WA tasks
   - Must include dual reporting (console + file)
   - Must update TASK_CARDS.md and outbox.json 