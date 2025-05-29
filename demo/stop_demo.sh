#!/bin/bash

# Bluelabel Autopilot Demo Stop Script
# =====================================
# This script stops all demo services cleanly

echo "🛑 Stopping Bluelabel Autopilot Demo Environment..."
echo "=================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to kill process by PID
kill_process() {
    local pid=$1
    local name=$2
    
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        print_status "Stopping $name (PID: $pid)..."
        kill "$pid" 2>/dev/null
        
        # Wait for process to die
        local attempts=0
        while kill -0 "$pid" 2>/dev/null && [ $attempts -lt 10 ]; do
            sleep 1
            attempts=$((attempts + 1))
        done
        
        # Force kill if still running
        if kill -0 "$pid" 2>/dev/null; then
            print_warning "Force killing $name..."
            kill -9 "$pid" 2>/dev/null
        fi
        
        print_status "$name stopped ✓"
    else
        print_warning "$name was not running"
    fi
}

# Read PIDs from files
if [ -f "demo/api.pid" ]; then
    API_PID=$(cat demo/api.pid)
    kill_process "$API_PID" "Backend API"
    rm -f demo/api.pid
fi

if [ -f "demo/web.pid" ]; then
    WEB_PID=$(cat demo/web.pid)
    kill_process "$WEB_PID" "Frontend Web Server"
    rm -f demo/web.pid
fi

# Kill any remaining processes on demo ports
print_status "Checking for any remaining processes on demo ports..."

# Check port 8000 (API)
API_PIDS=$(lsof -ti:8000 2>/dev/null || true)
if [ -n "$API_PIDS" ]; then
    print_status "Found processes on port 8000, stopping them..."
    echo "$API_PIDS" | xargs kill 2>/dev/null || true
fi

# Check port 3000 (Web)
WEB_PIDS=$(lsof -ti:3000 2>/dev/null || true)
if [ -n "$WEB_PIDS" ]; then
    print_status "Found processes on port 3000, stopping them..."
    echo "$WEB_PIDS" | xargs kill 2>/dev/null || true
fi

# Clean up log files
print_status "Cleaning up log files..."
rm -f demo/api.log demo/web.log
rm -f apps/api/api.log apps/web/web.log

# Clean up any demo data if needed
if [ "$1" = "--clean" ]; then
    print_status "Cleaning demo data..."
    rm -rf workflows/demo/
fi

echo ""
print_status "Demo environment stopped successfully! ✓"
echo ""
echo "To restart the demo:"
echo "  ./demo/start_demo.sh"
echo "" 