# EnterpriseAssist AI — Phase Notes

Built incrementally, one phase at a time, following a 12-phase roadmap. Each phase introduced one core concept and applied it immediately to the project.

## Phase 0 — Architecture & Repo Setup
Drew the core architecture by hand before writing any code: Employee → AI Assistant → HR/IT/Finance/Travel/Knowledge. Scaffolded the repo structure (backend/, frontend/, agents/, api/, tools/, rag/, docs/).

## Phase 1 — Basic Chatbot
Plain LLM call loop using the Gemini API (`google-genai` SDK). No memory, no tools — proved the basic request/response mechanism worked.

## Phase 2 — Conversation Memory
Learned that LLMs are stateless — "memory" is just re-sending the full conversation transcript on every call. Implemented via a running `chat_history` list.

## Phase 3 — Prompt Engineering
Upgraded the system prompt from one generic sentence to a structured prompt with scope boundaries, behavior rules, and guardrails against hallucinating data the assistant didn't actually have access to yet.

## Phase 4 — Backend APIs
Built the "real" company systems as plain FastAPI endpoints (leave, tickets, employees) — no AI involved. Learned GET vs POST, and restructured into `APIRouter` so multiple route files could be combined under one FastAPI app.

## Phase 5 — Tool Calling
Gave the AI real tools (Python functions hitting the FastAPI backend over HTTP) instead of letting it guess. The `google-genai` SDK handled the "decide → call → respond" loop automatically. Expanded scope significantly beyond the original roadmap here: built out full HR/IT/Finance/Travel functionality, added a real login system (1000 Faker-generated employees, password auth), and bound tools to the logged-in employee's ID so the AI could no longer act on another employee's behalf just because a message mentioned their ID.

## Phase 6 — AI Agent (LangGraph)
Rebuilt the tool-calling loop as an explicit LangGraph `StateGraph` instead of relying on the SDK's implicit black-box loop. This gave real visibility and control over the think → tool → think-again → answer cycle, which became essential for the next two phases.

## Phase 7 — Human-in-the-Loop
The system prompt alone wasn't a real guarantee — "confirm before submitting" was a request to the model's good behavior, not something enforced. Rebuilt the graph's routing so sensitive tools (`submit_leave`, `create_ticket`, `submit_expense`, `request_travel`) pause and require an explicit "yes" in code before the tool function ever actually runs. Read-only tools skip this entirely.

## Phase 8 — RAG (Knowledge Base)
Generated 20 realistic company policy documents, chunked them, embedded them with Gemini's embedding model, and stored them in a local Chroma vector store. Added a `search_policy` tool that retrieves the most relevant chunks and grounds the AI's answer in the actual retrieved text rather than guessing.

## Phase 9 — Multi-Agent Architecture
Split the single generalist agent into five specialists (HR, IT, Finance, Travel, Knowledge), each with its own scoped LangGraph, short system prompt, and only the tools relevant to its domain. A supervisor agent classifies each incoming message and routes it to the correct specialist. The user never sees this split — it's one continuous chat from their perspective; the routing is invisible internal plumbing.

## Phase 10 — Production Engineering
Added structured file+console logging (every routing decision and employee action recorded to `logs/app.log`), a retry wrapper for transient network failures on tool calls, and confirmed the system fails gracefully (a clear "temporarily unavailable" message) rather than crashing when the backend is unreachable — verified by deliberately stopping the backend mid-conversation. Centralized the backend URL into one config file/environment variable instead of duplicating it across five agent files.

## Phase 11 — LangSmith Tracing
Enabled tracing with zero code changes (LangGraph auto-instruments when the right environment variables are set). Reviewed real traces across 10+ conversations. Confirmed there were no genuine failures — some traces showed empty AI text content, which turned out to be a normal intermediate step (a tool-call request has no text content of its own), not an error. Found a real, actionable insight: RAG/Knowledge-agent queries ran noticeably slower (~2.6s) than simple tool lookups (~0.7–1.2s), consistent with the added retrieval step. Used the traces to find and fix a real router bug — greetings and "what can you help with" questions were being misclassified as OFF_TOPIC — by expanding the Knowledge agent's routing scope and confirming the fix with a retest.

## Phase 12 — Deployment
[to be completed]

---

## Known Limitations / Honest Gaps

- **Date awareness**: the AI has no built-in knowledge of the current date, so it occasionally guesses a wrong year (e.g. defaulting to 2024) when a user gives a date without a year. Not fixed — a good example of a small but real production gap.
- **HR approval workflow**: deliberately out of scope. The system currently has no role-based review/approval flow (e.g. an HR staff member seeing and approving pending leave requests). Flagged early as a meaningful architectural addition (needs real authentication/session identity beyond simple login, and role-based tool access) — treated as a genuine future phase rather than half-building it.
- **"Generate travel plan"**: one sub-feature from the original capstone brief's Travel section was set aside — it's closer to open-ended AI reasoning/itinerary generation than a data lookup, and wasn't built.
- **In-memory chat history**: conversation history lives in Streamlit's session state, not persisted to the database — a fresh login starts a fresh conversation. All *business* data (employees, leave requests, tickets, expenses, travel requests) is persisted in PostgreSQL and survives restarts; only the chat transcript itself is session-scoped.
- **No automated tests**: the project was verified through manual testing and LangSmith trace review at each phase, not a formal test suite.