# ContentMind Prompt Templates

This directory contains modernized prompt templates extracted from bluelabel-AIOS-V2 for use in the bluelabel-autopilot system.

## Available Templates

### 1. summarization.yaml
- **Purpose**: Generate concise summaries of technical and business content
- **Use Case**: Summarizing documentation, articles, reports
- **Key Features**: 
  - Structured output with summary, key points, and action items
  - Configurable chunk processing for long documents
  - Examples included

### 2. event_summary.yaml
- **Purpose**: Create structured summaries of meetings and events
- **Use Case**: Meeting notes, conference proceedings, event transcripts
- **Key Features**:
  - Chronological timeline extraction
  - Participant identification
  - Decision and action item tracking
  - Structured output format

### 3. technical_analysis.yaml
- **Purpose**: Analyze technical content and provide insights
- **Use Case**: Code reviews, architecture assessments, technical documentation analysis
- **Key Features**:
  - Architecture pattern identification
  - Risk analysis
  - Improvement recommendations
  - Defined analysis criteria

## Usage

Each template follows a consistent structure:
```yaml
config:
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 2000

prompt_template:
  system: "System prompt..."
  user: "User prompt template..."
  assistant: "Expected output format..."
```

Templates support variable substitution using `{{ variable_name }}` syntax.

## Migration Notes

These templates were modernized from the original bluelabel-AIOS-V2 versions:
- Removed overly complex configuration options
- Simplified prompt structures
- Updated to use GPT-4 by default
- Focused on practical, actionable outputs
- Removed deprecated error handling patterns