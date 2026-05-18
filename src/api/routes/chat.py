import json
import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent.graph import stream_agent
from api.middleware.auth import GoogleUser, validate_google_token
from api.middleware.validation import validate_prompt
from db.mongo import save_thread, save_user
from models.agent import AgentState
from models.user import UserRecord

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    prompt:    str
    thread_id: str | None = None


class BookEntry(BaseModel):
    title:  str
    author: str | None = None
    year:   str | None = None
    url:    str
    rating: float | None = None


class ChatResponse(BaseModel):
    output:    str
    thread_id: str
    books:     list[BookEntry] = []


NODE_STATUS_MESSAGES = {
    "start": "Parsing your request.",
    "search_books": "Searching book catalog and ranking matches.",
    "purchase": "Finding purchase options.",
    "download_ebook": "Finding ebook download links.",
    "download_audiobook": "Finding audiobook download links.",
    "validate_audiobook": "Validating audiobook link relevance.",
}


def _status_message(node_name: str, state: AgentState) -> str:
    if node_name == "start" and state.intent:
        return f"Request parsed. Detected intent: {state.intent}."
    return NODE_STATUS_MESSAGES.get(node_name, f"Completed step: {node_name}.")


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _extract_books(state: AgentState) -> list[BookEntry]:
    if state.intent == "search" and state.books:
        return [
            BookEntry(title=b.title, author=b.author, year=b.year, url=b.hardcover_url, rating=b.rating)
            for b in state.books
        ]
    pq = state.parsed_query
    if state.intent == "purchase" and state.links and pq:
        return [
            BookEntry(title=pq.title or "", author=pq.author or "", year=pq.year, url=link.url)
            for link in state.links
        ]
    if state.intent == "ebook" and state.ebook_links and pq:
        return [
            BookEntry(title=pq.title or "", author=pq.author or "", year=pq.year, url=link.url)
            for link in state.ebook_links
        ]
    if state.intent == "audiobook" and state.audio_links and pq:
        return [
            BookEntry(title=link.title, author=None, year=None, url=link.url)
            for link in state.audio_links
        ]
    return []


@router.post("/chat")
async def chat(req: ChatRequest, request: Request, user: GoogleUser = Depends(validate_google_token)):
    """Main agent endpoint. Requires a valid Google ID token."""
    validate_prompt(req.prompt)
    await save_user(UserRecord(email=user.email, google_id=user.sub))

    async def event_stream() -> AsyncIterator[str]:
        latest_state: AgentState | None = None
        try:
            async for node_name, state in stream_agent(
                graph=request.app.state.graph,
                prompt=req.prompt,
                user_id=user.sub,
                thread_id=req.thread_id,
            ):
                latest_state = state
                yield _sse("status", {
                    "node": node_name,
                    "message": _status_message(node_name, state),
                    "thread_id": state.thread_id,
                })

            if latest_state is None:
                return

            await save_thread(user_id=user.sub, thread_id=latest_state.thread_id, prompt=req.prompt)

            final = ChatResponse(
                output=latest_state.output or "",
                thread_id=latest_state.thread_id,
                books=_extract_books(latest_state),
            )
            yield _sse("final", final.model_dump())
        except Exception:
            logger.exception("Error while streaming /chat response")
            yield _sse("error", {"message": "An unexpected error occurred while processing the request."})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
