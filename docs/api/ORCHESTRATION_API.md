# API Reference

This document provides a comprehensive API reference for all tools and utilities in the BlueLabelAutopilot orchestration system.

## Table of Contents

- [Orchestration.Validate Outbox](#orchestration-validate_outbox)

## Orchestration.Validate Outbox

**File**: `orchestration/validate_outbox.py`

### class OutboxValidator

Validates outbox.json files against the standard schema

*Source: orchestration/validate_outbox.py:21*

#### Methods

##### __init__(self)

**Examples:**
```python
super().__init__(
super().__init__("Unhealthy Agent", "Always fails")
super().__init__("Test Agent", "A test agent")
```

*Source: orchestration/validate_outbox.py:29*

##### _validate_history_entry(self, entry: Dict[str, Any], path: str)

Validate a history entry

*Source: orchestration/validate_outbox.py:114*

##### _validate_task(self, task: Dict[str, Any], path: str)

Validate a task object

*Source: orchestration/validate_outbox.py:83*

##### _validate_timestamp(self, timestamp: str, path: str)

Validate ISO 8601 timestamp format

*Source: orchestration/validate_outbox.py:133*

##### validate_file(self, file_path: Path) -> Tuple[bool, List[str], List[str]]

Validate a single outbox.json file

*Source: orchestration/validate_outbox.py:33*

### Functions

#### find_all_outbox_files(base_path: Path) -> List[Path]

Find all outbox.json files in the postbox directory

*Source: orchestration/validate_outbox.py:141*

#### main()

**Examples:**
```python
asyncio.run(main())
pytest.main([__file__, "-v", "-s"])
"from_domain": "aiweekly.com",
```

*Source: orchestration/validate_outbox.py:156*

---
