import json
import logging
import re

from langchain_openai import ChatOpenAI

from models.agent import AgentState
from utils.llm_stream import collect_stream

logger = logging.getLogger(__name__)

_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def _extract_indices(raw_content: object) -> list[int]:
    """Parse a list of integer indices from strict JSON or mixed text output."""
    content = raw_content if isinstance(raw_content, str) else str(raw_content)

    # Best case: model returns a plain JSON array like `[0, 2]`.
    try:
        parsed = json.loads(content)
        if isinstance(parsed, list):
            return [int(x) for x in parsed if isinstance(x, int)]
    except json.JSONDecodeError:
        pass

    # Common fallback: model wraps the JSON in explanation/code fences.
    match = re.search(r"\[[\s\d,]+\]", content)
    if not match:
        raise ValueError("No JSON-style index array found in model response")

    fallback = json.loads(match.group(0))
    return [int(x) for x in fallback if isinstance(x, int)]


async def validate_audiobook_node(state: AgentState) -> AgentState:
    """
    Filters audio_links using GPT-4o-mini, keeping only results whose title
    matches the book and author from parsed_query.
    """
    if not state.audio_links:
        return state

    pq = state.parsed_query
    title = (pq.title or "") if pq else ""
    author = (pq.author or "") if pq else ""

    numbered = "\n".join(f"{i}. {link.title}" for i, link in enumerate(state.audio_links))

    prompt = (
        f'You are a filter. Given a target audiobook and a list of scraped result titles, '
        f'return a JSON array of the indices (0-based) of results that match the target book.\n\n'
        f'Target: "{title}" by {author}\n\n'
        f'Results:\n{numbered}\n\n'
        f'Reply ONLY with a JSON array of integer indices to keep (e.g. [0, 2]). '
        f'If none match, return [].'
        f'Example if the Title is "It" and Author is "Stephen King", and one the results is '
        f'"title": "The End of the World As We Know It - Stephen King, Christopher Golden, Brian Keene" then ignore it since its not the same book as It'
    )

    response = await collect_stream(_llm.astream(prompt))
    response_content = getattr(response, "content", str(response))
    try:
        indices = _extract_indices(response_content)
        filtered = [state.audio_links[i] for i in indices if 0 <= i < len(state.audio_links)]
    except Exception:
        logger.warning("Failed to parse audiobook validation response; keeping all links")
        filtered = state.audio_links

    if not filtered:
        return state.model_copy(update={
            "audio_links": [],
            "output": "I couldn't find any matching audiobook download links for that book.",
        })

    lines = [f"- [{link.title}]({link.url})" for link in filtered]
    return state.model_copy(update={
        "audio_links": filtered,
        "output": "Here are audiobook download links:\n" + "\n".join(lines),
    })
