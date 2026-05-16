from models.agent import AgentState
from models.mirror import MirrorQuery
from models.ebook import EbookQuery
from agent.tools.search_current_mirror import search_current_mirror
from agent.tools.find_ebook_link import find_ebook_link


async def ebook_node(state: AgentState) -> AgentState:
    """
    Finds ebook download links.
    First discovers the current Anna's Archive mirror, then searches for the book.
    Sets state.ebook_links and state.output.
    """
    mirror = await search_current_mirror.ainvoke({"query": {"source": "annas_archive"}})
    query = EbookQuery(
        title=state.parsed_query.title or state.prompt,
        author=state.parsed_query.author or "",
        year=state.parsed_query.year,
        mirror_url=mirror.url,
    )
    links = await find_ebook_link.ainvoke({"query": query.model_dump()})
    if not links:
        return state.model_copy(update={
            "output": "I couldn't find any ebook download links for that book."
        })
    lines = [f"- [{link.format.upper()}]({link.url}) via {link.source}" for link in links]
    return state.model_copy(update={
        "mirror_url": mirror.url,
        "ebook_links": links,
        "output": "Here are ebook download links:\n" + "\n".join(lines),
    })
