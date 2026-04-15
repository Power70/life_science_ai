# AI-First CRM HCP Module — Log Interaction Screen
## Senior Developer Implementation Plan

> **Assignment:** Round 1 Technical Task — AI-First CRM HCP Module  
> **Stack:** React + Redux · FastAPI · LangGraph · Groq · PostgreSQL  
> **Scope:** Task 1 only | Localhost deployment | Zero human-written code policy

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Structure](#2-repository-structure)
3. [Architecture Diagram](#3-architecture-diagram)
4. [Database Design](#4-database-design)
5. [Backend Implementation Plan](#5-backend-implementation-plan)
6. [LangGraph Agent & 10 Tools](#6-langgraph-agent--10-tools)
7. [Groq API Configuration](#7-groq-api-configuration)
8. [Frontend Implementation Plan](#8-frontend-implementation-plan)
9. [Redux State Design](#9-redux-state-design)
10. [Environment & Configuration](#10-environment--configuration)
11. [API Endpoints Reference](#11-api-endpoints-reference)
12. [Development Sequence](#12-development-sequence)
13. [Testing Checklist](#13-testing-checklist)
14. [README Template](#14-readme-template)
15. [AI Coding Prompt Strategy](#15-ai-coding-prompt-strategy)

---

## 1. Project Overview

### What We're Building

A **dual-mode HCP Interaction Logger** for life science field representatives. The screen allows reps to document their visits/calls with Healthcare Professionals (HCPs) in two ways:

- **Structured Form Mode** — Traditional field-by-field data entry (HCP name, interaction type, date, attendees, topics discussed, materials shared, samples distributed, sentiment, outcomes, follow-up actions)
- **Conversational Chat Mode** — Natural language entry via an AI assistant panel. The rep describes the interaction in plain text; the LangGraph agent extracts structured data, summarizes it, and populates the form automatically.

### Business Context (Life Sciences)

Field reps visit doctors, pharmacists, and hospital administrators daily to detail pharmaceutical products. Logging these interactions is **regulatory and compliance-critical**. The AI layer reduces documentation time, improves data quality, and surfaces intelligent follow-up recommendations — making reps more effective in the field.

---

## 2. Repository Structure

```
hcp-crm/
├── README.md
├── .gitignore
├── docker-compose.yml              # Optional: for PostgreSQL local setup
│
├── backend/
│   ├── .env                        # Groq API key, DB URL, etc.
│   ├── requirements.txt
│   ├── main.py                     # FastAPI app entry point
│   ├── config.py                   # Settings (pydantic-settings)
│   ├── database.py                 # SQLAlchemy engine + session
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── hcp.py                  # HCP table model
│   │   ├── interaction.py          # Interaction table model
│   │   ├── material.py             # Materials/samples table model
│   │   └── followup.py             # Follow-up actions table model
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── hcp.py                  # Pydantic schemas for HCP
│   │   ├── interaction.py          # Pydantic schemas for Interaction
│   │   └── chat.py                 # Pydantic schemas for chat messages
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── hcp.py                  # /api/hcp routes
│   │   ├── interactions.py         # /api/interactions routes
│   │   └── agent.py                # /api/agent/chat route
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py                # LangGraph StateGraph definition
│   │   ├── state.py                # AgentState TypedDict
│   │   ├── nodes.py                # Graph nodes (router, tool_executor, responder)
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── log_interaction.py
│   │       ├── edit_interaction.py
│   │       ├── get_hcp_profile.py
│   │       ├── suggest_follow_up.py
│   │       ├── analyze_sentiment.py
│   │       ├── search_interactions.py
│   │       ├── distribute_sample.py
│   │       ├── share_material.py
│   │       ├── generate_call_summary.py
│   │       └── schedule_followup_meeting.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── groq_client.py          # Groq LLM wrapper
│       └── interaction_service.py  # Business logic layer
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    ├── .env
    │
    └── src/
        ├── main.jsx
        ├── App.jsx
        │
        ├── store/
        │   ├── index.js             # Redux store
        │   ├── slices/
        │   │   ├── interactionSlice.js
        │   │   ├── chatSlice.js
        │   │   └── hcpSlice.js
        │   └── middleware/
        │       └── apiMiddleware.js
        │
        ├── api/
        │   └── client.js            # Axios instance + all API calls
        │
        ├── components/
        │   ├── layout/
        │   │   ├── Header.jsx
        │   │   └── PageWrapper.jsx
        │   │
        │   ├── form/
        │   │   ├── LogInteractionForm.jsx   # Main form container
        │   │   ├── HCPSearch.jsx
        │   │   ├── InteractionTypeSelect.jsx
        │   │   ├── DateTimePicker.jsx
        │   │   ├── AttendeesInput.jsx
        │   │   ├── TopicsDiscussed.jsx
        │   │   ├── MaterialsShared.jsx
        │   │   ├── SamplesDistributed.jsx
        │   │   ├── SentimentSelector.jsx
        │   │   ├── OutcomesTextarea.jsx
        │   │   ├── FollowUpActions.jsx
        │   │   ├── AISuggestedFollowUps.jsx
        │   │   └── VoiceNoteStub.jsx        # Stubbed — UI only
        │   │
        │   └── chat/
        │       ├── AIAssistantPanel.jsx     # Right-side chat panel
        │       ├── ChatMessage.jsx
        │       ├── ChatInput.jsx
        │       └── ToolResultCard.jsx       # Shows tool execution results
        │
        └── pages/
            └── LogInteractionPage.jsx       # Main page — splits form + chat
```

---

## 3. Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     BROWSER (React)                     │
│                                                         │
│  ┌──────────────────────┐  ┌───────────────────────┐   │
│  │   Structured Form    │  │   AI Assistant Chat   │   │
│  │   (Redux-controlled) │  │   Panel (right side)  │   │
│  └──────────┬───────────┘  └───────────┬───────────┘   │
│             │                          │                │
│             └──────────┬───────────────┘                │
│                        │ Axios HTTP                     │
└────────────────────────┼────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                  FastAPI Backend                         │
│                                                         │
│  POST /api/interactions        → CRUD routes            │
│  GET  /api/hcp/search          → HCP lookup             │
│  POST /api/agent/chat          → LangGraph invocation   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │              LangGraph Agent                     │   │
│  │                                                  │   │
│  │  [user_message] → [router_node]                  │   │
│  │       ↓                                          │   │
│  │  [tool_executor_node] ←──── Tool Selection       │   │
│  │       ↓                                          │   │
│  │  [responder_node] → structured JSON response     │   │
│  │                                                  │   │
│  │  Tools: log · edit · profile · sentiment ·       │   │
│  │         search · sample · material · summary ·   │   │
│  │         followup · schedule                      │   │
│  └──────────────────────┬───────────────────────────┘   │
│                         │                               │
│  ┌──────────────────────▼───────────────────────────┐   │
│  │              Groq API Client                     │   │
│  │  Model: gemma2-9b-it (primary)                   │   │
│  │  Model: llama-3.3-70b-versatile (fallback/ctx)   │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │ SQLAlchemy ORM
┌────────────────────────▼────────────────────────────────┐
│                   PostgreSQL                            │
│  Tables: hcps · interactions · materials ·              │
│          samples · followup_actions                     │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Database Design

### 4.1 Tables

#### `hcps` — Healthcare Professionals
```sql
CREATE TABLE hcps (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name       VARCHAR(255) NOT NULL,
    specialty       VARCHAR(100),
    institution     VARCHAR(255),
    email           VARCHAR(255),
    phone           VARCHAR(50),
    territory       VARCHAR(100),
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);
```

#### `interactions` — Core interaction log
```sql
CREATE TABLE interactions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hcp_id              UUID REFERENCES hcps(id) ON DELETE CASCADE,
    interaction_type    VARCHAR(50) NOT NULL,  -- Meeting, Call, Email, Event
    interaction_date    DATE NOT NULL,
    interaction_time    TIME,
    attendees           TEXT[],               -- Array of names
    topics_discussed    TEXT,
    ai_summary          TEXT,                 -- LLM-generated summary
    sentiment           VARCHAR(20),          -- Positive | Neutral | Negative
    sentiment_score     FLOAT,               -- -1.0 to 1.0
    outcomes            TEXT,
    raw_chat_input      TEXT,                 -- Original conversational input
    logged_via          VARCHAR(20),          -- 'form' | 'chat'
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);
```

#### `materials_shared`
```sql
CREATE TABLE materials_shared (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interaction_id  UUID REFERENCES interactions(id) ON DELETE CASCADE,
    material_name   VARCHAR(255) NOT NULL,
    material_type   VARCHAR(100),            -- Brochure, Study, PDF, etc.
    quantity        INT DEFAULT 1,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

#### `samples_distributed`
```sql
CREATE TABLE samples_distributed (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interaction_id  UUID REFERENCES interactions(id) ON DELETE CASCADE,
    product_name    VARCHAR(255) NOT NULL,
    dosage          VARCHAR(100),
    quantity        INT NOT NULL,
    lot_number      VARCHAR(100),
    created_at      TIMESTAMP DEFAULT NOW()
);
```

#### `followup_actions`
```sql
CREATE TABLE followup_actions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interaction_id  UUID REFERENCES interactions(id) ON DELETE CASCADE,
    action_text     TEXT NOT NULL,
    due_date        DATE,
    status          VARCHAR(20) DEFAULT 'pending',  -- pending | done | cancelled
    source          VARCHAR(20) DEFAULT 'ai',       -- 'ai' | 'manual'
    created_at      TIMESTAMP DEFAULT NOW()
);
```

#### `chat_messages` — Persist chat history per session
```sql
CREATE TABLE chat_messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      VARCHAR(255) NOT NULL,
    role            VARCHAR(20) NOT NULL,    -- 'user' | 'assistant'
    content         TEXT NOT NULL,
    tool_used       VARCHAR(100),            -- Which LangGraph tool was called
    tool_result     JSONB,                   -- Structured result from tool
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### 4.2 SQLAlchemy Setup (`database.py`)
```python
# Prompt for AI:
# "Create a SQLAlchemy async engine using asyncpg for PostgreSQL.
#  Include a get_db dependency for FastAPI. Use pydantic-settings
#  to load DATABASE_URL from .env. Include Base = declarative_base()."
```

---

## 5. Backend Implementation Plan

### 5.1 Dependencies (`requirements.txt`)
```
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy[asyncio]==2.0.30
asyncpg==0.29.0
alembic==1.13.1
pydantic==2.7.1
pydantic-settings==2.2.1
python-dotenv==1.0.1
groq==0.9.0
langgraph==0.1.19
langchain-core==0.2.5
langchain-groq==0.1.5
httpx==0.27.0
python-multipart==0.0.9
```

### 5.2 FastAPI App Entry (`main.py`)

```
# AI Prompt:
# "Create a FastAPI application with:
# - CORS middleware allowing http://localhost:5173
# - Lifespan context manager for DB init (create_all tables)
# - Include routers: hcp, interactions, agent
# - All routes prefixed with /api
# - Health check at GET /health"
```

### 5.3 Groq Client (`services/groq_client.py`)

```
# AI Prompt:
# "Create a Groq client wrapper using the official groq Python SDK.
# - Primary model: gemma2-9b-it
# - Fallback model: llama-3.3-70b-versatile (for long-context summarization)
# - Implement: get_completion(messages, model=None, temperature=0.3, max_tokens=1024)
# - Implement: get_structured_output(prompt, output_schema_description) that
#   instructs the model to return only JSON matching the schema
# - Load GROQ_API_KEY from environment"
```

**Critical note on Groq API Key setup:**
1. Go to https://console.groq.com
2. Sign up / log in → navigate to **API Keys**
3. Click **Create API Key** → name it `hcp-crm-dev`
4. Copy key → add to `backend/.env` as `GROQ_API_KEY=gsk_...`
5. The Groq Python SDK reads this automatically via `os.environ`

### 5.4 Router: Interactions (`routers/interactions.py`)

```
# AI Prompt:
# "Create a FastAPI router for /interactions with:
# - POST /interactions — create new interaction (with nested materials/samples/followups)
# - GET /interactions — list all interactions with optional hcp_id filter
# - GET /interactions/{id} — get single interaction with all relations
# - PUT /interactions/{id} — update interaction fields
# - DELETE /interactions/{id} — soft delete
# Use async SQLAlchemy. Return Pydantic response models."
```

### 5.5 Router: HCP Search (`routers/hcp.py`)

```
# AI Prompt:
# "Create FastAPI router for /hcp:
# - GET /hcp/search?q=<name> — fuzzy search HCPs by name (ILIKE)
# - GET /hcp/{id} — full HCP profile with last 5 interactions
# - POST /hcp — create new HCP
# Return paginated results for search."
```

### 5.6 Router: Agent Chat (`routers/agent.py`)

```
# AI Prompt:
# "Create FastAPI router for /agent:
# - POST /agent/chat — accepts {session_id, message, context: {current_form_state}}
# - Invokes the LangGraph agent with the message + form context
# - Persists user message and assistant response to chat_messages table
# - Returns {response: str, tool_used: str, tool_result: dict, form_updates: dict}
# The form_updates dict allows the frontend to auto-populate form fields."
```

---

## 6. LangGraph Agent & 10 Tools

### 6.1 Agent State (`agent/state.py`)

```python
# AI Prompt:
# "Define a TypedDict called AgentState with these fields:
# - messages: list of LangChain BaseMessages (conversation history)
# - current_tool: Optional[str] — which tool is being called
# - tool_result: Optional[dict] — result from last tool execution
# - form_updates: Optional[dict] — fields to push back to frontend form
# - session_id: str
# - context: dict — contains current form state passed from frontend"
```

### 6.2 Graph Definition (`agent/graph.py`)

```
# AI Prompt:
# "Build a LangGraph StateGraph with these nodes:
# 1. router_node — uses gemma2-9b-it to decide which tool to call based on user message
# 2. tool_executor_node — executes the selected tool function
# 3. responder_node — formats the tool result into a natural language response
#
# Edges:
# - START → router_node
# - router_node → tool_executor_node (conditional, if tool needed)
# - router_node → responder_node (direct, if no tool needed)
# - tool_executor_node → responder_node
# - responder_node → END
#
# Bind all 10 tools to the LLM using bind_tools()
# Use GroqChat (langchain-groq) as the LLM"
```

### 6.3 The 10 LangGraph Tools

---

#### Tool 1: `log_interaction` *(Mandatory)*
**File:** `agent/tools/log_interaction.py`

**Purpose:** Captures a full interaction from natural language input. Uses the LLM to extract structured data (HCP name, date, sentiment, topics, outcomes) and persists it to the database.

```
# AI Prompt:
# "Create a LangGraph tool called 'log_interaction'.
# Input: raw_text (the rep's description of the meeting), session_id, optional hcp_id
#
# Steps:
# 1. Send raw_text to gemma2-9b-it with a prompt that extracts:
#    {hcp_name, interaction_type, date, topics_discussed, sentiment,
#     materials_mentioned, samples_mentioned, outcomes, follow_up_actions}
#    — return as JSON only
# 2. Fuzzy-match hcp_name against hcps table
# 3. Create new interaction record in DB
# 4. Create related materials, samples, followup_actions records
# 5. Return: {interaction_id, ai_summary, extracted_fields, form_updates}
#    where form_updates is a dict the frontend uses to populate all form fields
#
# Use @tool decorator from langchain_core.tools"
```

**Example trigger phrases:** *"Log my meeting with Dr. Adeyemi this morning"*, *"I just visited Dr. Chukwu and discussed OncoBoost Phase III"*

---

#### Tool 2: `edit_interaction` *(Mandatory)*
**File:** `agent/tools/edit_interaction.py`

**Purpose:** Allows the rep to modify a previously logged interaction via natural language. Parses which fields to change and updates the DB record.

```
# AI Prompt:
# "Create a LangGraph tool called 'edit_interaction'.
# Input: interaction_id (UUID), change_request (natural language), session_id
#
# Steps:
# 1. Fetch existing interaction from DB by interaction_id
# 2. Send [existing_data + change_request] to LLM with prompt:
#    'Given the current interaction data and the change request, return only
#     a JSON object with the fields that need to be updated.'
# 3. Validate the diff — only allow updating known fields
# 4. Apply updates to DB
# 5. Return: {updated_fields, updated_interaction, form_updates}
#
# Example: 'Change the sentiment to Positive and add a follow-up for next Friday'"
```

---

#### Tool 3: `get_hcp_profile`
**File:** `agent/tools/get_hcp_profile.py`

**Purpose:** Retrieves a full HCP profile with interaction history, enabling the rep to get context before or during a visit.

```
# AI Prompt:
# "Create a LangGraph tool called 'get_hcp_profile'.
# Input: hcp_name or hcp_id
#
# Steps:
# 1. Search hcps table (ILIKE on full_name if name given, direct lookup if ID)
# 2. Fetch last 10 interactions for this HCP
# 3. Ask LLM to generate a brief 'relationship summary':
#    key topics discussed, overall sentiment trend, pending follow-ups
# 4. Return: {hcp, interaction_count, last_interaction_date,
#             sentiment_trend, relationship_summary, pending_followups}
#
# Frontend displays this in a profile card in the chat panel."
```

---

#### Tool 4: `suggest_follow_up`
**File:** `agent/tools/suggest_follow_up.py`

**Purpose:** Analyzes the current interaction context and generates intelligent, personalized follow-up action recommendations.

```
# AI Prompt:
# "Create a LangGraph tool called 'suggest_follow_up'.
# Input: interaction_id or current context dict (topics, outcomes, sentiment, hcp_specialty)
#
# Steps:
# 1. Fetch interaction data (or use context dict if not yet saved)
# 2. Fetch HCP's last 3 interactions for additional context
# 3. Send all context to llama-3.3-70b-versatile (better for reasoning):
#    Prompt: 'As a pharma field rep assistant, suggest 3 specific, actionable
#    follow-up actions for this HCP interaction. Be concise and sales-relevant.'
# 4. Parse LLM response into [{action, rationale, suggested_due_date}]
# 5. Return list of suggestions + save them to followup_actions with source='ai'
#
# This populates the 'AI Suggested Follow-ups' section in the UI."
```

---

#### Tool 5: `analyze_sentiment`
**File:** `agent/tools/analyze_sentiment.py`

**Purpose:** Performs deep sentiment analysis on the interaction description, going beyond simple Positive/Neutral/Negative to surface nuanced signals.

```
# AI Prompt:
# "Create a LangGraph tool called 'analyze_sentiment'.
# Input: text (topics discussed, outcomes, rep's description)
#
# Steps:
# 1. Send text to gemma2-9b-it with prompt:
#    'Analyze the sentiment of this HCP interaction from a pharma sales perspective.
#     Return JSON with:
#     {overall_sentiment: Positive|Neutral|Negative,
#      confidence_score: 0.0-1.0,
#      sentiment_signals: [list of specific phrases driving sentiment],
#      hcp_engagement_level: High|Medium|Low,
#      concern_flags: [any objections or concerns raised],
#      opportunity_signals: [any buying signals or interest expressed]}'
# 2. Update interaction record with sentiment + sentiment_score
# 3. Return the full analysis object
#
# Frontend updates the sentiment radio buttons and shows analysis in chat."
```

---

#### Tool 6: `search_interactions`
**File:** `agent/tools/search_interactions.py`

**Purpose:** Semantic and keyword search across all logged interactions, enabling reps to find past meetings, topics, or outcomes quickly.

```
# AI Prompt:
# "Create a LangGraph tool called 'search_interactions'.
# Input: query (natural language search), filters: {hcp_name, date_from, date_to,
#        interaction_type, sentiment}
#
# Steps:
# 1. Use LLM to extract structured search intent from natural language query:
#    e.g., 'meetings with Dr. Okonkwo about OncoBoost last month'
#    → {hcp_name: 'Okonkwo', topic_keyword: 'OncoBoost', date_from: ..., date_to: ...}
# 2. Build dynamic SQL query with ILIKE on topics_discussed + ai_summary
# 3. Return: {results: [{interaction_id, hcp_name, date, summary, sentiment}],
#             total_count, search_interpretation}
# 4. search_interpretation is the LLM's understanding of the query (show in chat)"
```

---

#### Tool 7: `distribute_sample`
**File:** `agent/tools/distribute_sample.py`

**Purpose:** Logs pharmaceutical sample distribution to an HCP, capturing product, dosage, quantity, and lot number — critical for regulatory compliance.

```
# AI Prompt:
# "Create a LangGraph tool called 'distribute_sample'.
# Input: interaction_id, sample_details (natural language or structured)
#
# Steps:
# 1. If natural language input, use LLM to extract:
#    {product_name, dosage, quantity, lot_number}
#    e.g., 'dropped off 5 boxes of OncoBoost 50mg lot #OB2025' →
#    {product_name: 'OncoBoost', dosage: '50mg', quantity: 5, lot_number: 'OB2025'}
# 2. Insert record into samples_distributed table linked to interaction
# 3. Return: {sample_id, extracted_data, confirmation_message}
# 4. Update form_updates to refresh the Samples Distributed section in UI"
```

---

#### Tool 8: `share_material`
**File:** `agent/tools/share_material.py`

**Purpose:** Logs marketing materials, clinical studies, or product brochures shared with an HCP during an interaction.

```
# AI Prompt:
# "Create a LangGraph tool called 'share_material'.
# Input: interaction_id, material_description (natural language)
#
# Steps:
# 1. Use LLM to extract material details from description:
#    {material_name, material_type (Brochure|Study|PDF|Flyer|Poster), quantity}
# 2. Insert into materials_shared table linked to interaction
# 3. Check if any previously shared materials to this HCP are similar
#    (to avoid repetition) — query DB, flag if duplicate
# 4. Return: {material_id, extracted_data, duplicate_warning (if any),
#             total_materials_this_interaction}"
```

---

#### Tool 9: `generate_call_summary`
**File:** `agent/tools/generate_call_summary.py`

**Purpose:** Generates a comprehensive, professional call report from all interaction data. Uses llama-3.3-70b-versatile for richer, longer-form generation.

```
# AI Prompt:
# "Create a LangGraph tool called 'generate_call_summary'.
# Input: interaction_id
#
# Steps:
# 1. Fetch complete interaction with all relations (materials, samples, followups)
# 2. Fetch HCP profile + last 2 interactions for context
# 3. Send all data to llama-3.3-70b-versatile with prompt:
#    'Generate a professional pharma field rep call report. Include:
#     - Executive Summary (2-3 sentences)
#     - Key Discussion Points
#     - HCP Sentiment & Engagement Analysis
#     - Materials & Samples Provided
#     - Action Items & Next Steps
#     - Risk Flags (any objections, concerns, or compliance notes)
#     Format as clean plain text, appropriate for CRM filing.'
# 4. Save summary to interactions.ai_summary field
# 5. Return: {summary_text, word_count, key_highlights: [list of bullet points]}"
```

---

#### Tool 10: `schedule_followup_meeting`
**File:** `agent/tools/schedule_followup_meeting.py`

**Purpose:** Creates a structured follow-up action item with a specific date, extracted from natural language, and saves it as a trackable task.

```
# AI Prompt:
# "Create a LangGraph tool called 'schedule_followup_meeting'.
# Input: interaction_id, scheduling_request (natural language)
#
# Steps:
# 1. Use LLM to parse date/time from natural language:
#    'schedule a follow-up with Dr. Adeyemi in 2 weeks' →
#    {action: 'Follow-up meeting with Dr. Adeyemi', due_date: <today + 14 days>}
#    'Call her next Monday to discuss the Phase III results' →
#    {action: 'Call re: Phase III results', due_date: <next Monday>}
# 2. Use Python's datetime for date arithmetic — do NOT let LLM guess actual dates
# 3. Insert into followup_actions table with source='ai', status='pending'
# 4. Return: {followup_id, action, due_date, confirmation_message}
# 5. Update form_updates to add item to Follow-up Actions section"
```

---

### 6.4 Tool Registration Summary

```python
# In agent/graph.py — all tools registered to LLM:
ALL_TOOLS = [
    log_interaction,
    edit_interaction,
    get_hcp_profile,
    suggest_follow_up,
    analyze_sentiment,
    search_interactions,
    distribute_sample,
    share_material,
    generate_call_summary,
    schedule_followup_meeting,
]

llm_with_tools = ChatGroq(
    model="gemma2-9b-it",
    api_key=settings.GROQ_API_KEY,
    temperature=0.3,
).bind_tools(ALL_TOOLS)
```

---

## 7. Groq API Configuration

### 7.1 Getting Your API Key (Step-by-Step)

1. Navigate to [https://console.groq.com](https://console.groq.com)
2. Sign up with Google or email
3. Go to **API Keys** section in the left sidebar
4. Click **+ Create API Key**
5. Name: `hcp-crm-dev` → Click **Submit**
6. **Copy the key immediately** (shown only once)
7. Add to `backend/.env`:
   ```
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### 7.2 Model Selection Strategy

| Model | Use Case | Why |
|-------|----------|-----|
| `gemma2-9b-it` | Primary: routing, entity extraction, sentiment, short generations | Fast, instruction-following, low latency — ideal for interactive chat |
| `llama-3.3-70b-versatile` | Complex: call summaries, relationship analysis, long-form context | Better reasoning on complex multi-part tasks |

### 7.3 Groq Client Implementation

```python
# services/groq_client.py
# AI Prompt:
# "Create a singleton GroqService class:
# - __init__ reads GROQ_API_KEY from settings
# - async get_completion(messages: list, model: str = 'gemma2-9b-it',
#                        temperature: float = 0.3, max_tokens: int = 1024)
# - async get_json_output(prompt: str, schema_description: str) -> dict:
#     Appends 'Respond ONLY with valid JSON, no markdown, no explanation'
#     Parses and returns the JSON, raises ValueError on parse failure
# - Implement retry logic: 3 attempts with exponential backoff on rate limit errors
# - Log all requests with model used and token count to stdout"
```

### 7.4 LangChain-Groq Integration

```python
# In agent/graph.py
from langchain_groq import ChatGroq

primary_llm = ChatGroq(
    model_name="gemma2-9b-it",
    groq_api_key=settings.GROQ_API_KEY,
    temperature=0.3,
    max_tokens=1024,
    streaming=False,
)

context_llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    groq_api_key=settings.GROQ_API_KEY,
    temperature=0.4,
    max_tokens=2048,
)
```

---

## 8. Frontend Implementation Plan

### 8.1 Tech Setup

```bash
# Setup commands (AI generates, human runs):
npm create vite@latest frontend -- --template react
cd frontend
npm install redux @reduxjs/toolkit react-redux axios
npm install react-hook-form @hookform/resolvers
npm install date-fns
npm install lucide-react
```

### 8.2 Design Specification

**Visual Design (strictly following the PDF mockup):**
- **Font:** Google Inter (all weights: 300, 400, 500, 600, 700)
- **Layout:** Two-column — Left: form (≈60%), Right: AI chat panel (≈40%)
- **Color palette:**
  - Background: `#F8F9FA` (light gray page background)
  - Card/Panel: `#FFFFFF`
  - Primary accent: `#2563EB` (blue — buttons, active states)
  - Border: `#E5E7EB`
  - Text primary: `#111827`
  - Text secondary: `#6B7280`
  - Sentiment Positive: `#10B981`, Neutral: `#6B7280`, Negative: `#EF4444`
  - AI badge: gradient `#2563EB → #7C3AED`

```css
/* Import in index.html */
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

/* Root variables */
:root {
  --font-primary: 'Inter', sans-serif;
  --color-primary: #2563EB;
  --color-bg: #F8F9FA;
  --color-surface: #FFFFFF;
  --color-border: #E5E7EB;
  --color-text: #111827;
  --color-text-muted: #6B7280;
  --radius-md: 8px;
  --radius-lg: 12px;
  --shadow-card: 0 1px 3px rgba(0,0,0,0.1);
}
```

### 8.3 Page Layout (`LogInteractionPage.jsx`)

```
# AI Prompt:
# "Build LogInteractionPage with:
# - Full-height layout, no scroll on outer container
# - Header: 'Log HCP Interaction' title + breadcrumb
# - Two-column grid: form column (flex:3) + chat column (flex:2)
# - Both columns independently scrollable
# - Sticky header, sticky chat input at bottom of chat panel
# - Responsive: stack columns vertically on mobile (<768px)
# - Use Google Inter font via CSS variable --font-primary"
```

### 8.4 Form Components

#### `LogInteractionForm.jsx`
```
# AI Prompt:
# "Build the main form with sections matching the PDF mockup exactly:
# 1. HCP Name (searchable dropdown — calls GET /api/hcp/search?q=)
# 2. Interaction Type (dropdown: Meeting, Call, Email, Conference, Event)
# 3. Date (date picker, default today) + Time (time input, default now)
# 4. Attendees (tag input — type name, press Enter to add)
# 5. Topics Discussed (textarea, 4 rows, with mic icon stub)
# 6. Voice Note stub button (UI only, shows 'Coming Soon' toast on click)
# 7. Materials Shared (search/add interface with list below)
# 8. Samples Distributed (add button → modal with product/dosage/qty fields)
# 9. Sentiment (radio group: Positive ● Neutral ○ Negative — with color coding)
# 10. Outcomes (textarea)
# 11. Follow-up Actions (textarea)
# 12. AI Suggested Follow-ups (read-only list, populated by agent)
# 13. Submit button: 'Log Interaction' (calls POST /api/interactions)
# 
# Form uses react-hook-form. All fields connected to Redux interactionSlice.
# Form auto-populates when Redux state gets form_updates from chat agent."
```

#### `AIAssistantPanel.jsx`
```
# AI Prompt:
# "Build the right-panel AI chat assistant:
# - Header: '🤖 AI Assistant' with subtitle 'Log interaction via chat'
# - Instructional placeholder text (matching PDF mockup example)
# - Scrollable message list (auto-scroll to bottom on new message)
# - Each message: avatar + bubble (user=right/blue, assistant=left/gray)
# - Tool result cards: when a tool runs, show a compact card with:
#   tool name badge, key result data, and 'Form Updated ✓' indicator if applicable
# - Bottom input bar: textarea (Enter=send, Shift+Enter=newline) + Log button
# - Loading state: animated typing indicator (three dots)
# - On send: POST /api/agent/chat with {session_id, message, context: formState}
# - On response: dispatch form_updates to Redux → form auto-populates"
```

### 8.5 Key UX Behaviors

1. **Bidirectional sync:** When the agent returns `form_updates`, Redux dispatches `updateFormFields(form_updates)` which instantly populates the structured form. The rep sees the form fill itself in real-time.

2. **Session management:** Generate a `session_id` (UUID) on page load, stored in component state. Sent with every chat message to maintain conversation context.

3. **Tool transparency:** Each assistant message shows which tool was used (e.g., `🔧 log_interaction`) so the rep understands what the AI is doing.

4. **Dual submission path:**
   - Chat → agent fills form → rep reviews → clicks "Log Interaction" (submits full form)
   - OR agent auto-submits via `log_interaction` tool → shows confirmation in chat

---

## 9. Redux State Design

### 9.1 Store Structure

```javascript
// store/index.js
{
  interaction: {
    // All form fields
    hcp: null,                    // {id, full_name, specialty, institution}
    interactionType: 'Meeting',
    date: 'YYYY-MM-DD',
    time: 'HH:MM',
    attendees: [],
    topicsDiscussed: '',
    materialsShared: [],
    samplesDistributed: [],
    sentiment: 'Neutral',
    outcomes: '',
    followUpActions: '',
    aiSuggestedFollowUps: [],     // From suggest_follow_up tool
    loggedVia: 'form',            // 'form' | 'chat'
    savedInteractionId: null,
    isSaving: false,
    saveError: null,
  },
  chat: {
    messages: [],                 // [{id, role, content, toolUsed, toolResult, timestamp}]
    isLoading: false,
    sessionId: null,              // UUID generated on mount
    error: null,
  },
  hcp: {
    searchResults: [],
    isSearching: false,
    selectedProfile: null,
  }
}
```

### 9.2 Key Actions

```
# AI Prompt:
# "Create interactionSlice with reducers:
# - setField(state, {payload: {field, value}}) — update any single field
# - updateFormFields(state, {payload: formUpdates}) — batch update from agent
# - resetForm(state) — clear all fields to initial state
# - setSaving / setSaveError / setSavedId
#
# Create chatSlice with:
# - addMessage(state, {payload: message})
# - setLoading(state, {payload: bool})
# - initSession(state) — generate UUID for sessionId
# - updateLastMessageToolResult(state, {payload: toolResult})
#
# Use createAsyncThunk for:
# - submitInteraction — POST /api/interactions
# - sendChatMessage — POST /api/agent/chat, then dispatch updateFormFields"
```

---

## 10. Environment & Configuration

### `backend/.env`
```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/hcp_crm

# Groq
GROQ_API_KEY=gsk_your_key_here

# App
APP_ENV=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173
```

### `frontend/.env`
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_TITLE=HCP CRM
```

### `backend/config.py`
```python
# AI Prompt:
# "Create Settings class using pydantic-settings BaseSettings.
# Load all env vars. Add computed property db_url that strips +asyncpg
# for sync Alembic migrations. Include model_config with env_file='.env'"
```

---

## 11. API Endpoints Reference

| Method | Endpoint | Description | Tool Used |
|--------|----------|-------------|-----------|
| `POST` | `/api/interactions` | Create new interaction | Direct form submit |
| `GET` | `/api/interactions` | List interactions (with filters) | `search_interactions` |
| `GET` | `/api/interactions/{id}` | Get single interaction | `get_hcp_profile` |
| `PUT` | `/api/interactions/{id}` | Update interaction | `edit_interaction` |
| `GET` | `/api/hcp/search` | Search HCPs by name | `get_hcp_profile` |
| `GET` | `/api/hcp/{id}` | Get HCP profile + history | `get_hcp_profile` |
| `POST` | `/api/hcp` | Create new HCP | — |
| `POST` | `/api/agent/chat` | Send message to LangGraph agent | All tools |

---

## 12. Development Sequence

Follow this exact order to avoid blockers:

### Phase 1: Foundation (Day 1)
- [ ] Initialize Git repo, create folder structure
- [ ] Set up PostgreSQL locally (`createdb hcp_crm`)
- [ ] Get Groq API key, test with `curl`
- [ ] Backend: `config.py` → `database.py` → all SQLAlchemy models
- [ ] Run Alembic migrations: `alembic init`, generate first migration, `alembic upgrade head`
- [ ] Seed 5–10 sample HCPs into DB

### Phase 2: Backend Core (Day 2)
- [ ] `groq_client.py` — test with standalone script
- [ ] FastAPI `main.py` with health check
- [ ] HCP router — test `/api/hcp/search` with Postman
- [ ] Interactions router — test CRUD with Postman
- [ ] Seed 3–4 sample interactions with known HCPs

### Phase 3: LangGraph Agent (Day 2–3)
- [ ] `state.py` and `nodes.py`
- [ ] Implement `log_interaction` tool — test in isolation
- [ ] Implement `edit_interaction` tool — test in isolation
- [ ] Implement remaining 8 tools
- [ ] Build `graph.py` — wire all nodes and edges
- [ ] `agent.py` router — test `/api/agent/chat` with Postman
- [ ] Verify each tool is callable via agent

### Phase 4: Frontend (Day 3–4)
- [ ] Vite setup + dependencies
- [ ] Redux store: all 3 slices
- [ ] API client (`client.js`)
- [ ] `LogInteractionPage.jsx` layout (no logic yet)
- [ ] All form field components
- [ ] `AIAssistantPanel.jsx`
- [ ] Wire Redux → form auto-population
- [ ] Wire chat → API → form updates

### Phase 5: Integration & Polish (Day 4–5)
- [ ] End-to-end test: type in chat → form fills → submit → DB record
- [ ] Test all 10 tools via chat interface
- [ ] Add loading states, error handling, success toasts
- [ ] Match UI exactly to PDF mockup design
- [ ] README.md
- [ ] GitHub push

### Phase 6: Recording (Day 5)
- [ ] Record 10–15 min video
- [ ] Demonstrate all 5 required tool demos (pick best 5 from 10)
- [ ] Walk through code architecture
- [ ] Submit GitHub URL + video via Google Form

---

## 13. Testing Checklist

### Backend Tests
```bash
# Health check
curl http://localhost:8000/health

# Create HCP
curl -X POST http://localhost:8000/api/hcp \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Dr. Emeka Okonkwo", "specialty": "Oncology"}'

# Test agent — log_interaction tool
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-001",
    "message": "Log my meeting with Dr. Okonkwo today. We discussed OncoBoost Phase III trials. He was very positive and interested. I left a brochure and 3 samples.",
    "context": {}
  }'
```

### Chat Trigger Phrases for Each Tool

| Tool | Test Phrase |
|------|-------------|
| `log_interaction` | *"Log my meeting with Dr. Adeyemi this morning about OncoBoost"* |
| `edit_interaction` | *"Change the sentiment of the last interaction to Positive"* |
| `get_hcp_profile` | *"Show me Dr. Okonkwo's profile and recent visits"* |
| `suggest_follow_up` | *"What follow-ups should I do after this meeting?"* |
| `analyze_sentiment` | *"Analyze the sentiment of this interaction"* |
| `search_interactions` | *"Find all meetings about OncoBoost last month"* |
| `distribute_sample` | *"Add 5 boxes of OncoBoost 50mg lot OB2025 to this interaction"* |
| `share_material` | *"I shared the Phase III clinical study brochure with the doctor"* |
| `generate_call_summary` | *"Generate a full call report for this interaction"* |
| `schedule_followup_meeting` | *"Schedule a follow-up call with Dr. Adeyemi in 2 weeks"* |

---

## 14. README Template

```markdown
# HCP CRM — AI-First Log Interaction Module

An AI-powered CRM screen for life science field representatives to log
HCP interactions via structured form or conversational AI chat.

## Tech Stack
- **Frontend:** React 18, Redux Toolkit, Vite
- **Backend:** Python 3.11, FastAPI
- **AI Agent:** LangGraph + LangChain-Groq
- **LLM:** Groq API (gemma2-9b-it, llama-3.3-70b-versatile)
- **Database:** PostgreSQL 15

## Setup

### Prerequisites
- Node.js 20+
- Python 3.11+
- PostgreSQL 15 running locally
- Groq API key (console.groq.com)

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Add GROQ_API_KEY and DATABASE_URL
alembic upgrade head
python seed.py         # Seed sample HCPs
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev            # Runs on http://localhost:5173
```

## LangGraph Tools
1. `log_interaction` — Natural language → structured interaction record
2. `edit_interaction` — Modify logged data via chat
3. `get_hcp_profile` — HCP profile + interaction history
4. `suggest_follow_up` — AI-generated follow-up recommendations
5. `analyze_sentiment` — Deep sentiment analysis
6. `search_interactions` — Semantic interaction search
7. `distribute_sample` — Log sample distribution
8. `share_material` — Track shared materials
9. `generate_call_summary` — Full professional call report
10. `schedule_followup_meeting` — Natural language meeting scheduling

## Architecture
See IMPLEMENTATION_PLAN.md for full architecture diagram and design decisions.
```

---

## 15. AI Coding Prompt Strategy

Since the task requires **zero human-written code**, use these strategies when prompting Gemini 2.5 Pro or ChatGPT:

### Prompting Principles

1. **Be maximally specific** — Include exact file paths, function signatures, return types, DB table names, and model names in every prompt.

2. **One file per prompt** — Don't ask for the whole backend at once. Ask for `database.py`, verify it, then ask for `models/interaction.py`, etc.

3. **Include context** — Always paste the relevant existing code (e.g., paste `state.py` when asking for `graph.py`).

4. **Specify error handling** — Always append: *"Include comprehensive error handling, log errors to stdout, and return meaningful HTTP error responses."*

5. **Groq-specific prompt** — When asking for LLM calls, always specify:
   - Model name (`gemma2-9b-it`)
   - That the response must be JSON-only for structured outputs
   - Temperature and max_tokens values

### Example Prompt Template

```
Context: I'm building an AI-first CRM HCP module using FastAPI, LangGraph, 
Groq (gemma2-9b-it), and PostgreSQL with async SQLAlchemy.

File to generate: backend/agent/tools/log_interaction.py

Requirements:
- LangGraph @tool decorated function
- Takes: raw_text: str, session_id: str, hcp_id: Optional[str]
- Calls gemma2-9b-it via langchain_groq.ChatGroq to extract:
  {hcp_name, interaction_type, date, topics, sentiment, materials, samples, outcomes, follow_ups}
  — JSON only response
- Fuzzy matches hcp_name against hcps PostgreSQL table (ILIKE)
- Creates interaction + related records using async SQLAlchemy
- Returns: {interaction_id, ai_summary, extracted_fields, form_updates}
- Include full error handling and docstrings

Existing code for reference:
[paste agent/state.py here]
[paste database.py here]
[paste models/interaction.py here]
```

---

*This implementation plan covers every component needed to build, demo, and submit Task 1 at senior developer quality. Follow the Development Sequence in order, use the AI Prompt Strategy for code generation, and refer to the Testing Checklist before recording your video.*
