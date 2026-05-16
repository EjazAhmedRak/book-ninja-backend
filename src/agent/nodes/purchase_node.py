from models.agent import AgentState
from models.purchase import PurchaseQuery
from agent.tools.find_purchase_links import find_purchase_links


async def purchase_node(state: AgentState) -> AgentState:
    """
    Finds purchase links for the book in state.parsed_query.
    Sets state.links and state.output.
    """
    query = PurchaseQuery(
        title=state.parsed_query.title or state.prompt,
        author=state.parsed_query.author or "",
        year=state.parsed_query.year,
        format=state.parsed_query.format or "ebook",
    )
    links = await find_purchase_links.ainvoke({"query": query.model_dump()})
    if not links:
        return state.model_copy(update={
            "output": "I couldn't find any purchase links for that book. Try a different search."
        })
    lines = [f"- [{link.store}]({link.url})" for link in links]
    return state.model_copy(update={
        "links": links,
        "output": "Here are some places to purchase the book:\n" + "\n".join(lines),
    })
