import logging
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException
from langchain_core.tools import tool

from models.ebook import EbookLink, EbookQuery

logger = logging.getLogger(__name__)


@tool
async def find_ebook_link(query: EbookQuery) -> list[EbookLink]:
    """
    Searches Anna's Archive for the specified book and returns the first result URL.
    The mirror_url must be obtained from search_current_mirror first.
    """
    fmt = query.format if hasattr(query, "format") else "epub"
    q = f"{quote_plus(query.title)}%2B{quote_plus(query.author)}%2B{quote_plus(fmt)}"
    mirror_url = query.mirror_url.rstrip("/")
    search_url = f"{mirror_url}/search?index=&page=1&sort=&display=&q={q}"
    logger.info("Anna's Archive search URL: %s", search_url)

    for attempt in range(3):
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
                r = await client.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
                r.raise_for_status()
            break
        except (httpx.HTTPError, httpx.RequestError) as e:
            logger.warning("Attempt %d/3 failed for Anna's Archive: %s", attempt + 1, e)
            if attempt == 2:
                raise HTTPException(status_code=500, detail="Anna's Archive is currently unavailable")

    soup = BeautifulSoup(r.content, "html.parser")
    upper_title = query.title.strip().upper()
    all_tags = soup.find_all(
        lambda tag: tag.name == "a" and tag.text.strip().upper() == upper_title
    )
    if len(all_tags) == 0:
        all_tags = soup.find_all(
            lambda tag: tag.name == "a" and tag.text.strip().upper().startswith(upper_title)
        )
    if len(all_tags) == 0:
        logger.info("No ebook result found for: %s by %s", query.title, query.author)
        return []

    href = all_tags[0].get("href", "")
    if href.startswith("/"):
        href = mirror_url + href

    logger.info("Found ebook URL: %s", href)
    return [EbookLink(source="Anna's Archive", format="epub", url=href)]
