from venv import logger

from models.agent import AgentState
from models.mirror import MirrorQuery
from models.audiobook import AudiobookQuery
from agent.tools.search_current_mirror import search_current_mirror
from agent.tools.find_audiobook_link import find_audiobook_link


async def audiobook_node(state: AgentState) -> AgentState:
    """
    Finds audiobook download links.
    First discovers the current AudiobookBay mirror, then searches for the book.
    Sets state.audio_links and state.output.
    """
    mirror = await search_current_mirror.ainvoke({"query": {"source": "audiobookbay"}})
    query = AudiobookQuery(
        title=state.parsed_query.title or state.prompt,
        author=state.parsed_query.author or "",
        mirror_url=mirror.url,
    )
    logger.info("Mirror url for AudiobookBay: %s", mirror.url)
    links = await find_audiobook_link.ainvoke({"query": query.model_dump()})
    if not links:
        return state.model_copy(update={
            "output": "I couldn't find any audiobook download links for that book."
        })
    lines = [f"- [{link.title}]({link.url})" for link in links]
    return state.model_copy(update={
        "mirror_url": mirror.url,
        "audio_links": links,
        "output": "Here are audiobook download links:\n" + "\n".join(lines),
    })
