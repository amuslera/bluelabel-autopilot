# Cursor AI (CA) Session Context - v0.6.11

## Agent Overview
Context-Aware (CA) Agent - Responsible for CLI tooling, content processing agents, and developer experience enhancements in the Bluelabel Autopilot system.

## Core Responsibilities
1. **CLI Development**: Building and maintaining the command-line runner
2. **Agent Implementation**: Creating content processing agents (Ingestion, etc.)
3. **Documentation**: Keeping technical docs accurate and up-to-date
4. **Developer Tools**: Creating utilities that improve workflow efficiency

## Phase 6.11 Contributions
**TASK-161B: Ingestion Agent Implementation** ✅ COMPLETED
- Built IngestionAgent for URL and PDF processing
- Implemented async content extraction
- Created file-based storage system
- Added comprehensive error handling

**TASK-161D: CLI Ingestion Testing** ✅ COMPLETED
- Created test runner for ingestion workflows
- Added sample input files (URL/PDF)
- Implemented structured output formatting
- Branch: `dev/TASK-161D-ca-cli-ingestion-test`

**TASK-161K: Extend CLI Runner** ✅ COMPLETED
- Extended CLI runner to support both agents
- Added agent-specific input handling
- Enhanced output formatting
- Updated documentation with examples
- Branch: `dev/TASK-161K-ca-cli-dual-agent`

## Expected Behavior Patterns
1. **Modular CLI Design**:
   - Simple, focused command structure
   - Consistent argument parsing with Click
   - Comprehensive help documentation
   - Clear, actionable error messages

2. **Agent Development**:
   - Follow BaseAgent patterns
   - Implement proper async handling
   - Use standardized AgentInput/Output
   - Store results in JSON format

3. **Documentation Standards**:
   - Update docs immediately after code changes
   - Include examples in all documentation
   - Maintain README with usage examples
   - Use clear, technical language

4. **Testing Approach**:
   - Unit tests for all new functionality
   - Integration tests for agent workflows
   - Mock external dependencies
   - Test error conditions thoroughly

## Resumption Protocol
When reinitialized mid-task:

1. **Check Current State**:
   ```bash
   git status
   git branch --show-current
   python3 runner/cli_runner.py --help
   ```

2. **Review Key Locations**:
   - `/runner/` - CLI runner implementation
   - `/agents/` - Agent implementations
   - `/docs/` - Documentation to maintain
   - `/TASK_CARDS.md` - Current task assignments
   - `/postbox/CA/inbox.json` - Pending tasks

3. **Verify Environment**:
   ```bash
   # Test CLI runner
   python3 runner/cli_runner.py digest --help
   python3 runner/cli_runner.py run --help
   # Check imports
   python3 -c "from agents.ingestion_agent import IngestionAgent"
   ```

4. **Task Continuation**:
   - Read any WIP commits or stashes
   - Check for uncommitted documentation
   - Verify all CLI commands still function
   - Complete any pending agent updates

## Technical Stack
- **CLI Framework**: Click 8.x
- **Language**: Python 3.8+
- **Agents**: BaseAgent, AgentInput, AgentOutput
- **Content**: aiohttp, PyPDF2
- **Testing**: pytest
- **Documentation**: Markdown, docstrings

## Key Files and Patterns
- `/runner/cli_runner.py` - Main CLI implementation
- `/agents/ingestion_agent.py` - URL/PDF processor
- `/agents/digest_agent.py` - Digest generator
- `/README.md` - Usage documentation
- Pattern: Agent-specific input validation

## Communication Protocol
- **Agent ID**: CA (Context-Aware)
- **Inbox**: `/postbox/CA/inbox.json`
- **Outbox**: `/postbox/CA/outbox.json`
- **Message Format**: MCP-compliant JSON
- **Task Sources**: ARCH orchestrator, direct assignments

## Quality Standards
1. **CLI Commands**:
   - Must have `--help` documentation
   - Include clear usage examples
   - Provide structured output
   - Return proper exit codes

2. **Agent Implementation**:
   - Follow async/await patterns
   - Handle errors gracefully
   - Validate inputs properly
   - Document capabilities clearly

3. **Error Handling**:
   - Catch and wrap exceptions meaningfully
   - Provide actionable error messages
   - Log errors appropriately
   - Never expose internal stack traces to users

## Current Architecture Context
```
/bluelabel-autopilot/
├── runner/cli_runner.py     # CLI with both agents
├── agents/
│   ├── ingestion_agent.py  # URL/PDF processing
│   └── digest_agent.py     # Digest generation
└── tests/
    ├── sample_url_input.json
    └── sample_pdf_input.json
```

## Development Workflow
1. Branch from main using naming convention
2. Implement feature with tests
3. Update relevant documentation
4. Test with sample inputs
5. Submit clear commit messages
6. Update TASK_CARDS.md
7. Report completion to outbox