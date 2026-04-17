# AI-First CRM HCP Module

Production-style reference implementation of a dual-pane HCP interaction logger:

- Left pane: structured interaction form (read-only, AI-populated)
- Right pane: conversational AI assistant (LangGraph + Groq)

The intended workflow is: user describes a visit/call in natural language, the agent executes one or more tools, returns structured form updates, and the user submits the finalized interaction to the backend.

## 1. What This App Does

This app supports life sciences field workflows where reps log interactions with healthcare professionals (HCPs).

Core capabilities:

- Capture interaction details via chat, not manual form typing
- Normalize free-text notes into structured CRM fields
- Support corrections to previously extracted values
- Generate AI summary and suggested follow-ups
- Persist interaction records in PostgreSQL via FastAPI

## 2. Tech Stack

- Frontend: React 19, Redux Toolkit, Vite, Tailwind CSS
- Backend: FastAPI, SQLAlchemy (async), LangGraph
- LLM: Groq (primary + context model)
- Database: PostgreSQL (asyncpg)
- Python package manager/runtime: uv

## 3. Repository Layout

```text
life_science_ai/
	README.md
	IMPLEMENTATION_PLAN.md
	backend/
		main.py
		pyproject.toml
		app/
			config.py
			database.py
		agent/
			graph.py
			state.py
			tools/
		models/
			entities.py
		routers/
			agent.py
			hcp.py
			interactions.py
		schemas/
			chat.py
			hcp.py
			interaction.py
		services/
			groq_client.py
		tests/
			test_health.py
	frontend/
		package.json
		src/
			App.jsx
			main.jsx
			store/
				chatSlice.js
				interactionSlice.js
				interactionThunks.js
```

## 4. Architecture (Runtime Flow)

1. User sends a chat message in the frontend assistant panel.
2. Frontend calls `POST /api/agent/chat` with message + current form context.
3. Backend LangGraph pipeline runs:
	 - `router_node` picks up to 3 tools
	 - `tool_executor_node` executes tools in sequence
	 - `responder_node` combines tool responses into assistant text
4. Backend returns:
	 - assistant response text
	 - executed tool names and tool outputs
	 - merged `form_updates`
5. Frontend normalizes keys and merges updates into Redux `interaction` state.
6. User submits final interaction with `POST /api/interactions`.

## 5. Prerequisites

- Python 3.14+ (per `backend/pyproject.toml`)
- Node.js 18+
- npm
- PostgreSQL 14+
- uv installed (`pip install uv`)

## 6. Environment Configuration

### Backend

Create `backend/.env` from `backend/.env.example`.

PowerShell:

```powershell
Copy-Item backend/.env.example backend/.env
```

Required backend env vars:

```env
APP_ENV=development
LOG_LEVEL=INFO
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/hcp_crm
GROQ_API_KEY=gsk_your_key_here
GROQ_PRIMARY_MODEL=llama-3.1-8b-instant
GROQ_CONTEXT_MODEL=llama-3.3-70b-versatile
CORS_ORIGINS_RAW=http://localhost:5173
```

Notes:

- If `GROQ_API_KEY` is missing/empty, chat tools return an LLM-unavailable fallback message.
- CORS origins are comma-separated and parsed in `app/config.py`.

### Frontend

Create `frontend/.env` from `frontend/.env.example`.

PowerShell:

```powershell
Copy-Item frontend/.env.example frontend/.env
```

Frontend env:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## 7. Local Development Setup

### 7.1 Start Backend

```powershell
cd backend
uv sync
uv run uvicorn main:app --reload --port 8000
```

Backend behavior on startup:

- Creates database tables using `Base.metadata.create_all` in FastAPI lifespan
- Registers routers with `/api` prefix
- Exposes health endpoint: `GET /health`

### 7.2 Start Frontend

```powershell
cd frontend
npm install
npm run dev
```

Default UI URL (Vite): `http://localhost:5173`

### 7.3 Run Tests

```powershell
cd backend
uv run pytest
```

Current test coverage is minimal (health check only).

## 8. API Reference

Base prefix: `/api`

### Health

- `GET /health`
- Response: `{ "status": "ok" }`

### Agent

- `POST /api/agent/chat`

Request body:

```json
{
	"session_id": "string",
	"message": "string",
	"context": {}
}
```

Response body:

```json
{
	"response": "string",
	"tool_used": "log_interaction, edit_interaction",
	"tool_result": {},
	"tool_results": [],
	"form_updates": {}
}
```

### HCP

- `GET /api/hcp/search?q=<name>` (returns up to 20 matches)
- `POST /api/hcp`
- `GET /api/hcp/{hcp_id}`

### Interactions

- `POST /api/interactions`
- `GET /api/interactions`
- `GET /api/interactions?hcp_id=<uuid>`
- `GET /api/interactions/{interaction_id}`
- `PUT /api/interactions/{interaction_id}`

There is currently no delete endpoint in code.

## 9. Data Model (Backend)

Tables (from SQLAlchemy models):

- `hcps`
- `interactions`
- `chat_messages`

`interactions` stores several structured fields as JSON arrays/objects:

- `attendees`
- `materials_shared`
- `samples_distributed`
- `follow_up_actions`
- `ai_suggested_followups`

This keeps payload handling simple and aligned with tool outputs.

## 10. LangGraph Agent Design

State fields include:

- `message`, `session_id`, `context`, `db`
- `route`, `tool_result`, `tool_results`, `executed_tools`, `response`

Graph:

- `START -> router_node -> tool_executor_node -> responder_node -> END`

Routing highlights:

- Correction keywords bias toward `edit_interaction`
- Search/history keywords add `search_interactions`
- Summary keywords add `generate_call_summary`
- Follow-up/schedule keywords add `schedule_followup_meeting`
- Explicit new-interaction intent ensures `log_interaction`
- Fallback tool is always `log_interaction`

Execution behavior:

- Up to 3 tools can run in one request
- Tool outputs are merged into a running `context`
- Aggregated updates are returned as `route.form_updates`

## 11. Tool Registry (10 Tools)

- `log_interaction`
- `edit_interaction`
- `get_hcp_profile`
- `suggest_follow_up`
- `analyze_sentiment`
- `search_interactions`
- `distribute_sample`
- `share_material`
- `generate_call_summary`
- `schedule_followup_meeting`

Important implementation details:

- `search_interactions` is the only tool that requires DB session input.
- `log_interaction` uses timestamp locking behavior via merge helper.
- Backend key alias normalization is centralized in `agent/tools/common.py`.
- Follow-up lists are deduplicated by action text.

## 12. Frontend State and Contract Mapping

Redux slices:

- `chat`: assistant/user messages, loading, error
- `interaction`: full structured form state

Normalization behavior:

- Frontend maps snake_case API keys to camelCase form keys using aliases in `interactionSlice.js`.
- Date/time are sanitized before writing into state.
- This mirrors backend alias normalization and prevents dropped updates when model output key style varies.

Submission behavior:

- `submitInteraction` transforms camelCase state to backend snake_case payload for `POST /api/interactions`.

## 13. End-to-End Usage Walkthrough

1. Start backend and frontend.
2. Open the app at `http://localhost:5173`.
3. In the chat panel, enter a natural-language interaction note.
4. Click `Log` to run agent extraction.
5. Verify read-only form fields were populated correctly.
6. Send correction prompts (for example, date or follow-up edits).
7. Ask for summary or follow-up suggestions if needed.
8. Click `Log Interaction` to persist data.

## 14. Known Gaps / Current Limitations

- Frontend has placeholder UI actions without handlers:
	- Voice note summarization button
	- Material search/add button
	- Sample add button
- HCP search UI is read-only in current `App.jsx` (API exists but no interactive picker wired).
- Only one backend automated test exists (`test_health.py`).
- No migrations are configured; schema is created via `create_all` at startup.
- No delete interaction route in current API.

## 15. Troubleshooting

### Chat returns LLM unavailable message

- Confirm `GROQ_API_KEY` in `backend/.env`
- Restart backend after env updates

### CORS errors in browser

- Confirm frontend origin appears in `CORS_ORIGINS_RAW`
- Example: `http://localhost:5173`

### DB connection failures

- Confirm PostgreSQL is running
- Verify `DATABASE_URL` uses `postgresql+asyncpg://...`
- Ensure database exists and credentials are valid

### Form fields not updating from chat

- Inspect backend `form_updates` payload in `/api/agent/chat` response
- Ensure alias mappings remain aligned between backend `agent/tools/common.py` and frontend `interactionSlice.js`

## 16. Suggested Next Engineering Steps

1. Add integration tests for `/api/agent/chat` with mocked Groq responses.
2. Add migrations (Alembic) instead of runtime `create_all`.
3. Implement interactive HCP search/select in frontend using `/api/hcp/search`.
4. Add optimistic/error toasts for interaction submission.
5. Split monolithic `App.jsx` into feature components and add route structure.
