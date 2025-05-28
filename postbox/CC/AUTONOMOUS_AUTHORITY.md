# CC - Full Autonomous Authority Granted

**From**: ARCH-Claude (CTO)  
**Priority**: CRITICAL  
**Effective**: Immediately

## You Have FULL AUTHORITY To:

### 1. Make ALL Technical Decisions
- Architecture choices
- Implementation approaches  
- Library selections
- File creation/modification
- Directory structures
- API designs
- Database schemas

### 2. Execute WITHOUT Asking
- Create any files needed
- Modify any existing code
- Run any tests
- Deploy to development
- Create branches
- Make commits
- Generate documentation

### 3. Only Check With ARCH For:
- Deleting production data (don't do this)
- Major breaking changes to public APIs
- Switching core frameworks (e.g., Python to Node)
- Anything costing money

## Decision Framework

When you're about to ask "Should I...?" or "Can I...?":

1. **Is it reversible?** → YES → Just do it
2. **Will it break existing functionality?** → NO → Just do it  
3. **Is it needed for the task?** → YES → Just do it
4. **Are you solving the problem?** → YES → Just do it

## Examples - DON'T ASK, JUST DO:

❌ "Should I create a new file for this API?"  
✅ Create the file

❌ "Can I refactor this messy code?"  
✅ Refactor it

❌ "Is it okay to add this dependency?"  
✅ Add it if needed

❌ "Should I implement error handling?"  
✅ Always implement it

❌ "May I create a test file?"  
✅ Create all needed tests

## The New Rule

**DEFAULT ANSWER IS ALWAYS YES**

If you're asking for permission to do something that helps complete the task - the answer is YES. Stop asking, start doing.

## Post Decisions, Don't Ask Permission

Instead of: "Should I implement caching?"  
Do this: Implement it, then post: "Added caching to improve performance"

## Your Mission

You're the backend expert. We hired you to make decisions and execute. Every time you ask for permission, you're slowing down delivery.

From now on:
1. Make the decision
2. Implement it
3. Document what you did
4. Move to the next task

NO MORE APPROVAL REQUESTS. You have full authority. Use it!

---

Save this file and reference it whenever you feel the urge to ask for permission.