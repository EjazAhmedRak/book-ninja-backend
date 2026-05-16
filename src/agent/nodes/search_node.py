from langchain_openai import ChatOpenAI
from models.agent import AgentState
from models.book import BookResult
from agent.tools.search_books import search_books
from agent.tools.parse_query import parse_query

search_llm  = ChatOpenAI(model="gpt-4o-mini")
reflect_llm = ChatOpenAI(model="gpt-4o")


def _format_results(books: list[BookResult]) -> str:
    if not books:
        return (
            "I couldn't find any books matching your query. "
            "Could you provide more details such as the author, genre, or year of publication?"
        )
    lines = []
    for b in books:
        lines.append(f"- {b.title} by {b.author} ({b.year or 'N/A'}) — Rating: {b.rating}")
        lines.append(f"  {b.summary[:200]}")
        lines.append(f"  {b.hardcover_url}")
    return "\n".join(lines)


def _extract_refined_query(reflection_content: str) -> str | None:
    """Pulls a refined search query from the reflection response if present."""
    marker = "refined query:"
    lower = reflection_content.lower()
    if marker in lower:
        idx = lower.index(marker) + len(marker)
        return reflection_content[idx:].strip().split("\n")[0].strip()
    return None


async def search_books_node(state: AgentState) -> AgentState:
    """
    Searches for books using the search_books tool.
    Runs up to 2 reflection iterations with gpt-4o to improve results.
    Exits early if the reflection model deems results "satisfactory".
    """
    results = await search_books.ainvoke({"query": state.parsed_query.model_dump()})

    for _ in range(2):
        reflection = await reflect_llm.ainvoke(
            f"Review these book search results for relevance and completeness:\n{results}\n"
            f"Original query: {state.prompt}\n"
            "Are the results relevant and complete? If not, suggest a refined search query."
        )
        if "satisfactory" in reflection.content.lower():
            break
        refined = _extract_refined_query(reflection.content)
        if refined:
            refined_parsed = await parse_query.ainvoke({"prompt": refined})
            results = await search_books.ainvoke({"query": refined_parsed.model_dump()})

    return state.model_copy(update={
        "books": results,
        "output": _format_results(results),
    })
