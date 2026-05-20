from models.agent import AgentState
from agent.tools.parse_query import parse_query


def _forced_intent_from_prompt(prompt: str) -> str | None:
    """
    Deterministic guardrail for explicit user intents that should not be misrouted.
    """
    lower = prompt.lower()
    if "audiobook" in lower and any(k in lower for k in ("download", "listen", "audio book")):
        return "audiobook"
    if "ebook" in lower and any(k in lower for k in ("download", "epub", "mobi")):
        return "ebook"
    return None


async def start_node(state: AgentState) -> AgentState:
    """
    First node in the agent graph.
    Runs parse_query tool on state.prompt.
    Sets state.parsed_query and state.intent for conditional routing.
    If intent cannot be determined, sets state.output to a clarifying question.
    """
    parsed = await parse_query.ainvoke({"prompt": state.prompt})
    forced_intent = _forced_intent_from_prompt(state.prompt)
    if parsed and forced_intent and parsed.intent != forced_intent:
        parsed = parsed.model_copy(update={"intent": forced_intent})

    if not parsed or not parsed.intent:
        return state.model_copy(update={
            "output": (
                "I wasn't sure what you're looking for. "
                "Are you searching for a book, looking to buy one, "
                "or want to download an ebook or audiobook?"
            )
        })
    return state.model_copy(update={
        "parsed_query": parsed,
        "intent": parsed.intent,
    })
