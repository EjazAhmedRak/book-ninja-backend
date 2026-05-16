# Book Ninja Backend — Claude Code Reference

## Project Overview
AI-powered book discovery API built with FastAPI + LangGraph. Accepts natural language prompts, routes them through a 5-node agent graph (parse → search/purchase/ebook/audiobook), and returns structured responses. MongoDB persists threads and user records.

## Tech Stack
| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| API | FastAPI + Uvicorn |
| Validation | Pydantic v2 |
| Agent | LangChain + LangGraph |
| LLMs | gpt-4o-mini (tool calls), gpt-4o (reflection) |
| Search | Tavily API |
| Books | HardCover API |
| Database | MongoDB via Motor (async) — Clever Cloud in prod |
| Auth | Google OAuth2 ID token verification |
| Observability | LangSmith |
| HTTP client | httpx (async) |
| Retry | tenacity |
| Testing | pytest + pytest-asyncio + pytest-cov |
| Lint | ruff |

## Folder Structure
```
src/                Source root — added to PYTHONPATH so imports work without a package prefix
  main.py           FastAPI entry point — includes all 3 routers
  config.py         Loads all env vars from .env via python-dotenv
  models/           All Pydantic models (requests, responses, agent state, DB records)
  api/routes/       Route handlers: chat.py, threads.py, health.py
  api/middleware/   auth.py (Google token), validation.py (prompt guards)
  agent/graph.py    LangGraph StateGraph — defines nodes, edges, run_agent()
  agent/nodes/      One file per graph node (5 nodes)
  agent/tools/      One file per LangChain tool (6 tools)
  db/mongo.py       Motor client + ping_mongo, save_user, get_latest_threads
  db/checkpointer.py  MongoDBSaver with MemorySaver fallback
  utils/retry.py    Shared tenacity call_with_retry decorator
tests/              Test suite; conftest.py for shared fixtures
```

## Environment Variables
Copy `.env.example` to `.env` and fill in real values. Never commit `.env`.

| Variable | Purpose |
|---|---|
| OPENAI_API_KEY | OpenAI API access |
| TAVILY_API_KEY | Tavily search/scrape |
| HARDCOVER_API_KEY | HardCover book search API |
| MONGO_URI | MongoDB Atlas/Clever Cloud URI |
| LANGSMITH_API_KEY | LangSmith observability |
| LANGCHAIN_PROJECT | LangSmith project name (book-ninja) |
| LANGCHAIN_TRACING_V2 | Set to "true" to enable tracing |
| GOOGLE_CLIENT_ID | Google OAuth2 audience claim |

## Key Conventions

### All data is Pydantic
Every request body, response body, tool input, tool output, agent state, and DB record is a Pydantic BaseModel. Never pass raw dicts between layers.

### Agent state is immutable — use model_copy
Nodes must not mutate state in-place. Always return:
`return state.model_copy(update={...})`

### Tools use @tool decorator and are async
All LangChain tools are async and decorated with `@tool` from `langchain_core.tools`.

### Thread ID format
`{user_id}_{uuid4}` — constructed by `build_thread_id()` in `agent/graph.py`.
If the client sends a `thread_id`, it is reused (continuing a conversation).

### Auth flow
All `/chat` and `/latestThreads` requests require `Authorization: Bearer <google-id-token>`.
`validate_google_token()` in `api/middleware/auth.py` handles verification and returns `GoogleUser`.
`/health` is unauthenticated.

### Retry pattern
Wrap all external HTTP calls with `call_with_retry()` from `utils/retry.py` (tenacity, 30s total, exponential backoff 1s→10s).

### Reflection loop (search node only)
`search_node.py` runs up to 2 iterations with gpt-4o as the reflection model. The loop exits early if "satisfactory" appears in the reflection response.

### Import path convention
All imports use top-level package names: `from models.agent import AgentState`.
`PYTHONPATH=src` (set in Dockerfile, docker-compose, and pyproject.toml) makes `src/` the import root.
Always run commands from the project root, never from inside `src/`.

## Setup Commands
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# fill in .env values
PYTHONPATH=src uvicorn main:app --reload --port 8000
```

## Testing Commands
```bash
pytest                                          # all tests (pythonpath=src set in pyproject.toml)
pytest --cov=src --cov-report=term-missing     # with coverage
pytest --cov=src --cov-fail-under=80          # CI gate (80% required)
pytest tests/test_chat.py -v                  # single file
```

## Linting
```bash
ruff check .     # lint
ruff format .    # format
```

## API Endpoints
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /chat | Required | Main agent endpoint |
| GET | /latestThreads | Required | 5 most recent threads for user |
| GET | /health | None | Integration health check |

## LangGraph Agent Graph
```
parse_query (start_node)
    └─ conditional route on state.intent ─┬─ "search"    → search_books_node → END
                                          ├─ "purchase"  → purchase_node → END
                                          ├─ "ebook"     → ebook_node → END
                                          └─ "audiobook" → audiobook_node → END
```

## Important Notes for Claude Code
- The spec file is `Book_Ninja_Backend_Dev.md` — consult it for authoritative decisions.
- `langgraph-checkpoint-mongodb` is a separate PyPI package (not part of `langgraph`).
- The MongoDBSaver fallback uses `MemorySaver` — degrade gracefully, don't crash.
- HardCover API: `https://api.hardcover.app/v1/books/search` (Bearer token auth).
- Anna's Archive and AudiobookBay mirrors change — always call `search_current_mirror` first.
- LangSmith tracing is activated by setting `LANGCHAIN_TRACING_V2=true` in the environment; `main.py` writes this env var before FastAPI starts.
- `id_token.verify_oauth2_token` (Google auth) is synchronous — wrap in `asyncio.to_thread()` in async context.
- Tavily's `TavilyClient.search()` is synchronous — wrap in `asyncio.to_thread()` in async tool functions.
