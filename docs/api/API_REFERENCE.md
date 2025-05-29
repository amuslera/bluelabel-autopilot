# API Reference

This document provides a comprehensive API reference for all tools and utilities in the BlueLabelAutopilot orchestration system.

## Table of Contents

- [Tools.Agent Metrics](#tools-agent_metrics)
- [Tools.Agent Monitor](#tools-agent_monitor)
- [Tools.Dashboard Server](#tools-dashboard_server)
- [Tools.Generate Api Docs](#tools-generate_api_docs)
- [Tools.Quick Status](#tools-quick_status)

## Tools.Agent Metrics

**File**: `tools/agent_metrics.py`

### class AgentMetrics

Manages agent performance metrics collection and reporting

*Source: tools/agent_metrics.py:55*

#### Methods

##### __init__(self, base_path: str)

**Examples:**
```python
def __init__(self):
super().__init__("Test Agent", "A test agent")
super().__init__("Unhealthy Agent", "Always fails")
```

*Source: tools/agent_metrics.py:58*

##### collect_metrics_from_outbox(self, agent_id: str) -> List[TaskMetric]

Collect metrics from an agent's outbox file

*Source: tools/agent_metrics.py:68*

##### generate_performance_report(self) -> Dict[str, Any]

Generate a comprehensive performance report across all agents

*Source: tools/agent_metrics.py:167*

##### print_summary_report(self, report: Dict[str, Any])

Print a human-readable summary of the performance report

*Source: tools/agent_metrics.py:242*

##### save_agent_metrics(self, agent_id: str, metrics: List[TaskMetric])

Save metrics for a specific agent

*Source: tools/agent_metrics.py:120*

##### track_task_complete(self, agent_id: str, task_id: str, status: str)

Mark a task as completed and record the timestamp

*Source: tools/agent_metrics.py:290*

##### track_task_start(self, agent_id: str, task_id: str)

Mark a task as started and record the timestamp

*Source: tools/agent_metrics.py:269*

### class TaskMetric

`@dataclass`

Individual task execution metric

*Source: tools/agent_metrics.py:22*

#### Methods

##### efficiency_score(self) -> Optional[float]

`@property`

Calculate efficiency score (0-100)

*Source: tools/agent_metrics.py:45*

##### execution_time(self) -> Optional[float]

`@property`

Calculate execution time in hours

*Source: tools/agent_metrics.py:36*

### Functions

#### main()

CLI interface for agent metrics

**Examples:**
```python
"from_domain": "aiweekly.com",
unittest.main()
pytest.main([__file__, "-v"])
```

*Source: tools/agent_metrics.py:323*

---

## Tools.Agent Monitor

### class AgentMonitor

*Source: tools/agent_monitor.py:13*

#### Methods

##### __init__(self)

**Examples:**
```python
def __init__(self):
super().__init__("Test Agent", "A test agent")
super().__init__("Unhealthy Agent", "Always fails")
```

*Source: tools/agent_monitor.py:14*

##### display_status(self)

Display current status

*Source: tools/agent_monitor.py:87*

##### get_agent_status(self, agent_id)

Check agent's current task from outbox

*Source: tools/agent_monitor.py:19*

##### get_next_planned_tasks(self)

Return list of next planned tasks

*Source: tools/agent_monitor.py:75*

##### get_sprint_progress(self)

Load sprint progress from file

*Source: tools/agent_monitor.py:64*

##### run(self)

Run the monitor with auto-refresh

**Examples:**
```python
asyncio.run(coro(self))
result = subprocess.run([
subprocess.run([
```

*Source: tools/agent_monitor.py:185*

---

## Tools.Dashboard Server

**File**: `tools/dashboard_server.py`

### class DashboardServer

*Source: tools/dashboard_server.py:27*

#### Methods

##### __init__(self, port, debug)

**Examples:**
```python
def __init__(self):
super().__init__("Test Agent", "A test agent")
super().__init__("Unhealthy Agent", "Always fails")
```

*Source: tools/dashboard_server.py:28*

##### calculate_average_duration(self, tasks: List[Dict[str, Any]]) -> float

Calculate average task duration in hours

*Source: tools/dashboard_server.py:408*

##### calculate_task_duration(self, created_at: str, completed_at: str) -> Optional[str]

Calculate duration between two timestamps

*Source: tools/dashboard_server.py:426*

##### create_app(self)

Create and configure Flask application

*Source: tools/dashboard_server.py:48*

##### get_agent_status(self, agent_id: str) -> Dict[str, Any]

Get status for a specific agent

*Source: tools/dashboard_server.py:181*

##### get_performance_metrics(self) -> Dict[str, Any]

Get system performance metrics

*Source: tools/dashboard_server.py:294*

##### get_sprint_progress(self) -> Dict[str, Any]

Get current sprint progress

*Source: tools/dashboard_server.py:357*

##### get_system_overview(self) -> Dict[str, Any]

Get system overview statistics

*Source: tools/dashboard_server.py:146*

##### get_task_history(self, limit: int, agent_filter: Optional[str]) -> Dict[str, Any]

Get recent task history across all agents

*Source: tools/dashboard_server.py:234*

##### load_agent_outbox(self, agent_id: str) -> Optional[Dict[str, Any]]

Load agent outbox data

*Source: tools/dashboard_server.py:394*

##### register_routes(self, app)

Register all application routes

*Source: tools/dashboard_server.py:62*

##### run(self, host)

Run the dashboard server

**Examples:**
```python
asyncio.run(coro(self))
result = subprocess.run([
subprocess.run([
```

*Source: tools/dashboard_server.py:440*

### Functions

#### agent_status(agent_id)

`@app.route('/api/agents/<agent_id>/status')`

Get specific agent status

*Source: tools/dashboard_server.py:85*

#### all_agents_status()

`@app.route('/api/agents/status')`

Get status for all agents

*Source: tools/dashboard_server.py:97*

#### health_check()

`@app.route('/api/health')`

Health check endpoint

**Examples:**
```python
async def test_health_check_all(self, registry):
assert metadata.last_health_check is not None
is_healthy = await registry.health_check("healthy")
```

*Source: tools/dashboard_server.py:138*

#### index()

`@app.route('/')`

Serve the main dashboard

*Source: tools/dashboard_server.py:66*

#### main()

Main entry point

**Examples:**
```python
"from_domain": "aiweekly.com",
unittest.main()
pytest.main([__file__, "-v"])
```

*Source: tools/dashboard_server.py:465*

#### performance_metrics()

`@app.route('/api/metrics/performance')`

Get performance metrics

*Source: tools/dashboard_server.py:120*

#### sort_key(task)

*Source: tools/dashboard_server.py:273*

#### sprint_progress()

`@app.route('/api/sprint/progress')`

Get current sprint progress

*Source: tools/dashboard_server.py:129*

#### static_files(filename)

`@app.route('/static/<path:filename>')`

Serve static files

*Source: tools/dashboard_server.py:71*

#### system_overview()

`@app.route('/api/system/overview')`

Get system overview statistics

*Source: tools/dashboard_server.py:76*

#### task_history()

`@app.route('/api/tasks/history')`

Get recent task history

*Source: tools/dashboard_server.py:108*

---

## Tools.Generate Api Docs

**File**: `tools/generate_api_docs.py`

### class APIDocGenerator

Generates API documentation from Python source files

*Source: tools/generate_api_docs.py:48*

#### Methods

##### __init__(self, base_path: str)

**Examples:**
```python
def __init__(self):
super().__init__("Test Agent", "A test agent")
super().__init__("Unhealthy Agent", "Always fails")
```

*Source: tools/generate_api_docs.py:51*

##### _extract_class_doc(self, node: ast.ClassDef, file_path: Path) -> ClassDoc

Extract documentation from a class node

*Source: tools/generate_api_docs.py:134*

##### _extract_function_doc(self, node: ast.FunctionDef, file_path: Path, parent_class: Optional[ast.ClassDef]) -> FunctionDoc

Extract documentation from a function node

*Source: tools/generate_api_docs.py:94*

##### _format_class_doc(self, class_doc: ClassDoc) -> List[str]

Format class documentation as markdown

*Source: tools/generate_api_docs.py:257*

##### _format_function_doc(self, func_doc: FunctionDoc, indent: str) -> List[str]

Format function documentation as markdown

*Source: tools/generate_api_docs.py:287*

##### _get_parent_class(self, tree: ast.AST, node: ast.FunctionDef) -> Optional[ast.ClassDef]

Find the parent class of a function node

*Source: tools/generate_api_docs.py:85*

##### extract_docs_from_file(self, file_path: Path) -> Tuple[List[FunctionDoc], List[ClassDoc]]

Extract documentation from a Python file

*Source: tools/generate_api_docs.py:57*

##### extract_examples_from_tests(self, test_dir: Path)

Extract usage examples from test files

*Source: tools/generate_api_docs.py:158*

##### generate_markdown(self) -> str

Generate markdown documentation

*Source: tools/generate_api_docs.py:208*

##### generate_tools_reference(self) -> str

Generate specific reference for tools/ directory

*Source: tools/generate_api_docs.py:324*

##### scan_directory(self, directory: Path, pattern: str)

Scan a directory for Python files and extract documentation

*Source: tools/generate_api_docs.py:186*

### class ClassDoc

`@dataclass`

Documentation for a class

*Source: tools/generate_api_docs.py:38*

### class FunctionDoc

`@dataclass`

Documentation for a single function

*Source: tools/generate_api_docs.py:20*

#### Methods

##### __post_init__(self)

*Source: tools/generate_api_docs.py:32*

### Functions

#### main()

CLI interface for API documentation generator

**Examples:**
```python
"from_domain": "aiweekly.com",
unittest.main()
pytest.main([__file__, "-v"])
```

*Source: tools/generate_api_docs.py:342*

---

## Tools.Quick Status

**File**: `tools/quick_status.py`

### Functions

#### check_agent_status(agent_id)

Check an agent's current task status

*Source: tools/quick_status.py:11*

#### main()

Display agent status summary

**Examples:**
```python
"from_domain": "aiweekly.com",
unittest.main()
pytest.main([__file__, "-v"])
```

*Source: tools/quick_status.py:53*

---
