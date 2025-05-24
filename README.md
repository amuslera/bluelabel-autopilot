# Bluelabel Autopilot

A modernized, MCP-compliant agent system extracted from the legacy AIOS-V2 codebase. This repository contains core agent components redesigned for simplicity, maintainability, and file-based operations.

## Overview

Bluelabel Autopilot is a lightweight content processing system that:
- Processes content from various sources (URLs, PDFs, documents)
- Generates summaries and digests
- Provides a simple CLI interface
- Uses file-based storage instead of databases
- Follows Model Context Protocol (MCP) standards

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

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/bluelabel-autopilot.git
cd bluelabel-autopilot

# Install dependencies (Python 3.8+)
pip install -r requirements.txt
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