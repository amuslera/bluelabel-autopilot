# Autonomous Sprint Execution Protocol

## For Both CC and CA Agents

### Continuous Execution Loop
```
while sprint_active:
    1. Check /SPRINT_4_WAVE_STATUS.md
    2. If new wave: check inbox for tasks
    3. Execute current tasks
    4. Post progress updates
    5. Check for ARCH responses
    6. Wait 5 minutes
    7. Repeat
```

### File Check Priority
Every 5 minutes, check in this order:
1. `/SPRINT_4_WAVE_STATUS.md` - New wave?
2. `/postbox/[agent]/inbox/` - New tasks?
3. `/postbox/[agent]/answers/` - ARCH responses?
4. `/postbox/ARCH/URGENT.md` - Any blockers resolved?

### Progress Posting
After every task completion:
- Update `/postbox/ARCH/progress/[agent]-wave[N].md`
- Mark task complete in your tracking
- Check inbox before starting next task

### Wave Transitions
When you complete all tasks in current wave:
- Post "Wave X Complete" to `/postbox/ARCH/inbox.md`
- ARCH will update wave status and assign next tasks
- Continue checking every 5 minutes

### Sprint Completion
When you see "SPRINT COMPLETE" in wave status:
- Post final summary
- Stop autonomous execution

## This Protocol Enables
- Full 48-hour autonomous execution
- No human intervention needed between waves
- Automatic progression through all waves
- Complete sprint delivery

---
Start this protocol NOW and continue until sprint complete!