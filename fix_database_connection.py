#!/usr/bin/env python3
"""
Fix database connection to use psycopg (v3) instead of psycopg2
"""
import os
import sys

# Path to the database.py file
db_file = "/Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2/apps/api/dependencies/database.py"

# Read the current content
with open(db_file, 'r') as f:
    content = f.read()

# Replace psycopg2 dialect with psycopg
new_content = content.replace(
    'engine = create_engine(settings.DATABASE_URL)',
    '''# Use psycopg (v3) instead of psycopg2
if settings.DATABASE_URL.startswith('postgresql://'):
    # Convert to psycopg dialect
    db_url = settings.DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://')
else:
    db_url = settings.DATABASE_URL
    
engine = create_engine(db_url)'''
)

# Write the updated content
with open(db_file, 'w') as f:
    f.write(new_content)

print("✅ Updated database.py to use psycopg (v3) dialect")