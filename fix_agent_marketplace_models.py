#!/usr/bin/env python3
"""
Fix agent marketplace models Pydantic issue
"""
import re

# Path to the file
model_file = "/Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2/apps/api/models/agent_marketplace.py"

# Read the current content
with open(model_file, 'r') as f:
    content = f.read()

# Fix the enum classes - replace with proper Python enums
fixes = [
    (
        'class AgentStatus(str, BaseModel):\n    ACTIVE = "active"\n    INACTIVE = "inactive" \n    MAINTENANCE = "maintenance"\n    DEPRECATED = "deprecated"\n    BETA = "beta"',
        '''class AgentStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive" 
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"
    BETA = "beta"'''
    ),
    (
        'class AgentTier(str, BaseModel):\n    FREE = "free"\n    PREMIUM = "premium"\n    ENTERPRISE = "enterprise"\n    CUSTOM = "custom"',
        '''class AgentTier(str, enum.Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"'''
    )
]

# Add enum import if not present
if "import enum" not in content:
    content = content.replace("import uuid", "import uuid\nimport enum")

# Apply fixes
for old, new in fixes:
    content = content.replace(old, new)

# Write the updated content
with open(model_file, 'w') as f:
    f.write(content)

print("✅ Fixed agent marketplace models")