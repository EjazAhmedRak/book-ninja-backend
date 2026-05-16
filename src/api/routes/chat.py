from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from models.agent import AgentState
from models.user import UserRecord
from api.middleware.auth import validate_google_token, GoogleUser
from api.middleware.validation import validate_prompt
from agent.graph import run_agent
from db.mongo import save_user, save_thread

router = APIRouter()


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


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request, user: GoogleUser = Depends(validate_google_token)):
    """Main agent endpoint. Requires a valid Google ID token."""
    validate_prompt(req.prompt)
    await save_user(UserRecord(email=user.email, google_id=user.sub))
    result = await run_agent(
        graph=request.app.state.graph,
        prompt=req.prompt,
        user_id=user.sub,
        thread_id=req.thread_id,
    )
    await save_thread(user_id=user.sub, thread_id=result.thread_id, prompt=req.prompt)
    return ChatResponse(
        output=result.output or "",
        thread_id=result.thread_id,
        books=_extract_books(result),
    )
