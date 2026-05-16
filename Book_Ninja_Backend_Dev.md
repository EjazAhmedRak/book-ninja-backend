# Book Ninja — Backend Development Guide

**Version:** v2  
**Author:** Ejaz Ahmed Ansari  
**Date:** 10 May 2026  
**Status:** Draft

> **Note:** This is an internal test application not intended for public release.

---

## 1. Overview

The Book Ninja backend is an AI agent exposed via a FastAPI REST API. It uses LangChain as the agent framework and ChatGPT as the LLM engine. The agent accepts natural language prompts, routes them through a graph of nodes (Search, Purchase, Download), and returns structured responses. MongoDB persists threads and memory across sessions. All data structures throughout the application are defined as **Pydantic models**, ensuring type safety, automatic validation, and clean OpenAPI documentation.

---

## 2. Tech Stack

| Technology | Purpose | Why |
|---|---|---|
| Python | Primary language | Strong ecosystem for AI/ML; LangChain is Python-native |
| FastAPI | API wrapper | Async, high-performance, auto-generates OpenAPI docs |
| Pydantic | Data modelling | Type-safe models for all request, response, and internal data; native to FastAPI |
| LangChain | AI agent framework | Provides graph-based agent architecture, tool management, and memory primitives |
| ChatGPT (gpt-4o-mini) | Search LLM | Fast and cost-effective for book search and query parsing |
| ChatGPT (gpt-4o) | Reflection LLM | More capable model for evaluating and improving search results |
| Tavily | Web search & scraping | Purpose-built for LLM use cases; reliable for real-time search and mirror discovery |
| MongoDB | Persistence | Document store well-suited for storing conversation threads and agent memory |
| LangSmith | Observability | Native LangChain integration; traces every node execution with no extra code |

---

## 3. Project Setup

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install fastapi uvicorn langchain langchain-openai langgraph \
            langsmith tavily-python pymongo motor python-dotenv \
            google-auth google-auth-httplib2 tenacity pydantic \
            pytest pytest-cov pytest-asyncio httpx
```

### Folder Structure

```
book_ninja_backend/
├── main.py                      # FastAPI app entry point
├── config.py                    # Environment variable loading
├── models/                      # All Pydantic data models
│   ├── query.py                 # ParsedQuery
│   ├── book.py                  # BookResult
│   ├── purchase.py              # PurchaseLink
│   ├── ebook.py                 # EbookLink
│   ├── audiobook.py             # AudiobookLink
│   ├── thread.py                # ThreadRecord, ThreadsResponse
│   ├── health.py                # HealthResponse, IntegrationStatus
│   ├── agent.py                 # AgentState
│   └── user.py                  # UserRecord
├── api/
│   ├── routes/
│   │   ├── chat.py              # /chat endpoint
│   │   ├── threads.py           # /latestThreads endpoint
│   │   └── health.py            # /health endpoint
│   └── middleware/
│       ├── auth.py              # Google token validation
│       └── validation.py        # Prompt validation
├── agent/
│   ├── graph.py                 # LangGraph agent graph definition
│   ├── nodes/
│   │   ├── start_node.py
│   │   ├── search_node.py
│   │   ├── purchase_node.py
│   │   ├── ebook_node.py
│   │   └── audiobook_node.py
│   └── tools/
│       ├── parse_query.py
│       ├── search_books.py
│       ├── find_purchase_links.py
│       ├── search_current_mirror.py
│       ├── find_ebook_link.py
│       └── find_audiobook_link.py
├── db/
│   ├── mongo.py                 # MongoDB connection and helpers
│   └── checkpointer.py          # LangGraph checkpointer using MongoDB
└── tests/
    ├── test_chat.py
    ├── test_validation.py
    ├── test_tools.py
    └── test_health.py
```

---

## 4. Pydantic Models

All data flowing through the application — API requests, API responses, tool inputs/outputs, agent state, and database records — is typed as a Pydantic model. This gives automatic validation, clear error messages, and a self-documenting OpenAPI schema.

### 4.1 Query Models

```python
# models/query.py
from pydantic import BaseModel
from typing import Literal

class ParsedQuery(BaseModel):
    """Structured output of the parse_query tool."""
    title:  str | None = None
    genre:  str | None = None
    year:   str | None = None
    author: str | None = None
    intent: Literal["search", "purchase", "ebook", "audiobook"] | None = None
```

### 4.2 Book Model

```python
# models/book.py
from pydantic import BaseModel, HttpUrl

class BookResult(BaseModel):
    """A single book returned by the Search Books tool."""
    title:         str
    author:        str
    year:          str | None = None
    summary:       str              # 200-word summary from HardCover
    hardcover_url: HttpUrl
    rating:        float = 0.0
```

### 4.3 Purchase Model

```python
# models/purchase.py
from pydantic import BaseModel, HttpUrl

class PurchaseLink(BaseModel):
    """A single purchase option for an ebook or audiobook."""
    store: str
    url:   HttpUrl
```

### 4.4 Ebook & Audiobook Download Models

```python
# models/ebook.py
from pydantic import BaseModel, HttpUrl
from typing import Literal

class EbookLink(BaseModel):
    """A download link for an ebook file."""
    source: str                          # e.g. "Anna's Archive"
    format: Literal["epub", "mobi"]
    url:    HttpUrl

# models/audiobook.py
from pydantic import BaseModel, HttpUrl

class AudiobookLink(BaseModel):
    """A download link for an audiobook."""
    source: str                          # e.g. "AudiobookBay"
    url:    HttpUrl
```

### 4.5 Thread Models

```python
# models/thread.py
from pydantic import BaseModel
from datetime import datetime

class ThreadRecord(BaseModel):
    """A single thread entry shown in the sidebar."""
    thread_id: str
    preview:   str       # first 100 characters of the opening user message
    timestamp: datetime

class ThreadsResponse(BaseModel):
    """Response body for /latestThreads."""
    threads: list[ThreadRecord]
```

### 4.6 Health Models

```python
# models/health.py
from pydantic import BaseModel
from typing import Literal

IntegrationStatus = Literal["ok", "degraded", "unavailable"]

class HealthResponse(BaseModel):
    """Response body for /health."""
    status:       Literal["ok", "degraded"]
    integrations: dict[str, IntegrationStatus]
    # Keys: hardcover, mongodb, tavily, langsmith
```

### 4.7 Agent State Model

The LangGraph agent state is a Pydantic model so every node has typed access to shared state.

```python
# models/agent.py
from pydantic import BaseModel
from models.query import ParsedQuery
from models.book import BookResult
from models.purchase import PurchaseLink
from models.ebook import EbookLink
from models.audiobook import AudiobookLink

class AgentState(BaseModel):
    """Shared state passed between all nodes in the LangGraph agent."""
    prompt:       str
    user_id:      str
    thread_id:    str
    parsed_query: ParsedQuery | None          = None
    intent:       str | None                  = None
    books:        list[BookResult]            = []
    links:        list[PurchaseLink]          = []
    ebook_links:  list[EbookLink]             = []
    audio_links:  list[AudiobookLink]         = []
    mirror_url:   str | None                  = None  # current working mirror
    output:       str | None                  = None
```

### 4.8 User Model

```python
# models/user.py
from pydantic import BaseModel, EmailStr

class UserRecord(BaseModel):
    """A user stored in MongoDB."""
    email:     EmailStr
    google_id: str
```

---

## 5. Configuration & Secret Management

All secrets are loaded from environment variables. Never hardcode keys.

```python
# config.py
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY    = os.environ["OPENAI_API_KEY"]
TAVILY_API_KEY    = os.environ["TAVILY_API_KEY"]
HARDCOVER_API_KEY = os.environ["HARDCOVER_API_KEY"]
MONGO_URI         = os.environ["MONGO_URI"]
LANGSMITH_API_KEY = os.environ["LANGSMITH_API_KEY"]
GOOGLE_CLIENT_ID  = os.environ["GOOGLE_CLIENT_ID"]
LANGCHAIN_TRACING_V2 = os.environ.get("LANGCHAIN_TRACING_V2", "true")
```

### Local (`.env` file)

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
HARDCOVER_API_KEY=...
MONGO_URI=mongodb+srv://...
LANGSMITH_API_KEY=ls-...
GOOGLE_CLIENT_ID=...apps.googleusercontent.com
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=book-ninja
```

### Cloud (Kubernetes Secrets)

Each key above becomes a Kubernetes Secret and is mounted as an environment variable in the pod. Never store secrets in Docker images or source code.

```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: book-ninja-secrets
type: Opaque
stringData:
  OPENAI_API_KEY: "sk-..."
  MONGO_URI: "mongodb+srv://..."
  # etc.
```

---

## 6. FastAPI Application Entry Point

```python
# main.py
from fastapi import FastAPI
from api.routes import chat, threads, health
from config import LANGCHAIN_TRACING_V2
import os

os.environ["LANGCHAIN_TRACING_V2"] = LANGCHAIN_TRACING_V2

app = FastAPI(title="Book Ninja API", version="2.0")

app.include_router(chat.router)
app.include_router(threads.router)
app.include_router(health.router)
```

Run locally:
```bash
uvicorn main:app --reload --port 8000
```

---

## 7. Session Management — Google Token Validation

Every request to `/chat` and `/latestThreads` must include a valid Google ID token. The backend validates this token using Google's auth library and extracts the user's email and Google ID.

```python
# api/middleware/auth.py
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from fastapi import HTTPException, Header
from pydantic import BaseModel
from config import GOOGLE_CLIENT_ID

class GoogleUser(BaseModel):
    """Decoded Google ID token payload fields used by the app."""
    sub:   str       # Google user ID — used as user_id throughout the app
    email: str

def validate_google_token(authorization: str = Header(...)) -> GoogleUser:
    """
    Validates the Bearer token from the Authorization header.
    Returns a typed GoogleUser. Raises 401 if the token is invalid or expired.
    The 'aud' claim is verified against GOOGLE_CLIENT_ID to prevent token misuse.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format.")
    token = authorization.split(" ")[1]
    try:
        payload = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
        return GoogleUser(sub=payload["sub"], email=payload["email"])
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
```

---

## 8. Input Validation

Applied to every `/chat` request before the prompt reaches the agent.

```python
# api/middleware/validation.py
from fastapi import HTTPException
import re

MAX_PROMPT_LENGTH = 3000

INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"you are now",
    r"act as",
    r"disregard all",
    r"system prompt",
    r"forget everything",
]

def validate_prompt(prompt: str) -> None:
    """
    Validates the user prompt. Raises HTTP 400 on failure.
    Checks: non-empty, max 3000 characters, prompt injection patterns.
    Note: 400 Bad Request is correct for input validation failures.
          403 Forbidden is reserved for authorisation failures only.
    """
    if not prompt or prompt.strip() == "":
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    if len(prompt) > MAX_PROMPT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Prompt exceeds maximum length of {MAX_PROMPT_LENGTH} characters."
        )
    lowered = prompt.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            raise HTTPException(status_code=400, detail="Prompt contains disallowed content.")
```

---

## 9. API Endpoints

### 9.1 `/chat` — POST

```python
# api/routes/chat.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from api.middleware.auth import validate_google_token, GoogleUser
from api.middleware.validation import validate_prompt
from agent.graph import run_agent
from db.mongo import save_user

router = APIRouter()

class ChatRequest(BaseModel):
    prompt:    str
    thread_id: str | None = None

class ChatResponse(BaseModel):
    output:    str
    thread_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, user: GoogleUser = Depends(validate_google_token)):
    validate_prompt(req.prompt)
    await save_user(UserRecord(email=user.email, google_id=user.sub))
    result = await run_agent(
        prompt=req.prompt,
        user_id=user.sub,
        thread_id=req.thread_id
    )
    return ChatResponse(output=result.output, thread_id=result.thread_id)
```

### 9.2 `/latestThreads` — GET

Returns the 5 most recent threads for the authenticated user. Each thread includes the thread ID, a 100-character preview of the first user message, and a timestamp.

```python
# api/routes/threads.py
from fastapi import APIRouter, Depends
from api.middleware.auth import validate_google_token, GoogleUser
from models.thread import ThreadsResponse
from db.mongo import get_latest_threads

router = APIRouter()

@router.get("/latestThreads", response_model=ThreadsResponse)
async def latest_threads(user: GoogleUser = Depends(validate_google_token)):
    threads = await get_latest_threads(user_id=user.sub, limit=5)
    return ThreadsResponse(threads=threads)
```

### 9.3 `/health` — GET

Checks the status of all four external integrations. Does not require authentication — used by infrastructure monitoring and the frontend to detect degraded services.

```python
# api/routes/health.py
from fastapi import APIRouter
from models.health import HealthResponse
from db.mongo import ping_mongo
from config import HARDCOVER_API_KEY
import httpx

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health():
    integrations: dict[str, str] = {}

    # HardCover API
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                "https://api.hardcover.app/v1/ping",
                headers={"Authorization": f"Bearer {HARDCOVER_API_KEY}"},
                timeout=5
            )
        integrations["hardcover"] = "ok" if r.status_code == 200 else "degraded"
    except Exception:
        integrations["hardcover"] = "unavailable"

    # MongoDB
    integrations["mongodb"] = "ok" if await ping_mongo() else "unavailable"

    # Tavily
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://api.tavily.com/health", timeout=5)
        integrations["tavily"] = "ok" if r.status_code == 200 else "degraded"
    except Exception:
        integrations["tavily"] = "unavailable"

    # LangSmith
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://api.smith.langchain.com/health", timeout=5)
        integrations["langsmith"] = "ok" if r.status_code == 200 else "degraded"
    except Exception:
        integrations["langsmith"] = "unavailable"

    overall = "ok" if all(v == "ok" for v in integrations.values()) else "degraded"
    return HealthResponse(status=overall, integrations=integrations)
```

---

## 10. Thread & Memory Management

### Thread ID Construction

```python
# agent/graph.py (helper)
import uuid

def build_thread_id(user_id: str, incoming_thread_id: str | None) -> str:
    """
    If the client passes a thread_id, reuse it (continuing an existing conversation).
    Otherwise, generate a new one using the pattern: userId_UUID.
    The '_' separator is intentional — matches the spec for thread ID format.
    """
    if incoming_thread_id:
        return incoming_thread_id
    return f"{user_id}_{uuid.uuid4()}"
```

### MongoDB Checkpointer

LangGraph's checkpointer persists the agent's state (the `AgentState` Pydantic model) between turns, enabling multi-turn conversations.

```python
# db/checkpointer.py
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.checkpoint.memory import MemorySaver
from config import MONGO_URI

def get_checkpointer():
    """
    Returns a MongoDB-backed checkpointer for production use.
    Falls back to in-memory if MongoDB is unavailable — every prompt
    in a degraded session is treated as a new conversation.
    """
    try:
        return MongoDBSaver.from_conn_string(MONGO_URI, db_name="book_ninja")
    except Exception:
        return MemorySaver()
```

---

## 11. AI Agent — LangGraph Architecture

The agent is built as a directed graph using LangGraph. The `AgentState` Pydantic model is the shared state object passed between all nodes.

### 11.1 Nodes

| Node | Responsibility |
|---|---|
| Start Node | Runs `parse_query` tool; sets `intent` on state to route to the correct node |
| Search Books Node | Calls `search_books` tool; runs up to 2 reflection iterations |
| Purchase Node | Calls `find_purchase_links` tool; returns purchase URLs |
| Download Ebook Node | Calls `search_current_mirror` then `find_ebook_link`; returns epub/mobi links |
| Download Audiobook Node | Calls `search_current_mirror` then `find_audiobook_link`; returns download links |

### 11.2 Conditional Edges

```python
# agent/graph.py
from langgraph.graph import StateGraph, END
from models.agent import AgentState

def route(state: AgentState) -> str:
    if state.intent == "search":    return "search_books"
    if state.intent == "purchase":  return "purchase"
    if state.intent == "ebook":     return "download_ebook"
    if state.intent == "audiobook": return "download_audiobook"
    return END

graph = StateGraph(AgentState)
graph.add_node("start",              start_node)
graph.add_node("search_books",       search_books_node)
graph.add_node("purchase",           purchase_node)
graph.add_node("download_ebook",     ebook_node)
graph.add_node("download_audiobook", audiobook_node)

graph.set_entry_point("start")
graph.add_conditional_edges("start", route)
graph.add_edge("search_books",       END)
graph.add_edge("purchase",           END)
graph.add_edge("download_ebook",     END)
graph.add_edge("download_audiobook", END)
```

### 11.3 Reflection on Search Node

```python
# agent/nodes/search_node.py
from langchain_openai import ChatOpenAI
from models.agent import AgentState

search_llm  = ChatOpenAI(model="gpt-4o-mini")
reflect_llm = ChatOpenAI(model="gpt-4o")

async def search_books_node(state: AgentState) -> AgentState:
    results = await search_books_tool.ainvoke(state.parsed_query)

    for _ in range(2):   # max 2 reflection iterations
        reflection = await reflect_llm.ainvoke(
            f"Review these book search results for relevance and completeness:\n{results}\n"
            f"Original query: {state.prompt}\n"
            "Are the results relevant and complete? If not, suggest a refined search query."
        )
        if "satisfactory" in reflection.content.lower():
            break
        refined = extract_refined_query(reflection.content)
        if refined:
            results = await search_books_tool.ainvoke(refined)

    return state.model_copy(update={"books": results, "output": format_results(results)})
```

---

## 12. Tools

All tools use Pydantic models for their inputs and outputs, providing type safety and clear contracts between nodes.

### 12.1 `Parse_query`

Extracts structured fields from a natural language prompt and returns a typed `ParsedQuery`.

```python
# agent/tools/parse_query.py
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from models.query import ParsedQuery
import json

llm = ChatOpenAI(model="gpt-4o-mini")

@tool
async def parse_query(prompt: str) -> ParsedQuery:
    """
    Parses a natural language book query into structured fields.
    Returns a ParsedQuery with title, genre, year, author, and intent.
    Intent is one of: search, purchase, ebook, audiobook.
    """
    response = await llm.ainvoke(
        f"Extract the following fields from this book query: title, genre, year, author, intent.\n"
        f"Intent must be one of: search, purchase, ebook, audiobook.\n"
        f"Query: {prompt}\n"
        f"Return as JSON only."
    )
    data = json.loads(response.content)
    return ParsedQuery(**data)
```

### 12.2 `Search_Books`

Queries the HardCover API with the parsed fields. Returns up to 5 books as `BookResult` objects sorted by average star rating.

```python
# agent/tools/search_books.py
import httpx
from langchain_core.tools import tool
from models.query import ParsedQuery
from models.book import BookResult
from config import HARDCOVER_API_KEY

@tool
async def search_books(query: ParsedQuery) -> list[BookResult]:
    """
    Searches HardCover API for books matching the parsed query.
    Returns up to 5 BookResult objects sorted by average star rating (descending).
    """
    params = {k: v for k, v in query.model_dump().items() if v and k != "intent"}
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://api.hardcover.app/v1/books/search",
            headers={"Authorization": f"Bearer {HARDCOVER_API_KEY}"},
            params=params,
            timeout=10
        )
        r.raise_for_status()
        raw_books = r.json()["results"]

    books = [BookResult(**b) for b in raw_books]
    return sorted(books, key=lambda b: b.rating, reverse=True)[:5]
```

### 12.3 `Find_purchase_links`

Uses Tavily to search Amazon, Google Books, and Kobo for purchase options. Returns typed `PurchaseLink` objects.

```python
# agent/tools/find_purchase_links.py
from tavily import TavilyClient
from langchain_core.tools import tool
from pydantic import BaseModel
from models.purchase import PurchaseLink
from config import TAVILY_API_KEY

tavily = TavilyClient(api_key=TAVILY_API_KEY)

class PurchaseQuery(BaseModel):
    title:  str
    author: str
    year:   str | None = None
    format: str        # 'ebook' or 'audiobook'

@tool
async def find_purchase_links(query: PurchaseQuery) -> list[PurchaseLink]:
    """
    Searches for ebook or audiobook purchase options on Amazon, Google Books, and Kobo.
    Returns a list of PurchaseLink objects with store name and URL.
    """
    search_query = (
        f"buy {query.format} \"{query.title}\" by {query.author} "
        f"site:amazon.com OR site:books.google.com OR site:kobo.com"
    )
    results = tavily.search(query=search_query, max_results=6)
    return [PurchaseLink(store=r["title"], url=r["url"]) for r in results["results"]]
```

### 12.4 `Search_current_mirror`

Anna's Archive and AudiobookBay frequently change domain. This tool uses Tavily to discover the current working mirror URL before any scraping occurs. It is always called first by the ebook and audiobook download nodes.

```python
# agent/tools/search_current_mirror.py
from tavily import TavilyClient
from langchain_core.tools import tool
from pydantic import BaseModel
from typing import Literal
from config import TAVILY_API_KEY

tavily = TavilyClient(api_key=TAVILY_API_KEY)

class MirrorQuery(BaseModel):
    source: Literal["annas_archive", "audiobookbay"]

class MirrorResult(BaseModel):
    source: str
    url:    str    # current working mirror URL

@tool
async def search_current_mirror(query: MirrorQuery) -> MirrorResult:
    """
    Discovers the current working mirror URL for Anna's Archive or AudiobookBay.
    These sites change domains frequently; this tool finds the live URL before scraping.
    Returns a MirrorResult containing the source name and its current URL.
    """
    search_terms = {
        "annas_archive":  "Anna's Archive current mirror working URL 2024",
        "audiobookbay":   "AudioBookBay current mirror working URL 2024",
    }
    results = tavily.search(query=search_terms[query.source], max_results=3)
    if not results["results"]:
        raise ValueError(f"Could not find a working mirror for {query.source}")
    return MirrorResult(source=query.source, url=results["results"][0]["url"])
```

### 12.5 `Find_ebook_link`

Takes the mirror URL from `search_current_mirror` and searches Anna's Archive for the specific book. Returns epub and mobi download links as `EbookLink` objects.

```python
# agent/tools/find_ebook_link.py
from tavily import TavilyClient
from langchain_core.tools import tool
from pydantic import BaseModel
from models.ebook import EbookLink
from config import TAVILY_API_KEY

tavily = TavilyClient(api_key=TAVILY_API_KEY)

class EbookQuery(BaseModel):
    title:      str
    author:     str
    year:       str | None = None
    mirror_url: str         # current Anna's Archive URL from search_current_mirror

@tool
async def find_ebook_link(query: EbookQuery) -> list[EbookLink]:
    """
    Searches Anna's Archive (via the current mirror URL) for the specified book.
    Returns a list of EbookLink objects for epub and mobi formats.
    The mirror_url must be obtained from search_current_mirror first.
    """
    search_query = (
        f"\"{query.title}\" {query.author} {query.year or ''} "
        f"epub mobi download site:{query.mirror_url}"
    )
    results = tavily.search(query=search_query, max_results=6)
    links = []
    for r in results["results"]:
        url = r["url"]
        fmt = "epub" if "epub" in url.lower() else "mobi" if "mobi" in url.lower() else "epub"
        links.append(EbookLink(source="Anna's Archive", format=fmt, url=url))
    return links
```

### 12.6 `Find_audiobook_link`

Takes the mirror URL from `search_current_mirror` and searches AudiobookBay for the specific book. Returns `AudiobookLink` objects.

```python
# agent/tools/find_audiobook_link.py
from tavily import TavilyClient
from langchain_core.tools import tool
from pydantic import BaseModel
from models.audiobook import AudiobookLink
from config import TAVILY_API_KEY

tavily = TavilyClient(api_key=TAVILY_API_KEY)

class AudiobookQuery(BaseModel):
    title:      str
    author:     str
    mirror_url: str   # current AudiobookBay URL from search_current_mirror

@tool
async def find_audiobook_link(query: AudiobookQuery) -> list[AudiobookLink]:
    """
    Searches AudiobookBay (via the current mirror URL) for the specified book.
    Returns a list of AudiobookLink objects with download URLs.
    The mirror_url must be obtained from search_current_mirror first.
    """
    search_query = (
        f"\"{query.title}\" {query.author} audiobook download site:{query.mirror_url}"
    )
    results = tavily.search(query=search_query, max_results=6)
    return [
        AudiobookLink(source="AudiobookBay", url=r["url"])
        for r in results["results"]
    ]
```

---

## 13. Edge Cases

### Unclear Prompt

If `parse_query` returns a `ParsedQuery` with no intent, the agent asks a clarifying question:

```python
if not state.parsed_query or not state.parsed_query.intent:
    return state.model_copy(update={
        "output": "I wasn't sure what you're looking for. "
                  "Are you searching for a book, looking to buy one, "
                  "or want to download an ebook or audiobook?"
    })
```

### No Books Found

If `search_books` returns an empty list after reflection:

```python
if not state.books:
    return state.model_copy(update={
        "output": "I couldn't find any books matching your query. "
                  "Could you provide more details such as the author, genre, or year of publication?"
    })
```

### API Timeout / Connection Error

All external tool calls use the `tenacity` library for retry with exponential backoff:

```python
from tenacity import retry, stop_after_delay, wait_exponential, retry_if_exception_type
import httpx

@retry(
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    stop=stop_after_delay(30),                        # give up after 30 seconds total
    wait=wait_exponential(multiplier=1, min=1, max=10),  # 1s → 2s → 4s → ...
    reraise=True
)
async def call_with_retry(fn, *args, **kwargs):
    return await fn(*args, **kwargs)
```

### MongoDB Unavailable

The checkpointer falls back to `MemorySaver` (see Section 10). Every prompt in the degraded session is treated as a new conversation. A warning is logged to LangSmith.

---

## 14. LangSmith Metrics

LangSmith captures all metrics automatically via tracing. Set `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_PROJECT=book-ninja` in the environment.

| Metric | What it measures |
|---|---|
| Latency per node | Time each graph node takes to complete |
| End-to-end response time | Total time from API request to response |
| Traces for failed requests | Full execution trace for any request that errors |
| Reflection iteration count | How many reflection loops ran per search request |
| Node routing accuracy | Which nodes are selected; used to audit routing logic |
| Tool call success rate | % of tool calls that return valid results vs. errors |
| Tokens used per model | Input/output token counts for gpt-4o-mini and gpt-4o separately |
| Cost per session | Total token spend per thread (derived from token counts) |
| Fallback/clarification rate | How often the agent returns a clarifying question instead of a result |

Custom metrics are logged as LangSmith feedback:

```python
from langsmith import Client

ls_client = Client()

def log_fallback(run_id: str) -> None:
    ls_client.create_feedback(run_id, key="fallback", score=1)

def log_cost(run_id: str, cost_usd: float) -> None:
    ls_client.create_feedback(run_id, key="cost_usd", score=cost_usd)
```

---

## 15. Database — MongoDB

```python
# db/mongo.py
from motor.motor_asyncio import AsyncIOMotorClient
from models.user import UserRecord
from models.thread import ThreadRecord
from config import MONGO_URI
from datetime import datetime, timezone

client      = AsyncIOMotorClient(MONGO_URI)
db          = client["book_ninja"]
users_col   = db["users"]
threads_col = db["threads"]

async def ping_mongo() -> bool:
    try:
        await client.admin.command("ping")
        return True
    except Exception:
        return False

async def save_user(user: UserRecord) -> None:
    """Upsert user by google_id — safe to call on every authenticated request."""
    await users_col.update_one(
        {"google_id": user.google_id},
        {"$set": user.model_dump()},
        upsert=True
    )

async def get_latest_threads(user_id: str, limit: int = 5) -> list[ThreadRecord]:
    cursor = threads_col.find(
        {"user_id": user_id},
        {"_id": 0, "thread_id": 1, "preview": 1, "timestamp": 1}
    ).sort("timestamp", -1).limit(limit)
    raw = await cursor.to_list(length=limit)
    return [ThreadRecord(**r) for r in raw]
```

### Deployment

MongoDB is hosted on **Clever Cloud** for cloud deployments. Clever Cloud provides a managed MongoDB add-on with automated backups and connection string injection via environment variables.

---

## 16. Testing

### Running Tests

```bash
pytest                                       # all tests
pytest --cov=. --cov-report=term-missing     # with coverage report
pytest tests/test_chat.py -v                 # specific file
```

### Coverage Target
80% across all modules.

### Example Tests

```python
# tests/test_validation.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

MOCK_USER = {"sub": "user123", "email": "test@test.com"}

@patch("api.middleware.auth.validate_google_token", return_value=MOCK_USER)
def test_empty_prompt_returns_400(_):
    res = client.post("/chat", json={"prompt": ""})
    assert res.status_code == 400
    assert "empty" in res.json()["detail"].lower()

@patch("api.middleware.auth.validate_google_token", return_value=MOCK_USER)
def test_prompt_too_long_returns_400(_):
    res = client.post("/chat", json={"prompt": "a" * 3001})
    assert res.status_code == 400
    assert "maximum length" in res.json()["detail"].lower()

def test_health_returns_all_integration_statuses():
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert "status" in body
    assert set(body["integrations"].keys()) == {"hardcover", "mongodb", "tavily", "langsmith"}

# tests/test_tools.py
from models.query import ParsedQuery
from models.book import BookResult

def test_parsed_query_rejects_invalid_intent():
    with pytest.raises(Exception):
        ParsedQuery(title="Dune", intent="unknown_intent")

def test_book_result_requires_title_and_author():
    with pytest.raises(Exception):
        BookResult(summary="A great book", hardcover_url="https://hardcover.app/books/dune")
```

---

## 17. CI/CD

```yaml
# .github/workflows/backend.yml
name: Backend CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: flake8 .                                   # Lint
      - run: pytest --cov=. --cov-fail-under=80        # Test + Coverage (fails if < 80%)
      - name: Build Docker image
        run: docker build -t book-ninja-backend .
      - name: Push to registry
        if: github.ref == 'refs/heads/main'
        run: |
          echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
          docker push book-ninja-backend:latest
```

---

## 18. Deployment

### Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### AWS ECS / GCP Cloud Run

The Docker image is pushed to a container registry (ECR or Artifact Registry) and deployed as a container service. Both support environment variable injection from secrets managers, keeping credentials out of the image.

### Environments

| Environment | Branch | Purpose |
|---|---|---|
| Development | `develop` | Local and PR testing |
| Staging | `staging` | Pre-production validation |
| Production | `main` | Live traffic |

Each environment has its own MongoDB database, separate LangSmith project, and separate set of secrets.
