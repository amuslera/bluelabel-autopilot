# Enhanced Agent Monitor v2 Guide
## TASK-165L Implementation

> 🔍 **Complete guide to the enhanced agent status monitor with advanced UI features**

## Overview

The Enhanced Agent Monitor v2 is a powerful terminal-based application that provides real-time monitoring of AI agent status with advanced features including export functionality, multiple view modes, historical tracking, desktop notifications, and user customization.

## 🆕 New Features (v2 Enhancements)

### 1. Export Functionality
- **CSV Export**: Export current metrics and status to CSV files
- **Automatic Export**: Optional hourly auto-export of metrics
- **Custom Export Paths**: Configurable export directory
- **Export History**: Maintain export file history with automatic cleanup

### 2. View Modes
- **Normal View**: Full detailed status display
- **Compact View**: Minimal single-line status for each agent
- **Historical View**: 24-hour activity timeline and trends

### 3. Desktop Notifications
- **Task Completion Alerts**: Notifications when agents complete tasks
- **Sound Notifications**: Optional audio alerts
- **Configurable Notifications**: Enable/disable specific notification types
- **Cross-platform Support**: macOS native notifications with fallback

### 4. Copy to Clipboard
- **Status Reports**: Copy current status summary to clipboard
- **Quick Sharing**: Easy status sharing via clipboard
- **Formatted Output**: Clean, readable status report format

### 5. User Preferences
- **Configuration File**: Persistent user preferences in JSON format
- **Runtime Configuration**: Change settings without restarting
- **Command Line Options**: Override config with CLI arguments
- **Multiple Profiles**: Support for different configuration profiles

### 6. Historical Tracking
- **24-Hour History**: Track agent activity over 24 hours
- **Activity Patterns**: Visualize agent activity patterns
- **Status Changes**: Track and display status transitions
- **Performance Trends**: Historical performance metrics

## 🚀 Getting Started

### Quick Start
```bash
# Run with default settings
python3 tools/agent_monitor_v2.py

# Run in compact mode
python3 tools/agent_monitor_v2.py --view compact

# Export metrics only
python3 tools/agent_monitor_v2.py --export-only

# Disable notifications
python3 tools/agent_monitor_v2.py --no-notifications
```

### Installation Requirements
```bash
# Install required dependencies
pip3 install pyperclip

# Verify installation
python3 -c "import pyperclip; print('✅ pyperclip installed')"
```

## 📊 View Modes

### Normal View (Default)
The full-featured view showing comprehensive agent status and metrics.

**Features:**
- Complete agent status with task details
- Performance metrics with star ratings
- Sprint progress with visual bar
- Recent activity timeline
- System alerts and notifications
- Next planned tasks list

**Navigation:**
- `c` - Copy status to clipboard
- `e` - Export metrics to CSV
- `h` - Switch to historical view
- `C` - Switch to compact view
- `n` - Toggle notifications
- `q` - Quit monitor

### Compact View
Minimalist view showing essential information in a condensed format.

**Features:**
- Single-line status per agent
- Essential sprint progress
- Quick navigation commands
- Reduced screen real estate usage

**Best For:**
- Small terminal windows
- Quick status checks
- Background monitoring
- Remote access scenarios

### Historical View
24-hour activity tracking and trend analysis.

**Features:**
- Hourly activity bars
- Agent status transitions
- Activity pattern visualization
- Historical trend analysis
- Event timeline

**Data Retention:**
- 24 hours of historical data
- Configurable retention period
- Automatic data cleanup
- Memory-efficient storage

## 📁 Export Functionality

### Manual Export
```bash
# Interactive export (press 'e' during monitoring)
# Or command line export
python3 tools/agent_monitor_v2.py --export-only
```

### CSV Export Format
```csv
Agent,Status,Current_Task,Pending_Tasks,Completed_Tasks,Success_Rate,Avg_Duration,Last_Active,Export_Time
CA,working,TASK-165L,0,3,95.0,2.4,2025-05-29T08:57:17Z,2025-05-29T12:34:56Z
CB,ready,,2,5,88.0,3.1,2025-05-29T08:45:30Z,2025-05-29T12:34:56Z
```

### Export Location
```
.metrics/exports/
├── agent_metrics_20250529_123456.csv
├── agent_metrics_20250529_134567.csv
└── ...
```

### Auto-Export Configuration
```json
{
  "auto_export": true,
  "export_settings": {
    "auto_export_interval": "hourly",
    "export_location": ".metrics/exports/",
    "max_export_files": 50
  }
}
```

## 🔔 Desktop Notifications

### Notification Types

#### Task Completion Notifications
- **Trigger**: When an agent completes a task
- **Content**: Agent name, task title, duration
- **Sound**: Optional completion sound
- **Example**: "Task Completed - CA: Dashboard implementation (2.4h)"

#### Status Change Notifications
- **Trigger**: When agent status changes (optional)
- **Content**: Agent name, status transition
- **Example**: "CA changed from working to ready"

#### Sprint Milestone Notifications
- **Trigger**: Sprint progress milestones
- **Content**: Sprint completion percentage
- **Example**: "Sprint 50% complete - 5/10 tasks finished"

### Configuration
```json
{
  "notification_settings": {
    "task_completion": true,
    "agent_status_change": false,
    "sprint_milestones": true,
    "error_alerts": true,
    "sound_enabled": true
  }
}
```

### Platform Support
- **macOS**: Native notification center integration
- **Cross-platform**: Console notification fallback
- **Sound Support**: System sound integration

## 📋 Clipboard Integration

### Status Report Format
```
Agent Status Report - 2025-05-29 12:34:56
==================================================
CA: Working on TASK-165L - Monitor UI enhancements (1h 23m)
CB: Ready (2 pending tasks)
CC: Idle
ARCH: Idle

Sprint Progress: 5/10 (50%)
```

### Usage
- Press `c` during monitoring to copy current status
- Status is automatically formatted for sharing
- Compatible with all clipboard-aware applications

## ⚙️ Configuration

### Configuration File Location
```
tools/monitor_config.json
```

### Configuration Structure
```json
{
  "view_mode": "normal",
  "auto_export": false,
  "notifications_enabled": true,
  "refresh_interval": 5,
  "show_performance": true,
  "max_history_hours": 24,
  "export_format": "csv",
  "notification_sound": true
}
```

### Runtime Configuration Changes
```bash
# Toggle notifications during monitoring
Press 'n' key

# Switch view modes
Press 'h' for historical, 'C' for compact

# Export current metrics
Press 'e' key
```

### Command Line Overrides
```bash
# Override configuration file settings
python3 tools/agent_monitor_v2.py \
  --view compact \
  --refresh 10 \
  --no-notifications \
  --config custom_config.json
```

## 🎛️ Interactive Controls

### Keyboard Commands

#### Universal Commands
- `q` - Quit monitor
- `c` - Copy status to clipboard
- `e` - Export metrics to CSV
- `n` - Toggle notifications

#### View Navigation
- `h` - Switch to historical view
- `C` - Switch to compact view
- `1` - Switch to normal view
- `2` - Switch to compact view
- `3` - Switch to historical view

#### Quick Actions
- `Space` - Force refresh
- `Ctrl+C` - Quit with export option

### Mouse Support
The monitor is keyboard-driven for terminal compatibility, but supports:
- Copy/paste operations via system clipboard
- Terminal window resizing
- Scroll buffer access

## 📈 Performance Metrics

### Agent Performance Indicators

#### Star Rating System
- ⭐⭐⭐⭐⭐ (95%+ success rate)
- ⭐⭐⭐⭐☆ (90-94% success rate)
- ⭐⭐⭐☆☆ (80-89% success rate)
- ⭐⭐☆☆☆ (70-79% success rate)
- ⭐☆☆☆☆ (<70% success rate)

#### Metrics Tracked
- **Success Rate**: Percentage of successfully completed tasks
- **Average Duration**: Mean task completion time
- **Task Velocity**: Tasks completed per day
- **Active Time**: Time spent in working status

### Sprint Metrics
- **Completion Percentage**: Visual progress bar
- **Task Distribution**: Completed vs. pending vs. in-progress
- **Velocity Tracking**: Daily task completion rate
- **Milestone Tracking**: Sprint checkpoint progress

## 🔧 Advanced Features

### Historical Data Analysis
```bash
# Access historical view
python3 tools/agent_monitor_v2.py --view historical

# Export historical data
python3 tools/agent_monitor_v2.py --export-only --include-history
```

### Custom Export Formats
```json
{
  "export_settings": {
    "include_historical_data": true,
    "custom_fields": ["task_priorities", "time_tracking"],
    "export_format": "csv"
  }
}
```

### Performance Optimization
```json
{
  "advanced_settings": {
    "cache_historical_data": true,
    "performance_tracking": true,
    "memory_limit_mb": 100
  }
}
```

## 🛠️ Troubleshooting

### Common Issues

#### Notifications Not Working
```bash
# Check notification permissions on macOS
# System Preferences > Security & Privacy > Privacy > Notifications

# Test notification manually
osascript -e 'display notification "Test" with title "Test"'

# Disable notifications if unsupported
python3 tools/agent_monitor_v2.py --no-notifications
```

#### Clipboard Not Working
```bash
# Install/reinstall pyperclip
pip3 install --upgrade pyperclip

# Test clipboard functionality
python3 -c "import pyperclip; pyperclip.copy('test'); print('✅ Clipboard working')"

# Alternative: Use terminal copy/paste
# Copy output manually from terminal
```

#### Export Issues
```bash
# Check export directory permissions
ls -la .metrics/exports/

# Create export directory if missing
mkdir -p .metrics/exports/

# Test export manually
python3 tools/agent_monitor_v2.py --export-only
```

#### Configuration Problems
```bash
# Reset configuration to defaults
rm tools/monitor_config.json
python3 tools/agent_monitor_v2.py  # Will recreate default config

# Validate JSON configuration
python3 -m json.tool tools/monitor_config.json
```

### Performance Issues

#### High Memory Usage
```json
{
  "max_history_hours": 12,
  "advanced_settings": {
    "cache_historical_data": false,
    "memory_limit_mb": 50
  }
}
```

#### Slow Refresh
```json
{
  "refresh_interval": 10,
  "display_settings": {
    "show_agent_metrics": false,
    "show_recent_activity": false
  }
}
```

## 📚 API Reference

### Configuration Options

#### Core Settings
- `view_mode`: "normal" | "compact" | "historical"
- `refresh_interval`: Integer (seconds)
- `notifications_enabled`: Boolean
- `auto_export`: Boolean

#### Display Settings
- `show_performance`: Boolean
- `show_recent_activity`: Boolean
- `show_alerts`: Boolean
- `color_coding`: Boolean

#### Export Settings
- `export_format`: "csv" | "json"
- `auto_export_interval`: "hourly" | "daily"
- `max_export_files`: Integer

### Command Line Arguments
```bash
python3 tools/agent_monitor_v2.py [OPTIONS]

Options:
  --view {normal,compact,historical}
                        Initial view mode
  --config CONFIG       Configuration file path
  --export-only         Export metrics and exit
  --no-notifications    Disable desktop notifications
  --refresh REFRESH     Refresh interval in seconds
  --help               Show help message
```

## 🔄 Integration

### CI/CD Integration
```bash
# Export metrics for CI/CD pipelines
python3 tools/agent_monitor_v2.py --export-only > metrics.csv

# Monitor specific agents
AGENT_FILTER=CA python3 tools/agent_monitor_v2.py --export-only
```

### Script Integration
```python
from tools.agent_monitor_v2 import EnhancedAgentMonitor

# Programmatic access
monitor = EnhancedAgentMonitor()
status = monitor.get_agent_status("CA")
metrics = monitor.export_metrics_to_csv()
```

### Automation Integration
```bash
# Automated monitoring with exports
*/30 * * * * cd /path/to/project && python3 tools/agent_monitor_v2.py --export-only
```

## 📊 Use Cases

### Development Monitoring
- **Real-time Status**: Monitor active development tasks
- **Performance Tracking**: Track agent efficiency and bottlenecks
- **Sprint Progress**: Visualize sprint completion progress
- **Team Coordination**: Share status via clipboard integration

### Project Management
- **Status Reporting**: Export metrics for project reports
- **Historical Analysis**: Analyze productivity patterns
- **Milestone Tracking**: Monitor sprint and project milestones
- **Resource Planning**: Identify agent capacity and allocation

### Operations Monitoring
- **System Health**: Monitor agent system health
- **Alert Management**: Receive notifications for critical events
- **Performance Optimization**: Identify performance improvement opportunities
- **Capacity Planning**: Plan resource allocation based on historical data

## 🔮 Future Enhancements

### Planned Features
- **Web Dashboard**: Browser-based monitoring interface
- **Mobile Notifications**: Push notifications to mobile devices
- **Custom Dashboards**: User-configurable dashboard layouts
- **Advanced Analytics**: Machine learning-powered insights
- **Team Collaboration**: Multi-user monitoring and sharing
- **API Integration**: REST API for external tool integration

### Extensibility
- **Plugin System**: Custom plugin development
- **Custom Metrics**: User-defined performance metrics
- **Integration Hooks**: Custom integration points
- **Theme Support**: Customizable visual themes

---

**Guide Version**: 1.0.0  
**TASK ID**: TASK-165L  
**Implementation Date**: May 29, 2025  
**Status**: ✅ COMPLETE  

*🎯 Enhanced monitor with all UI improvements operational*

## Quick Reference Card

### Essential Commands
```bash
# Start monitor
python3 tools/agent_monitor_v2.py

# Compact view
python3 tools/agent_monitor_v2.py --view compact

# Export metrics
python3 tools/agent_monitor_v2.py --export-only

# Custom refresh rate
python3 tools/agent_monitor_v2.py --refresh 10
```

### Interactive Keys
- `c` Copy status  
- `e` Export CSV  
- `h` Historical view  
- `C` Compact view  
- `n` Toggle notifications  
- `q` Quit  

### File Locations
- **Config**: `tools/monitor_config.json`
- **Exports**: `.metrics/exports/`
- **Documentation**: `docs/tools/MONITOR_V2_GUIDE.md` 