# Docker Quickstart Guide

This guide helps you get Bluelabel Autopilot running in Docker quickly.

## Prerequisites

- Docker installed and running
- Git (to clone the repository)
- A `.env` file with your configuration (see Configuration section)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd bluelabel-autopilot

# Copy the sample environment file
cp config/.env.sample .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

### 2. Build and Run

The `start.sh` script handles everything:

```bash
# Development mode (default)
./start.sh dev

# Production mode
./start.sh prod

# Run a specific command
./start.sh dev python runner/cli_runner.py run digest --input tests/sample_digest_input.json
```

### 3. Common Commands

```bash
# Show CLI help
./start.sh dev python runner/cli_runner.py --help

# Run ingestion agent
./start.sh dev python runner/cli_runner.py run ingestion --input tests/sample_url_input.json

# Execute a workflow
./start.sh dev python runner/workflow_executor.py workflows/sample_ingestion_digest.yaml

# Run with email delivery
./start.sh dev python runner/workflow_executor_with_email.py workflows/sample_ingestion_digest.yaml
```

## Configuration

### Environment Variables

The Docker container uses environment variables from your `.env` file:

```bash
# Core settings
ENVIRONMENT=development
LOG_LEVEL=INFO

# Gmail settings (for email triggers)
GMAIL_USER=your-email@gmail.com
GMAIL_CLIENT_ID=your-client-id
GMAIL_CLIENT_SECRET=your-client-secret

# SMTP settings (for email delivery)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Optional: LLM API keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Volume Mounts

The container automatically mounts:
- `.env` file (read-only)
- `data/` directory (for workflow outputs)
- `postbox/` directory (for agent communication)

## Manual Docker Commands

If you prefer not to use `start.sh`:

```bash
# Build the image
docker build -t bluelabel-autopilot:latest .

# Run with mounted volumes
docker run -it --rm \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/postbox:/app/postbox \
  bluelabel-autopilot:latest \
  python runner/cli_runner.py --help
```

## Troubleshooting

### Build Errors

If the build fails:
1. Ensure Docker daemon is running
2. Check you have sufficient disk space
3. Try `docker system prune` to clean up

### Runtime Errors

If the container fails to start:
1. Check your `.env` file exists
2. Verify file permissions on mounted volumes
3. Check Docker logs: `docker logs <container-id>`

### Permission Issues

The container runs as non-root user `appuser` (UID 1000). If you encounter permission issues:

```bash
# Fix ownership of data directories
sudo chown -R 1000:1000 data/ postbox/
```

## Development vs Production

### Development Mode
- Uses `.env` file
- Runs with `-it` flags for interactive terminal
- Shows detailed logging

### Production Mode
- Uses `.env.prod` file
- Runs without interactive flags
- Optimized for background execution

## Advanced Usage

### Custom Dockerfile

To extend the Dockerfile:

```dockerfile
# Add your customizations
FROM bluelabel-autopilot:latest

# Install additional packages
RUN pip install your-package

# Add custom scripts
COPY custom-scripts/ /app/custom-scripts/
```

### Docker Compose

For complex deployments, create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  autopilot:
    build: .
    environment:
      - ENVIRONMENT=production
    volumes:
      - ./.env.prod:/app/.env:ro
      - ./data:/app/data
      - ./postbox:/app/postbox
    command: python runner/email_workflow_runner.py
```

## Security Notes

1. Never commit `.env` files to version control
2. Use app-specific passwords for SMTP
3. Run as non-root user (already configured)
4. Keep base image updated: `docker pull python:3.11-slim`

## Next Steps

- Set up Gmail OAuth for email triggers
- Configure SMTP for email delivery
- Create custom workflows in `workflows/`
- Monitor outputs in `data/workflows/`