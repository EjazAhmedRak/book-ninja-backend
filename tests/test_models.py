import pytest
from models.query import ParsedQuery
from models.book import BookResult
from models.purchase import PurchaseLink, PurchaseQuery
from models.ebook import EbookLink, EbookQuery
from models.audiobook import AudiobookLink, AudiobookQuery
from models.mirror import MirrorQuery, MirrorResult
from models.thread import ThreadRecord, ThreadsResponse
from models.health import HealthResponse
from models.agent import AgentState
from models.user import UserRecord
from datetime import datetime, timezone


def test_parsed_query_accepts_valid_intent():
    q = ParsedQuery(title="Dune", intent="search")
    assert q.intent == "search"


def test_parsed_query_rejects_invalid_intent():
    with pytest.raises(Exception):
        ParsedQuery(title="Dune", intent="unknown_intent")


def test_parsed_query_all_fields_optional():
    q = ParsedQuery()
    assert q.title is None
    assert q.intent is None


def test_book_result_requires_title_and_author():
    with pytest.raises(Exception):
        BookResult(summary="A great book", hardcover_url="https://hardcover.app/books/dune")


def test_book_result_valid():
    b = BookResult(
        title="Dune",
        author="Frank Herbert",
        summary="Epic sci-fi",
        hardcover_url="https://hardcover.app/books/dune",
        rating=4.8,
    )
    assert b.title == "Dune"
    assert b.rating == 4.8


def test_purchase_link_requires_url():
    with pytest.raises(Exception):
        PurchaseLink(store="Amazon")


def test_ebook_link_format_literal():
    link = EbookLink(source="Anna's Archive", format="epub", url="https://example.com/book.epub")
    assert link.format == "epub"


def test_ebook_link_rejects_invalid_format():
    with pytest.raises(Exception):
        EbookLink(source="Anna's Archive", format="pdf", url="https://example.com/book.pdf")


def test_mirror_query_valid():
    q = MirrorQuery(source="annas_archive")
    assert q.source == "annas_archive"


def test_mirror_query_rejects_invalid_source():
    with pytest.raises(Exception):
        MirrorQuery(source="piratebay")


def test_thread_record_valid():
    t = ThreadRecord(
        thread_id="user123_abc",
        preview="Find me a book about Python",
        timestamp=datetime.now(timezone.utc),
    )
    assert t.thread_id == "user123_abc"


def test_health_response_valid():
    h = HealthResponse(
        status="ok",
        integrations={"hardcover": "ok", "mongodb": "ok", "tavily": "ok", "langsmith": "ok"},
    )
    assert h.status == "ok"


def test_agent_state_defaults():
    state = AgentState(prompt="find Dune", user_id="u1", thread_id="u1_abc")
    assert state.books == []
    assert state.output is None


def test_agent_state_immutable_copy():
    state = AgentState(prompt="find Dune", user_id="u1", thread_id="u1_abc")
    updated = state.model_copy(update={"output": "Here are results"})
    assert state.output is None
    assert updated.output == "Here are results"


def test_user_record_requires_valid_email():
    with pytest.raises(Exception):
        UserRecord(email="not-an-email", google_id="abc")


def test_user_record_valid():
    u = UserRecord(email="test@example.com", google_id="google123")
    assert u.google_id == "google123"
