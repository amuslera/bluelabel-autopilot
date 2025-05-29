# Agent Status Dashboard Setup Guide
## TASK-165G Implementation

> 🖥️ **Real-time web-based dashboard for monitoring AI agent status and task progress**

## Overview

The Agent Status Dashboard provides a comprehensive web-based interface for monitoring the real-time status of AI agents, tracking task progress, and visualizing system performance. It offers a modern, responsive UI with live data updates and detailed analytics.

## 🎯 Features

### Core Functionality
- **Real-time Agent Monitoring**: Live status updates for all agents (CA, CB, CC, WA, ARCH, BLUE)
- **Task Progress Tracking**: Visual progress bars and completion statistics
- **Task History Timeline**: Chronological view of completed and pending tasks
- **Performance Metrics**: Success rates, average duration, productivity analytics
- **Sprint Progress**: Current sprint completion tracking with visual indicators
- **Interactive Filtering**: Filter tasks by agent, status, or time period
- **Data Export**: CSV export functionality for task history and metrics

### User Interface
- **Modern Design**: Dark theme with glassmorphism effects and smooth animations
- **Responsive Layout**: Optimized for desktop, tablet, and mobile devices
- **Real-time Updates**: Auto-refresh every 30 seconds with manual refresh option
- **Connection Status**: Live connection indicator with error handling
- **Loading States**: Smooth loading animations and error recovery

## 🏗️ Architecture

### Frontend Components
```
apps/dashboard/
├── index.html              # Main dashboard HTML
├── static/
│   ├── css/
│   │   └── dashboard.css   # Responsive styling with CSS custom properties
│   └── js/
│       └── dashboard.js    # Real-time dashboard logic and API integration
```

### Backend Server
```
tools/
└── dashboard_server.py     # Flask-based API server with data aggregation
```

### Data Sources
- **Agent Outboxes**: `postbox/{AGENT}/outbox.json` - Current task status
- **Sprint Progress**: `.sprint/progress.json` - Overall sprint tracking
- **Historical Data**: Agent completion records and task history

## 🚀 Quick Start

### 1. Prerequisites

#### Python Dependencies
```bash
# Install required Python packages
pip install flask flask-cors

# Or using requirements (if available)
pip install -r requirements.txt
```

#### Verify Installation
```bash
# Check that dashboard files exist
ls -la apps/dashboard/
ls -la tools/dashboard_server.py
```

### 2. Start the Dashboard Server

#### Basic Usage
```bash
# Start with default settings (localhost:3000)
python3 tools/dashboard_server.py

# Or make it executable and run directly
chmod +x tools/dashboard_server.py
./tools/dashboard_server.py
```

#### Advanced Configuration
```bash
# Custom port and host
python3 tools/dashboard_server.py --port 8080 --host 0.0.0.0

# Enable debug mode for development
python3 tools/dashboard_server.py --debug

# Get help on all options
python3 tools/dashboard_server.py --help
```

### 3. Access the Dashboard

Once the server is running, access the dashboard at:
- **Local Access**: http://localhost:3000
- **Network Access**: http://{YOUR_IP}:3000 (if using --host 0.0.0.0)

You should see:
```
🌐 Agent Status Dashboard Server
================================
Server: http://localhost:3000
Dashboard: http://localhost:3000
API Base: http://localhost:3000/api
Health Check: http://localhost:3000/api/health

Press Ctrl+C to stop
```

## 📊 Dashboard Sections

### 1. System Overview
- **Total Tasks**: Aggregate count across all agents
- **Completed Tasks**: Successfully finished tasks
- **In Progress**: Currently active tasks
- **Efficiency Rate**: Overall completion percentage
- **Sprint Progress Bar**: Visual representation of current sprint

### 2. Agent Status Cards
Each agent displays:
- **Current Status**: Working, Ready, Idle, or Error
- **Current Task**: Active task ID (if working)
- **Task Statistics**: Pending, completed, success rate, average duration
- **Visual Indicators**: Color-coded status with animations

### 3. Task History Timeline
- **Recent Activity**: Chronological list of task completions
- **Agent Filtering**: Filter by specific agent or view all
- **Task Details**: ID, title, duration, timestamp
- **Export Option**: Download history as CSV

### 4. Performance Metrics
- **Average Duration**: Mean task completion time
- **Success Rate**: Percentage of successful completions
- **Weekly Activity**: Tasks completed in the last 7 days
- **Active Agents**: Count of agents with pending work

## 🔧 Configuration

### Environment Configuration

#### Dashboard Server Settings
```python
# Default configuration in dashboard_server.py
PORT = 3000
HOST = 'localhost'
DEBUG = False
REFRESH_INTERVAL = 30  # seconds
```

#### Customizing Agent Information
```python
# Edit agent configuration in dashboard_server.py
self.agents = {
    'CA': {'name': 'Custom Agent Name', 'role': 'Custom Role'},
    # Add or modify agent definitions
}
```

### Frontend Configuration

#### Refresh Interval
```javascript
// Edit in static/js/dashboard.js
this.refreshInterval = 30000; // 30 seconds (in milliseconds)
```

#### API Endpoint
```javascript
// Change API base URL if needed
this.apiBaseUrl = 'http://localhost:3000/api';
```

## 🔗 API Endpoints

The dashboard server provides RESTful API endpoints for external integration:

### System Information
```http
GET /api/health
GET /api/system/overview
GET /api/sprint/progress
```

### Agent Data
```http
GET /api/agents/status                    # All agents
GET /api/agents/{agent_id}/status         # Specific agent
```

### Task Data
```http
GET /api/tasks/history?limit=50&agent=CA  # Task history with filters
GET /api/metrics/performance              # Performance metrics
```

### Response Examples

#### System Overview
```json
{
  "total_tasks": 15,
  "completed_tasks": 8,
  "in_progress_tasks": 2,
  "pending_tasks": 5,
  "completion_rate": 53.3,
  "last_updated": "2025-05-29T10:35:00Z"
}
```

#### Agent Status
```json
{
  "agent_id": "CA",
  "agent_name": "Cursor AI Frontend",
  "status": "working",
  "current_task": "TASK-165G",
  "pending_tasks": 1,
  "completed_tasks": 5,
  "success_rate": 95.0,
  "avg_duration": 2.4
}
```

## 🛠️ Development

### Local Development Setup

#### 1. Development Mode
```bash
# Enable debug mode and auto-reload
python3 tools/dashboard_server.py --debug

# Use development port
python3 tools/dashboard_server.py --port 3001
```

#### 2. Frontend Development
```bash
# Serve dashboard files for live editing
cd apps/dashboard
python3 -m http.server 8080

# Access at http://localhost:8080
# Configure API base URL in dashboard.js for cross-origin requests
```

#### 3. Hot Reload Setup
For development with hot reloading:
```bash
# Use flask debug mode
export FLASK_ENV=development
python3 tools/dashboard_server.py --debug
```

### Customization

#### Adding New Metrics
1. **Backend**: Add new endpoint in `dashboard_server.py`
```python
@app.route('/api/custom/metric')
def custom_metric():
    # Implement your metric calculation
    return jsonify({'value': calculated_value})
```

2. **Frontend**: Add data fetching in `dashboard.js`
```javascript
async loadCustomMetric() {
    const response = await fetch(`${this.apiBaseUrl}/custom/metric`);
    const data = await response.json();
    // Update UI elements
}
```

#### Styling Customization
Edit `static/css/dashboard.css`:
```css
:root {
    /* Customize color scheme */
    --primary: #your-color;
    --bg-primary: #your-bg-color;
}
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Server Won't Start
```bash
# Check if port is in use
lsof -i :3000

# Use alternative port
python3 tools/dashboard_server.py --port 3001
```

#### 2. No Data Showing
```bash
# Verify agent outbox files exist
ls -la postbox/*/outbox.json

# Check sprint progress file
ls -la .sprint/progress.json

# Verify file permissions
chmod 644 postbox/*/outbox.json
```

#### 3. Connection Issues
- **CORS Errors**: Ensure the server includes CORS headers
- **Network Access**: Use `--host 0.0.0.0` for network access
- **Firewall**: Check that port 3000 is not blocked

#### 4. Performance Issues
```bash
# Check system resources
top | grep python

# Monitor server logs
python3 tools/dashboard_server.py --debug
```

### Debugging

#### Enable Debug Logging
```bash
# Run with debug mode
python3 tools/dashboard_server.py --debug

# Check browser console for client-side errors
# Open Developer Tools > Console
```

#### Health Check
```bash
# Test API endpoints
curl http://localhost:3000/api/health
curl http://localhost:3000/api/system/overview
```

#### Data Validation
```bash
# Validate JSON files
python3 -m json.tool postbox/CA/outbox.json
python3 -m json.tool .sprint/progress.json
```

## 📈 Monitoring & Maintenance

### Performance Monitoring

#### Server Performance
- Monitor memory usage during long-running sessions
- Check response times for API endpoints
- Monitor concurrent connection handling

#### Client Performance
- Check for memory leaks in browser
- Monitor network request frequency
- Validate refresh interval efficiency

### Regular Maintenance

#### Data Cleanup
```bash
# Archive old task data periodically
# Implement data retention policies
# Clean up temporary files
```

#### Security Updates
```bash
# Keep Flask and dependencies updated
pip install --upgrade flask flask-cors

# Regularly review CORS configuration
# Monitor for security vulnerabilities
```

## 🚀 Production Deployment

### Production Setup

#### 1. Process Management
```bash
# Use systemd service (recommended)
sudo systemctl enable dashboard
sudo systemctl start dashboard

# Or use PM2 for Node.js-style management
pm2 start tools/dashboard_server.py --name "agent-dashboard"
```

#### 2. Reverse Proxy
```nginx
# nginx configuration
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 3. SSL/HTTPS
```bash
# Use Let's Encrypt for SSL
certbot --nginx -d your-domain.com
```

### Production Configuration
```python
# Production settings
DEBUG = False
HOST = '127.0.0.1'  # Bind to localhost only
PORT = 3000

# Enable logging
import logging
logging.basicConfig(level=logging.INFO)
```

## 🔧 Integration

### Integration with CI/CD

#### GitHub Actions Example
```yaml
name: Dashboard Deployment
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy Dashboard
        run: |
          python3 tools/dashboard_server.py --port 3000 &
          # Add health check
          curl --retry 5 http://localhost:3000/api/health
```

### Integration with Monitoring Tools

#### Prometheus Metrics
Add metrics endpoint:
```python
from prometheus_client import Counter, Histogram, generate_latest

@app.route('/metrics')
def metrics():
    return generate_latest()
```

#### Grafana Dashboard
- Import agent status metrics
- Create custom dashboards
- Set up alerting rules

## 📚 Additional Resources

### Related Documentation
- [Agent Autonomy Guidelines](../system/AGENT_AUTONOMY_GUIDELINES.md)
- [Outbox Schema](../system/OUTBOX_SCHEMA.md)
- [Morning Kickoff Automation](../tools/README_MORNING_KICKOFF.md)

### API Documentation
- Swagger/OpenAPI documentation available at `/api/docs` (if enabled)
- Postman collection for API testing

### Community Resources
- Issue tracker for bug reports
- Feature request guidelines
- Contribution guide for enhancements

## 📊 Success Metrics

### Key Performance Indicators
- **Uptime**: Target 99.9% availability
- **Response Time**: < 200ms for API endpoints
- **Data Accuracy**: 100% consistency with source files
- **User Experience**: < 3 second page load time

### Usage Analytics
- Track dashboard access patterns
- Monitor feature usage
- Collect user feedback

---

**Implementation Date**: May 29, 2025  
**Version**: 1.0.0  
**TASK ID**: TASK-165G  
**Status**: ✅ COMPLETED  

*🎯 Dashboard accessible at localhost:3000 showing live agent status* 

## Quick Reference Commands

```bash
# Start dashboard
python3 tools/dashboard_server.py

# Custom port
python3 tools/dashboard_server.py --port 8080

# Network access
python3 tools/dashboard_server.py --host 0.0.0.0

# Debug mode
python3 tools/dashboard_server.py --debug

# Health check
curl http://localhost:3000/api/health

# View all agents
curl http://localhost:3000/api/agents/status

# System overview
curl http://localhost:3000/api/system/overview
``` 