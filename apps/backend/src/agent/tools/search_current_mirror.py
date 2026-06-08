import asyncio
import re

import httpx
from ddgs import DDGS
from fastapi import logger
from langchain_core.tools import tool

from config import AUDIOBOOKBAY_FALLBACK_URL
from models.mirror import MirrorQuery, MirrorResult

_ANNAS_ARCHIVE_PAGE = "https://shadowlibraries.github.io/DirectDownloads/AnnasArchive/"
_AUDIOBOOKBAY_SEARCH = "Audiobookbay"

_HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)


async def _get_mirror_links(page_url: str) -> list[str]:
    """Fetches the links page and returns external URLs, excluding the host itself."""
    async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
        r = await client.get(page_url)
        r.raise_for_status()
    return [
        href for href in _HREF_RE.findall(r.text)
        if href.startswith("http") and "github" not in href
    ]


async def _is_reachable(url: str) -> bool:
    """Returns True if the URL responds with a non-error HTTP status."""
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            r = await client.head(url)
            return r.status_code < 400
    except Exception:
        return False


def _ddg_search(query: str, max_results: int) -> list[dict]:
    """Synchronous DuckDuckGo text search — invoked via asyncio.to_thread."""
    with DDGS() as ddgs:
        return ddgs.text(query, max_results=max_results)


@tool
async def search_current_mirror(query: MirrorQuery) -> MirrorResult:
    """
    Discovers the current working mirror URL for Anna's Archive or AudiobookBay.
    For Anna's Archive: scrapes the shadow libraries links page and validates
    the first reachable URL. For AudiobookBay: uses DuckDuckGo to find the
    first result whose URL contains 'audiobookbay'.
    """
    if query.source == "annas_archive":
        links = await _get_mirror_links(_ANNAS_ARCHIVE_PAGE)
        for link in links[:2]:
            if await _is_reachable(link):
                clean_url = link.split("?", 1)[0].rstrip("/")
                return MirrorResult(source=query.source, url=clean_url)
        raise ValueError("Could not find a reachable Anna's Archive mirror")

    for _ in range(3):
        results = await asyncio.to_thread(_ddg_search, _AUDIOBOOKBAY_SEARCH, 10)
        for r in results:
            url = r.get("href", "")
            if "https://audiobookbay." in url.lower() and "shop" not in url.lower():
                return MirrorResult(source=query.source, url=url)
    logger.info(f"Failed to find AudiobookBay mirror via DuckDuckGo search after 3 attempts. Using fallback URL: {AUDIOBOOKBAY_FALLBACK_URL}")
    return MirrorResult(source=query.source, url=AUDIOBOOKBAY_FALLBACK_URL)
