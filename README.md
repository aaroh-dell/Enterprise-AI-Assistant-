# EnterpriseAssist AI

A multi-agent enterprise workplace assistant that lets employees handle HR, IT, Finance, and Travel requests — and search company policies — through a single conversational interface, instead of navigating separate internal portals.

Built incrementally as a 12-phase learning project: from a basic chatbot with no memory, up through tool calling, an explicit LangGraph agent, enforced human-in-the-loop confirmation, RAG-based policy search, a full multi-agent architecture, and production concerns like logging, retries, and tracing. Full phase-by-phase breakdown in [`docs/phase-notes.md`](docs/phase-notes.md).

## What it does

- **HR** — check leave balance, apply for leave, view the holiday calendar, look up employee info
- **IT** — raise and check support tickets, reset password
- **Finance** — submit expense reimbursements, check reimbursement status
- **Travel** — request business travel, check status, estimate trip budget
- **Knowledge** — ask questions about company policies (leave, benefits, security, IT) and get answers grounded in real policy documents, not guesses

Every state-changing action (submitting leave, creating a ticket, submitting an expense, requesting travel) requires explicit user confirmation before it actually executes — enforced in code, not just requested via prompt.

## Architecture

```
Employee (Streamlit chat UI, logged in)
   ↓
Supervisor Agent  →  classifies each message into a department
   ↓
   ├── HR Agent        → leave, holidays, employee info
   ├── IT Agent         → tickets, password reset
   ├── Finance Agent     → expenses
   ├── Travel Agent       → travel requests, budget estimation
   └── Knowledge Agent    → RAG search over company policy documents
   ↓
FastAPI backend  →  PostgreSQL (employees, leave requests, tickets, expenses, travel requests)
```

Each specialist agent is its own scoped LangGraph, with only the tools and system prompt relevant to its domain. The supervisor routes invisibly — the employee only ever sees one continuous conversation.

## Tech stack

- **AI / Orchestration**: Google Gemini (`gemini-3.5-flash-lite`), LangGraph, LangChain, LangSmith (tracing)
- **RAG**: Chroma vector store, Gemini embeddings (`gemini-embedding-001`)
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Streamlit
- **Auth**: employee ID + password login, backed by a Faker-generated employee dataset

## Project structure

```
backend/
  agents/       # supervisor + 5 specialist LangGraph agents
  api/          # FastAPI routes (leave, tickets, employees, it, expenses, travel)
  rag/          # policy documents, ingestion script, Chroma vector store
  database.py   # SQLAlchemy models and connection
  config.py     # centralized configuration (backend URL, etc.)
  logger.py     # structured logging setup
  retry_utils.py
  ai_core.py    # thin entrypoint used by the frontend
  main.py       # FastAPI app
frontend/
  app.py        # Streamlit UI (login, chat, session state)
docs/
  phase-notes.md
tests/
```

## Running locally

1. Clone the repo and create a virtual environment
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in:
   - `GEMINI_API_KEY` — from Google AI Studio
   - `DATABASE_URL` — your PostgreSQL connection string
   - `BACKEND_URL` — `http://127.0.0.1:8000` for local development
   - `LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2`, `LANGCHAIN_PROJECT` — for LangSmith tracing (optional)
4. Generate the employee dataset: `python -m backend.database` then `python -m backend.generate_employees`
5. Ingest the policy documents into Chroma: `python -m backend.rag.ingest`
6. Start the backend: `python -m uvicorn backend.main:app --reload`
7. In a separate terminal, start the frontend: `python -m streamlit run frontend/app.py`

## Known limitations

See the "Known Limitations / Honest Gaps" section in [`docs/phase-notes.md`](docs/phase-notes.md) — includes the current lack of a role-based HR approval workflow, no AI awareness of the current date, and a few other deliberately scoped-out features.

## Future enhancements

- Role-based HR approval workflow (HR staff reviewing/approving pending requests)
- AI-generated travel itinerary planning
- Persisted chat history across sessions