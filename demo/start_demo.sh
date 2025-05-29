#!/bin/bash

# Bluelabel Autopilot Demo Startup Script
# =====================================
# This script sets up the complete demo environment for recording

set -e  # Exit on any error

echo "🚀 Starting Bluelabel Autopilot Demo Environment..."
echo "=================================================="

# Configuration
API_PORT=8000
WEB_PORT=3000
DEMO_RESOLUTION="1920x1080"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 1
    else
        return 0
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            print_status "$service_name is ready!"
            return 0
        fi
        
        printf "."
        sleep 1
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start within $max_attempts seconds"
    return 1
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is required but not installed"
    exit 1
fi

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is required but not installed"
    exit 1
fi

print_status "Prerequisites check passed ✓"

# Check if ports are available
print_status "Checking port availability..."

if ! check_port $API_PORT; then
    print_error "Port $API_PORT is already in use"
    print_warning "Run: lsof -ti:$API_PORT | xargs kill -9"
    exit 1
fi

if ! check_port $WEB_PORT; then
    print_error "Port $WEB_PORT is already in use"
    print_warning "Run: lsof -ti:$WEB_PORT | xargs kill -9"
    exit 1
fi

print_status "Ports are available ✓"

# Set up demo data
print_status "Setting up demo data..."

# Create demo workflow files if they don't exist
mkdir -p workflows/demo

if [ ! -f "workflows/demo/demo_simple.yaml" ]; then
    cat > "workflows/demo/demo_simple.yaml" << EOF
name: demo-simple-workflow
description: "Simple demo workflow for testing"
steps:
  - id: test_step
    name: "Test Processing Step"
    agent: ingestion_agent
    inputs:
      demo: true
    expected_duration: 3
EOF
fi

print_status "Demo data setup complete ✓"

# Start backend API server
print_status "Starting backend API server on port $API_PORT..."

cd apps/api

# Install Python dependencies if needed
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r ../../requirements.txt 2>/dev/null || true

# Start API server in background
python3 api.py > api.log 2>&1 &
API_PID=$!

cd ../..

# Wait for API to be ready
if ! wait_for_service "http://localhost:$API_PORT/api/workflows/dag-runs" "Backend API"; then
    print_error "Failed to start backend API"
    kill $API_PID 2>/dev/null || true
    exit 1
fi

print_status "Backend API started ✓ (PID: $API_PID)"

# Start frontend web server
print_status "Starting frontend web server on port $WEB_PORT..."

cd apps/web

# Install Node dependencies if needed
if [ ! -d "node_modules" ]; then
    print_status "Installing Node.js dependencies..."
    npm install --silent
fi

# Start web server in background
npm run dev > web.log 2>&1 &
WEB_PID=$!

cd ../..

# Wait for web server to be ready
if ! wait_for_service "http://localhost:$WEB_PORT" "Frontend Web Server"; then
    print_error "Failed to start frontend web server"
    kill $API_PID $WEB_PID 2>/dev/null || true
    exit 1
fi

print_status "Frontend web server started ✓ (PID: $WEB_PID)"

# Store PIDs for cleanup
echo "$API_PID" > demo/api.pid
echo "$WEB_PID" > demo/web.pid

# Open browser for demo
print_status "Opening demo in browser..."

# Detect OS and open browser accordingly
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "http://localhost:$WEB_PORT"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "http://localhost:$WEB_PORT" 2>/dev/null || true
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    start "http://localhost:$WEB_PORT"
fi

# Display demo ready message
echo ""
echo "🎥 DEMO ENVIRONMENT READY!"
echo "========================="
echo ""
echo "📊 Frontend URL: http://localhost:$WEB_PORT"
echo "🔧 Backend API: http://localhost:$API_PORT"
echo "📝 WebSocket: ws://localhost:$API_PORT/ws/dag-updates"
echo ""
echo "📋 Quick Actions:"
echo "  • View workflows: http://localhost:$WEB_PORT"
echo "  • Test API: curl http://localhost:$API_PORT/api/workflows/dag-runs"
echo "  • Run sample workflow: Click 'Run Sample Workflow' button"
echo ""
echo "🎬 Demo Recording Tips:"
echo "  • Use browser zoom: Cmd/Ctrl + '+' for better visibility"
echo "  • Enable browser DevTools to show WebSocket traffic"
echo "  • Resolution optimized for $DEMO_RESOLUTION"
echo ""
echo "🛑 To stop demo environment:"
echo "   ./demo/stop_demo.sh"
echo ""
print_status "Ready for demo recording! 🎬"

# Keep script running to maintain services
echo "Press Ctrl+C to stop all services..."
trap 'echo; print_status "Stopping demo environment..."; kill $API_PID $WEB_PID 2>/dev/null; rm -f demo/api.pid demo/web.pid; exit 0' INT

# Monitor services
while true; do
    # Check if services are still running
    if ! kill -0 $API_PID 2>/dev/null; then
        print_error "Backend API stopped unexpectedly"
        break
    fi
    
    if ! kill -0 $WEB_PID 2>/dev/null; then
        print_error "Frontend web server stopped unexpectedly"
        break
    fi
    
    sleep 5
done

# Cleanup
print_status "Cleaning up..."
kill $API_PID $WEB_PID 2>/dev/null || true
rm -f demo/api.pid demo/web.pid 