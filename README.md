# AI-First CRM HCP Module (Task 1)

Task 1 implementation for the life sciences assignment: a dual-mode Log Interaction screen with a structured form (left) and AI assistant (right), where the form is populated by AI chat.

## Stack

- Frontend: React + Redux Toolkit + Tailwind (mobile-first responsive)
- Backend: FastAPI + PostgreSQL + LangGraph + Groq
- Python package/runtime: `uv`

## Backend Setup (uv)

```bash
cd backend
copy .env.example .env
# Fill DATABASE_URL and GROQ_API_KEY in .env
uv sync
uv run uvicorn main:app --reload --port 8000
```

Run tests:

```bash
cd backend
uv run pytest
```

## Frontend Setup

```bash
cd frontend
copy .env.example .env
npm install
npm run dev
```

## Key Assignment Behaviors Implemented

- Left form is read-only and AI-driven for data entry/editing.
- Right chat panel uses LangGraph tools to update form state.
- Implemented 10 tools (including mandatory `log_interaction` and `edit_interaction`).
- Uses Groq models (`gemma2-9b-it`, `llama-3.3-70b-versatile`) via `.env` key.
