# Bluelabel Autopilot 🚀

MCP-native agent orchestration platform for intelligent document processing with real-time capabilities.

## Overview

Bluelabel Autopilot is a high-performance content processing system that:
- Processes emails with PDF attachments in real-time
- Generates executive summaries using AI agents
- Provides REST API with WebSocket updates
- Features a unified workflow engine architecture
- Achieves <3 second processing for typical documents
- Follows Model Context Protocol (MCP) standards

## 🎯 Key Features

- **Unified Architecture**: Single adapter for multiple workflow engines
- **Real-time Updates**: WebSocket streaming of processing progress
- **High Performance**: <100ms API response, <3s PDF processing
- **Zero Breaking Changes**: Backward compatible with existing workflows
- **Production Ready**: Full test coverage, monitoring, and error handling

## Architecture

```
bluelabel-autopilot/
├── agents/                 # Core agent implementations
│   ├── base_agent.py      # Base class with MCP-compliant I/O
│   ├── agent_models.py    # Shared data models
│   ├── digest_agent.py    # Content digest generation
│   └── ingestion_agent.py # URL and PDF content processing
├── prompts/               # YAML prompt templates
│   └── contentmind/       # Content processing prompts
├── runner/                # CLI and execution
│   └── cli_runner.py      # Command-line interface
└── storage/               # File-based data storage
    └── knowledge/         # Processed content storage
```

## 📁 Repository Structure

### Active Development
- **`/agents/`** - Agent implementations and core processing logic
- **`/apps/`** - Application code (web UI, API server)
  - `/apps/api/` - FastAPI backend server
  - `/apps/web/` - Next.js frontend application
- **`/core/`** - Core system functionality and shared libraries
- **`/services/`** - Service implementations and microservices
- **`/workflows/`** - Workflow definitions and processing pipelines
- **`/tests/`** - Active test suites (unit, integration, e2e)

### Documentation
- **`/docs/`** - Organized documentation by category
  - `/docs/architecture/` - System architecture and design docs
  - `/docs/operations/` - Operational guides and live status
  - `/docs/development/` - Development standards and guidelines
  - `/docs/project-management/` - Sprint protocols and coordination
  - `/docs/reports/` - Performance reports and analysis
  - `/docs/security/` - Security documentation and audits
  - `/docs/devphases/PHASE_6.15/` - Current development phase documentation

### Configuration & Scripts
- **`/config/`** - Configuration files and environment settings
- **`/scripts/`** - Utility scripts and automation tools
- **`/demo/`** - Demo scenarios and example workflows

### Archived Content
- **`/archive/`** - Historical documentation and deprecated files
  - `/archive/phases/` - Previous development phases (6.11, 6.12, 6.13)
  - `/archive/sprints/` - Historical sprint documentation
  - `/archive/context/` - Old context and coordination files
  - `/archive/test_artifacts/` - Legacy test files and artifacts
  - `/archive/old_docs/` - Deprecated documentation
  - `ARCHIVE_INDEX.json` - Complete index of archived content

### Current Development Phase
- **Phase 6.15** - Multi-Agent Orchestration & AIOS v2 MVP
- **Sprint 3** - Production Deployment (COMPLETED)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/bluelabel-autopilot.git
cd bluelabel-autopilot

# Install dependencies (Python 3.8+)
pip install -r requirements.txt

# Install API dependencies
cd apps/api
pip install -r requirements.txt
cd ../..
```

### Running the System

1. **Start the API Server**:
```bash
cd apps/api
python main.py
# API available at http://localhost:8000
# WebSocket at ws://localhost:8000/ws
# API docs at http://localhost:8000/docs
```

2. **Run the Demo**:
```bash
python demo/email_to_summary.py
```

3. **Test the Integration**:
```bash
# Open in browser
open http://localhost:8000/static/test.html
```

## Usage

### CLI Commands

#### Digest Agent

```bash
# Generate a digest from stored summaries
python runner/cli_runner.py digest --format markdown

# Add a new summary
python runner/cli_runner.py add-summary "TechCrunch Article" "AI startup raises $50M..." --url "https://example.com"

# Run digest agent with custom JSON input
python runner/cli_runner.py run digest '{"task_id": "test", "content": {"action": "generate_digest"}}'
```

#### Ingestion Agent

```bash
# Process a URL
python runner/cli_runner.py run ingestion '{
    "task_id": "test-url",
    "task_type": "url",
    "content": {
        "url": "https://example.com/sample-article"
    }
}'

# Process a PDF
python runner/cli_runner.py run ingestion '{
    "task_id": "test-pdf",
    "task_type": "pdf",
    "content": {
        "file_path": "path/to/document.pdf"
    }
}'

# Using sample input files
python runner/cli_runner.py run ingestion --input tests/sample_url_input.json
python runner/cli_runner.py run ingestion --input tests/sample_pdf_input.json
```

### Common Options

```bash
# Specify custom storage paths
python runner/cli_runner.py run ingestion --input tests/sample_url_input.json \
    --storage-path ./custom/knowledge \
    --temp-path ./custom/temp
```

### Python API

```python
from agents.digest_agent import DigestAgent
from agents.ingestion_agent import IngestionAgent
from agents.base_agent import AgentInput

# Create agents
digest_agent = DigestAgent()
ingestion_agent = IngestionAgent(
    storage_path=Path("./data/knowledge"),
    temp_path=Path("./data/temp")
)

# Process URL content
url_input = AgentInput(
    task_id="url-001",
    task_type="url",
    source="api",
    content={"url": "https://example.com"}
)
url_result = await ingestion_agent.process(url_input)

# Process PDF content
pdf_input = AgentInput(
    task_id="pdf-001",
    task_type="pdf",
    source="api",
    content={"file_path": "path/to/document.pdf"}
)
pdf_result = await ingestion_agent.process(pdf_input)

# Generate digest
digest_input = AgentInput(
    task_id="digest-001",
    source="api",
    content={"action": "generate_digest", "format": "markdown"}
)
digest_result = await digest_agent.process(digest_input)
```

## Agents

### DigestAgent
Generates formatted digests from stored content summaries.

**Features:**
- Multiple output formats (Markdown, HTML, JSON)
- File-based summary storage
- Chronological ordering
- Source attribution

**Example Output:**
```markdown
# Content Digest

Generated on: 2025-01-23

## Summary 1
**Source:** TechCrunch Article  
**Date:** 2025-01-23T10:30:00  
AI startup raises $50M for revolutionary content processing...

[Read more](https://example.com)
```

### IngestionAgent
Processes content from URLs and PDFs.

**Features:**
- URL content extraction
- PDF text extraction
- Metadata extraction
- Content validation
- File-based storage

**Example Output:**
```
Processing Results:
------------------
Task ID: test-url
Status: success
Duration: 1234ms

Content Details:
Content ID: url_abc123
Content Type: url
Content Length: 12345 characters

Metadata:
title: Sample Article
author: John Doe
date: 2025-01-23
```

## Prompt Templates

The `prompts/contentmind/` directory contains YAML templates for:
- `summarization.yaml` - General content summarization
- `event_summary.yaml` - Meeting and event summaries  
- `technical_analysis.yaml` - Technical document analysis

Templates use Jinja2 syntax and can be customized for different use cases.

## Development

### Adding New Agents

1. Create a new file in `agents/`
2. Inherit from `BaseAgent`
3. Implement the `process()` method
4. Add to CLI runner registry

```python
from agents.base_agent import BaseAgent, AgentInput, AgentOutput

class MyAgent(BaseAgent):
    agent_id = "my-agent"
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        # Your implementation here
        return AgentOutput(
            task_id=input_data.task_id,
            status="completed",
            result="Result"
        )
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agents --cov=runner
```

## Migration from AIOS-V2

This repository represents a clean extraction of core components from the legacy AIOS-V2 system:

**Key Changes:**
- Removed PostgreSQL dependencies
- Simplified agent architecture
- Eliminated complex abstractions
- File-based storage instead of database
- MCP-compliant input/output models
- Modernized Python async/await patterns

**Preserved Components:**
- Core agent logic
- Prompt templates (simplified)
- Content processing workflows

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Original AIOS-V2 team for the foundational concepts
- Model Context Protocol (MCP) for standardization guidelines
- The agent-comms-mvp project for architectural patterns