# AIOS v2 Console - Complete UI/UX Scope

**Created:** May 30, 2025  
**Purpose:** Comprehensive UI/UX documentation for AIOS v2 MVP

## Overview

AIOS v2 requires a complete user interface that supports:
- File/URL/text upload with agent selection
- Agent CRUD operations with prompt management
- Multi-LLM configuration and routing
- Future MCP data source integration

## Core Pages Structure

### 1. Dashboard 🏠

**Purpose:** Home/landing page after login

```
┌─────────────────────────────────────────────────────┐
│ AIOS v2                              🔔 👤 John Doe │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Welcome back, John!                                 │
│                                                     │
│ ┌─── Quick Actions ─────────┐  ┌─── Stats ────────┐│
│ │ [📤 Upload & Process]     │  │ 📄 156 Processed  ││
│ │ [🤖 Create New Agent]     │  │ 🤖 12 Agents      ││
│ │ [📝 New Prompt Template]  │  │ 💾 2.3 GB Used    ││
│ └────────────────────────────┘  └──────────────────┘│
│                                                     │
│ Recent Activity                                     │
│ ├─ ✅ PDF Analysis completed (2 min ago)           │
│ ├─ 🔄 URL Processing in progress (5 min ago)      │
│ └─ 🤖 New agent "Legal Doc Analyzer" created      │
│                                                     │
│ Favorite Agents                          [See All >]│
│ ┌────┐ ┌────┐ ┌────┐ ┌────┐                      │
│ │ 📊 │ │ 📝 │ │ 🔍 │ │ 💼 │                      │
│ └────┘ └────┘ └────┘ └────┘                      │
└─────────────────────────────────────────────────────┘
```

**Key Elements:**
- Welcome message with user name
- Quick action buttons for common tasks
- Stats overview (files processed, agents, storage)
- Recent activity feed
- Favorite agents for quick access

### 2. Process Hub 📤

**Purpose:** Central interface for uploading and processing content

```
┌─────────────────────────────────────────────────────┐
│ Process Content                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Input Type: [File ▼] [URL] [Text] [Audio]         │
│                                                     │
│ ┌─── Drop Zone ─────────────────────────────────┐  │
│ │                                               │  │
│ │     📎 Drop files here or click to browse     │  │
│ │                                               │  │
│ └───────────────────────────────────────────────┘  │
│                                                     │
│ Select Agent:                          [Browse >]   │
│ ┌─────────────────────────────────────────────┐   │
│ │ 🤖 Document Analyzer Pro          [Select] │   │
│ │ Extracts key insights from documents        │   │
│ │ LLMs: GPT-4 (primary), Claude (fallback)   │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ ⚙️ Advanced Options                      [Show ▼]   │
│                                                     │
│ [Process Now] [Save as Template]                    │
└─────────────────────────────────────────────────────┘
```

**Key Features:**
- Input type selector (File/URL/Text/Audio)
- Drag & drop file upload
- Agent selection with preview
- Advanced options (collapsed by default)
- Process and template actions

### 3. Agent Studio 🤖

**Purpose:** Browse, create, and manage agents

```
┌─────────────────────────────────────────────────────┐
│ Agent Studio                    [+ Create Agent]    │
├─────────────────────────────────────────────────────┤
│ My Agents | Marketplace | Templates                 │
│                                                     │
│ Search: [_______________] Filter: [All Types ▼]    │
│                                                     │
│ ┌─── Agent Card ────────────────────────────────┐  │
│ │ 🤖 Document Analyzer Pro         ⚙️ 📊 🗑️     │  │
│ │ Created: 3 days ago | Used: 45 times          │  │
│ │ Prompts: 3 | LLMs: GPT-4, Claude             │  │
│ │ Data Sources: Google Drive, Notion (MCP)      │  │
│ └───────────────────────────────────────────────┘  │
│                                                     │
│ ┌─── Agent Card ────────────────────────────────┐  │
│ │ 📊 Sales Report Generator        ⚙️ 📊 🗑️     │  │
│ │ Created: 1 week ago | Used: 123 times         │  │
│ │ Prompts: 5 | LLMs: GPT-3.5                   │  │
│ │ Data Sources: Salesforce (MCP)                │  │
│ └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**Tabs:**
- My Agents - User's custom agents
- Marketplace - Public/shared agents
- Templates - Starting points

### 4. Agent Editor ✏️

**Purpose:** Create and configure agents

```
┌─────────────────────────────────────────────────────┐
│ Edit Agent: Document Analyzer Pro                   │
├─────────────────────────────────────────────────────┤
│ Basic | Prompts | LLMs | Data Sources | Test       │
│                                                     │
│ ┌─── Basic Information ─────────────────────────┐  │
│ │ Name: [Document Analyzer Pro]                 │  │
│ │ Icon: [🤖] Description: [_______________]     │  │
│ │ Category: [Analysis ▼] Tags: [doc, pdf, ai]  │  │
│ └───────────────────────────────────────────────┘  │
│                                                     │
│ ┌─── Capabilities ──────────────────────────────┐  │
│ │ Input Types:                                  │  │
│ │ ☑ PDF  ☑ Text  ☑ URL  ☐ Audio  ☐ Image     │  │
│ │                                               │  │
│ │ Output Formats:                               │  │
│ │ ☑ Summary  ☑ Key Points  ☑ JSON  ☐ Table    │  │
│ └───────────────────────────────────────────────┘  │
│                                                     │
│ [Save Draft] [Test Agent] [Publish]                 │
└─────────────────────────────────────────────────────┘
```

**Tabs:**
- Basic - Name, description, capabilities
- Prompts - Prompt configuration
- LLMs - Model selection and routing
- Data Sources - MCP connections
- Test - Testing console

### 5. Prompt Configuration Tab

```
┌─────────────────────────────────────────────────────┐
│ ┌─── Prompts Configuration ─────────────────────┐  │
│ │ Main Prompt:                    [Template ▼]  │  │
│ │ ┌─────────────────────────────────────────┐  │  │
│ │ │ System: You are an expert analyzer...   │  │  │
│ │ │ ${include:base-analyst}                 │  │  │
│ │ │                                          │  │  │
│ │ │ User: Analyze ${documentType}:          │  │  │
│ │ │ ${content}                               │  │  │
│ │ └─────────────────────────────────────────┘  │  │
│ │                                               │  │
│ │ Variables:                         [Add +]    │  │
│ │ • documentType (select) [PDF/TXT/URL]        │  │
│ │ • content (file/text)                        │  │
│ │                                               │  │
│ │ Task-Specific Prompts:             [Add +]    │  │
│ │ • Summarization → summary-template           │  │
│ │ • Extraction → extraction-template           │  │
│ └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 6. LLM Configuration Tab

```
┌─────────────────────────────────────────────────────┐
│ ┌─── LLM Configuration ─────────────────────────┐  │
│ │ Primary LLM:                                  │  │
│ │ Provider: [OpenAI ▼] Model: [GPT-4 ▼]       │  │
│ │ Temperature: [0.7] Max Tokens: [2000]        │  │
│ │                                               │  │
│ │ Fallback LLMs:                     [Add +]    │  │
│ │ 1. Claude 3 (Anthropic) - If primary fails   │  │
│ │ 2. GPT-3.5 (OpenAI) - For cost optimization  │  │
│ │                                               │  │
│ │ Task-Specific Routing:                        │  │
│ │ • Summarization → GPT-3.5 (cost-effective)   │  │
│ │ • Analysis → GPT-4 (high accuracy)           │  │
│ │ • Extraction → Claude (structured output)    │  │
│ └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 7. Prompt Builder 📝

**Purpose:** Create and manage reusable prompt templates

```
┌─────────────────────────────────────────────────────┐
│ Prompt Template Library          [+ New Template]   │
├─────────────────────────────────────────────────────┤
│ Search: [_______________] Tags: [Analysis ▼]       │
│                                                     │
│ ┌─── Template Editor ───────────────────────────┐  │
│ │ Name: base-analyst                            │  │
│ │ Version: 1.2.0                    [History]   │  │
│ │                                               │  │
│ │ System Prompt:                                │  │
│ │ ┌─────────────────────────────────────────┐  │  │
│ │ │ You are a professional analyst with      │  │  │
│ │ │ expertise in:                            │  │  │
│ │ │ - ${expertise_areas}                     │  │  │
│ │ │ - Data extraction and synthesis          │  │  │
│ │ │                                          │  │  │
│ │ │ Follow these guidelines:                 │  │  │
│ │ │ ${include:safety-guidelines}             │  │  │
│ │ └─────────────────────────────────────────┘  │  │
│ │                                               │  │
│ │ Includes: [safety-guidelines] [json-output]  │  │
│ │ Used by: 12 agents | 1,234 times            │  │
│ └───────────────────────────────────────────────┘  │
│                                                     │
│ [Save Version] [Fork] [Test] [Share]                │
└─────────────────────────────────────────────────────┘
```

**Features:**
- Version control for prompts
- Template composition (includes)
- Variable system
- Usage analytics
- Sharing capabilities

### 8. Data Sources 🔌 (Future MCP Integration)

**Purpose:** Connect and manage external data sources

```
┌─────────────────────────────────────────────────────┐
│ Data Sources                    [+ Connect Source]  │
├─────────────────────────────────────────────────────┤
│ Connected Sources:                                  │
│                                                     │
│ ┌─── Source Card ───────────────────────────────┐  │
│ │ 📁 Google Drive              ✅ Connected     │  │
│ │ MCP Provider: @drive-mcp                      │  │
│ │ Access: Read-only | Folders: /AI-Docs        │  │
│ │ Used by: 3 agents                    [⚙️]     │  │
│ └───────────────────────────────────────────────┘  │
│                                                     │
│ ┌─── Source Card ───────────────────────────────┐  │
│ │ 🔷 Notion Workspace          ✅ Connected     │  │
│ │ MCP Provider: @notion-mcp                     │  │
│ │ Access: Read/Write | DBs: 5          [⚙️]     │  │
│ └───────────────────────────────────────────────┘  │
│                                                     │
│ Available MCP Providers:               [Browse >]   │
│ • Slack  • GitHub  • Jira  • Salesforce           │
└─────────────────────────────────────────────────────┘
```

### 9. Knowledge Base 📚

**Purpose:** View all processed content and results

```
┌─────────────────────────────────────────────────────┐
│ Knowledge Base                                      │
├─────────────────────────────────────────────────────┤
│ Search: [_______________] Agent: [All ▼] Date: [▼] │
│                                                     │
│ ┌─── Result Entry ──────────────────────────────┐  │
│ │ 📄 Q3 Financial Report Analysis               │  │
│ │ Agent: Document Analyzer | 2 hours ago        │  │
│ │                                               │  │
│ │ Key Insights:                                 │  │
│ │ • Revenue up 23% YoY                         │  │
│ │ • Operating margins improved to 18%          │  │
│ │                                               │  │
│ │ [View Full] [Re-process] [Export] [Share]    │  │
│ └───────────────────────────────────────────────┘  │
│                                                     │
│ Processing History                      [View All >]│
│ ├─ ✅ invoice.pdf - Completed (5 min ago)         │
│ ├─ ✅ report.url - Completed (1 hour ago)        │
│ └─ ❌ data.csv - Failed (2 hours ago)            │
└─────────────────────────────────────────────────────┘
```

### 10. Settings ⚙️

**Purpose:** User and system configuration

```
┌─────────────────────────────────────────────────────┐
│ Settings                                            │
├─────────────────────────────────────────────────────┤
│ Profile | Preferences | API Keys | LLM Config      │
│                                                     │
│ ┌─── LLM Configuration ─────────────────────────┐  │
│ │ OpenAI:                                       │  │
│ │ API Key: [sk-...******************]          │  │
│ │ Organization: [my-org]                        │  │
│ │ Default Model: [GPT-4 ▼]                     │  │
│ │                                               │  │
│ │ Anthropic:                                    │  │
│ │ API Key: [sk-ant-...***************]         │  │
│ │ Default Model: [Claude 3 Opus ▼]             │  │
│ │                                               │  │
│ │ Cost Limits:                                  │  │
│ │ Daily: [$50.00] Monthly: [$1000.00]         │  │
│ └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Navigation Structure

**Main Navigation (Sidebar):**
- 🏠 Dashboard
- 📤 Process Hub
- 🤖 Agent Studio
- 📝 Prompt Builder
- 🔌 Data Sources
- 📚 Knowledge Base
- ⚙️ Settings

**Top Bar:**
- Search (global)
- Notifications
- User profile menu

## Key User Flows

### 1. Upload → Process → View Results
```
Dashboard → Process Hub → Select Input Type → Upload/Enter Content → 
Select Agent → Configure Options → Process → View Progress → 
See Results → Save to Knowledge Base
```

### 2. Create Custom Agent
```
Agent Studio → Create New Agent → Configure Basic Info → 
Set Up Prompts → Configure LLMs → Add Data Sources → 
Test Agent → Publish → Use in Process Hub
```

### 3. Build Reusable Prompt
```
Prompt Builder → New Template → Write System/User Prompts → 
Add Variables → Include Other Templates → Test → 
Save Version → Use in Agents
```

## Technical Requirements

### Frontend Stack
- **Framework:** React/Next.js (existing)
- **UI Library:** Tailwind CSS + Custom components
- **State Management:** Redux/Zustand
- **Forms:** React Hook Form
- **Code Editor:** Monaco Editor (for prompts)
- **Charts:** Recharts (for analytics)

### Component Library Needs
- **Cards:** Agent cards, result cards, source cards
- **Forms:** Multi-step forms, validation
- **Modals:** Upload modal, preview modal
- **Editors:** Code editor with syntax highlighting
- **Drag & Drop:** File upload zones
- **Tables:** Sortable, filterable data tables
- **Loading States:** Skeletons, spinners, progress bars

### API Endpoints Required

**Agent Management:**
```
POST   /api/agents              # Create agent
GET    /api/agents              # List agents
GET    /api/agents/:id          # Get agent details
PUT    /api/agents/:id          # Update agent
DELETE /api/agents/:id          # Delete agent
POST   /api/agents/:id/test     # Test agent
```

**Prompt Management:**
```
POST   /api/prompts             # Create prompt
GET    /api/prompts             # List prompts
GET    /api/prompts/:id         # Get prompt
PUT    /api/prompts/:id         # Update prompt
GET    /api/prompts/:id/versions # Get versions
```

**Processing:**
```
POST   /api/process             # Process content
GET    /api/process/:id         # Get status
GET    /api/process/:id/result  # Get results
```

**Knowledge Base:**
```
GET    /api/knowledge           # List results
GET    /api/knowledge/:id       # Get result
DELETE /api/knowledge/:id       # Delete result
POST   /api/knowledge/:id/reprocess # Reprocess
```

## Database Schema

### Core Tables

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  name VARCHAR(255),
  created_at TIMESTAMP
);

-- Agents table
CREATE TABLE agents (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  name VARCHAR(255),
  description TEXT,
  icon VARCHAR(50),
  capabilities JSONB,
  is_public BOOLEAN DEFAULT false,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Prompts table
CREATE TABLE prompts (
  id UUID PRIMARY KEY,
  name VARCHAR(255),
  system_prompt TEXT,
  user_prompt_template TEXT,
  variables JSONB,
  version VARCHAR(50),
  parent_id UUID REFERENCES prompts(id),
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP
);

-- Agent prompts relationship
CREATE TABLE agent_prompts (
  agent_id UUID REFERENCES agents(id),
  prompt_id UUID REFERENCES prompts(id),
  task_type VARCHAR(50),
  PRIMARY KEY (agent_id, prompt_id, task_type)
);

-- Agent LLM configurations
CREATE TABLE agent_llm_configs (
  id UUID PRIMARY KEY,
  agent_id UUID REFERENCES agents(id),
  provider VARCHAR(50),
  model VARCHAR(100),
  is_primary BOOLEAN,
  parameters JSONB,
  task_types TEXT[]
);

-- Processing jobs
CREATE TABLE processing_jobs (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  agent_id UUID REFERENCES agents(id),
  input_type VARCHAR(50),
  input_data JSONB,
  status VARCHAR(50),
  result JSONB,
  created_at TIMESTAMP,
  completed_at TIMESTAMP
);

-- Knowledge base
CREATE TABLE knowledge_items (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  job_id UUID REFERENCES processing_jobs(id),
  title VARCHAR(255),
  content JSONB,
  metadata JSONB,
  created_at TIMESTAMP
);
```

## Mobile Considerations

- **Responsive breakpoints:** Mobile (<768px), Tablet (768-1024px), Desktop (>1024px)
- **Mobile navigation:** Bottom tab bar
- **Touch targets:** Minimum 44x44px
- **Simplified flows:** Fewer options on mobile
- **Offline support:** Cache recent results

## Accessibility Requirements

- **WCAG 2.1 AA compliance**
- **Keyboard navigation** for all interactions
- **Screen reader support** with proper ARIA labels
- **Color contrast** ratios meeting standards
- **Focus indicators** clearly visible

## Performance Targets

- **Initial load:** <3 seconds
- **Navigation:** <100ms between pages
- **API responses:** <500ms average
- **File upload:** Progress indication for large files
- **Real-time updates:** WebSocket for live status

## Security Considerations

- **Authentication:** JWT tokens with refresh
- **Authorization:** Role-based access control
- **API rate limiting:** Per user and global
- **File validation:** Type and size checks
- **Sanitization:** Input and output cleaning

## Next Steps

1. **Phase 1: Core UI Implementation** (Week 1-2)
   - Process Hub with agent selection
   - Basic Agent Studio (list/view)
   - Knowledge Base viewer

2. **Phase 2: Agent Management** (Week 3-4)
   - Agent creation/editing
   - Prompt configuration
   - LLM setup

3. **Phase 3: Advanced Features** (Week 5-6)
   - Prompt Builder
   - Data Sources (MCP ready)
   - Analytics dashboard

4. **Phase 4: Polish & Launch** (Week 7-8)
   - Mobile optimization
   - Performance tuning
   - User testing
   - Documentation

---

This comprehensive UI/UX scope provides the foundation for building a production-ready AIOS v2 console that supports agent creation, prompt management, multi-LLM configuration, and future MCP integrations.