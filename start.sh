#!/bin/bash

# Bluelabel Autopilot Docker Startup Script
# Usage: ./start.sh [dev|prod] [command]

# Set defaults
ENV=${1:-dev}
SHIFT_COUNT=1

# Validate environment
if [[ "$ENV" != "dev" && "$ENV" != "prod" ]]; then
    echo "Error: Environment must be 'dev' or 'prod'"
    echo "Usage: ./start.sh [dev|prod] [command]"
    exit 1
fi

# Set environment-specific variables
if [ "$ENV" = "dev" ]; then
    echo "Starting Bluelabel Autopilot in DEVELOPMENT mode..."
    ENV_FILE=".env"
    DOCKER_TAG="bluelabel-autopilot:dev"
    EXTRA_ARGS="-it"
else
    echo "Starting Bluelabel Autopilot in PRODUCTION mode..."
    ENV_FILE=".env.prod"
    DOCKER_TAG="bluelabel-autopilot:prod"
    EXTRA_ARGS=""
fi

# Check if env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Warning: $ENV_FILE not found. Using defaults from .env.sample"
    if [ -f ".env.sample" ]; then
        cp .env.sample "$ENV_FILE"
        echo "Created $ENV_FILE from .env.sample - please update with your credentials"
    fi
fi

# Build Docker image
echo "Building Docker image..."
docker build -t "$DOCKER_TAG" .

if [ $? -ne 0 ]; then
    echo "Error: Docker build failed"
    exit 1
fi

# Shift arguments to get command
shift $SHIFT_COUNT
COMMAND="$@"

# If no command provided, show help
if [ -z "$COMMAND" ]; then
    COMMAND="python runner/cli_runner.py --help"
fi

# Run Docker container
echo "Running command: $COMMAND"
docker run \
    $EXTRA_ARGS \
    --rm \
    -v "$(pwd)/$ENV_FILE:/app/.env:ro" \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/postbox:/app/postbox" \
    -e ENVIRONMENT="$ENV" \
    "$DOCKER_TAG" \
    $COMMAND