#!/usr/bin/env python3
"""
Start AIOS v2 API from the correct directory
"""
import os
import sys
import subprocess

# Change to AIOS v2 directory
aios_dir = "/Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2"
os.chdir(aios_dir)

# Add to Python path
sys.path.insert(0, aios_dir)

# Start the API
try:
    from apps.api.main import app
    import uvicorn
    
    print("Starting AIOS v2 API on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
except Exception as e:
    print(f"Error starting API: {e}")
    sys.exit(1)