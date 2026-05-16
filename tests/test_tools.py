import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from models.query import ParsedQuery
from models.purchase import PurchaseQuery
from models.ebook import EbookQuery
from models.audiobook import AudiobookQuery
from models.mirror import MirrorQuery


def test_parsed_query_valid_intent_search():
    q = ParsedQuery(title="Dune", author="Frank Herbert", intent="search")
    assert q.intent == "search"


def test_parsed_query_valid_intent_ebook():
    q = ParsedQuery(title="Dune", intent="ebook")
    assert q.intent == "ebook"


def test_parsed_query_rejects_invalid_intent():
    with pytest.raises(Exception):
        ParsedQuery(title="Dune", intent="stream")


def test_purchase_query_format():
    q = PurchaseQuery(title="Dune", author="Frank Herbert", format="ebook")
    assert q.format == "ebook"


def test_ebook_query_requires_mirror_url():
    with pytest.raises(Exception):
        EbookQuery(title="Dune", author="Frank Herbert")


def test_audiobook_query_requires_mirror_url():
    with pytest.raises(Exception):
        AudiobookQuery(title="Dune", author="Frank Herbert")


def test_mirror_query_annas_archive():
    q = MirrorQuery(source="annas_archive")
    assert q.source == "annas_archive"


def test_mirror_query_audiobookbay():
    q = MirrorQuery(source="audiobookbay")
    assert q.source == "audiobookbay"


async def test_find_purchase_links_returns_list():
    mock_results = {
        "results": [
            {"title": "Dune on Amazon", "url": "https://amazon.com/dune"},
            {"title": "Dune on Kobo", "url": "https://kobo.com/dune"},
        ]
    }
    with patch("agent.tools.find_purchase_links.asyncio.to_thread", new_callable=AsyncMock,
               return_value=mock_results):
        from agent.tools.find_purchase_links import find_purchase_links
        query = PurchaseQuery(title="Dune", author="Frank Herbert", format="ebook")
        result = await find_purchase_links.ainvoke(query)
        assert len(result) == 2
        assert result[0].store == "Dune on Amazon"


async def test_search_current_mirror_returns_url():
    mock_results = {
        "results": [{"url": "https://annas-archive.org", "title": "Anna's Archive"}]
    }
    with patch("agent.tools.search_current_mirror.asyncio.to_thread", new_callable=AsyncMock,
               return_value=mock_results):
        from agent.tools.search_current_mirror import search_current_mirror
        result = await search_current_mirror.ainvoke(MirrorQuery(source="annas_archive"))
        assert result.url == "https://annas-archive.org"
        assert result.source == "annas_archive"


async def test_search_current_mirror_raises_when_no_results():
    mock_results = {"results": []}
    with patch("agent.tools.search_current_mirror.asyncio.to_thread", new_callable=AsyncMock,
               return_value=mock_results):
        from agent.tools.search_current_mirror import search_current_mirror
        with pytest.raises(ValueError):
            await search_current_mirror.ainvoke(MirrorQuery(source="annas_archive"))
