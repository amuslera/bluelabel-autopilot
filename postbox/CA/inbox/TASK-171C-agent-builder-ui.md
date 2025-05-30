# TASK-171C: Custom Agent Builder UI

**Agent**: CA (Frontend Specialist)  
**Priority**: HIGH  
**Sprint**: Phase 6.17 - Production MVP Sprint 1  
**Working Directory**: `/Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2`

## Your Specialization Reminder
You are CA, the frontend specialist. You own ALL decisions related to UI/UX, React components, TypeScript interfaces, styling, and user interactions. Make design decisions autonomously - create the best user experience possible.

## Context
We're expanding the MVP-Lite to allow users to create their own custom agents. Users should be able to define agent name, description, capabilities, system prompts, and input/output configurations through an intuitive interface.

## Branch Setup (MANDATORY)
```bash
cd /Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2
git checkout main
git pull origin main
git checkout -b dev/TASK-171C-agent-builder-ui
```

## Acceptance Criteria
1. ✅ New page at `/agents/builder` with agent creation form
2. ✅ Multi-step form or single page with clear sections
3. ✅ Live preview of agent card as user fills form
4. ✅ System prompt configuration with syntax highlighting
5. ✅ Input/output type selection with validation
6. ✅ Save draft functionality (localStorage for now)
7. ✅ Publish flow with confirmation
8. ✅ Mobile responsive design

## UI Components to Build

### 1. Agent Builder Page (`/pages/agents/builder.tsx`)
Main page with form layout and preview panel:
- Left side: Form inputs (2/3 width on desktop)
- Right side: Live preview (1/3 width on desktop)
- Mobile: Stacked layout with preview at top

### 2. Form Sections

**Basic Information Section**
```typescript
interface AgentBasicInfo {
  name: string;          // Required, 3-50 chars
  category: string;      // Select from predefined list
  description: string;   // Required, 10-200 chars
  icon?: string;        // Optional icon selection
}
```
Categories: "Document Processing", "Data Analysis", "Content Generation", "Research", "Automation", "Custom"

**Capabilities Section**
```typescript
interface AgentCapabilities {
  capabilities: string[];  // Array of capability tags
  primaryCapability: string; // Main function
}
```
- Tag input component for adding capabilities
- Suggested tags based on category
- Max 5 capabilities

**System Prompt Configuration**
```typescript
interface AgentPromptConfig {
  systemPrompt: string;     // The main prompt
  examples?: string[];      // Optional usage examples
  constraints?: string[];   // Optional limitations
}
```
- Textarea with syntax highlighting
- Template variables: {{input}}, {{context}}
- Character count and best practices hints
- Example templates for common patterns

**Input/Output Configuration**
```typescript
interface AgentIOConfig {
  acceptedInputs: InputType[];  // file, url, text, audio
  outputFormat: OutputFormat;   // text, json, markdown, structured
  processingTime: 'fast' | 'normal' | 'slow';
  maxInputSize?: number;        // In MB for files
}
```

### 3. Components to Create

**AgentBuilderForm Component**
- Main form container with sections
- Form validation using react-hook-form
- Auto-save to localStorage every 30 seconds
- Progress indicator showing completion

**AgentPreview Component**
- Live preview of agent card
- Updates in real-time as form is filled
- Shows how agent will appear in marketplace
- "Test Agent" button (disabled for MVP)

**PromptEditor Component**
- Syntax highlighting for prompt text
- Variable autocomplete
- Common patterns dropdown
- Validation for required variables

**TagInput Component**
- Add/remove capability tags
- Autocomplete suggestions
- Keyboard navigation (Enter to add, Backspace to remove)
- Visual chips for selected tags

**IconPicker Component**
- Grid of predefined icons
- Search functionality
- Currently selected indicator
- Default to first icon in category

### 4. Form Behavior

**Validation Rules**
- Name: Required, 3-50 characters, alphanumeric + spaces
- Description: Required, 10-200 characters
- System Prompt: Required, minimum 50 characters
- At least one capability required
- At least one input type required

**Save & Publish Flow**
1. "Save Draft" - Saves to localStorage with timestamp
2. "Preview" - Shows full-screen preview of agent
3. "Publish" - Shows confirmation modal with:
   - Review of all settings
   - Terms acceptance checkbox
   - "Publish Agent" final button

**Draft Management**
- Auto-load latest draft on page load
- "Clear Form" button with confirmation
- "Load Template" dropdown with common agent types
- Draft indicator: "Draft saved 2 minutes ago"

### 5. Styling Requirements
- Consistent with existing MVP-Lite design
- Use existing color scheme and component library
- Form sections with clear visual separation
- Helpful tooltips on hover for complex fields
- Error states with clear messages
- Loading states during save/publish
- Success notifications using existing toast system

### 6. Mobile Responsiveness
- Single column layout on mobile
- Preview panel as collapsible accordion
- Larger touch targets for mobile
- Simplified icon picker on mobile
- Bottom sheet for publish confirmation

## Files to Create/Modify
- `/pages/agents/builder.tsx` - Main builder page
- `/components/agents/AgentBuilderForm.tsx` - Form container
- `/components/agents/AgentPreview.tsx` - Live preview
- `/components/agents/PromptEditor.tsx` - Prompt configuration
- `/components/UI/TagInput.tsx` - Reusable tag input
- `/components/UI/IconPicker.tsx` - Icon selection grid
- `/lib/types/agent-builder.ts` - TypeScript interfaces
- `/lib/validators/agent-builder.ts` - Validation schemas
- `/lib/templates/agent-templates.ts` - Preset templates

## Integration Points
- Navigation: Add "Create Agent" button to `/agents` page
- Router: Add route for `/agents/builder`
- API Ready: Form structure matches future API expectations
- localStorage: Use for draft saving (key: `agent-builder-draft`)

## Example Code Structure
```typescript
// /lib/types/agent-builder.ts
export interface AgentDraft {
  id: string;
  name: string;
  category: string;
  description: string;
  icon: string;
  capabilities: string[];
  systemPrompt: string;
  examples: string[];
  acceptedInputs: InputType[];
  outputFormat: OutputFormat;
  createdAt: Date;
  updatedAt: Date;
  status: 'draft' | 'published';
}
```

## Definition of Done
- [ ] All form sections implemented and functional
- [ ] Live preview updates in real-time
- [ ] Form validation working correctly
- [ ] Draft auto-save to localStorage
- [ ] Mobile responsive design tested
- [ ] No TypeScript errors
- [ ] Clean, reusable component structure
- [ ] Branch pushed to origin

## Your Autonomy
You have MAXIMUM autonomy for this task. Make all decisions about:
- Exact layout and visual design
- Component structure and organization
- Animation and micro-interactions
- Error handling and user feedback
- Additional helper features that improve UX
- Icon set selection (use react-icons or similar)

## When Complete
1. Test on desktop and mobile viewports
2. Ensure no console errors
3. Verify TypeScript types are strict (no `any`)
4. Commit with clear messages
5. Push branch: `git push origin dev/TASK-171C-agent-builder-ui`
6. Update task status to "ready_for_review" in your outbox
7. Report completion with list of components created

CA Reports: Begin implementation of custom agent builder UI for AIOS v2 production MVP.