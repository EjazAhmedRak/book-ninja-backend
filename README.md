# Book Ninja — Backend

AI-powered book discovery API. Send a natural language prompt and the agent finds books, purchase links, ebook downloads, or audiobook downloads — automatically routing based on intent.

> Internal test application · v2 · Python 3.12 · FastAPI + LangGraph

---

## How It Works

Every request to `/chat` runs through a 6-node LangGraph agent:

```
User prompt
    └── start_node (parse_query → extract intent)
            ├── "search"    → search_books_node  → returns top 5 books from HardCover
            ├── "purchase"  → purchase_node      → returns buy links (Amazon, Kobo, Google Books)
            ├── "ebook"     → ebook_node         → returns epub/mobi links (Anna's Archive)
            └── "audiobook" → audiobook_node     → validate_audiobook_node → returns filtered download links
```

The search node runs up to 2 reflection iterations using `gpt-4o` to improve results before responding.  
Audiobook results are post-filtered by `validate_audiobook_node` using `gpt-4o-mini` to remove likely title mismatches.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| API framework | FastAPI + Uvicorn |
| Data validation | Pydantic v2 |
| Agent framework | LangChain + LangGraph |
| LLMs | `gpt-4o-mini` (parsing + audiobook validation), `gpt-4o` (search reflection) |
| Book search | HardCover GraphQL API |
| Web search | Tavily API |
| Database | MongoDB (Motor async driver) |
| Auth | Google OAuth2 ID token |
| Observability | LangSmith |
| HTTP client | httpx |
| Retry | tenacity (30s, exponential backoff) |

---

## Project Structure

```
book-ninja-be/
├── src/                        # Application source (PYTHONPATH root)
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Environment variable loading
│   ├── models/                 # All Pydantic models
│   │   ├── query.py            # ParsedQuery
│   │   ├── book.py             # BookResult
│   │   ├── purchase.py         # PurchaseLink, PurchaseQuery
│   │   ├── ebook.py            # EbookLink, EbookQuery
│   │   ├── audiobook.py        # AudiobookLink, AudiobookQuery
│   │   ├── mirror.py           # MirrorQuery, MirrorResult
│   │   ├── thread.py           # ThreadRecord, ThreadsResponse
│   │   ├── health.py           # HealthResponse
│   │   ├── agent.py            # AgentState
│   │   └── user.py             # UserRecord
│   ├── api/
│   │   ├── routes/             # chat.py · threads.py · health.py
│   │   └── middleware/         # auth.py · validation.py
│   ├── agent/
│   │   ├── graph.py            # LangGraph StateGraph + stream_agent()/run_agent()
│   │   ├── nodes/              # start · search · purchase · ebook · audiobook · validate_audiobook
│   │   └── tools/              # parse_query · search_books · find_purchase_links
│   │                           # search_current_mirror · find_ebook_link · find_audiobook_link
│   ├── db/
│   │   ├── mongo.py            # Motor client, ping_mongo, save_user, get_latest_threads
│   │   └── checkpointer.py     # LangGraph InMemorySaver (MongoDB saver: see note below)
│   └── utils/
│       ├── llm_stream.py       # collect_stream() helper for LLM .astream() aggregation
│       └── retry.py            # call_with_retry() tenacity wrapper
├── tests/                      # pytest suite
│   ├── conftest.py             # Shared fixtures (mock env, mock auth, test client)
│   ├── test_chat.py
│   ├── test_health.py
│   ├── test_models.py
│   ├── test_threads.py
│   ├── test_tools.py
│   ├── test_validate_audiobook_node.py
│   └── test_validation.py
├── .env.example                # Environment variable template
├── requirements.txt
├── pyproject.toml              # pytest + ruff + coverage config
├── Dockerfile                  # Multi-stage production image
├── docker-compose.yml          # Local dev with MongoDB sidecar
└── .github/workflows/
    └── backend.yml             # CI: lint → test → docker build
```

---

## Setup

### 1. Clone and create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in all values:

| Variable | Description |
|---|---|
| `APP_ENV` | `dev`, `qa`, or `prod` — controls auth bypass availability |
| `OPENAI_API_KEY` | OpenAI API key (`sk-...`) |
| `HARDCOVER_API_KEY` | HardCover Bearer token — copy the full `Bearer eyJ...` value from your HardCover account |
| `TAVILY_API_KEY` | Tavily API key (`tvly-...`) |
| `MONGO_URI` | MongoDB connection string (`mongodb+srv://...`) |
| `LANGSMITH_API_KEY` | LangSmith API key (`ls-...`) |
| `LANGCHAIN_PROJECT` | LangSmith project name (e.g. `book-ninja`) |
| `LANGCHAIN_TRACING_V2` | `true` to enable LangSmith tracing |
| `GOOGLE_CLIENT_ID` | Google OAuth2 client ID (`...apps.googleusercontent.com`) |

> **Note:** `HARDCOVER_API_KEY` must include the `Bearer ` prefix — paste the full Authorization header value from your HardCover account settings.

### 3. Start the server

```bash
PYTHONPATH=src venv/bin/uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

For Debug Mode:
PYTHONPATH=src venv/bin/uvicorn main:app --reload --port 8000 --log-level debug
---

## Running with Docker Compose

Starts the API and a local MongoDB instance:

```bash
docker-compose up --build
```

The API mounts the source directory, so `--reload` picks up changes without rebuilding.

---

## API Endpoints

### `POST /chat`

Send a natural language book query. Requires authentication.  
This endpoint streams results as **Server-Sent Events (SSE)** (`text/event-stream`).

```bash
curl -N -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <google-id-token>" \
  -d '{"prompt": "find me Dune by Frank Herbert"}'
```

**Request body:**
```json
{
  "prompt": "find me sci-fi books about space exploration",
  "thread_id": "optional-existing-thread-id"
}
```

**SSE events:**
```text
event: status
data: {"node":"start","message":"Request parsed. Detected intent: search.","thread_id":"user123_4f8a2b1c-..."}

event: status
data: {"node":"search_books","message":"Searching book catalog and ranking matches.","thread_id":"user123_4f8a2b1c-..."}

event: final
data: {"output":"- Dune by Frank Herbert (1965) — Rating: 4.5\n  ...","thread_id":"user123_4f8a2b1c-...","books":[]}
```

Event types:
- `status`: emitted after each graph node completes
- `final`: emitted once with final payload (`output`, `thread_id`, `books`)
- `error`: emitted if processing fails

Pass `thread_id` in the request to continue the same conversation.

#### Frontend Consumption Example (`fetch` + stream reader)

Use `fetch` instead of `EventSource` because `/chat` is a `POST` endpoint and requires auth headers.

```ts
type ChatStatusEvent = {
  node: string;
  message: string;
  thread_id: string;
};

type ChatFinalEvent = {
  output: string;
  thread_id: string;
  books: Array<{ title: string; author?: string; year?: string; url: string; rating?: number }>;
};

export async function streamChat({
  prompt,
  threadId,
  token,
  onStatus,
  onFinal,
  onError,
}: {
  prompt: string;
  threadId?: string;
  token: string;
  onStatus: (event: ChatStatusEvent) => void;
  onFinal: (event: ChatFinalEvent) => void;
  onError: (message: string) => void;
}) {
  const res = await fetch("http://localhost:8000/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ prompt, thread_id: threadId }),
  });

  if (!res.ok || !res.body) {
    throw new Error(`Chat request failed: ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const blocks = buffer.split("\n\n");
    buffer = blocks.pop() ?? "";

    for (const block of blocks) {
      const lines = block.split("\n");
      const eventLine = lines.find((l) => l.startsWith("event: "));
      const dataLine = lines.find((l) => l.startsWith("data: "));
      if (!eventLine || !dataLine) continue;

      const event = eventLine.slice("event: ".length).trim();
      const data = JSON.parse(dataLine.slice("data: ".length));

      if (event === "status") onStatus(data as ChatStatusEvent);
      if (event === "final") onFinal(data as ChatFinalEvent);
      if (event === "error") onError((data?.message as string) || "Unknown error");
    }
  }
}
```

---

### `GET /latestThreads`

Returns the 5 most recent conversation threads for the authenticated user.

```bash
curl http://localhost:8000/latestThreads \
  -H "Authorization: Bearer <google-id-token>"
```

**Response:**
```json
{
  "threads": [
    {
      "thread_id": "user123_4f8a2b1c-...",
      "preview": "find me Dune by Frank Herbert",
      "timestamp": "2026-05-11T10:00:00Z"
    }
  ]
}
```

---

### `GET /health`

Checks all external integrations. No authentication required.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "integrations": {
    "hardcover": "ok",
    "mongodb": "ok",
    "tavily": "ok",
    "langsmith": "ok"
  }
}
```

Possible values per integration: `ok` · `degraded` · `unavailable`.  
Overall `status` is `ok` only when all integrations are `ok`.

---

## Dev / QA Auth Bypass

When `APP_ENV` is `dev` or `qa`, you can skip Google token validation by passing `X-Debug-Email` instead of a Bearer token. The email is used as both the user email and user ID.

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-Debug-Email: you@example.com" \
  -d '{"prompt": "find me a book about machine learning"}'

curl http://localhost:8000/latestThreads \
  -H "X-Debug-Email: you@example.com"
```

> The bypass is completely disabled when `APP_ENV=prod`. Setting it in production has no effect.

---

## Integrations

### HardCover (Book Search)
- **API:** GraphQL at `https://api.hardcover.app/v1/graphql`
- **Auth:** Bearer token — paste the full `Bearer eyJ...` value as `HARDCOVER_API_KEY`
- **Usage:** `search` query with `query_type: "Book"` — returns title, author, rating, description, and slug
- **Get token:** [hardcover.app/account/api](https://hardcover.app/account/api)

### Tavily (Web Search & Mirror Discovery)
- **Usage:** Purchase link search (Amazon, Kobo, Google Books) and live mirror discovery for Anna's Archive / AudiobookBay
- **Get key:** [tavily.com](https://tavily.com)

### MongoDB
- **Driver:** Motor (async)
- **Collections:** `users` (upserted on each authenticated request), `threads` (conversation history)
- **Local:** `docker-compose up` starts a MongoDB 7.0 sidecar on port 27017
- **Cloud:** [Clever Cloud](https://www.clever-cloud.com) managed MongoDB add-on for production

> **Checkpointer note:** The LangGraph `MongoDBSaver` now requires a FastAPI lifespan context manager and is not yet wired up. The app currently uses `InMemorySaver` — threads are not persisted across server restarts in this mode.

### LangSmith (Observability)
- **Usage:** Set `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_PROJECT=book-ninja` to enable. All node executions, tool calls, and LLM calls are traced automatically.
- **Dashboard:** [smith.langchain.com](https://smith.langchain.com)
- **Get key:** LangSmith account → Settings → API Keys

### Google OAuth2 (Authentication)
- **Flow:** Client obtains a Google ID token; passes it as `Authorization: Bearer <token>`; backend verifies the `aud` claim against `GOOGLE_CLIENT_ID`
- **Library:** `google-auth` — `id_token.verify_oauth2_token()`
- **Get client ID:** [Google Cloud Console](https://console.cloud.google.com) → APIs & Services → Credentials → OAuth 2.0 Client

---

## Testing

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=src --cov-report=term-missing

# Enforce 80% coverage gate (used in CI)
pytest --cov=src --cov-fail-under=80

# Single file
pytest tests/test_chat.py -v
```

Tests use `app.dependency_overrides` to bypass Google auth — no real token needed. All external API calls (OpenAI, HardCover, Tavily, MongoDB) are mocked.

---

## Linting

```bash
ruff check src      # lint
ruff format src     # format
```

---

## CI/CD

GitHub Actions runs on every push to `main` / `develop` and on pull requests to `main`:

1. **Lint** — `ruff check src`
2. **Test + Coverage** — `pytest --cov=src --cov-fail-under=80` (with dummy env vars injected)
3. **Docker build** — `docker build` to confirm the image compiles cleanly

Push-to-registry is configured but commented out pending registry selection (ECR or Artifact Registry). Uncomment and configure in `.github/workflows/backend.yml` when ready.

---

## Deployment

### Build and run the Docker image

```bash
docker build -t book-ninja-backend .
docker run -p 8000:8000 --env-file .env book-ninja-backend
```

### Environment targets

| Environment | Branch | Purpose |
|---|---|---|
| Development | `develop` | Local and PR testing |
| Staging | `staging` | Pre-production validation |
| Production | `main` | Live traffic |

Each environment should have its own MongoDB database, LangSmith project, and secret set. Secrets are injected as environment variables — never baked into the image.

---

## Prompt Examples

| Intent | Example prompt |
|---|---|
| Search | `"find me sci-fi books about space exploration"` |
| Search | `"best novels by Ursula K. Le Guin"` |
| Purchase | `"where can I buy The Martian as an ebook?"` |
| Ebook | `"download Project Hail Mary epub"` |
| Audiobook | `"audiobook download for Atomic Habits"` |
