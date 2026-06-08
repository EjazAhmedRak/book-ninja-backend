import logging

import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException
from langchain_core.tools import tool

from models.audiobook import AudiobookLink, AudiobookQuery

logger = logging.getLogger(__name__)


@tool
async def find_audiobook_link(query: AudiobookQuery) -> list[AudiobookLink]:
    """
    Searches AudiobookBay (via the current mirror URL) for the specified book.
    Returns a list of AudiobookLink objects with download URLs.
    The mirror_url must be obtained from search_current_mirror first.
    """
    mirror_url = query.mirror_url.rstrip("/")
    author_parts = query.author.split(" ")
    search_url = f"{mirror_url}/?s=%22{query.title}+{'+'.join(author_parts)}%22"
    logger.info("AudiobookBay search URL: %s", search_url)

    for attempt in range(3):
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
                r = await client.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
                r.raise_for_status()
            break
        except (httpx.HTTPError, httpx.RequestError) as e:
            logger.warning("Attempt %d/3 failed for AudiobookBay: %s", attempt + 1, e)
            if attempt == 2:
                raise HTTPException(status_code=500, detail="AudiobookBay is currently unavailable")

    soup = BeautifulSoup(r.content, "html.parser")
    title_divs = soup.find_all("div", class_="postTitle")

    links = []
    for div in title_divs:
        a_tag = div.find("a")
        if not a_tag:
            continue
        href = a_tag.get("href", "")
        if not href:
            continue
        if not href.startswith("http"):
            href = mirror_url + href
        links.append(AudiobookLink(source="AudiobookBay", title=a_tag.text.strip(), url=href))

    if not links:
        logger.info("No audiobook result found for: %s by %s", query.title, query.author)

    return links
