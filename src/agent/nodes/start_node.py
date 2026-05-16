from models.agent import AgentState
from agent.tools.parse_query import parse_query


async def start_node(state: AgentState) -> AgentState:
    """
    First node in the agent graph.
    Runs parse_query tool on state.prompt.
    Sets state.parsed_query and state.intent for conditional routing.
    If intent cannot be determined, sets state.output to a clarifying question.
    """
    parsed = await parse_query.ainvoke({"prompt": state.prompt})
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
