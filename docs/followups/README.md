# Follow-up Tracker

This directory contains the `FOLLOW_UP_TRACKER.yaml` file, which serves as a centralized repository for tracking future functionality ideas and deferred roadmap items.

## Format Specification

Each entry in the tracker follows this structure:

```yaml
- id: FU-XXX          # Unique identifier (FU-001, FU-002, etc.)
  title: "Title"      # Brief description of the feature/improvement
  source: "TASK-XXX"  # Source task or planning document
  tags: []            # Relevant categories
  priority: high      # Priority level (high/medium/low)
  status: queued      # Current status
  sprint_target: "Phase X.Y"  # Target phase for implementation
```

## Purpose

The tracker helps:
- Maintain visibility of deferred features
- Track cross-sprint dependencies
- Plan future phases
- Document feature requests and improvements

## Maintenance

- New entries should be added with unique IDs
- Update status as items are completed
- Review and update sprint targets regularly
- Keep tags consistent and meaningful 